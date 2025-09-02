from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.api import warning
from django.contrib.postgres.fields.ranges import DateRangeField
from django.db.models import (
    Case,
    CharField,
    DateField,
    Exists,
    ExpressionWrapper,
    F,
    IntegerField,
    OuterRef,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Cast, Concat
from django.http import HttpResponse
from django.utils.functional import cached_property
from rest_framework import status
from rest_framework.decorators import action
from wbcore import viewsets
from wbcore.contrib.guardian.models import UserObjectPermission
from wbcore.contrib.icons import WBIcon

from wbcompliance.filters import (
    CheckedObjectIncidentRelationshipFilterSet,
    RiskIncidentFilterSet,
)
from wbcompliance.models import RuleThreshold
from wbcompliance.models.risk_management import (
    CheckedObjectIncidentRelationship,
    RiskIncident,
    RiskIncidentType,
    RiskRule,
)
from wbcompliance.models.risk_management.incidents import resolve_all_incidents_as_task
from wbcompliance.permissions import RulePermission
from wbcompliance.serializers import (
    CheckedObjectIncidentRelationshipModelSerializer,
    CheckedObjectIncidentRelationshipRepresentationSerializer,
    RiskIncidentModelSerializer,
    RiskIncidentRepresentationSerializer,
    RiskIncidentTypeRepresentationSerializer,
)
from wbcompliance.viewsets.buttons import RiskIncidentButtonConfig
from wbcompliance.viewsets.display import (
    CheckedObjectIncidentRelationshipRiskRuleDisplayConfig,
    RiskIncidentDisplayConfig,
)
from wbcompliance.viewsets.endpoints import (
    CheckedObjectIncidentRelationshipEndpointConfig,
    CheckedObjectIncidentRelationshipRiskRuleEndpointConfig,
    RiskIncidentEndpointConfig,
)

User = get_user_model()


class RiskIncidentTypeRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = RiskIncidentType.objects.all()
    serializer_class = RiskIncidentTypeRepresentationSerializer
    search_fields = ("name",)


class RiskIncidentRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = RiskIncident.objects.all()
    serializer_class = RiskIncidentRepresentationSerializer
    search_fields = (
        "rule__name",
        "breached_object_repr",
    )


class CheckedObjectIncidentRelationshipRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = CheckedObjectIncidentRelationship.objects.all()
    serializer_class = CheckedObjectIncidentRelationshipRepresentationSerializer


class RiskIncidentModelViewSet(viewsets.ModelViewSet):
    permission_classes = [RulePermission]
    display_config_class = RiskIncidentDisplayConfig
    endpoint_config_class = RiskIncidentEndpointConfig
    button_config_class = RiskIncidentButtonConfig

    ordering_fields = [
        "status",
        "date_range",
        "rule__name",
        "object_repr",
        "severity__name",
        "resolved_by__computed_str",
        "comment",
    ]
    ordering = ["-date_range", "-severity__severity_order", "id"]
    serializer_class = RiskIncidentModelSerializer
    queryset = RiskIncident.objects.select_related(
        "resolved_by",
        "breached_content_type",
        "rule",
        "severity",
    ).prefetch_related("checked_object_relationships")
    filterset_class = RiskIncidentFilterSet

    @action(detail=False, methods=["PATCH"])
    def resolveallincidents(self, request, pk=None):
        resolve_status = request.POST.get("resolve_status", RiskIncident.Status.RESOLVED.name)
        resolve_all_incidents_as_task.delay(
            request.user.id,
            request.POST.get("comment", ""),
            resolve_status == RiskIncident.Status.RESOLVED.name,
            rule_id=request.GET.get("rule_id", None),
        )
        return HttpResponse("All opened incidents are resolved", status=status.HTTP_200_OK)

    @cached_property
    def rule_content_type(self):
        return ContentType.objects.get_for_model(RiskRule)

    @cached_property
    def view_rule_permission(self):
        return Permission.objects.get(codename="view_riskrule", content_type__app_label="wbcompliance")

    def get_queryset(self):
        """
        We protect the queryset to allow only user to see their respective incidents
        """
        queryset = super().get_queryset()
        if not self.request.user.has_perm("administrate_riskrule"):
            queryset = queryset.annotate(
                rule_pk=Cast(
                    "rule_id", output_field=CharField()
                ),  # We need to cast the rule id into a charfield otherwise postgres complains with the operator
                have_view_permission_on_rule=Exists(
                    UserObjectPermission.objects.filter(
                        permission=self.view_rule_permission,
                        content_type=self.rule_content_type,
                        object_pk=OuterRef("rule_pk"),
                        user=self.request.user,
                    )
                ),
            ).filter(have_view_permission_on_rule=True)
        queryset = queryset.annotate(
            status_icon=Case(
                When(status=RiskIncident.Status.OPEN.value, then=Value(WBIcon.VIEW.icon)), default=Value(None)
            ),
            has_subincidents=Exists(CheckedObjectIncidentRelationship.objects.filter(incident=OuterRef("pk"))),
            _group_key=Case(When(has_subincidents=True, then=F("id")), default=None, output_field=IntegerField()),
            checked_date=ExpressionWrapper(F("date_range__endswith") - 1, output_field=DateField()),
            object_repr=Concat(Value("Breached: "), F("breached_object_repr")),
            threshold_repr=Subquery(
                RuleThreshold.objects.filter(severity=OuterRef("severity"), rule=OuterRef("rule")).values(
                    "computed_str"
                )[:1]
            ),
        )
        return queryset

    def add_messages(self, request, instance: RiskIncident | None = None, **kwargs):
        if instance:
            if instance.status == RiskIncident.Status.OPEN and instance.last_ignored_date:
                warning(
                    request,
                    f"This incident was automatically reopened after being ignored from {instance.last_ignored_date:%Y-%m-%d} to {instance.get_ignore_until_date():%Y-%m-%d}",
                )


class RiskIncidentRiskRuleModelViewSet(RiskIncidentModelViewSet):
    permission_classes = [RulePermission]

    def get_queryset(self):
        return super().get_queryset().filter(rule=self.kwargs["rule_id"])


class CheckedObjectIncidentRelationshipModelViewSet(viewsets.ModelViewSet):
    permission_classes = [RulePermission]
    ordering = ["-rule_check__evaluation_date"]
    ordering_fields = ["status", "object_repr", "checked_date"]
    serializer_class = CheckedObjectIncidentRelationshipModelSerializer
    queryset = CheckedObjectIncidentRelationship.objects.select_related(
        "resolved_by",
        "incident",
        "rule_check",
        "severity",
    ).annotate(
        object_repr=F("rule_check__checked_object_repr"),
        checked_date=F("rule_check__evaluation_date"),
        date_range=Cast(
            Concat(Value("["), F("checked_date"), Value(","), F("checked_date"), Value("]")),
            output_field=DateRangeField(),
        ),
        threshold_repr=Subquery(
            RuleThreshold.objects.filter(severity=OuterRef("severity"), rule=OuterRef("incident__rule")).values(
                "computed_str"
            )[:1]
        ),
    )
    display_config_class = CheckedObjectIncidentRelationshipRiskRuleDisplayConfig
    endpoint_config_class = CheckedObjectIncidentRelationshipEndpointConfig
    filterset_class = CheckedObjectIncidentRelationshipFilterSet


class CheckedObjectIncidentRelationshipRiskRuleModelViewSet(CheckedObjectIncidentRelationshipModelViewSet):
    endpoint_config_class = CheckedObjectIncidentRelationshipRiskRuleEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(incident=self.kwargs["incident_id"])
