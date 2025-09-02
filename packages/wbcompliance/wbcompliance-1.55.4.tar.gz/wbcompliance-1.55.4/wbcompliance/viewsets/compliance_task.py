from datetime import datetime, timedelta

import pandas as pd
from django.contrib.contenttypes.models import ContentType
from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from reversion.views import RevisionMixin
from wbcore import viewsets
from wbcore.contrib.authentication.authentication import JWTCookieAuthentication
from wbcore.pandas import fields as pf
from wbcore.pandas.views import PandasAPIViewSet

from wbcompliance.filters import (
    ComplianceActionFilter,
    ComplianceEventFilter,
    ComplianceTaskFilter,
    ComplianceTaskGroupFilter,
    ComplianceTaskInstanceFilter,
    ComplianceTaskMatrixFilter,
    ComplianceTaskReviewFilter,
    ReviewComplianceTaskFilter,
)
from wbcompliance.models import (
    ComplianceAction,
    ComplianceEvent,
    ComplianceTask,
    ComplianceTaskGroup,
    ComplianceTaskInstance,
    ReviewComplianceTask,
    update_or_create_compliance_document,
)
from wbcompliance.serializers import (
    ComplianceActionModelSerializer,
    ComplianceEventModelSerializer,
    ComplianceTaskGroupModelSerializer,
    ComplianceTaskGroupRepresentationSerializer,
    ComplianceTaskInstanceListModelSerializer,
    ComplianceTaskInstanceModelSerializer,
    ComplianceTaskModelSerializer,
    ComplianceTaskRepresentationSerializer,
    ComplianceTaskReviewModelSerializer,
    ReviewComplianceTaskModelSerializer,
    ReviewComplianceTaskRepresentationSerializer,
)

from .buttons import ComplianceTaskButtonConfig, ReviewComplianceTaskButtonConfig
from .display import (
    ComplianceActionDisplayConfig,
    ComplianceEventDisplayConfig,
    ComplianceTaskDisplayConfig,
    ComplianceTaskGroupDisplayConfig,
    ComplianceTaskInstanceComplianceTaskDisplayConfig,
    ComplianceTaskInstanceDisplayConfig,
    ComplianceTaskInstanceReviewDisplayConfig,
    ComplianceTaskMatrixPandasDisplayConfig,
    ComplianceTaskReviewDisplayConfig,
    ReviewComplianceTaskDisplayConfig,
)
from .endpoints import (
    ComplianceActionEndpointConfig,
    ComplianceEventEndpointConfig,
    ComplianceTaskComplianceTaskGroupEndpointConfig,
    ComplianceTaskEndpointConfig,
    ComplianceTaskGroupEndpointConfig,
    ComplianceTaskInstanceComplianceTaskEndpointConfig,
    ComplianceTaskInstanceEndpointConfig,
    ComplianceTaskInstanceReviewGroupEndpointConfig,
    ComplianceTaskInstanceReviewNoGroupEndpointConfig,
    ComplianceTaskMatrixEndpointConfig,
    ComplianceTaskReviewGroupEndpointConfig,
    ComplianceTaskReviewNoGroupEndpointConfig,
    ReviewComplianceTaskEndpointConfig,
)
from .titles import (
    ComplianceTaskComplianceTaskGroupTitleConfig,
    ComplianceTaskGroupTitleConfig,
    ComplianceTaskInstanceTitleConfig,
    ComplianceTaskMatrixPandasTitleConfig,
    ComplianceTaskTitleConfig,
    ReviewComplianceTaskTitleConfig,
)


class ComplianceTaskGroupRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbcompliance:compliancetaskgrouprepresentation"
    search_fields = ["name"]
    ordering_fields = ["name"]

    queryset = ComplianceTaskGroup.objects.all()
    serializer_class = ComplianceTaskGroupRepresentationSerializer


class ComplianceTaskRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbcompliance:compliancetaskrepresentation"
    search_fields = ["title"]
    ordering_fields = ["title", "occurrence", "active", "type"]

    queryset = ComplianceTask.objects.all()
    serializer_class = ComplianceTaskRepresentationSerializer


class ReviewComplianceTaskRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbcompliance:reviewcompliancetaskrepresentation"
    search_fields = ordering_fields = ["title"]
    ordering = ["-year", "-occured", "title"]
    filterset_class = ReviewComplianceTaskFilter

    queryset = ReviewComplianceTask.objects.all()
    serializer_class = ReviewComplianceTaskRepresentationSerializer


