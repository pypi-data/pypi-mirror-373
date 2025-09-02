from wbcompliance.permissions import (
    is_admin_compliance,
    is_internal_employee_compliance,
)

from .compliance_form import COMPLIANCEFORM_MENU, COMPLIANCEFORMSIGNATURE_MENUITEM
from .compliance_task import (
    COMPLIANCE_SETTINGS_MENU,
    COMPLIANCEEVENT_MENUITEM,
    COMPLIANCEREPORT_MENU,
)
from .compliance_type import COMPLIANCETYPE_MENUITEM
from .risk_management import (
    RISK_INCIDENT_MENUITEM,
    RISKINCIDENTTABLE_MENUITEM,
    RULE_MENUITEM,
)
