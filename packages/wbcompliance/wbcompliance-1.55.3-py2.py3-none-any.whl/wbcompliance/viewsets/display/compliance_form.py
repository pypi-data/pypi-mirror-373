from typing import Optional

from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from wbcore.contrib.color.enums import WBColor
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbcompliance.models import (
    ComplianceForm,
    ComplianceFormSection,
    ComplianceFormSignatureSection,
    ComplianceFormType,
)


# TYPE OF THE COMPLIANCE FORM
class ComplianceFormTypeDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="name", label=_("Name")),
            dp.Field(key="type", label=_("Type")),
        ]
        return dp.ListDisplay(
            fields=fields,
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["name", "type"]])


# SECTION OF THE COMPLIANCE FORM
class ComplianceFormSectionDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="name", label=_("Titles")),
        ]
        return dp.ListDisplay(
            fields=fields,
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["compliance_form", "name"] if "compliance_form_id" not in self.view.kwargs else ["name", "name"],
                [repeat_field(2, "rules_section")],
            ],
            [create_simple_section("rules_section", _("Rules"), [["rules"]], "rules", collapsed=False)],
        )


# RULES OF THE SECTION
class ComplianceFormRuleDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="text", label=_("Text")),
            dp.Field(key="ticked", label=_("Expected Answer")),
        ]
        return dp.ListDisplay(
            fields=fields,
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["ticked", repeat_field(2, "text")]])


# RULES OF THE SECTION OF THE COMPLIANCE FORM SIGNATURE
class ComplianceFormSignatureSectionRuleDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="text", label=_("Text")),
            dp.Field(
                key="ticked", label=_("Answer"), formatting_rules=[dp.FormattingRule(style={"fontWeight": "bold"})]
            ),
            dp.Field(key="comments", label=_("Comments")),
        ]
        if self.request.user.has_perm("wbcompliance.administrate_compliance") and (
            section_id := self.view.kwargs.get("section_id")
        ):
            section_signature = get_object_or_404(ComplianceFormSignatureSection, pk=section_id)
            if section_signature.compliance_form_signature.person != self.request.user.profile:
                fields = [
                    dp.Field(key="text", label=_("Text")),
                    dp.Field(key="expected_result", label=_("Expected Answer")),
                    dp.Field(
                        key="ticked",
                        label=_("Answer"),
                        formatting_rules=[dp.FormattingRule(style={"fontWeight": "bold"})],
                    ),
                    dp.Field(key="comments", label=_("Comments")),
                ]
        return dp.ListDisplay(
            fields=fields,
            formatting=[
                dp.Formatting(
                    column="same_answer",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.YELLOW_LIGHT.value},
                            condition=("==", False),
                        ),
                    ],
                ),
            ],
        )

    def get_instance_display(self) -> Display:
        grid_fields = [
            ["section", "ticked"],
            [repeat_field(2, "text")],
            [repeat_field(2, "comments")],
        ]
        if self.request.user.has_perm("wbcompliance.administrate_compliance") and (
            section_id := self.view.kwargs.get("section_id")
        ):
            section_signature = get_object_or_404(ComplianceFormSignatureSection, pk=section_id)
            if section_signature.compliance_form_signature.person != self.request.user.profile:
                grid_fields = [
                    ["section", "ticked", "expected_result"],
                    [repeat_field(3, "text")],
                    [repeat_field(3, "comments")],
                ]
        return create_simple_display(grid_fields)


