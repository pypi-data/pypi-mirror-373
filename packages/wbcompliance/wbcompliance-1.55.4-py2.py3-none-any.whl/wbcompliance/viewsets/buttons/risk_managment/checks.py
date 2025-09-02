from django.utils.translation import gettext as _
from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig


class RiskCheckButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return {
            bt.WidgetButton(key="incidents", label=_("Incidents"), icon=WBIcon.WARNING.icon),
        }
