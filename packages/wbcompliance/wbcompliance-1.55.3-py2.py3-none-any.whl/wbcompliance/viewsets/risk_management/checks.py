from django.contrib.auth import get_user_model
from django.contrib.postgres.aggregates import StringAgg
from django.db import models
from django.db.models import F
from wbcore import viewsets

from wbcompliance.filters.risk_management.checks import RiskCheckFilterSet
from wbcompliance.models.risk_management import RiskCheck
from wbcompliance.serializers import (
    RiskCheckModelSerializer,
    RiskCheckRepresentationSerializer,
)
from wbcompliance.viewsets.buttons import RiskCheckButtonConfig
from wbcompliance.viewsets.display import RiskCheckDisplayConfig
from wbcompliance.viewsets.endpoints import RiskCheckEndpointConfig

User = get_user_model()


class RiskCheckRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = RiskCheck.objects.all()
    serializer_class = RiskCheckRepresentationSerializer


class RiskCheckModelViewSet(viewsets.ModelViewSet):
    button_config_class = RiskCheckButtonConfig
    display_config_class = RiskCheckDisplayConfig
    endpoint_config_class = RiskCheckEndpointConfig
    queryset = RiskCheck.all_objects.all()
    serializer_class = RiskCheckModelSerializer
    ordering_fields = [
        "evaluation_date",
        "creation_datetime",
    ]
    filterset_class = RiskCheckFilterSet

    def get_queryset(self):
        return (
            RiskCheck.all_objects.annotate(
                status_icon=models.Case(
                    *[
                        models.When(status=value, then=models.Value(RiskCheck.CheckStatus[value].icon))
                        for value in RiskCheck.CheckStatus.values
                    ],
                    default=models.Value("none"),
                ),
                incident_reports=StringAgg(F("incidents__report"), delimiter="<br>"),
            )
            .select_related(
                "rule",
                "checked_object_content_type",
            )
            .prefetch_related("incidents")
        )