class ComplianceTaskGroupModelViewSet(RevisionMixin, viewsets.ModelViewSet):
    IDENTIFIER = "wbcompliance:compliancetaskgroup"
    display_config_class = ComplianceTaskGroupDisplayConfig
    endpoint_config_class = ComplianceTaskGroupEndpointConfig
    title_config_class = ComplianceTaskGroupTitleConfig

    search_fields = ["name"]
    ordering_fields = ["order", "name"]
    ordering = ["order", "name"]

    filterset_class = ComplianceTaskGroupFilter

    serializer_class = ComplianceTaskGroupModelSerializer

    queryset = ComplianceTaskGroup.objects.all()


class ComplianceTaskModelViewSet(RevisionMixin, viewsets.ModelViewSet):
    IDENTIFIER = "wbcompliance:compliancetask"
    display_config_class = ComplianceTaskDisplayConfig
    title_config_class = ComplianceTaskTitleConfig
    endpoint_config_class = ComplianceTaskEndpointConfig
    button_config_class = ComplianceTaskButtonConfig

    search_fields = ["title"]
    ordering_fields = ["title", "occurrence", "risk_level", "group", "active", "type", "review"]

    filterset_class = ComplianceTaskFilter

    serializer_class = ComplianceTaskModelSerializer

    queryset = ComplianceTask.objects.select_related(
        "group",
        "type",
    ).prefetch_related("review")

    @action(detail=True, methods=["PATCH"], authentication_classes=[JWTCookieAuthentication])
    def generate_instance(self, request, pk):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if occured := request.POST.get("occured", None):
            task = get_object_or_404(ComplianceTask, pk=pk)
            task.generate_compliance_task_instance(occured=datetime.strptime(occured, "%Y-%m-%d"))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"__notification": {"title": "Indicator Instance has been generated."}},
            status=status.HTTP_200_OK,
        )


class ComplianceTaskComplianceTaskGroupModelViewSet(ComplianceTaskModelViewSet):
    title_config_class = ComplianceTaskComplianceTaskGroupTitleConfig
    endpoint_config_class = ComplianceTaskComplianceTaskGroupEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(group__id=self.kwargs["group_id"])


class ComplianceTaskInstanceModelViewSet(RevisionMixin, viewsets.ModelViewSet):
    IDENTIFIER = "wbcompliance:compliancetaskinstance"
    display_config_class = ComplianceTaskInstanceDisplayConfig
    endpoint_config_class = ComplianceTaskInstanceEndpointConfig
    title_config_class = ComplianceTaskInstanceTitleConfig

    search_fields = ["task__title"]
    ordering_fields = ["task__title", "occured", "status", "review"]
    ordering = ["-occured", "-type_name", "group_name", "task__title"]

    filterset_class = ComplianceTaskInstanceFilter

    serializer_class = ComplianceTaskInstanceModelSerializer

    queryset = ComplianceTaskInstance.objects.select_related("task").prefetch_related("review")

    def get_serializer_class(self):
        if self.get_action() in ["list", "list-metadata"]:
            return ComplianceTaskInstanceListModelSerializer
        return ComplianceTaskInstanceModelSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                task_title=F("task__title"),
                active=F("task__active"),
                type_name=F("task__type__name"),
                group_name=F("task__group__name"),
            )
        )


class ComplianceTaskInstanceComplianceTaskModelViewSet(ComplianceTaskInstanceModelViewSet):
    IDENTIFIER = "wbcompliance:compliancetask-compliancetaskinstance"
    display_config_class = ComplianceTaskInstanceComplianceTaskDisplayConfig
    endpoint_config_class = ComplianceTaskInstanceComplianceTaskEndpointConfig

    def get_queryset(self):
        if task_id := self.kwargs.get("task_id", None):
            return (
                super()
                .get_queryset()
                .filter(task__id=task_id)
                .annotate(
                    task_title=F("task__title"),
                    active=F("task__active"),
                    type_name=F("task__type__name"),
                    group_name=F("task__group__name"),
                )
            )
        return ComplianceTask.objects.none()


