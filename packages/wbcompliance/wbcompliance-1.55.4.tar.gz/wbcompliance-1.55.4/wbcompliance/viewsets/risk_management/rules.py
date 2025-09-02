import pandas as pd
from django.contrib.auth import get_user_model
from django.db.models import Case, CharField, Count, OuterRef, Q, Subquery, Value, When
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from wbcore import serializers as wb_serializers
from wbcore import viewsets
from wbcore.contrib.guardian.viewsets.mixins import GuardianFilterMixin
from wbcore.utils.date import get_date_interval_from_request

from wbcompliance.filters import RiskRuleFilterSet
from wbcompliance.models.risk_management import (
    RiskIncident,
    RiskRule,
    RuleBackend,
    RuleCheckedObjectRelationship,
    RuleThreshold,
)
from wbcompliance.models.risk_management.rules import RuleGroup, process_rule_as_task
from wbcompliance.permissions import RulePermission
from wbcompliance.serializers import (
    RiskRuleModelSerializer,
    RiskRuleRepresentationSerializer,
    RuleBackendRepresentationSerializer,
    RuleCheckedObjectRelationshipModelSerializer,
    RuleCheckedObjectRelationshipRepresentationSerializer,
    RuleGroupRepresentationSerializer,
    RuleThresholdModelSerializer,
    RuleThresholdRepresentationSerializer,
)
from wbcompliance.viewsets.buttons import RiskRuleButtonConfig
from wbcompliance.viewsets.display import (
    RiskRuleDisplayConfig,
    RuleCheckedObjectRelationshipRiskRuleDisplayConfig,
    RuleThresholdRiskRuleDisplayConfig,
)
from wbcompliance.viewsets.endpoints import (
    RiskRuleEndpointConfig,
    RuleCheckedObjectRelationshipRiskRuleEndpointConfig,
    RuleThresholdRiskRuleEndpointConfig,
)

User = get_user_model()


class RuleGroupRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = RuleGroup.objects.all()
    serializer_class = RuleGroupRepresentationSerializer
    search_fields = ("name",)


class RuleCheckedObjectRelationshipRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = RuleCheckedObjectRelationship.objects.all()
    serializer_class = RuleCheckedObjectRelationshipRepresentationSerializer
    search_fields = ("checked_object_repr",)


class RuleBackendRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = RuleBackend.objects.all()
    serializer_class = RuleBackendRepresentationSerializer
    search_fields = ("name",)


class RuleThresholdRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = RuleThreshold.objects.all()
    serializer_class = RuleThresholdRepresentationSerializer


class RiskRuleRepresentationViewSet(GuardianFilterMixin, viewsets.RepresentationViewSet):
    queryset = RiskRule.objects.all()
    serializer_class = RiskRuleRepresentationSerializer
    search_fields = (
        "name",
        "description",
        "rule_backend__name",
    )


class RuleThresholdRiskRuleModelViewSet(viewsets.ModelViewSet):
    permission_classes = [RulePermission]
    display_config_class = RuleThresholdRiskRuleDisplayConfig
    endpoint_config_class = RuleThresholdRiskRuleEndpointConfig
    queryset = RuleThreshold.objects.all()
    serializer_class = RuleThresholdModelSerializer
    filterset_fields = {
        "severity": ["exact"],
    }

    def get_queryset(self):
        return super().get_queryset().filter(rule_id=self.kwargs["rule_id"])


class RuleCheckedObjectRelationshipRiskRuleModelViewSet(viewsets.ModelViewSet):
    permission_classes = [RulePermission]
    display_config_class = RuleCheckedObjectRelationshipRiskRuleDisplayConfig
    endpoint_config_class = RuleCheckedObjectRelationshipRiskRuleEndpointConfig
    queryset = RuleCheckedObjectRelationship.objects.all()
    serializer_class = RuleCheckedObjectRelationshipModelSerializer
    search_fields = ["checked_object_repr"]
    filterset_fields = {
        "checked_object_repr": ["icontains"],
    }

    def get_queryset(self):
        return super().get_queryset().filter(rule_id=self.kwargs["rule_id"])


class RiskRuleModelViewSet(GuardianFilterMixin, viewsets.ModelViewSet):
    display_config_class = RiskRuleDisplayConfig
    endpoint_config_class = RiskRuleEndpointConfig
    button_config_class = RiskRuleButtonConfig

    queryset = RiskRule.objects.all()
    serializer_class = RiskRuleModelSerializer
    filterset_class = RiskRuleFilterSet

    search_fields = ("name", "description", "checked_object_relationships__checked_object_repr")
    ordering_fields = (
        "name",
        "is_enable",
        "only_passive_check_allowed",
        "is_silent",
        "is_mandatory",
        "open_incidents_count",
    )
    ordering = ("name",)

    def get_serializer_class(self):
        if "pk" in self.kwargs:
            if rule := self.get_object():
                parameter_fields = rule.rule_backend.backend_class.get_serializer_class().get_parameter_fields()

                class TmpSerializer(RiskRuleModelSerializer):
                    class Meta(RiskRuleModelSerializer.Meta):
                        flatten_fields = {
                            "parameters": wb_serializers.JSONTableField(
                                serializer_class=rule.rule_backend.backend_class.get_serializer_class(),
                                flatten_field_names=parameter_fields,
                            )
                        }

                return TmpSerializer
        return RiskRuleModelSerializer

    def _subquery_open_risk_incidents_count(self):
        queryset = RiskIncident.objects.filter(status=RiskIncident.Status.OPEN, rule=OuterRef("pk"))
        return Coalesce(Subquery(queryset.values("rule").annotate(c=Count("rule")).values("c")[:1]), 0)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                open_incidents_count=self._subquery_open_risk_incidents_count(),
                in_breach=Case(
                    When(Q(open_incidents_count__gt=0) & Q(is_enable=True), then=Value("BREACH")),
                    When(Q(open_incidents_count=0) & Q(is_enable=True), then=Value("PASSED")),
                    default=Value("INACTIVE"),
                    output_field=CharField(),
                ),
            )
            .select_related(
                "rule_backend",
                "creator",
            )
            .prefetch_related("incidents")
        )

    @action(detail=True, methods=["PATCH"])
    def recheck(self, request, pk=None):
        start, end = get_date_interval_from_request(request, request_type="POST")
        if start and end:
            rule = get_object_or_404(RiskRule, pk=pk)
            for evaluation_date in pd.date_range(start, end, freq="B"):
                process_rule_as_task.delay(rule.id, evaluation_date, override_incident=False)
            return HttpResponse("Rule is checking", status=status.HTTP_200_OK)
        return HttpResponse("Wrong arguments", status=status.HTTP_400_BAD_REQUEST)
