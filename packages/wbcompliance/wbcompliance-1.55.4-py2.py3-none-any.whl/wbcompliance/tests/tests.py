import pytest
from wbcore.test import GenerateTest, default_config

config = {}
for key, value in default_config.items():
    config[key] = list(
        filter(
            lambda x: x.__module__.startswith("wbcompliance")
            and x.__name__
            not in [
                "RuleCheckedObjectRelationshipRiskRuleModelViewSet",
                "RuleThresholdRiskRuleModelViewSet",
                "ComplianceFormSignatureSectionRuleViewSet",
                "ComplianceFormSignatureModelViewSet",
            ],
            value,
        )
    )


@pytest.mark.django_db
@GenerateTest(config)
class TestProject:
    pass
