from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from wbcore import filters as wb_filters
from wbcore.signals.filters import add_filters

from wbcompliance.models.risk_management import CheckedObjectIncidentRelationship


def get_content_type_default(*args, **kwargs):
    content_type_id = (
        CheckedObjectIncidentRelationship.objects.values("rule_check__checked_object_content_type")
        .annotate(c=Count("rule_check__checked_object_content_type"))
        .order_by("c")
        .first()["rule_check__checked_object_content_type"]
    )
    return ContentType.objects.get(id=content_type_id).id


def filter_date_range(queryset, label, value):
    if value:
        return queryset.filter(
            Q(rule_check__evaluation_date__gte=value.lower) & Q(rule_check__evaluation_date__lte=value.upper)
        )
    return queryset


class RiskManagementIncidentFilter(wb_filters.FilterSet):
    incident_date_range = wb_filters.DateRangeFilter(label=_("Date Range"), method=filter_date_range)
    only_open_incident = wb_filters.BooleanFilter(
        initial=True, method="filter_only_open_incident", label=_("Only open incidents")
    )

    checked_object_content_type = wb_filters.ModelChoiceFilter(
        required=True,
        method="filter_checked_object_content_type",
        queryset=ContentType.objects.all(),
        endpoint="wbcore:contenttyperepresentation-list",
        value_key="id",
        label_key="{{app_label}} | {{model}}",
        label=_("Checked Object Type"),
        initial=get_content_type_default,
        filter_params={"related_name_isnull": "risk_management_checked_objects"},
        clearable=False,
    )

    def filter_checked_object_content_type(self, queryset, label, value):
        if value:
            return queryset.filter(rule_check__checked_object_content_type=value)
        return queryset

    def filter_only_open_incident(self, queryset, name, value):
        if value:
            return queryset.filter(status=CheckedObjectIncidentRelationship.Status.OPEN)
        return queryset

    class Meta:
        model = CheckedObjectIncidentRelationship
        fields = {
            # "rule_backend": ["exact"],
            # "is_enable": ["exact"],
            # "only_passive_check_allowed": ["exact"],
            # "is_silent": ["exact"],
            # "is_mandatory": ["exact"],
        }


@receiver(add_filters, sender=RiskManagementIncidentFilter)
def add_checked_object_repr_filter(sender, request=None, *args, **kwargs):
    content_type = None
    if request and (content_type_id := request.GET.get("checked_object_content_type", None)):
        content_type = ContentType.objects.get(id=content_type_id)
    elif default_callback := getattr(sender, "default", None):
        content_type = ContentType.objects.get(id=default_callback())
    if content_type:

        def filter_checked_object_repr(queryset, label, value):
            if value:
                return queryset.filter(rule_check__checked_object_id=value.id)
            return queryset

        model_class = content_type.model_class()
        return {
            "checked_object_repr": wb_filters.ModelChoiceFilter(
                label=content_type.name,
                field_name="checked_object_repr",
                queryset=model_class.objects.all(),
                endpoint=model_class.get_representation_endpoint(),
                value_key=model_class.get_representation_value_key(),
                label_key=model_class.get_representation_label_key(),
                method=filter_checked_object_repr,
            )
        }
    else:

        def filter_checked_object_repr(queryset, label, value):
            if value:
                return queryset.filter(rule_check__checked_object_repr__icontains=value)
            return queryset

        return {
            "checked_object_repr": wb_filters.CharFilter(
                label=_("Checked Object Repr."),
                method=filter_checked_object_repr,
                lookup_expr="icontains",
                field_name="checked_object_repr",
            )
        }