class ComplianceTaskMatrixPandasViewSet(PandasAPIViewSet):
    IDENTIFIER = "wbcommission:compliancetaskmatrix"
    queryset = ComplianceTaskInstance.objects.all()

    display_config_class = ComplianceTaskMatrixPandasDisplayConfig
    title_config_class = ComplianceTaskMatrixPandasTitleConfig
    endpoint_config_class = ComplianceTaskMatrixEndpointConfig

    filterset_class = ComplianceTaskMatrixFilter

    def get_pandas_fields(self, request):
        _fields = [
            pf.PKField("id", label=_("ID")),
            pf.CharField(key="type_name", label=_("Administrator")),
            pf.CharField(key="group_name", label=_("Group")),
            pf.CharField(key="task_title", label=_("Tasks")),
        ]
        if _dict := ComplianceTaskInstance.get_dict_max_count_task():
            qs_occured = (
                ComplianceTaskInstance.objects.filter(task=_dict.get("task"))
                .order_by("-occured")
                .values_list("occured", flat=True)
                .distinct()[:12]
            )
            for date in qs_occured:
                date_str = date.strftime("%Y-%m-%d")
                covered_month = (date - timedelta(days=1)).strftime("%Y-%h")
                _fields.append(pf.CharField(key=date_str, label=covered_month))
        return pf.PandasFields(fields=tuple(_fields))

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(task__active=True)
            .annotate(task_title=F("task__title"), type_name=F("task__type__name"), group_name=F("task__group__name"))
        )

    def get_dataframe(self, request, queryset, **kwargs):
        def _rename_columns(df):
            pass

            rename_map = {}
            for col in df.columns:
                if not isinstance(col, str):
                    rename_map[col] = str(col)
            rename_map["index"] = "task"
            return df.rename(columns=rename_map)

        df = pd.DataFrame()
        if queryset.exists():
            df = pd.DataFrame(
                queryset.values("task", "type_name", "group_name", "task_title", "occured", "status"),
                columns=["task", "type_name", "group_name", "task_title", "occured", "status"],
            )
            df["status"] = df["status"].apply(lambda x: ComplianceTaskInstance.Status[x].label)
            df = df.where(pd.notnull(df), "")
            df = df.pivot_table(
                index=["task", "type_name", "group_name", "task_title"],
                columns="occured",
                values="status",
                aggfunc="last",
            )
            df = _rename_columns(df)
            df = df.reset_index()
            df["id"] = df.index

        return df


class ComplianceActionModelViewSet(RevisionMixin, viewsets.ModelViewSet):
    IDENTIFIER = "wbcompliance:complianceaction"
    display_config_class = ComplianceActionDisplayConfig
    endpoint_config_class = ComplianceActionEndpointConfig

    search_fields = ["title"]
    ordering_fields = [
        "title",
        "deadline",
        "progress",
        "status",
        "active",
        "type",
        "creator",
        "changer",
        "last_modified",
    ]
    ordering = ["-last_modified", "active"]

    filterset_class = ComplianceActionFilter

    serializer_class = ComplianceActionModelSerializer

    queryset = ComplianceAction.objects.select_related("type", "creator", "changer")

    def get_queryset(self):
        if self.request.user.has_perm("wbcompliance.administrate_compliance"):
            return super().get_queryset()
        return ComplianceAction.objects.none()


class TypeComplianceActionModelViewSet(ComplianceActionModelViewSet):
    IDENTIFIER = "wbcompliance:type-complianceaction"

    def get_queryset(self):
        return super().get_queryset().filter(type=self.kwargs["type_id"])


class ComplianceEventModelViewSet(RevisionMixin, viewsets.ModelViewSet):
    IDENTIFIER = "wbcompliance:complianceevent"
    display_config_class = ComplianceEventDisplayConfig
    endpoint_config_class = ComplianceEventEndpointConfig

    search_fields = ["title"]
    ordering_fields = ["title", "type", "level", "active", "type", "creator", "last_modified", "confidential"]
    ordering = ["-last_modified", "active"]

    filterset_class = ComplianceEventFilter

    serializer_class = ComplianceEventModelSerializer

    queryset = ComplianceEvent.objects.select_related(
        "type",
        "creator",
        "changer",
    )

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm("wbcompliance.administrate_compliance"):
            return qs
        return qs.filter(Q(creator=self.request.user.profile) | Q(confidential=False))


class TypeComplianceEventModelViewSet(ComplianceEventModelViewSet):
    IDENTIFIER = "wbcompliance:type-complianceevent"

    def get_queryset(self):
        return super().get_queryset().filter(type=self.kwargs["type_id"])


