from django.contrib import admin

from wbcompliance.models.risk_management.incidents import (
    CheckedObjectIncidentRelationship,
    RiskIncident,
    RiskIncidentType,
)


class CheckedObjectIncidentRelationshipInLine(admin.TabularInline):
    model = CheckedObjectIncidentRelationship
    fields = ["status", "severity", "incident", "rule_check", "breached_value", "report_details", "report"]
    extra = 0
    raw_id_fields = ["incident", "rule_check"]
    readonly_fields = ["status", "severity", "incident", "rule_check"]


class IncidentInLine(admin.TabularInline):
    show_change_link = True
    model = RiskIncident
    fields = ["status", "severity", "date_range", "breached_content_type", "breached_object_id"]
    extra = 0


@admin.register(RiskIncidentType)
class RiskIncidentTypeModelAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "severity_order",
        "color",
        "is_ignorable",
        "is_automatically_closed",
        "is_informational",
    ]


@admin.register(RiskIncident)
class RiskIncidentModelAdmin(admin.ModelAdmin):
    list_display = [
        "status",
        "severity",
        "date_range",
        "rule",
        "breached_content_type",
        "breached_object_id",
        "resolved_by",
    ]

    inlines = [
        CheckedObjectIncidentRelationshipInLine,
    ]
