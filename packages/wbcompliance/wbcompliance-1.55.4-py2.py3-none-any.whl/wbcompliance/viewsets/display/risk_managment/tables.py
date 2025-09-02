from typing import Optional

from django.utils.translation import gettext as _
from wbcore.contrib.color.enums import WBColor
from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from .incidents import get_formatting, get_legends


class RiskManagementIncidentTableDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        if content_type := self.view.checked_object_content_type:
            field_name = content_type.name
        else:
            field_name = "Checked object"
        fields = [
            dp.Field(
                key="checked_object_repr",
                label=field_name,
                width=Unit.PIXEL(250),
                formatting_rules=[dp.FormattingRule(style={"fontWeight": "bold"})],
            )
        ]
        for key, label in self.view.get_rule_map:
            fields.append(
                dp.Field(
                    key=key,
                    label=label,
                    width=Unit.PIXEL(200),
                    formatting_rules=[
                        dp.FormattingRule(
                            condition=("==", -1),
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value, "color": WBColor.GREEN_LIGHT.value},
                        ),
                        *get_formatting(id_field="severity_order", color=True).formatting_rules,
                    ],
                )
            )
        return dp.ListDisplay(
            fields=fields,
            legends=[
                dp.Legend(
                    items=[
                        dp.LegendItem(icon=WBColor.GREEN_LIGHT.value, label=_("No Incident")),
                        *get_legends().items,
                    ]
                )
            ],
        )
