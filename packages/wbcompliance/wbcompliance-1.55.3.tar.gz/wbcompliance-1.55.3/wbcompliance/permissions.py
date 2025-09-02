from guardian.core import ObjectPermissionChecker
from rest_framework.permissions import IsAuthenticated
from wbcore.permissions.shortcuts import is_internal_user

from wbcompliance.models.risk_management import RiskRule


class RulePermission(IsAuthenticated):
    def has_permission(self, request, view):
        permission = super().has_permission(request, view)
        if rule_id := view.kwargs.get("rule_id", None):
            checker = ObjectPermissionChecker(request.user)
            rule = RiskRule.objects.get(id=rule_id)
            permission &= checker.has_perm(rule.view_perm_str, rule)
        return permission

    def has_object_permission(self, request, view, obj):
        permission = super().has_object_permission(request, view, obj)
        # Handle case when checked_objectincidentRelationship object is given
        if incident := getattr(obj, "incident", None):
            obj = incident
        if rule := getattr(obj, "rule", None):
            checker = ObjectPermissionChecker(request.user)
            permission &= checker.has_perm(rule.view_perm_str, rule)
        return permission


def is_admin_compliance(request):
    return is_internal_user(request.user) and request.user.has_perm("wbcompliance.administrate_compliance")


def is_internal_employee_compliance(request):
    return is_internal_user(request.user) and not is_admin_compliance(request)
