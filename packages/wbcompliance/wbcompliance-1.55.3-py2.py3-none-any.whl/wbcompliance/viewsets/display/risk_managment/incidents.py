from typing import Optional

from django.utils.translation import gettext as _
from rest_framework.reverse import reverse
from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbcompliance.models.risk_management import RiskIncident, RiskIncidentType


def get_formatting(id_field="id", color=False):
    formattings = []
    for _type in RiskIncidentType.objects.all():
        style = {"backgroundColor": _type.color}
        if color:
            style["color"] = _type.color
        formattings.append(
            dp.FormattingRule(
                style=style,
                condition=("==", getattr(_type, id_field)),
            ),
        )
    return dp.Formatting(column="severity", formatting_rules=formattings)


def get_legends():
    legends = []
    for _type in RiskIncidentType.objects.all():
        legends.append(dp.LegendItem(icon=_type.color, label=_type.name, value=_type.id))
    return dp.Legend(items=legends, key="severity")


class RiskIncidentDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="date_range", label=_("Date Range"), pinned="left"),
            dp.Field(
                key=None,
                label="Rule",
                open_by_default=False,
                children=[
                    # dp.Field(key="status_icon", label=""),
                    dp.Field(key="status", label=_("Status"), show="open"),
                    dp.Field(key="object_repr", label=_("Object")),
                    dp.Field(key="rule", label=_("Rule")),
                    dp.Field(key="threshold_repr", label=_("Breached Threshold")),
                ],
            ),
            dp.Field(
                key=None,
                label="Incident",
                open_by_default=False,
                children=[
                    dp.Field(key="breached_value", label=_("Breached Value")),
                    dp.Field(key="report", label=_("Report Detail"), show="open"),
                    dp.Field(key="checked_date", label=_("Date"), show="open"),
                ],
            ),
            dp.Field(
                key=None,
                label="Management",
                open_by_default=False,
                children=[
                    dp.Field(key="resolved_by", label=_("Resolved By")),
                    dp.Field(key="is_notified", label=_("Users notified"), show="open"),
                    dp.Field(key="ignore_until", label=_("Ignored Until"), show="open"),
                    dp.Field(key="comment", label=_("Comment"), show="open"),
                ],
            ),
        ]
        return dp.ListDisplay(
            fields=fields,
            tree=True,
            tree_group_level_options=[
                dp.TreeGroupLevelOption(
                    filter_key="incident",
                    filter_depth=1,
                    clear_filter=False,
                    filter_whitelist=["checked_object_relationships"],
                    list_endpoint=reverse(
                        "wbcompliance:checkedobjectincidentrelationship-list",
                        args=[],
                        request=self.request,
                    ),
                )
            ],
            # tree_group_lookup="id_repr",
            tree_group_field="date_range",
            legends=[
                get_legends(),
                dp.Legend(
                    key="status",
                    items=[
                        dp.LegendItem(
                            icon=WBIcon.VIEW.icon,
                            label=_("{} Incidents").format(RiskIncident.Status.OPEN.label),
                            value=RiskIncident.Status.OPEN.name,
                        ),
                    ],
                ),
            ],
            formatting=[
                get_formatting(),
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(3, "status")],
                ["date_range", "rule", "severity"],
                ["breached_content_type", "breached_object_id", "breached_object_repr"],
                ["comment", "resolved_by", "ignore_until"],
                [repeat_field(3, "relationships_section")],
            ],
            [
                create_simple_section(
                    "relationships_section", _("Relationships"), [["relationships"]], "relationships", collapsed=False
                )
            ],
        )


class CheckedObjectIncidentRelationshipRiskRuleDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="status", label=_("status")),
                dp.Field(key="checked_date", label=_("Date")),
                dp.Field(key="rule_check", label=_("Check")),
                dp.Field(key="checked_object", label=_("Checked Object")),
                dp.Field(key="breached_value", label=_("Breached Value")),
                dp.Field(key="report", label=_("Report")),
                dp.Field(key="resolved_by", label=_("resolved_by")),
                dp.Field(key="comment", label=_("comment")),
            ],
            legends=[get_legends()],
            formatting=[
                get_formatting(),
            ],
        )
