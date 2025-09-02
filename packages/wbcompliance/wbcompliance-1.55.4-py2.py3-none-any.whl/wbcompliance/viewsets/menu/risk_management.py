from contextlib import suppress

from django.utils.translation import gettext as _
from wbcore.menus import ItemPermission, Menu, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

from wbcompliance.models.risk_management.rules import RuleGroup

RULE_MENUITEM = MenuItem(
    label=_("Rules"),
    endpoint="wbcompliance:riskrule-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbcompliance.view_riskrule"]
    ),
    add=MenuItem(
        label=_("Add Rule"),
        endpoint="wbcompliance:riskrule-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbcompliance.add_riskrule"]
        ),
    ),
)


def _get_incident_menu():
    items = []
    with suppress(Exception):
        for rule_group in RuleGroup.objects.all():
            items.append(
                MenuItem(
                    label=rule_group.name,
                    endpoint="wbcompliance:riskincident-list",
                    permission=ItemPermission(
                        method=lambda request: is_internal_user(request.user),
                        permissions=["wbcompliance.view_riskincident"],
                    ),
                    endpoint_get_parameters={"rule_group": rule_group.id},
                )
            )
    if items:
        return Menu(label=_("Incidents"), items=items)
    return MenuItem(
        label=_("Incidents"),
        endpoint="wbcompliance:riskincident-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbcompliance.view_riskincident"]
        ),
    )


RISK_INCIDENT_MENUITEM = _get_incident_menu()

RISKINCIDENTTABLE_MENUITEM = MenuItem(
    label=_("Incident Table"),
    endpoint="wbcompliance:riskmanagementincidenttable-list",
    permission=ItemPermission(permissions=["wbcompliance.administrate_riskrule"]),
)
