from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.content_type.serializers import ContentTypeRepresentationSerializer
from wbcore.contrib.icons.serializers import IconSelectField

from wbcompliance.models.risk_management import RiskCheck
from wbcompliance.serializers.risk_management.rules import RiskRuleRepresentationSerializer


class RiskCheckRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = RiskCheck
        fields = ("id", "computed_str")


class RiskCheckModelSerializer(wb_serializers.ModelSerializer):
    _rule = RiskRuleRepresentationSerializer(source="rule")
    _checked_object_content_type = ContentTypeRepresentationSerializer(source="checked_object_content_type")

    incident_reports = wb_serializers.TextField()
    status_icon = IconSelectField(read_only=True)

    @wb_serializers.register_resource()
    def additional_resources(self, instance, request, user):
        res = {}
        if instance.incidents.exists():
            res["incidents"] = (
                f'{reverse("wbcompliance:checkedobjectincidentrelationship-list", args=[], request=request)}?rule_check={instance.id}'
            )

        return res

    class Meta:
        model = RiskCheck
        fields = (
            "id",
            "rule",
            "_rule",
            "incident_reports",
            "creation_datetime",
            "evaluation_date",
            "computed_str",
            "_checked_object_content_type",
            "checked_object_content_type",
            "checked_object_id",
            "status",
            "status_icon",
            "_additional_resources",
        )
        read_only_fields = fields
