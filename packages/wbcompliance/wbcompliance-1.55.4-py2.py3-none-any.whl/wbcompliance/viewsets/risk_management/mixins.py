from contextlib import suppress

from rest_framework.reverse import reverse
from wbcore.metadata.configs import buttons as bt
from wbcore.signals import add_instance_button

from wbcompliance.models.risk_management.checks import RiskCheck


class RiskCheckViewSetMixin:
    @classmethod
    def _get_risk_checks_button_title(cls) -> str:
        return "Checks"

    def _add_risk_check_button(self, sender, many, *args, view=None, **kwargs):
        with suppress(AssertionError):
            if view and (instance := view.get_object()):
                icon = RiskCheck.CheckStatus[instance.get_worst_check_status()].icon
                if instance.checks.exists():
                    return bt.WidgetButton(
                        endpoint=f'{reverse("wbcompliance:riskcheck-list", args=[], request=self.request)}?checked_objects=[[{instance.checked_object_content_type.id},{instance.checked_object.id}]]&evaluation_date={instance.check_evaluation_date}&activators=[[{instance.activator_content_type.id},{instance.activator_id}]]&passive_check=False',
                        label=self._get_risk_checks_button_title(),
                        icon=icon,
                    )

    def options(self, request, *args, **kwargs):
        """
        Handler method for HTTP 'OPTIONS' request.
        """
        add_instance_button.connect(
            self._add_risk_check_button,
            sender=self.__class__,
            dispatch_uid="wbcompliance_add_instance_button_riskcheck",
        )
        return super().options(request, *args, **kwargs)
