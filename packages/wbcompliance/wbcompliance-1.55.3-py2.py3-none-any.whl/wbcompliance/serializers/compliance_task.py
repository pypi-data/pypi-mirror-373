from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.directory.models import Person
from wbcore.contrib.directory.serializers import PersonRepresentationSerializer

from wbcompliance.models import (
    ComplianceAction,
    ComplianceEvent,
    ComplianceTask,
    ComplianceTaskGroup,
    ComplianceTaskInstance,
    ComplianceType,
    ReviewComplianceTask,
)

from .compliance_type import ComplianceTypeRepresentationSerializer


class ComplianceTaskGroupRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcompliance:compliancetaskgroup-detail")

    class Meta:
        model = ComplianceTaskGroup
        fields = ("id", "name", "_detail")


class ComplianceTaskRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcompliance:compliancetask-detail")

    class Meta:
        model = ComplianceTask
        fields = ("id", "title", "occurrence", "active", "type", "_detail")


class ReviewComplianceTaskRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcompliance:reviewcompliancetask-detail")

    class Meta:
        model = ReviewComplianceTask
        fields = ("id", "title", "computed_str", "occurrence", "year", "occured", "_detail")


class NoInstanceReviewComplianceTaskRepresentationSerializer(ReviewComplianceTaskRepresentationSerializer):
    def get_filter_params(self, request):
        if task_id := request.parser_context["view"].kwargs.get("pk"):
            task = get_object_or_404(ComplianceTask, pk=task_id)
            return {"is_instance": False, "type": task.type.id}
        return {"is_instance": False}


class InstanceReviewComplianceTaskRepresentationSerializer(ReviewComplianceTaskRepresentationSerializer):
    def get_filter_params(self, request):
        if task_id := request.parser_context["view"].kwargs.get("task_id"):
            task = get_object_or_404(ComplianceTask, pk=task_id)
            return {"is_instance": True, "type": task.type.id}
        return {"is_instance": True}


class ComplianceTaskGroupModelSerializer(wb_serializers.ModelSerializer):
    @wb_serializers.register_resource()
    def register_history_resource(self, instance, request, user):
        resources = {
            "compliancetask": reverse(
                "wbcompliance:compliancetaskgroup-compliancetask-list", args=[instance.id], request=request
            ),
        }
        return resources

    class Meta:
        model = ComplianceTaskGroup
        fields = ("id", "name", "order", "_additional_resources")


class ComplianceTaskModelSerializer(wb_serializers.ModelSerializer):
    @wb_serializers.register_resource()
    def register_history_resource(self, instance, request, user):
        resources = {
            "compliancetaskinstance": reverse(
                "wbcompliance:compliancetask-compliancetaskinstance-list", args=[instance.id], request=request
            ),
        }
        if user.is_superuser:
            resources["generateinstance"] = reverse(
                "wbcompliance:compliancetask-generate-instance", args=[instance.id], request=request
            )
        return resources

    _group = ComplianceTaskGroupRepresentationSerializer(source="group")
    review = wb_serializers.PrimaryKeyRelatedField(
        queryset=ReviewComplianceTask.objects.all(),
        label=_("Indicator Reports"),
        many=True,
        help_text=_("list of reports that contain this task"),
    )
    _review = NoInstanceReviewComplianceTaskRepresentationSerializer(
        source="review",
        many=True,
        optional_get_parameters={"type": "type"},
        depends_on=[{"field": "type", "options": {}}],
    )
    _type = ComplianceTypeRepresentationSerializer(source="type")
    type = wb_serializers.PrimaryKeyRelatedField(
        queryset=ComplianceType.objects.all(),
        label=_("Administrator"),
    )
    occurrence = wb_serializers.ChoiceField(
        default=wb_serializers.DefaultAttributeFromRemoteField("review_id", ReviewComplianceTask, "occurrence"),
        choices=ReviewComplianceTask.Occurrence.choices,
    )
    type = wb_serializers.PrimaryKeyRelatedField(
        queryset=ComplianceType.objects.all(),
        label=_("Administrator"),
        default=wb_serializers.DefaultAttributeFromRemoteField("review_id", ReviewComplianceTask, "type.id"),
    )

    class Meta:
        model = ComplianceTask
        # dependency_map = {
        #     "review": ["type"],
        # }
        fields = (
            "id",
            "title",
            "description",
            "occurrence",
            "active",
            "type",
            "_type",
            "group",
            "_group",
            "_additional_resources",
            "risk_level",
            "remarks",
            "review",
            "_review",
        )


class ComplianceTaskReviewModelSerializer(ComplianceTaskModelSerializer):
    def create(self, validated_data):
        if (view := self.context.get("view", None)) and (review_id := view.kwargs.get("review_id", None)):
            validated_data["review"] = ReviewComplianceTask.objects.filter(id=review_id)

        return super().create(validated_data)


