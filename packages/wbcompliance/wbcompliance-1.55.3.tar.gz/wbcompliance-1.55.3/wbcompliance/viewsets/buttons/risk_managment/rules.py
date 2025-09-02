from django.utils.translation import gettext as _
from wbcore import serializers as wb_serializers
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)


class RiskRuleButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self):
        class CheckSerializer(wb_serializers.Serializer):
            start = wb_serializers.DateField(label=_("Start"))
            end = wb_serializers.DateField(label=_("End"))

        return {
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("risk_management:riskcheck",),
                key="recheck",
                label=_("Recheck Rules"),
                icon=WBIcon.REGENERATE.icon,
                description_fields=_(
                    """
                <p>Recheck all the rules between a certain interval</p>
                """
                ),
                serializer=CheckSerializer,
                action_label=_("recheck"),
                title=_("Recheck Rules"),
                instance_display=create_simple_display([["start"], ["end"]]),
            )
        }
