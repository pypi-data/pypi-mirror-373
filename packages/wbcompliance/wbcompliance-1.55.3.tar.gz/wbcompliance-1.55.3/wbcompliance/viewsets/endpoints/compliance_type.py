from wbcore.metadata.configs.endpoints import EndpointViewConfig

from wbcompliance.models import ComplianceType


class ComplianceTypeEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        if ComplianceType.is_administrator(self.request.user):
            return super().get_endpoint()
        return None