class ComplianceTaskInstanceModelSerializer(wb_serializers.ModelSerializer):
    task = wb_serializers.PrimaryKeyRelatedField(
        queryset=ComplianceTask.objects.all(),
        label=_("Indicator"),
    )
    _task = ComplianceTaskRepresentationSerializer(source="task")
    type_name = wb_serializers.CharField(required=False, read_only=True, label=_("Administrator"))
    group_name = wb_serializers.CharField(required=False, read_only=True, label=_("Group"))
    task_title = wb_serializers.CharField(required=False, read_only=True, label=_("Indicators"))
    review = wb_serializers.PrimaryKeyRelatedField(
        queryset=ReviewComplianceTask.objects.all(),
        label=_("Indicator Instance Reports"),
        many=True,
        help_text=_("list of reports that contain this task"),
    )
    _review = InstanceReviewComplianceTaskRepresentationSerializer(source="review", many=True)

    text = wb_serializers.TextAreaField(
        required=False, label=_("Text"), allow_blank=True, allow_null=True, help_text=_("Information for Management")
    )
    summary_text = wb_serializers.TextAreaField(
        required=False,
        label=_("Summary Text"),
        allow_blank=True,
        allow_null=True,
        help_text=_("Information for the Board of Directors"),
    )

    class Meta:
        model = ComplianceTaskInstance
        fields = (
            "id",
            "occured",
            "status",
            "type_name",
            "group_name",
            "text",
            "summary_text",
            "_task",
            "task",
            "review",
            "_review",
            "_additional_resources",
            "task_title",
        )
        read_only_fields = ("review", "_review", "task", "_task")


class ComplianceTaskInstanceListModelSerializer(ComplianceTaskInstanceModelSerializer):
    class Meta:
        model = ComplianceTaskInstance
        fields = (
            "id",
            "occured",
            "status",
            "type_name",
            "group_name",
            "_task",
            "task",
            "task_title",
            "review",
            "_review",
        )


class ComplianceActionModelSerializer(wb_serializers.ModelSerializer):
    type = wb_serializers.PrimaryKeyRelatedField(
        queryset=ComplianceType.objects.all(),
        label=_("Administrator"),
    )
    _type = ComplianceTypeRepresentationSerializer(source="type")
    _creator = PersonRepresentationSerializer(source="creator")
    _changer = PersonRepresentationSerializer(source="changer")
    description = wb_serializers.TextField(
        default="", label=_("Description"), help_text=_("Explanation for Management")
    )
    summary_description = wb_serializers.TextField(
        default="", label=_("Summary Description"), help_text=_("Explanation for the Board of Directors")
    )

    class Meta:
        percent_fields = ["progress"]

        model = ComplianceAction
        fields = (
            "id",
            "title",
            "description",
            "summary_description",
            "deadline",
            "progress",
            "status",
            "type",
            "_type",
            "active",
            "creator",
            "_creator",
            "created",
            "changer",
            "_changer",
            "last_modified",
        )
        read_only_fields = ("creator", "created", "changer", "last_modified")

    @cached_property
    def user_profile(self) -> Person | None:
        if request := self.context.get("request"):
            return request.user.profile
        return None

    def create(self, validated_data):
        validated_data["creator"] = self.user_profile
        return super().create(validated_data)

    def update(self, instance, validated_data):
        profile = self.user_profile
        validated_data["changer"] = profile
        validated_data.pop("creator", None)
        validated_data.pop("created", None)
        return super().update(instance, validated_data)


class ComplianceEventModelSerializer(wb_serializers.ModelSerializer):
    type = wb_serializers.PrimaryKeyRelatedField(
        queryset=ComplianceType.objects.all(),
        label=_("Administrator"),
    )
    _type = ComplianceTypeRepresentationSerializer(source="type")
    _creator = PersonRepresentationSerializer(source="creator")
    _changer = PersonRepresentationSerializer(source="changer")
    title = wb_serializers.CharField(label=_("Title"), allow_null=False)
    exec_summary = wb_serializers.TextField(
        default="", label=_("Executive Summary for Management"), help_text=_("Executive Summary for Management")
    )
    exec_summary_board = wb_serializers.TextField(
        default="",
        label=_("Executive Summary for the Board of Directors"),
        help_text=_("Executive Summary for the Board of Directors"),
    )

    class Meta:
        model = ComplianceEvent
        fields = (
            "id",
            "type_event",
            "level",
            "title",
            "exec_summary",
            "exec_summary_board",
            "description",
            "actions_taken",
            "confidential",
            "consequences",
            "future_suggestions",
            "type",
            "_type",
            "active",
            "creator",
            "_creator",
            "created",
            "changer",
            "_changer",
            "last_modified",
        )
        read_only_fields = ("creator", "created", "changer", "last_modified")

    @cached_property
    def user_profile(self) -> Person | None:
        if request := self.context.get("request"):
            return request.user.profile
        return None

    def create(self, validated_data):
        validated_data["creator"] = self.user_profile
        return super().create(validated_data)

    def update(self, instance, validated_data):
        profile = self.user_profile
        validated_data["changer"] = profile
        validated_data.pop("creator", None)
        validated_data.pop("created", None)
        return super().update(instance, validated_data)


