from django.db.models import Count, F, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _
from wbcore import filters as wb_filters
from wbcore.contrib.directory.models import Person

from wbcompliance.models.risk_management import RiskRule, RuleThreshold

from ...models.risk_management.rules import RuleGroup
from .utils import get_default_handler


class RiskRuleFilterSet(wb_filters.FilterSet):
    checked_object_relationships = wb_filters.MultipleChoiceContentTypeFilter(
        label="Checked Objects",
        field_name="checked_object_relationships",
        distinct=True,
        object_id_label="checked_object_relationships__checked_object_id",
        content_type_label="checked_object_relationships__checked_object_content_type",
        hidden=True,
    )

    exclude_informational_rule = wb_filters.BooleanFilter(
        method="filter_exclude_informational_rule", initial=True, label=_("Exclude Informational Rule")
    )
    rule_group = wb_filters.ModelChoiceFilter(
        label=_("Group"),
        queryset=RuleGroup.objects.all(),
        endpoint=RuleGroup.get_representation_endpoint(),
        value_key=RuleGroup.get_representation_value_key(),
        label_key=RuleGroup.get_representation_label_key(),
        method="filter_rule_group",
    )

    def filter_rule_group(self, queryset, label, value):
        if value:
            return queryset.filter(Q(rule_backend__rule_group=value) | Q(rule_backend__rule_group__isnull=True))
        return queryset

    def filter_exclude_informational_rule(self, queryset, label, value):
        if value:
            queryset = queryset.annotate(
                threshold_count=Coalesce(
                    Subquery(
                        RuleThreshold.objects.filter(rule=OuterRef("pk"))
                        .values("rule")
                        .annotate(c=Count("rule"))
                        .values("c")[:1]
                    ),
                    0,
                ),
                informational_count=Coalesce(
                    Subquery(
                        RuleThreshold.objects.filter(rule=OuterRef("pk"), severity__is_informational=True)
                        .values("rule")
                        .annotate(c=Count("rule"))
                        .values("c")[:1]
                    ),
                    0,
                ),
            )
            return queryset.exclude(Q(threshold_count=F("informational_count")) & ~Q(threshold_count=0))
        return queryset

    in_breach = wb_filters.ChoiceFilter(
        method="filter_in_breach",
        label=_("Open Incidents"),
        choices=[("BREACH", "In Breach"), ("PASSED", "Passed"), ("INACTIVE", "Inactive")],
    )
    open_incidents_count = wb_filters.NumberFilter(
        label=_("Opened Incident"), field_name="open_incidents_count", lookup_expr="exact"
    )
    open_incidents_count__lte = wb_filters.NumberFilter(
        label=_("Opened Incident"), field_name="open_incidents_count", lookup_expr="lte"
    )
    open_incidents_count__gte = wb_filters.NumberFilter(
        label=_("Opened Incident"), field_name="open_incidents_count", lookup_expr="gte"
    )
    notified_by = wb_filters.ModelChoiceFilter(
        label=_("Notifed Users"),
        initial=get_default_handler,
        queryset=Person.objects.all(),
        endpoint=Person.get_representation_endpoint(),
        value_key=Person.get_representation_value_key(),
        label_key=Person.get_representation_label_key(),
        method="filter_notified_by",
    )

    def filter_notified_by(self, queryset, name, value):
        if value:
            thresholds = RuleThreshold.objects.filter(
                Q(notifiable_users=value) | Q(notifiable_groups__in=value.user_account.groups.all())
            )
            return queryset.filter(thresholds__in=thresholds).distinct()
        return queryset

    def filter_in_breach(self, queryset, name, value):
        if value:
            return queryset.filter(in_breach=value)
        return queryset

    class Meta:
        model = RiskRule
        fields = {
            "rule_backend": ["exact"],
            "is_enable": ["exact"],
            "only_passive_check_allowed": ["exact"],
            "is_silent": ["exact"],
            "is_mandatory": ["exact"],
            "automatically_close_incident": ["exact"],
        }