# COMPLIANCE FORM
class ComplianceFormDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="title", label=_("Title")),
            dp.Field(key="creator", label=_("Creator")),
            dp.Field(key="changer", label=_("Changer")),
            dp.Field(key="changed", label=_("Changed")),
            dp.Field(key="start", label=_("Start")),
            dp.Field(key="end", label=_("End")),
            dp.Field(key="version", label=_("Last Version")),
        ]
        if self.request.user.has_perm("wbcompliance.administrate_compliance"):
            fields.append(dp.Field(key="current_signed", label=_("Current Signed")))
        else:
            fields.append(
                dp.Field(
                    key="is_signed",
                    label=_("Is Signed"),
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"color": WBColor.RED.value, "fontWeight": "bold"},
                        ),
                    ],
                )
            )

        fields.append(dp.Field(key="form_type", label=_("Form Type")))
        fields.append(dp.Field(key="compliance_type", label=_("Administrator")))

        return dp.ListDisplay(
            fields=fields,
            formatting=[
                dp.Formatting(
                    column="status",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.BLUE_LIGHT.value},
                            condition=("==", ComplianceForm.Status.DRAFT.name),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.YELLOW_LIGHT.value},
                            condition=("==", ComplianceForm.Status.ACTIVATION_REQUESTED.name),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=("==", ComplianceForm.Status.ACTIVE.name),
                        ),
                    ],
                ),
            ],
            legends=[
                dp.Legend(
                    key="status",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.BLUE_LIGHT.value,
                            label=ComplianceForm.Status.DRAFT.label,
                            value=ComplianceForm.Status.DRAFT.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.YELLOW_LIGHT.value,
                            label=ComplianceForm.Status.ACTIVATION_REQUESTED.label,
                            value=ComplianceForm.Status.ACTIVATION_REQUESTED.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value,
                            label=ComplianceForm.Status.ACTIVE.label,
                            value=ComplianceForm.Status.ACTIVE.value,
                        ),
                    ],
                ),
            ],
        )

    def get_instance_display(self) -> Display:
        fields = [
            ["form_type", "compliance_type"],
            [repeat_field(2, "title")],
            ["start", "end"],
            ["version", "status"],
            [repeat_field(2, "signers_section")],
        ]
        sections = [
            create_simple_section(
                "signers_section",
                _("Signers"),
                [["assigned_to", "assigned_to", "only_internal"]],
                collapsed=True,
            )
        ]
        if (obj_id := self.view.kwargs.get("pk", None)) and (instance := self.view.get_object()):
            if instance.form_type.type == ComplianceFormType.Type.TEXT:
                fields += [[repeat_field(2, "policy")]]

            elif instance.form_type.type == ComplianceFormType.Type.FORM:
                fields.append([repeat_field(2, "sections_section")])
                sections.append(
                    create_simple_section(
                        "sections_section", _("Sections"), [["sections"]], "sections", collapsed=True
                    )
                )

                total = ComplianceFormSection.objects.filter(compliance_form=obj_id).count()
                for count, section in enumerate(
                    ComplianceFormSection.objects.filter(compliance_form=obj_id).order_by("id")
                ):
                    key = f"rules{section.id}"
                    fields.append([repeat_field(2, f"{key}_section")])
                    sections.append(
                        create_simple_section(
                            f"{key}_section", f"({count + 1}/{total}). {section.name}", [[key]], key, collapsed=True
                        )
                    )

        return create_simple_display(fields, sections)


# COMPLIANCE FORM SIGNATURE
class ComplianceFormSignatureDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="compliance_form", label=_("Compliance Form")),
            dp.Field(key="version", label=_("Version")),
            dp.Field(key="start", label=_("Start")),
            dp.Field(key="end", label=_("End")),
            dp.Field(key="signed", label=_("Signed")),
            # dp.Field(key="is_signed",  label=_("Is Signed"))
        ]
        if self.request.user.has_perm("wbcompliance.administrate_compliance"):
            fields.append(dp.Field(key="person", label=_("Signer")))

        return dp.ListDisplay(
            fields=fields,
            formatting=[
                dp.Formatting(
                    column="is_signed",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.YELLOW_LIGHT.value},
                            condition=("==", False),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=("==", True),
                        ),
                    ],
                ),
            ],
            legends=[
                dp.Legend(
                    # key="is_signed",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.YELLOW_LIGHT.value,
                            label=_("Unsigned"),
                            # value=False,
                        ),
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value,
                            label=_("Signed"),
                            # value=True,
                        ),
                    ],
                ),
            ],
        )

    def get_instance_display(self) -> Display:
        fields = [["compliance_form", "version"], ["person", "signed"], ["start", "end"]]
        sections = []
        if obj_id := self.view.kwargs.get("pk", None):
            instance = self.view.get_object()
            if instance.compliance_form.form_type.type == ComplianceFormType.Type.TEXT:
                fields.append([repeat_field(2, "policy")])
            elif instance.compliance_form.form_type.type == ComplianceFormType.Type.FORM:
                total = ComplianceFormSignatureSection.objects.filter(compliance_form_signature=obj_id).count()
                for count, section in enumerate(
                    ComplianceFormSignatureSection.objects.filter(compliance_form_signature=obj_id).order_by("id")
                ):
                    key = f"rules{section.id}"
                    fields.append([repeat_field(2, f"{key}_section")])
                    sections.append(
                        create_simple_section(
                            f"{key}_section", f"({count + 1}/{total}). {section.name}", [[key]], key, collapsed=True
                        )
                    )

        fields.append([repeat_field(2, "remark")])
        return create_simple_display(fields, sections)
