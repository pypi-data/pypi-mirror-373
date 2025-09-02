from typing import Optional

from django.utils.translation import gettext as _
from wbcore.contrib.color.enums import WBColor
from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class RuleThresholdRiskRuleDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                # dp.Field(key="range", label=_("Range")),
                dp.Field(key="range_lower", label=_("Lower Range")),
                dp.Field(key="range_upper", label=_("Upper Range")),
                dp.Field(key="severity", label=_("Severity")),
                dp.Field(key="notifiable_users", label=_("Notifiable Users")),
                dp.Field(key="notifiable_groups", label=_("Notifiable Groups")),
                dp.Field(key="upgradable_after_days", label=_("Upgrade severity after")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["severity", "upgradable_after_days", "range_lower", "range_upper"],
                [repeat_field(2, "notifiable_users"), repeat_field(2, "notifiable_groups")],
            ]
        )


class RuleCheckedObjectRelationshipRiskRuleDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                # dp.Field(key="checked_object_content_type",  label=_("Content Type")),
                # dp.Field(key="checked_object_id",  label=_("Object ID")),
                dp.Field(key="checked_object_repr", label=_("Checked Objects")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["checked_object_id" if self.new_mode else "checked_object_repr"]])


class RiskRuleDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label=_("Name"), width=Unit.PIXEL(300)),
                dp.Field(key="description", label=_("Description")),
                dp.Field(key="open_incidents_count", label=_("Open Incidents")),
                dp.Field(key="is_enable", label=_("Enable")),
                dp.Field(key="only_passive_check_allowed", label=_("Passive Only")),
                dp.Field(
                    key=None,
                    label="Administration",
                    open_by_default=False,
                    children=[
                        dp.Field(key="rule_backend", label=_("Rule Backend"), width=Unit.PIXEL(200)),
                        dp.Field(key="frequency", label=_("Frequency"), width=Unit.PIXEL(200)),
                        dp.Field(key="activation_date", label=_("Activation Date"), width=Unit.PIXEL(200)),
                        dp.Field(key="is_silent", label=_("Silent"), show="open"),
                        dp.Field(key="is_mandatory", label=_("Mandatory"), show="open"),
                        dp.Field(
                            key="automatically_close_incident", label=_("Automatically Close Incidents"), show="open"
                        ),
                        dp.Field(key="apply_to_all_active_relationships", label=_("All Checked Objects"), show="open"),
                        dp.Field(key="permission_type", label=_("Permission"), show="open"),
                    ],
                ),
            ],
            legends=[
                dp.Legend(
                    key="in_breach",
                    items=[
                        dp.LegendItem(icon=WBColor.RED_LIGHT.value, label=_("In Breach"), value="BREACH"),
                        dp.LegendItem(icon=WBColor.GREEN_LIGHT.value, label=_("Passed"), value="PASSED"),
                    ],
                ),
            ],
            formatting=[
                dp.Formatting(
                    column="in_breach",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.RED_LIGHT.value},
                            condition=("==", "BREACH"),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=("==", "PASSED"),
                        ),
                    ],
                )
            ],
        )

    def get_instance_display(self) -> Display:
        try:
            rule = self.view.get_object()
            parameter_fields = [
                [
                    f"parameters__{field}"
                    for field in rule.rule_backend.backend_class.get_serializer_class().get_parameter_fields()
                ]
            ]
        except Exception:
            parameter_fields = [["parameters"]]
        return create_simple_display(
            [
                [repeat_field(2, "name"), repeat_field(2, "rule_backend"), "is_enable"],
                ["permission_type", "frequency", "activation_date", repeat_field(2, "creator")],
                [
                    "only_passive_check_allowed",
                    "is_silent",
                    "is_mandatory",
                    "automatically_close_incident",
                    "apply_to_all_active_relationships",
                ],
                [repeat_field(5, "description")],
                [repeat_field(5, "parameters_section")],
                [repeat_field(5, "thresholds_section")],
                [repeat_field(5, "relationships_section")],
                [repeat_field(5, "incidents_section")],
            ],
            [
                create_simple_section("parameters_section", _("Parameters"), parameter_fields, collapsed=True),
                create_simple_section(
                    "thresholds_section", _("Thresholds"), [["thresholds"]], "thresholds", collapsed=True
                ),
                create_simple_section(
                    "relationships_section", _("Relationships"), [["relationships"]], "relationships", collapsed=True
                ),
                create_simple_section(
                    "incidents_section", _("Incidents"), [["incidents"]], "incidents", collapsed=False
                ),
            ],
        )
