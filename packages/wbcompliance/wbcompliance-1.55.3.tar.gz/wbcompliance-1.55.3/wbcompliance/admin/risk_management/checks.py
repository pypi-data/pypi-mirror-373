from django.contrib import admin

from wbcompliance.models.risk_management.checks import RiskCheck


@admin.register(RiskCheck)
class RiskCheckModelAdmin(admin.ModelAdmin):
    list_display = ["rule", "creation_datetime", "evaluation_date"]
