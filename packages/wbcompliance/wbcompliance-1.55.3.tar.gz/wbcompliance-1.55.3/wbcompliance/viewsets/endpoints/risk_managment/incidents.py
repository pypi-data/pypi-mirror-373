from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class RiskIncidentEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        if rule_id := self.view.kwargs.get("rule_id"):
            return reverse(
                "wbcompliance:riskrule-incident-list",
                args=[rule_id],
                request=self.request,
            )
        return super().get_endpoint(**kwargs)

    def get_create_endpoint(self, **kwargs):
        return None

    def get_delete_endpoint(self, **kwargs):
        return None


class CheckedObjectIncidentRelationshipEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class CheckedObjectIncidentRelationshipRiskRuleEndpointConfig(CheckedObjectIncidentRelationshipEndpointConfig):
    pass
