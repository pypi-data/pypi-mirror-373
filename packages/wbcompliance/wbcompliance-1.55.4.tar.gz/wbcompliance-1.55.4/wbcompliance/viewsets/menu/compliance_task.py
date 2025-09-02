from django.utils.translation import gettext as _
from wbcore.menus import ItemPermission, Menu, MenuItem

from wbcompliance.permissions import (
    is_admin_compliance,
    is_internal_employee_compliance,
)

from .compliance_type import COMPLIANCETYPE_MENUITEM

COMPLIANCETASKGROUP_MENUITEM = MenuItem(
    label=_("Groups Indicator"),
    endpoint="wbcompliance:compliancetaskgroup-list",
    permission=ItemPermission(
        method=is_admin_compliance,
        permissions=["wbcompliance.view_compliancetaskgroup", "wbcompliance.administrate_compliance"],
    ),
    add=MenuItem(
        label=_("Add Group Indicator"),
        endpoint="wbcompliance:compliancetaskgroup-list",
        permission=ItemPermission(method=is_admin_compliance, permissions=["wbcompliance.administrate_compliance"]),
    ),
)

COMPLIANCETASK_MENUITEM = MenuItem(
    label=_("Indicators"),
    endpoint="wbcompliance:compliancetask-list",
    permission=ItemPermission(
        method=is_admin_compliance,
        permissions=["wbcompliance.view_compliancetask", "wbcompliance.administrate_compliance"],
    ),
    add=MenuItem(
        label=_("Add Indicator"),
        endpoint="wbcompliance:compliancetask-list",
        permission=ItemPermission(method=is_admin_compliance, permissions=["wbcompliance.administrate_compliance"]),
    ),
)

COMPLIANCETASKINSTANCE_MENUITEM = MenuItem(
    label=_("Instances Indicator"),
    endpoint="wbcompliance:compliancetaskinstance-list",
    permission=ItemPermission(
        method=lambda request: request.user.is_superuser,
        permissions=["wbcompliance.view_compliancetaskinstance", "wbcompliance.administrate_compliance"],
    ),
)

COMPLIANCETASKMATRIX_MENUITEM = MenuItem(
    label=_("Indicator Matrix"),
    endpoint="wbcompliance:compliancetaskmatrix-list",
    permission=ItemPermission(
        method=is_admin_compliance,
        permissions=[
            "wbcompliance.view_compliancetaskinstance",
            "wbcompliance.view_compliancetask",
            "wbcompliance.administrate_compliance",
        ],
    ),
)

COMPLIANCEACTION_MENUITEM = MenuItem(
    label=_("Actions"),
    endpoint="wbcompliance:complianceaction-list",
    permission=ItemPermission(
        method=is_admin_compliance,
        permissions=["wbcompliance.view_complianceaction", "wbcompliance.administrate_compliance"],
    ),
    add=MenuItem(
        label=_("Add Compliance Action"),
        endpoint="wbcompliance:complianceaction-list",
        permission=ItemPermission(method=is_admin_compliance, permissions=["wbcompliance.administrate_compliance"]),
    ),
)

COMPLIANCEEVENT_MENUITEM = MenuItem(
    label=_("Events"),
    endpoint="wbcompliance:complianceevent-list",
    permission=ItemPermission(
        method=is_internal_employee_compliance, permissions=["wbcompliance.view_complianceevent"]
    ),
    add=MenuItem(
        label=_("Add Compliance Event"),
        endpoint="wbcompliance:complianceevent-list",
        permission=ItemPermission(
            method=is_internal_employee_compliance, permissions=["wbcompliance.add_complianceevent"]
        ),
    ),
)

ADMIN_COMPLIANCEEVENT_MENUITEM = MenuItem(
    label=_("Events"),
    endpoint="wbcompliance:complianceevent-list",
    permission=ItemPermission(method=is_admin_compliance, permissions=["wbcompliance.view_complianceevent"]),
    add=MenuItem(
        label=_("Add Compliance Event"),
        endpoint="wbcompliance:complianceevent-list",
        permission=ItemPermission(method=is_admin_compliance, permissions=["wbcompliance.add_complianceevent"]),
    ),
)

REVIEWCOMPLIANCETASK_MENUITEM = MenuItem(
    label=_("Reports"),
    endpoint="wbcompliance:reviewcompliancetask-list",
    permission=ItemPermission(method=is_admin_compliance, permissions=["wbcompliance.view_reviewcompliancetask"]),
    add=MenuItem(
        label=_("Add Report Indicator"),
        endpoint="wbcompliance:reviewcompliancetask-list",
        permission=ItemPermission(method=is_admin_compliance, permissions=["wbcompliance.add_reviewcompliancetask"]),
    ),
)


COMPLIANCEREPORT_MENU = Menu(
    label=_("Reports"),
    items=[
        REVIEWCOMPLIANCETASK_MENUITEM,
        COMPLIANCEACTION_MENUITEM,
        ADMIN_COMPLIANCEEVENT_MENUITEM,
        COMPLIANCETASKMATRIX_MENUITEM,
    ],
)

COMPLIANCE_SETTINGS_MENU = Menu(
    label=_("Settings"),
    items=[
        COMPLIANCETYPE_MENUITEM,
        COMPLIANCETASKGROUP_MENUITEM,
        COMPLIANCETASK_MENUITEM,
        COMPLIANCETASKINSTANCE_MENUITEM,
    ],
)
