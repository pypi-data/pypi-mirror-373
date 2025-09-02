from reversion.views import RevisionMixin
from wbcore import viewsets

from wbcompliance.filters import ComplianceTypeFilter
from wbcompliance.models import ComplianceType
from wbcompliance.serializers import (
    ComplianceTypeModelSerializer,
    ComplianceTypeRepresentationSerializer,
)

from .display import ComplianceTypeDisplayConfig
from .endpoints import ComplianceTypeEndpointConfig
from .titles import ComplianceTypeTitleConfig


class ComplianceTypeRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbcompliance:compliancetyperepresentation"
    search_fields = ["name"]
    ordering_fields = ["name"]

    queryset = ComplianceType.objects.all()
    serializer_class = ComplianceTypeRepresentationSerializer


class ComplianceTypeModelViewSet(RevisionMixin, viewsets.ModelViewSet):
    IDENTIFIER = "wbcompliance:compliancetype"
    display_config_class = ComplianceTypeDisplayConfig
    endpoint_config_class = ComplianceTypeEndpointConfig
    title_config_class = ComplianceTypeTitleConfig

    search_fields = ["name"]
    ordering_fields = ["name", "in_charge"]
    ordering = ["name"]

    filterset_class = ComplianceTypeFilter

    serializer_class = ComplianceTypeModelSerializer

    queryset = ComplianceType.objects.prefetch_related("in_charge")
