from django.utils.translation import gettext as _
from wbcore.menus import ItemPermission, Menu, MenuItem

from wbcompliance.permissions import is_admin_compliance

COMPLIANCEFORM_MENUITEM = MenuItem(
    label=_("Forms"),
    endpoint="wbcompliance:complianceform-list",
    permission=ItemPermission(
        method=is_admin_compliance,
        permissions=["wbcompliance.view_complianceform", "wbcompliance.administrate_compliance"],
    ),
    add=MenuItem(
        label=_("Add Form"),
        endpoint="wbcompliance:complianceform-list",
        permission=ItemPermission(method=is_admin_compliance, permissions=["wbcompliance.administrate_compliance"]),
    ),
)


COMPLIANCEFORMSIGNATURE_MENUITEM = MenuItem(
    label=_("Form Signatures"),
    endpoint="wbcompliance:complianceformsignature-list",
    permission=ItemPermission(permissions=["wbcompliance.view_complianceformsignature"]),
)

ADMIN_COMPLIANCEFORMSIGNATURE_MENUITEM = MenuItem(
    label=_("Form Signatures"),
    endpoint="wbcompliance:complianceformsignature-list",
    permission=ItemPermission(method=is_admin_compliance, permissions=["wbcompliance.view_complianceformsignature"]),
)

COMPLIANCEFORMTYPE_MENUITEM = MenuItem(
    label=_("Form Types"),
    endpoint="wbcompliance:complianceformtype-list",
    permission=ItemPermission(
        method=is_admin_compliance,
        permissions=["wbcompliance.view_complianceformtype", "wbcompliance.administrate_compliance"],
    ),
    add=MenuItem(
        label=_("Add Form Type"),
        endpoint="wbcompliance:complianceformtype-list",
        permission=ItemPermission(method=is_admin_compliance, permissions=["wbcompliance.administrate_compliance"]),
    ),
)

COMPLIANCEFORM_MENU = Menu(
    label=_("Forms"),
    items=[COMPLIANCEFORM_MENUITEM, ADMIN_COMPLIANCEFORMSIGNATURE_MENUITEM, COMPLIANCEFORMTYPE_MENUITEM],
)
