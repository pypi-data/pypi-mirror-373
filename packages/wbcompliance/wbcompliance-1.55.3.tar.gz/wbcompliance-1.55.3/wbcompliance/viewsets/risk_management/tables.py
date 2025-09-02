import pandas as pd
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from wbcore.pandas import fields as pf
from wbcore.pandas.views import PandasAPIViewSet
from wbcore.utils.models import get_object

from wbcompliance.filters import RiskManagementIncidentFilter
from wbcompliance.models.risk_management import (
    CheckedObjectIncidentRelationship,
    RiskRule,
)

from ..display import RiskManagementIncidentTableDisplayConfig
from ..endpoints import RiskManagementIncidentTableEndpointConfig
from ..titles import RiskManagementIncidentTableTitleConfig


class RiskManagementIncidentTableView(PandasAPIViewSet):
    IDENTIFIER = "wbcompliance:riskmanagementincidentpandas"
    filterset_class = RiskManagementIncidentFilter
    queryset = CheckedObjectIncidentRelationship.objects.all()

    display_config_class = RiskManagementIncidentTableDisplayConfig
    title_config_class = RiskManagementIncidentTableTitleConfig
    endpoint_config_class = RiskManagementIncidentTableEndpointConfig

    @cached_property
    def checked_object_content_type(self):
        if checked_object_content_type_id := self.request.GET.get("checked_object_content_type", None):
            return ContentType.objects.get(id=checked_object_content_type_id)

    @cached_property
    def get_rule_map(self):
        rules = RiskRule.objects.filter(
            Q(is_enable=True)
            & (
                Q(rule_backend__allowed_checked_object_content_type__isnull=True)
                | Q(rule_backend__allowed_checked_object_content_type=self.checked_object_content_type)
            )
        )
        return list(map(lambda x: (f'rule_{x["id"]}', x["name"]), rules.order_by("name").values("id", "name")))

    def get_ordering_fields(self):
        return ["checked_object_repr", *[x[0] for x in self.get_rule_map]]

    def get_pandas_fields(self, request):
        fields = [
            pf.PKField(key="id", label=_("ID")),
            pf.CharField(key="checked_object_repr", label=_("ID")),
        ]
        for key, label in self.get_rule_map:
            fields.append(pf.IntegerField(key=key, label=label))
        return pf.PandasFields(fields=tuple(fields))

    def get_queryset(self):
        return CheckedObjectIncidentRelationship.objects.filter(incident__rule__is_enable=True)

    def get_dataframe(self, request, queryset, **kwargs):
        df = pd.DataFrame()
        if checked_object_content_type := self.checked_object_content_type:
            df = pd.DataFrame(
                queryset.values(
                    "rule_check__checked_object_id",
                    "incident__rule__id",
                    "severity__severity_order",
                ),
                columns=[
                    "rule_check__checked_object_id",
                    "incident__rule__id",
                    "severity__severity_order",
                ],
            )
            df = df.rename(
                columns={
                    "rule_check__checked_object_id": "id",
                    "incident__rule__id": "rule",
                    "severity__severity_order": "severity",
                }
            )

            if not df.empty:
                df = (
                    df.pivot_table(index="id", columns=["rule"], values="severity", aggfunc="max", fill_value=-1)
                    .rename_axis(None, axis=1)
                    .astype("int")
                )
                df = df.rename(columns=lambda x: f"rule_{x}")
                df = df.reset_index()
                df["checked_object_repr"] = df.id.apply(
                    lambda x: str(get_object(checked_object_content_type.model_class(), x))
                )
                df = df.where(pd.notnull(df), -1)
        return df
