from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin

from wbcompliance.models import ComplianceType


@admin.register(ComplianceType)
class ComplianceTypeAdmin(CompareVersionAdmin):
    list_display = ["name"]
