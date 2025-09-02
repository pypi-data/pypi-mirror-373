from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from wbcompliance.models.risk_management.rules import (
    RiskRule,
    RuleBackend,
    RuleCheckedObjectRelationship,
    RuleGroup,
    RuleThreshold,
)

from .incidents import IncidentInLine


class RuleThresholdInLine(admin.TabularInline):
    model = RuleThreshold
    fields = ["range", "severity", "notifiable_users", "notifiable_groups"]
    extra = 0
    autocomplete_fields = ["notifiable_users"]
    raw_id_fields = ["notifiable_users", "notifiable_groups", "rule"]


class RuleCheckedObjectRelationshipInLine(admin.TabularInline):
    model = RuleCheckedObjectRelationship
    fields = [
        "checked_object_content_type",
        "checked_object_id",
    ]
    extra = 0
    raw_id_fields = ["checked_object_content_type", "rule"]


@admin.register(RuleGroup)
class RuleGroupModelAdmin(admin.ModelAdmin):
    list_display = [
        "key",
        "name",
    ]


@admin.register(RuleBackend)
class RuleBackendModelAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "rule_group",
        "backend_class_path",
        "backend_class_name",
        "allowed_checked_object_content_type",
    ]
    raw_id_fields = ["allowed_checked_object_content_type"]


@admin.register(RiskRule)
class RiskRuleModelAdmin(GuardedModelAdmin):
    list_display = [
        "name",
        "rule_backend",
        "is_enable",
        "only_passive_check_allowed",
        "is_silent",
        "is_mandatory",
        "parameters",
    ]
    inlines = [RuleThresholdInLine, IncidentInLine, RuleCheckedObjectRelationshipInLine]