class ReviewComplianceTaskModelSerializer(wb_serializers.ModelSerializer):
    @wb_serializers.register_only_instance_resource()
    def register_history_resource(self, instance, request, user, **kwargs):
        if not instance.is_instance:
            resources = {
                "task_group": reverse("wbcompliance:compliancetaskgroup-list", args=[], request=request),
                "task_no_group": reverse(
                    "wbcompliance:review-compliancetasknogroup-list", args=[instance.id], request=request
                ),
            }
            if instance.status == ReviewComplianceTask.Status.DRAFT and user.is_superuser:
                resources["link_tasks"] = reverse(
                    "wbcompliance:reviewcompliancetask-link-tasks", args=[instance.id], request=request
                )

            if instance.status == ReviewComplianceTask.Status.VALIDATED and user.has_perm(
                "wbcompliance.administrate_compliance"
            ):
                resources["regenerate_document"] = reverse(
                    "wbcompliance:reviewcompliancetask-regenerate-document", args=[instance.id], request=request
                )

                from_date, to_date = instance.get_period_date()
                if not ReviewComplianceTask.objects.filter(
                    review_task=instance, from_date=from_date, to_date=to_date
                ).exists():
                    resources["generate_instance"] = reverse(
                        "wbcompliance:reviewcompliancetask-generate-instance", args=[instance.id], request=request
                    )
            group_ids = instance.get_task_group_ids_from_review()
            for group_id in group_ids:
                resources[f"taskgroup{group_id}"] = reverse(
                    "wbcompliance:review-compliancetaskgroup-list",
                    args=[instance.id, group_id],
                    request=request,
                )
        else:
            resources = {
                "actions": reverse(
                    "wbcompliance:type-complianceaction-list", args=[instance.type.id], request=request
                ),
                "events": reverse("wbcompliance:type-complianceevent-list", args=[instance.type.id], request=request),
                "taskinstance_no_group": reverse(
                    "wbcompliance:review-compliancetaskinstancenogroup-list", args=[instance.id], request=request
                ),
            }
            group_ids = instance.get_task_group_ids_from_review(through_task=False)
            for group_id in group_ids:
                resources[f"taskinstancegroup{group_id}"] = reverse(
                    "wbcompliance:review-compliancetaskinstancegroup-list",
                    args=[instance.id, group_id],
                    request=request,
                )

        return resources

    year = wb_serializers.YearField(default=timezone.now().year)
    creator = wb_serializers.PrimaryKeyRelatedField(
        default=wb_serializers.CurrentUserDefault("profile"),
        many=False,
        read_only=True,
    )
    _creator = PersonRepresentationSerializer(source="creator")
    _changer = PersonRepresentationSerializer(source="changer")
    review_task = wb_serializers.PrimaryKeyRelatedField(read_only=True, label=_("Main Indicator Report"))
    _review_task = ReviewComplianceTaskRepresentationSerializer(source="review_task")
    type = wb_serializers.PrimaryKeyRelatedField(
        queryset=ComplianceType.objects.all(),
        label=_("Administrator"),
    )
    _type = ComplianceTypeRepresentationSerializer(source="type")
    occured = wb_serializers.DateField(read_only=True, label=_("Occured Instance Report"))
    occurrence = wb_serializers.ChoiceField(
        choices=ReviewComplianceTask.Occurrence.choices,
        read_only=lambda view: not getattr(view.get_object(), "is_instance", True)
        if "pk" in view.kwargs
        else not view.new_mode,
    )

    class Meta:
        model = ReviewComplianceTask
        fields = (
            "id",
            "title",
            "from_date",
            "to_date",
            "description",
            "year",
            "creator",
            "_creator",
            "created",
            "changer",
            "_changer",
            "changed",
            "status",
            "_additional_resources",
            "occurrence",
            "computed_str",
            "is_instance",
            "review_task",
            "_review_task",
            "occured",
            "type",
            "_type",
        )
        read_only_fields = (
            "creator",
            "created",
            "changer",
            "changed",
            "occured",
            "is_instance",
            "review_task",
        )

    @cached_property
    def user_profile(self) -> Person | None:
        if request := self.context.get("request"):
            return request.user.profile
        return None

    def create(self, validated_data):
        validated_data["creator"] = self.user_profile
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["changer"] = self.user_profile
        validated_data.pop("creator", None)
        validated_data.pop("created", None)
        return super().update(instance, validated_data)
