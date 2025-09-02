from datetime import timedelta
from typing import Optional

from django.utils.translation import gettext as _
from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbcompliance.models import (
    ComplianceAction,
    ComplianceEvent,
    ComplianceTaskGroup,
    ComplianceTaskInstance,
    ReviewComplianceTask,
)
from wbcompliance.models.enums import IncidentSeverity


def get_legends(model=None):
    """
    Dynamically create the activity legend based on Activity Enum
    """
    list_format = []
    if model:
        for _status, color in model.Status.get_color_map():
            list_format.append(dp.LegendItem(icon=color, label=_status.label, value=_status.value))
    return [dp.Legend(key="status", items=list_format)]


def get_list_formatting(model=None):
    """
    Dynamically create the activity list formatting based on Activity Enum
    """
    color_conditions = []
    if model:
        for _status, color in model.Status.get_color_map():
            color_conditions.append(
                dp.FormattingRule(condition=("==", _status.name), style={"backgroundColor": color})
            )
    return [
        dp.Formatting(column="status", formatting_rules=color_conditions),
    ]


class ComplianceTaskGroupDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label=_("Name")),
                dp.Field(key="order", label=_("Order")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [["name", "order"], [repeat_field(2, "compliancetask_section")]],
            [
                create_simple_section(
                    "compliancetask_section", _("Indicators"), [["compliancetask"]], "compliancetask", collapsed=False
                )
            ],
        )


class ComplianceTaskDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        color_conditions = []
        list_format = []
        for _type, color in IncidentSeverity.get_color_map():
            color_conditions.append(dp.FormattingRule(condition=("==", _type.name), style={"backgroundColor": color}))
            list_format.append(dp.LegendItem(icon=color, label=_type.label, value=_type.value))

        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label=_("Title"), width=Unit.PIXEL(600)),
                dp.Field(key="occurrence", label=_("Occurrence")),
                dp.Field(key="risk_level", label=_("Risk Level")),
                dp.Field(key="active", label=_("Active")),
                dp.Field(key="group", label=_("Group"), width=Unit.PIXEL(350)),
                dp.Field(key="type", label=_("Administrator")),
                dp.Field(key="review", label=_("Indicator Reports"), width=Unit.PIXEL(300)),
            ],
            legends=[dp.Legend(key="risk_level", items=list_format)],
            formatting=[
                dp.Formatting(column="risk_level", formatting_rules=color_conditions),
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["title", "title", "type"],
                ["occurrence", "risk_level", "active"],
                ["review", "review", "group"],
                [repeat_field(3, "description")],
                [repeat_field(3, "remarks")],
                [repeat_field(3, "compliancetaskinstance_section")],
            ],
            [
                create_simple_section(
                    "compliancetaskinstance_section",
                    _("Instances"),
                    [["compliancetaskinstance"]],
                    "compliancetaskinstance",
                    collapsed=True,
                )
            ],
        )


class ComplianceTaskReviewDisplayConfig(ComplianceTaskDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        color_conditions = []
        list_format = []
        for _type, color in IncidentSeverity.get_color_map():
            color_conditions.append(dp.FormattingRule(condition=("==", _type.name), style={"backgroundColor": color}))
            list_format.append(dp.LegendItem(icon=color, label=_type.label, value=_type.value))

        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label=_("Title"), width=Unit.PIXEL(400)),
                dp.Field(key="description", label=_("Description"), width=Unit.PIXEL(400)),
                dp.Field(key="occurrence", label=_("Occurrence"), width=Unit.PIXEL(150)),
                dp.Field(key="risk_level", label=_("Risk level"), width=Unit.PIXEL(150)),
                dp.Field(key="remarks", label=_("Remarks"), width=Unit.PIXEL(250)),
                dp.Field(key="group", label=_("Group"), width=Unit.PIXEL(250)),
                dp.Field(key="type", label=_("Administrator"), width=Unit.PIXEL(160)),
            ],
            legends=[dp.Legend(key="risk_level", items=list_format)],
            formatting=[
                dp.Formatting(column="risk_level", formatting_rules=color_conditions),
            ],
        )


class ComplianceTaskInstanceDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="task", label=_("Indicators")),
                dp.Field(key="occured", label=_("Occured")),
                dp.Field(key="status", label=_("Status")),
                dp.Field(key="type_name", label=_("Administrator")),
                dp.Field(key="group_name", label=_("Group")),
                dp.Field(key="review", label=_("Indicator Instance Report")),
            ],
            legends=get_legends(ComplianceTaskInstance),
            formatting=get_list_formatting(ComplianceTaskInstance),
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "type_name")],
                ["task", "review"],
                ["status", "occured"],
                [repeat_field(2, "text")],
                [repeat_field(2, "summary_text")],
            ]
        )


class ComplianceTaskInstanceComplianceTaskDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="occured", label=_("Occured")),
                dp.Field(key="status", label=_("Status")),
                dp.Field(key="type_name", label=_("Administrator")),
                dp.Field(key="group_name", label=_("Group")),
                dp.Field(key="review", label=_("Indicator Instance Report")),
            ],
            legends=get_legends(ComplianceTaskInstance),
            formatting=get_list_formatting(ComplianceTaskInstance),
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "type_name")],
                [repeat_field(2, "review")],
                ["status", "occured"],
                [repeat_field(2, "text")],
                [repeat_field(2, "summary_text")],
            ]
        )


class ComplianceTaskInstanceReviewDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="occured", label=_("Occured"), width=Unit.PIXEL(90)),
                dp.Field(key="task_title", label=_("Indicators"), width=Unit.PIXEL(380)),
                dp.Field(key="status", label=_("Status"), width=Unit.PIXEL(200)),
                dp.Field(key="text", label=_("Text"), width=Unit.PIXEL(500)),
                dp.Field(key="summary_text", label=_("Summary Text"), width=Unit.PIXEL(400)),
                dp.Field(key="type_name", label=_("Administrator"), width=Unit.PIXEL(100)),
            ],
            legends=get_legends(ComplianceTaskInstance),
            formatting=get_list_formatting(ComplianceTaskInstance),
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "type_name")],
                [repeat_field(2, "review")],
                ["status", "occured"],
                [repeat_field(2, "text")],
                [repeat_field(2, "summary_text")],
            ]
        )


class ComplianceTaskMatrixPandasDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        _color_conditions = []
        for _status, color in ComplianceTaskInstance.Status.get_color_map():
            _color_conditions.append(
                dp.FormattingRule(condition=("==", _status.label), style={"backgroundColor": color})
            )

        _fields = [
            dp.Field(key="type_name", label=_("Administrator"), width=Unit.PIXEL(100)),
            dp.Field(key="group_name", label=_("Group"), width=Unit.PIXEL(200)),
            dp.Field(
                key="task_title",
                label=_("Indicator"),
                width=Unit.PIXEL(270),
                formatting_rules=[dp.FormattingRule(condition=("!=", ""), style={"font-weight": "bold"})],
            ),
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
                _fields.append(
                    dp.Field(
                        key=date_str, label=covered_month, formatting_rules=_color_conditions, width=Unit.PIXEL(150)
                    )
                )
        return dp.ListDisplay(fields=_fields)


class ComplianceActionDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label=_("Title")),
                dp.Field(key="status", label=_("Status")),
                dp.Field(key="deadline", label=_("Deadline")),
                dp.Field(key="progress", label=_("Progress")),
                dp.Field(key="active", label=_("Active")),
                dp.Field(key="type", label="Administrator"),
                dp.Field(key="creator", label="Creator"),
                dp.Field(key="changer", label="Changer"),
                dp.Field(key="last_modified", label="Changed"),
            ],
            legends=get_legends(ComplianceAction),
            formatting=get_list_formatting(ComplianceAction),
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "title")],
                [repeat_field(2, "type")],
                ["active", "deadline"],
                ["status", "progress"],
                ["creator", "created"],
                ["changer", "last_modified"],
                [repeat_field(2, "description")],
                [repeat_field(2, "summary_description")],
            ]
        )


class ComplianceEventDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        color_conditions = []
        list_format = []
        for _type, color in ComplianceEvent.Type.get_color_map():
            color_conditions.append(dp.FormattingRule(condition=("==", _type.name), style={"backgroundColor": color}))
            list_format.append(dp.LegendItem(icon=color, label=_type.label, value=_type.value))

        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label="Title"),
                dp.Field(key="type_event", label="Type Event"),
                dp.Field(key="level", label="Level"),
                dp.Field(key="active", label="Active"),
                dp.Field(key="type", label="Administrator"),
                dp.Field(key="creator", label="Creator"),
                dp.Field(key="changer", label="Changer"),
                dp.Field(key="last_modified", label="Changed"),
                dp.Field(key="confidential", label="Confidential"),
            ],
            legends=[dp.Legend(key="type_event", items=list_format)],
            formatting=[
                dp.Formatting(column="type_event", formatting_rules=color_conditions),
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "title")],
                [repeat_field(2, "type")],
                ["active", "confidential"],
                ["type_event", "level"],
                ["creator", "created"],
                ["changer", "last_modified"],
                [repeat_field(2, "exec_summary")],
                [repeat_field(2, "exec_summary_board")],
                [repeat_field(2, "description")],
                [repeat_field(2, "actions_taken")],
                [repeat_field(2, "consequences")],
                [repeat_field(2, "future_suggestions")],
            ]
        )


class ReviewComplianceTaskDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="year", label="Year"),
                dp.Field(key="occured", label="Occured Instance"),
                dp.Field(key="title", label="Title"),
                dp.Field(key="from_date", label="From"),
                dp.Field(key="to_date", label="To"),
                dp.Field(key="status", label="Status"),
                dp.Field(key="occurrence", label="Occurrence"),
                dp.Field(key="changer", label="Changer"),
                dp.Field(key="changed", label="Changed"),
                dp.Field(key="type", label="Administrator"),
                dp.Field(key="review_task", label="Main Indicator Report"),
            ],
            legends=get_legends(ReviewComplianceTask),
            formatting=get_list_formatting(ReviewComplianceTask),
        )

    def get_instance_display(self) -> Display:
        nb_columns = 3
        fields = [
            ["title", "type", "review_task"],
            ["from_date", "to_date", "status"],
            ["is_instance", "occurrence", "occured"],
            [repeat_field(nb_columns, "description")],
        ]

        sections = []
        if self.view.kwargs.get("pk", None):
            instance = self.view.get_object()
            if not instance.is_instance:
                if instance.status == ReviewComplianceTask.Status.DRAFT:
                    fields.append([repeat_field(nb_columns, "task_group_section")])
                    sections.append(
                        create_simple_section(
                            "task_group_section", _("Groups Indicator"), [["task_group"]], "task_group", collapsed=True
                        )
                    )

                group_ids = instance.get_task_group_ids_from_review()
                no_group_ids = instance.get_task_group_ids_from_review(task_with_group=False)
                total = len(group_ids)
                if (
                    no_group_ids and instance.status != ReviewComplianceTask.Status.DRAFT
                ) or instance.status == ReviewComplianceTask.Status.DRAFT:
                    total += 1
                for count, group_id in enumerate(group_ids):
                    group = ComplianceTaskGroup.objects.get(id=group_id)
                    key = f"taskgroup{group.id}"
                    fields.append([repeat_field(nb_columns, f"{key}_section")])
                    sections.append(
                        create_simple_section(
                            f"{key}_section", f"({count + 1}/{total}). {group.name}", [[key]], key, collapsed=True
                        )
                    )

                if (
                    no_group_ids and instance.status != ReviewComplianceTask.Status.DRAFT
                ) or instance.status == ReviewComplianceTask.Status.DRAFT:
                    fields.append([repeat_field(nb_columns, "task_no_group_section")])
                    sections.append(
                        create_simple_section(
                            "task_no_group_section",
                            f'({total}/{total}). {_("No Indicator Group")}',
                            [["task_no_group"]],
                            "task_no_group",
                            collapsed=True,
                        )
                    )

            else:
                group_ids = instance.get_task_group_ids_from_review(through_task=False)
                no_group_ids = instance.get_task_group_ids_from_review(through_task=False, task_with_group=False)
                total = len(group_ids) + 2  # We add 2 to the total number to include Actions and events
                if no_group_ids:
                    total += 1
                for count, group_id in enumerate(group_ids):
                    group = ComplianceTaskGroup.objects.get(id=group_id)
                    key = f"taskinstancegroup{group.id}"
                    fields.append([repeat_field(nb_columns, f"{key}_section")])
                    sections.append(
                        create_simple_section(
                            f"{key}_section", f"({count + 1}/{total}). {group.name}", [[key]], key, collapsed=True
                        )
                    )

                if no_group_ids:
                    fields.append([repeat_field(nb_columns, "taskinstance_no_group_section")])
                    sections.append(
                        create_simple_section(
                            "taskinstance_no_group_section",
                            f'({count + 2}/{total}). {_("No Indicator Group")}',
                            [["taskinstance_no_group"]],
                            "taskinstance_no_group",
                            collapsed=True,
                        )
                    )

                fields.append([repeat_field(nb_columns, "actions_section")])
                sections.append(
                    create_simple_section(
                        "actions_section",
                        f'({total - 1}/{total}). {_("Actions")}',
                        [["actions"]],
                        "actions",
                        collapsed=True,
                    )
                )

                fields.append([repeat_field(nb_columns, "events_section")])
                sections.append(
                    create_simple_section(
                        "events_section", f'({total}/{total}). {_("Events")}', [["events"]], "events", collapsed=True
                    )
                )

        return create_simple_display(fields, sections)
