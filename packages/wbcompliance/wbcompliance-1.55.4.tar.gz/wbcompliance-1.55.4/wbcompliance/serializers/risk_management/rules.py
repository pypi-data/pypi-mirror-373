from django.contrib.contenttypes.models import ContentType
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.content_type.serializers import (
    ContentTypeRepresentationSerializer,
    DynamicObjectIDRepresentationSerializer,
)
from wbcore.contrib.authentication.serializers import UserRepresentationSerializer

from wbcompliance.models.risk_management import (
    RiskRule,
    RuleBackend,
    RuleCheckedObjectRelationship,
    RuleThreshold,
)
from wbcompliance.models.risk_management.rules import RuleGroup


class RuleGroupRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = RuleGroup
        fields = ("id", "name")


class RuleCheckedObjectRelationshipRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = RuleCheckedObjectRelationship
        fields = ("id", "computed_str", "checked_object_repr")


class RuleBackendRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = RuleBackend
        fields = ("id", "name")


class RuleThresholdRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = RuleThreshold
        fields = ("id", "computed_str")


class RiskRuleRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = RiskRule
        fields = ("id", "name")


class GetContentTypeFromKwargs:
    requires_context = True

    def __call__(self, serializer_instance):
        if (view := serializer_instance.view) and (rule_id := view.kwargs.get("rule_id", None)):
            rule = RiskRule.objects.get(id=rule_id)
            if content_type := rule.rule_backend.allowed_checked_object_content_type:
                return content_type.id
        return None


class RuleCheckedObjectRelationshipModelSerializer(wb_serializers.ModelSerializer):
    checked_object_content_type = wb_serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(), default=GetContentTypeFromKwargs()
    )
    _checked_object_content_type = ContentTypeRepresentationSerializer(source="checked_object_content_type")
    _checked_object_id = DynamicObjectIDRepresentationSerializer(
        content_type_field_name="checked_object_content_type",
        source="checked_object_id",
        optional_get_parameters={"checked_object_content_type": "content_type"},
        depends_on=[{"field": "checked_object_content_type", "options": {}}],
    )

    class Meta:
        model = RuleCheckedObjectRelationship
        # dependency_map = {
        #     "checked_object_content_type": ["checked_object_id"],
        # }
        read_only_fields = ("computed_str", "checked_object_repr")
        fields = (
            "id",
            "rule",
            "checked_object_content_type",
            "_checked_object_content_type",
            "checked_object_id",
            "_checked_object_id",
            "checked_object_repr",
            "computed_str",
        )


class RuleBackendModelSerializer(wb_serializers.ModelSerializer):
    class Meta:
        model = RuleBackend
        fields = ("id", "name", "backend_class_path", "backend_class_name", "allowed_checked_object_content_type")
        read_only_fields = fields


class RiskRuleModelSerializer(wb_serializers.ModelSerializer):
    parameters__group_by = wb_serializers.CharField(read_only=True)
    _rule_backend = RuleBackendRepresentationSerializer(source="rule_backend")
    _creator = UserRepresentationSerializer(source="creator")
    parameters = wb_serializers.JSONTableField()
    open_incidents_count = wb_serializers.IntegerField(default=0, read_only=True)
    in_breach = wb_serializers.ChoiceField(
        default=False,
        read_only=True,
        choices=[("BREACH", "In Breach"), ("PASSED", "Passed"), ("INACTIVE", "Inactive")],
    )

    def validate(self, data):
        if (not self.instance or not self.instance.creator) and (request := self.context.get("request")):
            data["creator"] = request.user
        return super().validate(data)

    @wb_serializers.register_resource()
    def additional_resources(self, instance, request, user):
        return {
            "relationships": reverse(
                "wbcompliance:riskrule-relationship-list",
                args=[instance.id],
                request=request,
            ),
            "thresholds": reverse(
                "wbcompliance:riskrule-threshold-list",
                args=[instance.id],
                request=request,
            ),
            "incidents": reverse(
                "wbcompliance:riskrule-incident-list",
                args=[instance.id],
                request=request,
            ),
        }

    class Meta:
        model = RiskRule
        read_only_fields = ("creator",)
        fields = (
            "id",
            "parameters__group_by",
            "permission_type",
            "creator",
            "_creator",
            "name",
            "description",
            "rule_backend",
            "_rule_backend",
            "is_enable",
            "only_passive_check_allowed",
            "automatically_close_incident",
            "is_silent",
            "is_mandatory",
            "apply_to_all_active_relationships",
            "parameters",
            "open_incidents_count",
            "in_breach",
            "frequency",
            "activation_date",
            "_additional_resources",
        )
