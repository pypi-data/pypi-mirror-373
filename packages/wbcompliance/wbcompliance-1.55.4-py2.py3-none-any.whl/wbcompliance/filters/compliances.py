from django.db.models import Max, Q
from django.utils.translation import gettext_lazy as _
from wbcore import filters as wb_filters

from wbcompliance.models import (
    ComplianceAction,
    ComplianceEvent,
    ComplianceForm,
    ComplianceFormSignature,
    ComplianceTask,
    ComplianceTaskGroup,
    ComplianceTaskInstance,
    ComplianceType,
    ReviewComplianceTask,
)


class ComplianceFormFilter(wb_filters.FilterSet):
    is_signed = wb_filters.BooleanFilter(label=_("Is Signed"), required=False)

    class Meta:
        model = ComplianceForm
        fields = {
            "form_type": ["exact"],
            "compliance_type": ["exact"],
            "title": ["exact", "icontains"],
            "creator": ["exact"],
            "changer": ["exact"],
            "version": ["exact"],
            "status": ["exact"],
            "start": ["gte", "lte"],
            "end": ["gte", "lte"],
        }


class ComplianceFormSignatureFilter(wb_filters.FilterSet):
    is_signed = wb_filters.BooleanFilter(label=_("Is Signed"), required=False)
    last_version = wb_filters.BooleanFilter(label=_("Last version"), initial=True, method="filter_version")
    # compliance_form = wb_filters.ModelChoiceFilter(
    #     label=_("Compliance Form"),
    #     queryset=ComplianceForm.objects.filter(status=ComplianceForm.Status.ACTIVE),
    #     endpoint=ComplianceForm.get_representation_endpoint(),
    #     value_key=ComplianceForm.get_representation_value_key(),
    #     label_key = ComplianceForm.get_representation_label_key(),
    #     method="filter_compliance_form"
    # )
    # def filter_compliance_form(self, queryset, name, value):
    #     return queryset.filter(status=ComplianceForm.Status.ACTIVE)

    class Meta:
        model = ComplianceFormSignature
        fields = {
            "person": ["exact"],
            "signed": ["gte", "lte"],
            "version": ["exact"],
            "compliance_form": ["exact"],
        }

    def filter_version(self, queryset, name, value):
        if value:
            max_compliance_forms = queryset.values("compliance_form").annotate(max_version=Max("version")).order_by()
            q_statement = Q()
            for max_compliance_form in max_compliance_forms:
                q_statement |= Q(compliance_form__exact=max_compliance_form["compliance_form"]) & Q(
                    version=max_compliance_form["max_version"]
                )
            return queryset.filter(q_statement)

        return queryset


class ComplianceTypeFilter(wb_filters.FilterSet):
    class Meta:
        model = ComplianceType
        fields = {
            "name": ["exact", "icontains"],
        }


class ComplianceTaskGroupFilter(wb_filters.FilterSet):
    class Meta:
        model = ComplianceTaskGroup
        fields = {
            "name": ["exact", "icontains"],
        }


class ComplianceTaskReviewFilter(wb_filters.FilterSet):
    class Meta:
        model = ComplianceTask
        fields = {
            "title": ["exact", "icontains"],
            "occurrence": ["exact"],
            "active": ["exact"],
            "type": ["exact"],
            "group": ["exact"],
            "risk_level": ["exact"],
        }


class ComplianceTaskFilter(ComplianceTaskReviewFilter):
    is_recurring = wb_filters.BooleanFilter(label=_("Is Recurring"), initial=True, method="filter_occurrence")
    active = wb_filters.BooleanFilter(label=_("Active"), initial=True)

    def filter_occurrence(self, queryset, name, value):
        if value is not None:
            if value:
                return queryset.filter(~Q(occurrence=ComplianceTask.Occurrence.NEVER))
            else:
                return queryset.filter(occurrence=ComplianceTask.Occurrence.NEVER)
        return queryset


class ComplianceTaskInstanceFilter(wb_filters.FilterSet):
    type_name = wb_filters.CharFilter(label=_("Administrator"), lookup_expr="icontains")
    group_name = wb_filters.CharFilter(label=_("Group"), lookup_expr="icontains")

    class Meta:
        model = ComplianceTaskInstance
        fields = {"task": ["exact"], "occured": ["lte", "gte"], "status": ["exact"], "review": ["exact"]}


class ComplianceTaskMatrixFilter(wb_filters.FilterSet):
    type_name = wb_filters.CharFilter(label=_("Administrator"), lookup_expr="icontains")
    group_name = wb_filters.CharFilter(label=_("Group"), lookup_expr="icontains")
    task_title = wb_filters.CharFilter(label=_("Tasks"), lookup_expr="icontains")

    class Meta:
        model = ComplianceTaskInstance
        fields = {}


class ComplianceActionFilter(wb_filters.FilterSet):
    active = wb_filters.BooleanFilter(label=_("Active"), initial=True)

    class Meta:
        model = ComplianceAction
        fields = {
            "title": ["exact", "icontains"],
            "deadline": ["exact"],
            "progress": ["exact"],
            "status": ["exact"],
            "active": ["exact"],
            "type": ["exact"],
            "creator": ["exact"],
            "changer": ["exact"],
            "last_modified": ["lte", "gte"],
        }


class ComplianceEventFilter(wb_filters.FilterSet):
    active = wb_filters.BooleanFilter(label=_("Active"), initial=True)

    class Meta:
        model = ComplianceEvent
        fields = {
            "title": ["exact", "icontains"],
            "type": ["exact"],
            "level": ["exact"],
            "active": ["exact"],
            "type_event": ["exact"],
            "creator": ["exact"],
            "last_modified": ["lte", "gte"],
            "confidential": ["exact"],
        }


class ReviewComplianceTaskFilter(wb_filters.FilterSet):
    is_instance = wb_filters.BooleanFilter(label=_("Is occurrence"), initial=True)

    class Meta:
        model = ReviewComplianceTask
        fields = {
            "year": ["exact"],
            "from_date": ["lte", "gte"],
            "to_date": ["lte", "gte"],
            "title": ["exact", "icontains"],
            "is_instance": ["exact"],
            "status": ["exact"],
            "changer": ["exact"],
            "changed": ["lte", "gte"],
            "occured": ["lte", "gte"],
            "review_task": ["exact"],
            "occurrence": ["exact"],
            "type": ["exact"],
        }
