from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import gettext as _
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)

from wbcompliance.models import ComplianceType, ReviewComplianceTask
from wbcompliance.viewsets.buttons.compliance_form import (
    AbstractComplianceDocumentButtonConfig,
)


def get_custom_report(_request, review: ReviewComplianceTask):
    try:
        content_type = ContentType.objects.get(app_label="wbcompliance", model="reviewcompliancetask")
        ReportVersion = apps.get_model("wbreport", "ReportVersion")
        BUTTTONS = []
        versions = ReportVersion.objects.filter(
            version_date=review.to_date, report__content_type=content_type, report__is_active=True
        ).filter(Q(parameters__type=review.type.name) | Q(parameters__type=review.type.id))
        for version in versions:
            BUTTTONS.append(
                bt.HyperlinkButton(
                    endpoint=reverse("report:reportversion-html", args=[version.id], request=_request),
                    label=_("Show {}").format(version.title),
                    icon=WBIcon.DOCUMENT.icon,
                )
            )
            if not version.lock:
                BUTTTONS.append(
                    bt.ActionButton(
                        method=RequestType.GET,
                        identifiers=("wbreport:reportversion",),
                        endpoint=reverse("wbreport:reportversion-updatecontext", args=[version.id], request=_request),
                        label=_("Update {}").format(version.title),
                        description_fields=_(
                            """
                        <p>Update and actualize context</p>
                        """
                        ),
                        icon=WBIcon.REGENERATE.icon,
                        action_label=_("Update Context {}").format(version.title),
                        title=_("Update {}").format(version.title),
                    ),
                )
        if BUTTTONS:
            return {
                bt.DropDownButton(
                    label=_("Report"),
                    icon=WBIcon.UNFOLD.icon,
                    buttons=tuple(BUTTTONS),
                ),
            }
    except LookupError:
        pass

    return set()


class ComplianceTaskButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self):
        class OccuredSerializer(wb_serializers.Serializer):
            occured = wb_serializers.DateField(required=True)

        BUTTONS = []
        if self.view.kwargs.get("pk", None) and self.request.user.is_superuser:
            review = self.view.get_object()
            if review.active:
                BUTTONS += [
                    bt.ActionButton(
                        method=RequestType.PATCH,
                        identifiers=("wbcompliance:compliancetask",),
                        key="generateinstance",
                        action_label=_("Generate Instance"),
                        title=_("Generate Instance "),
                        label=_("Generate Instance"),
                        icon=WBIcon.ADD.icon,
                        serializer=OccuredSerializer,
                        instance_display=create_simple_display([["occured"]]),
                    )
                ]
        return {*BUTTONS}


class ReviewComplianceTaskButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self):
        class LinkedTypeSerializer(wb_serializers.Serializer):
            type = wb_serializers.ChoiceField(
                required=True, choices=ComplianceType.objects.all().values_list("name", flat=True)
            )
            operation = wb_serializers.ChoiceField(
                choices=[("ADD", "Add existing indicators"), ("REMOVE", "Remove existing Indicators")],
            )

        BUTTONS = []
        if self.view.kwargs.get("pk", None) and self.request.user.has_perm("wbcompliance.administrate_compliance"):
            review = self.view.get_object()
            if review.is_instance:
                BUTTONS = get_custom_report(_request=self.request, review=review)
            else:
                if review.status == ReviewComplianceTask.Status.VALIDATED:
                    BUTTONS += [AbstractComplianceDocumentButtonConfig._get_compliance_document_button()]

                    if self.request.user.has_perm("wbcompliance.administrate_compliance"):
                        BUTTONS += [
                            bt.ActionButton(
                                method=RequestType.PATCH,
                                identifiers=("wbcompliance:reviewcompliancetask",),
                                key="generate_instance",
                                action_label="Generate Instance Report Indicator",
                                title="Generate Instance Report Indicator",
                                label="Generate Instance Report Indicator",
                                icon=WBIcon.ADD.icon,
                                confirm_config=bt.ButtonConfig(label=_("Confirm")),
                                cancel_config=bt.ButtonConfig(label=_("Cancel")),
                            ),
                        ]

                if review.status == ReviewComplianceTask.Status.DRAFT and self.request.user.is_superuser:
                    BUTTONS += [
                        bt.ActionButton(
                            method=RequestType.PATCH,
                            identifiers=("wbcompliance:reviewcompliancetask",),
                            key="link_tasks",
                            action_label=_("Add/Remove Indicators of a Type"),
                            title=_("Add/Remove existing indicators"),
                            label=_("Add/Remove existing indicators"),
                            icon=WBIcon.LINK.icon,
                            description_fields=_(
                                """
                            <p> <b>Indicators Report : <span>{{title}} </span></b><br/><br/>
                            Linking Indicators of type
                            """
                            ),
                            serializer=LinkedTypeSerializer,
                            instance_display=create_simple_display([["type"], ["operation"]]),
                            confirm_config=bt.ButtonConfig(label=_("Confirm")),
                            cancel_config=bt.ButtonConfig(label=_("Cancel")),
                        ),
                    ]

        return {*BUTTONS}
