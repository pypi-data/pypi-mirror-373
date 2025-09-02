from django.utils.translation import gettext as _
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)

from wbcompliance.models.risk_management import RiskIncident


class RiskIncidentButtonConfig(ButtonViewConfig):
    def get_custom_buttons(self):
        if not self.view.kwargs.get("pk", None) and RiskIncident.can_manage(self.request.user):

            class RiskRuleTypeSerializer(wb_serializers.Serializer):
                resolve_status = wb_serializers.ChoiceField(
                    label=_("Rule Type"),
                    choices=[
                        (RiskIncident.Status.RESOLVED.name, RiskIncident.Status.RESOLVED.label),
                        (RiskIncident.Status.IGNORED.name, RiskIncident.Status.IGNORED.label),
                    ],
                    default=RiskIncident.Status.RESOLVED,
                )
                comment = wb_serializers.TextField(default="", label=_("Comment"))

            endpoint = reverse("wbcompliance:riskincident-resolveallincidents", args=[], request=self.request)
            queryset = RiskIncident.objects.all()
            if rule_id := self.view.kwargs.get("rule_id", None):
                queryset = queryset.filter(rule=rule_id)
                endpoint += f"?rule_id={rule_id}"
            return {
                bt.ActionButton(
                    method=RequestType.PATCH,
                    identifiers=("wbcompliance:riskincident",),
                    endpoint=endpoint,
                    label=_("Resolve all open Incident"),
                    description_fields=_(
                        "<p>Are you sure you want to close the current <b>{}</b> opened incidents?</p>"
                    ).format(queryset.count()),
                    serializer=RiskRuleTypeSerializer,
                    action_label=_("resolveallincidents"),
                    title=_("Resolve all open Incident"),
                    instance_display=create_simple_display([["resolve_status"], ["comment"]]),
                )
            }
        return set()

    def get_custom_list_instance_buttons(self):
        return set()
