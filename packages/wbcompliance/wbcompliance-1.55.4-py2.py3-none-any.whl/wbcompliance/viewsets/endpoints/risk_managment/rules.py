from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class RuleThresholdRiskRuleEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        if rule_id := self.view.kwargs.get("rule_id"):
            return reverse(
                "wbcompliance:riskrule-threshold-list",
                args=[rule_id],
                request=self.request,
            )
        return super().get_endpoint(**kwargs)


class RuleCheckedObjectRelationshipRiskRuleEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        if rule_id := self.view.kwargs.get("rule_id"):
            return reverse(
                "wbcompliance:riskrule-relationship-list",
                args=[rule_id],
                request=self.request,
            )
        return super().get_endpoint(**kwargs)


class RiskRuleEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return super().get_endpoint(**kwargs)

    def get_delete_endpoint(self, **kwargs):
        return None
