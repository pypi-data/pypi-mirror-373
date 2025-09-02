from django.apps import apps
from django.db.models.signals import pre_migrate
from pytest_factoryboy import register
from wbcompliance.factories import (
    ComplianceActionFactory,
    ComplianceEventFactory,
    ComplianceFormFactory,
    ComplianceFormRuleFactory,
    ComplianceFormSectionFactory,
    ComplianceFormSignatureFactory,
    ComplianceFormTypeFactory,
    ComplianceTaskFactory,
    ComplianceTaskGroupFactory,
    ComplianceTaskInstanceFactory,
    ComplianceTypeFactory,
    UnsignedComplianceFormSignatureFactory,
)
from wbcompliance.factories.risk_management import (
    CheckedObjectIncidentRelationshipFactory,
    RiskCheckFactory,
    RiskIncidentFactory,
    RiskIncidentTypeFactory,
    RiskRuleFactory,
    RuleBackendFactory,
    RuleCheckedObjectRelationshipFactory,
    RuleThresholdFactory,
)
from wbcore.contrib.authentication.factories import (
    AuthenticatedPersonFactory,
    UserFactory,
)
from wbcore.contrib.directory.factories import PersonFactory

from wbcore.tests.conftest import *  # isort:skip

register(ComplianceFormRuleFactory)
register(ComplianceFormSectionFactory)
register(ComplianceFormTypeFactory)
register(ComplianceFormFactory)
register(ComplianceFormSignatureFactory)
register(UnsignedComplianceFormSignatureFactory)
register(ComplianceTaskFactory)
register(ComplianceTaskInstanceFactory)
register(ComplianceActionFactory)
register(ComplianceEventFactory)
register(ComplianceTypeFactory)
register(ComplianceTaskGroupFactory)
register(RiskCheckFactory)
register(RiskIncidentFactory)
register(CheckedObjectIncidentRelationshipFactory)
register(RuleBackendFactory)
register(RiskRuleFactory)
register(RuleThresholdFactory)
register(RuleCheckedObjectRelationshipFactory)
register(RiskIncidentTypeFactory)
register(PersonFactory)
register(UserFactory)
register(AuthenticatedPersonFactory)


from .signals import *

pre_migrate.connect(app_pre_migration, sender=apps.get_app_config("wbcompliance"))
