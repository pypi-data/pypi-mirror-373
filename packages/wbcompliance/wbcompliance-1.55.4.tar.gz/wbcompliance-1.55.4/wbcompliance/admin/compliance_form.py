from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin

from wbcompliance.models import (
    ComplianceForm,
    ComplianceFormRule,
    ComplianceFormSection,
    ComplianceFormSignature,
    ComplianceFormSignatureRule,
    ComplianceFormSignatureSection,
    ComplianceFormType,
)


@admin.register(ComplianceFormType)
class ComplianceFormTypeAdmin(CompareVersionAdmin):
    list_display = ["name", "type"]


@admin.register(ComplianceForm)
class ComplianceFormAdmin(CompareVersionAdmin):
    list_display = ["status", "creator", "created", "title"]

    autocomplete_fields = ["creator"]

    def reversion_register(self, model, **options):
        options = {
            "ignore_duplicates": True,
        }
        super().reversion_register(model, **options)


@admin.register(ComplianceFormSignature)
class ComplianceFormSignatureAdmin(CompareVersionAdmin):
    list_display = ["compliance_form", "version", "signed", "person"]

    autocomplete_fields = ["person"]


@admin.register(ComplianceFormSection)
class ComplianceFormSectionAdmin(CompareVersionAdmin):
    list_display = ["compliance_form", "name"]


@admin.register(ComplianceFormRule)
class ComplianceFormRuleAdmin(CompareVersionAdmin):
    list_display = ["section", "text", "ticked"]


@admin.register(ComplianceFormSignatureSection)
class ComplianceFormSignatureSectionAdmin(CompareVersionAdmin):
    list_display = ["compliance_form_signature", "name"]


@admin.register(ComplianceFormSignatureRule)
class ComplianceFormSignatureRuleAdmin(CompareVersionAdmin):
    list_display = ["section", "text", "ticked", "comments"]
