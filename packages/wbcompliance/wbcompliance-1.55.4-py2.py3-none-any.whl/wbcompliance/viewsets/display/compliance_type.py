from typing import Optional

from django.utils.translation import gettext as _
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class ComplianceTypeDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label=_("Name")),
                dp.Field(key="in_charge", label=_("Group of administrators")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["name", "description", "in_charge", "administrators"]])
