from wbcore import filters as wb_filters

from wbcompliance.models.risk_management import RiskCheck


class RiskCheckFilterSet(wb_filters.FilterSet):
    checked_objects = wb_filters.MultipleChoiceContentTypeFilter(
        label="Triggerers",
        field_name="checked_objects",
        object_id_label="checked_object_id",
        content_type_label="checked_object_content_type",
        distinct=True,
        hidden=True,
    )
    activators = wb_filters.MultipleChoiceContentTypeFilter(
        label="Activators",
        field_name="activators",
        object_id_label="activator_id",
        content_type_label="activator_content_type",
        distinct=True,
        hidden=True,
    )
    passive_check = wb_filters.BooleanFilter(initial=True, required=True, label="Passive")

    class Meta:
        model = RiskCheck

        fields = {
            "rule": ["exact"],
            "creation_datetime": ["gte", "exact", "lte"],
            "evaluation_date": ["exact"],
            "status": ["exact"],
        }
