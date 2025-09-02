from django.utils.translation import gettext as _
from wbcore.metadata.configs.titles import TitleViewConfig

from wbcompliance.models import (
    ComplianceForm,
    ComplianceFormRule,
    ComplianceFormSection,
    ComplianceFormSignatureRule,
    ComplianceFormSignatureSection,
)


class ComplianceFormTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Compliance Form: {{title}} - version {{version}}")

    def get_list_title(self):
        return _("Compliance Forms")

    def get_create_title(self):
        return _("New Compliance Form")


class ComplianceFormSignatureTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Compliance Form Signature: {{_compliance_form.title}} - version {{_compliance_form.version}}")

    def get_list_title(self):
        return _("Compliance Form Signatures")

    def get_create_title(self):
        return _("New Compliance Form Signature")


class ComplianceFormSectionTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        if ref_id := self.view.kwargs.get("pk"):
            _section = ComplianceFormSection.objects.get(id=ref_id)
            return _("Compliance Form Section: {} of Compliance Form: - version {}").format(
                _section.name, _section.compliance_form.title, _section.compliance_form.version
            )

        return _("Compliance Form Section: {{name}}")

    def get_list_title(self):
        if compliance_form_id := self.view.kwargs.get("compliance_form_id"):
            compliance_form = ComplianceForm.objects.get(id=compliance_form_id)
            return _("Compliance Form: {} - version {}").format(compliance_form.title, compliance_form.version)
        return _("Compliance Form Sections")

    def get_create_title(self):
        if compliance_form_id := self.view.kwargs.get("compliance_form_id"):
            compliance_form = ComplianceForm.objects.get(id=compliance_form_id)
            return _("New Section of Compliance Form: {} - version {}").format(
                compliance_form.title, compliance_form.version
            )
        return _("New Section")


class ComplianceFormSectionRuleTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        if ref_id := self.view.kwargs.get("pk"):
            _rule = ComplianceFormRule.objects.get(id=ref_id)
            return _("Compliance Form Rule: {} of Section: {}").format(_rule.id, _rule.section.name)
        return _("Compliance Form Rule: {{id}}")

    def get_list_title(self):
        if section_id := self.view.kwargs.get("section_id"):
            section = ComplianceFormSection.objects.get(id=section_id)
            return _("Compliance Form: {} - version {}").format(
                section.compliance_form.title, section.compliance_form.version
            )
        return _("Compliance Form Rules")

    def get_create_title(self):
        if section_id := self.view.kwargs.get("section_id"):
            section = ComplianceFormSection.objects.get(id=section_id)
            return _("New Rule of Section: {}").format(section.name)
        return _("New Rule")


class ComplianceFormSignatureSectionRuleTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        if ref_id := self.view.kwargs.get("pk"):
            _rule = ComplianceFormSignatureRule.objects.get(id=ref_id)
            return _("Compliance Form Signature Rule: {} of Section: {}").format(_rule.id, _rule.section.name)
        return _("Compliance Form Signature Rule: {{id}}")

    def get_list_title(self):
        if section_id := self.view.kwargs.get("section_id"):
            section = ComplianceFormSignatureSection.objects.get(id=section_id)
            return _("Compliance Form Signature: {} - version {}").format(
                section.compliance_form_signature.compliance_form.title,
                section.compliance_form_signature.compliance_form.version,
            )
        return _("Compliance Form Signature Rules")

    def get_create_title(self):
        if section_id := self.view.kwargs.get("section_id"):
            section = ComplianceFormSignatureSection.objects.get(id=section_id)
            return _("New Rule of Section: {}").format(section.name)
        return _("New Rule")