class ReviewComplianceTaskModelViewSet(RevisionMixin, viewsets.ModelViewSet):
    IDENTIFIER = "wbcompliance:reviewcompliancetask"
    display_config_class = ReviewComplianceTaskDisplayConfig
    endpoint_config_class = ReviewComplianceTaskEndpointConfig
    button_config_class = ReviewComplianceTaskButtonConfig
    title_config_class = ReviewComplianceTaskTitleConfig

    search_fields = ["title"]
    ordering = ["-year", "-is_instance", "-occured", "-changed", "title"]
    ordering_fields = [
        "title",
        "from_date",
        "to_date",
        "year",
        "status",
        "changer",
        "changed",
        "is_instance",
        "occured",
        "review_task",
        "ocurrance",
    ]

    filterset_class = ReviewComplianceTaskFilter

    serializer_class = ReviewComplianceTaskModelSerializer

    queryset = ReviewComplianceTask.objects.select_related(
        "creator",
        "changer",
        "review_task",
        "type",
    )

    @action(detail=True, methods=["PATCH"], authentication_classes=[JWTCookieAuthentication])
    def regenerate_document(self, request, pk):
        if not request.user.has_perm("wbcompliance.administrate_compliance"):
            return Response({}, status=status.HTTP_403_FORBIDDEN)
        content_type = ContentType.objects.get_for_model(ReviewComplianceTask)
        send_email = request.POST.get("send_email", "false") == "true"
        update_or_create_compliance_document.delay(request.user.id, content_type.id, pk, send_email=send_email)

        return Response(
            {"__notification": {"title": "PDF is going to be created and sent to you."}},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["PATCH"], authentication_classes=[JWTCookieAuthentication])
    def generate_instance(self, request, pk):
        if not request.user.has_perm("wbcompliance.administrate_compliance"):
            return Response({}, status=status.HTTP_403_FORBIDDEN)
        review = ReviewComplianceTask.objects.get(id=pk)
        review.generate_review_compliance_task_instance(link_instance=True)
        return Response(
            {"__notification": {"title": "Instance is going to be generate."}},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["PATCH"], authentication_classes=[JWTCookieAuthentication])
    def link_tasks(self, request, pk):
        if not request.user.has_perm("wbcompliance.administrate_compliance"):
            return Response({}, status=status.HTTP_403_FORBIDDEN)

        if (_type := request.POST.get("type", None)) and (operation := request.POST.get("operation", None)):
            review = ReviewComplianceTask.objects.get(id=pk)
            for task in ComplianceTask.objects.filter(type__name=_type):
                if operation == "ADD":
                    task.review.add(review)
                elif operation == "REMOVE":
                    task.review.remove(review)
                task.save()
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"__notification": {"title": "Tasks of a type is going to be linked."}},
            status=status.HTTP_200_OK,
        )


class ComplianceTaskReviewNoGroupModelViewSet(ComplianceTaskModelViewSet):
    display_config_class = ComplianceTaskReviewDisplayConfig
    endpoint_config_class = ComplianceTaskReviewNoGroupEndpointConfig
    filterset_class = ComplianceTaskReviewFilter
    serializer_class = ComplianceTaskReviewModelSerializer

    def get_queryset(self):
        return super().get_queryset().filter(Q(review__id=self.kwargs["review_id"]) & Q(group=None))


class ComplianceTaskReviewGroupModelViewSet(ComplianceTaskModelViewSet):
    display_config_class = ComplianceTaskReviewDisplayConfig
    endpoint_config_class = ComplianceTaskReviewGroupEndpointConfig
    filterset_class = ComplianceTaskReviewFilter
    serializer_class = ComplianceTaskReviewModelSerializer

    def get_queryset(self):
        return super().get_queryset().filter(Q(review__id=self.kwargs["review_id"]) & Q(group=self.kwargs["group_id"]))


class ComplianceTaskInstanceReviewNoGroupModelViewSet(ComplianceTaskInstanceModelViewSet):
    IDENTIFIER = "wbcompliance:review-compliancetaskinstancenogroup"
    display_config_class = ComplianceTaskInstanceReviewDisplayConfig
    endpoint_config_class = ComplianceTaskInstanceReviewNoGroupEndpointConfig

    def get_serializer_class(self):
        return ComplianceTaskInstanceModelSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(Q(review__id=self.kwargs["review_id"]) & Q(task__group=None))
            .annotate(
                task_title=F("task__title"),
                active=F("task__active"),
                type_name=F("task__type__name"),
                group_name=F("task__group__name"),
            )
        )


class ComplianceTaskInstanceReviewGroupModelViewSet(ComplianceTaskInstanceModelViewSet):
    IDENTIFIER = "wbcompliance:review-compliancetaskinstancegroup"
    display_config_class = ComplianceTaskInstanceReviewDisplayConfig
    endpoint_config_class = ComplianceTaskInstanceReviewGroupEndpointConfig

    def get_serializer_class(self):
        return ComplianceTaskInstanceModelSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(Q(review__id=self.kwargs["review_id"]) & Q(task__group=self.kwargs["group_id"]))
            .annotate(
                task_title=F("task__title"),
                active=F("task__active"),
                type_name=F("task__type__name"),
                group_name=F("task__group__name"),
            )
        )
