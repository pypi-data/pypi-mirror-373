from django.utils.translation import gettext as _
from wbcore import serializers as wb_serializers
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)

from wbcompliance.serializers import ComplianceFormSignatureModelSerializer


class AbstractComplianceDocumentButtonConfig:
    @classmethod
    def _get_compliance_document_button(cls) -> bt.ActionButton:
        class ComplianceDocumentSerializer(wb_serializers.Serializer):
            send_email = wb_serializers.BooleanField(default=False, label=_("Email me the document"))

        return bt.ActionButton(
            method=RequestType.PATCH,
            key="regenerate_document",
            action_label=_("Regenerate Document"),
            title=_("Regenerate Document"),
            label=_("Regenerate Document"),
            icon=WBIcon.DOCUMENT.icon,
            serializer=ComplianceDocumentSerializer,
            instance_display=create_simple_display([["send_email"]]),
        )


# COMPLIANCE FORM
class ComplianceFormButtonConfig(ButtonViewConfig):
    CUSTOM_INSTANCE_BUTTONS = CUSTOM_LIST_INSTANCE_BUTTONS = {
        bt.ActionButton(
            method=RequestType.PATCH,
            identifiers=("wbcompliance:compliance_form",),
            key="send_compliance_form_notification",
            action_label=_("Send signature reminder notification"),
            title=_("Send signature reminder notification"),
            label=_("Send signature reminder notification"),
            icon=WBIcon.FEEDBACK.icon,
            description_fields=_(
                """<p> <b>{{_form_type.name}} :</b> {{title}}</p>
             <p>Do you want to send a Compliance Form reminder notification ? </p>"""
            ),
            confirm_config=bt.ButtonConfig(label=_("Confirm")),
            cancel_config=bt.ButtonConfig(label=_("Cancel")),
        ),
        bt.WidgetButton(key="signatures", label=_("List all signatures"), icon=WBIcon.VIEW.icon),
        AbstractComplianceDocumentButtonConfig._get_compliance_document_button(),
    }


# COMPLIANCE FORM SIGNATURE
class ComplianceFormSignatureButtonConfig(ButtonViewConfig):
    CUSTOM_INSTANCE_BUTTONS = CUSTOM_LIST_INSTANCE_BUTTONS = {
        bt.ActionButton(
            method=RequestType.PATCH,
            identifiers=("wbcompliance:complianceformsignature",),
            key="signature",
            action_label=_("Signature"),
            title=_("Signature Compliance Form"),
            label=_("Signature"),
            icon=WBIcon.CONFIRM.icon,
            description_fields=_(
                """
            <p> <b>{{_compliance_form.form_type}} : <span>{{_compliance_form.title}}</span></b></p>
            <p>Version : {{version}}</p> <p><br/><br/>Do you want to sign <b>{{_compliance_form.title}}</b> ? </p>
            <p><span style='color:red'>This action is not reversible</span></p>
            """
            ),
            serializer=ComplianceFormSignatureModelSerializer,
            confirm_config=bt.ButtonConfig(label=_("Confirm")),
            cancel_config=bt.ButtonConfig(label=_("Cancel")),
            instance_display=create_simple_display([["remark"]]),
        ),
        AbstractComplianceDocumentButtonConfig._get_compliance_document_button(),
    }
