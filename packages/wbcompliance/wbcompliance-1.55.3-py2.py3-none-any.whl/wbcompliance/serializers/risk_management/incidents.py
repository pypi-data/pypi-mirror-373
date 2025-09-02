from datetime import timedelta

from django.utils.translation import gettext as _
from psycopg.types.range import NumericRange
from rest_framework import serializers
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.content_type.serializers import ContentTypeRepresentationSerializer
from wbcore.contrib.authentication.serializers import GroupRepresentationSerializer
from wbcore.contrib.directory.serializers import PersonRepresentationSerializer

from wbcompliance.models.risk_management import (
    CheckedObjectIncidentRelationship,
    RiskIncident,
    RiskIncidentType,
    RuleThreshold,
)

from .checks import RiskCheckRepresentationSerializer
from .rules import RiskRuleRepresentationSerializer


class RiskIncidentTypeRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = RiskIncidentType
        fields = ("id", "name")


class RiskIncidentRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = RiskIncident
        fields = ("id", "computed_str")


class CheckedObjectIncidentRelationshipRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = CheckedObjectIncidentRelationship
        fields = ("id", "computed_str")


class RuleThresholdModelSerializer(wb_serializers.ModelSerializer):
    _rule = RiskRuleRepresentationSerializer(source="rule")
    _notifiable_users = PersonRepresentationSerializer(source="notifiable_users", many=True)
    _notifiable_groups = GroupRepresentationSerializer(source="notifiable_groups", many=True)
    _severity = RiskIncidentTypeRepresentationSerializer(source="severity")
    range_lower = wb_serializers.FloatField(source="range.lower", allow_null=True, required=False, precision=4)
    range_upper = wb_serializers.FloatField(source="range.upper", allow_null=True, required=False, precision=4)
    range = wb_serializers.DecimalRangeField(required=False)

    def validate(self, data):
        range_dict = data.pop("range", {})
        range_upper = range_dict.pop("upper", self.instance.range.upper if self.instance else None)
        range_lower = range_dict.pop("lower", self.instance.range.lower if self.instance else None)
        if range_upper and range_lower and range_upper < range_lower:
            raise serializers.ValidationError({"range": "Lower needs to be strictly lower than upper bound"})
        data["range"] = NumericRange(lower=range_lower, upper=range_upper)
        return data

    class Meta:
        model = RuleThreshold
        read_only_fields = ("computed_str",)
        fields = (
            "id",
            "rule",
            "_rule",
            "range_lower",
            "range_upper",
            "range",
            "severity",
            "notifiable_users",
            "_notifiable_users",
            "notifiable_groups",
            "_notifiable_groups",
            "computed_str",
            "upgradable_after_days",
            "_severity",
            "severity",
        )


class RiskIncidentModelSerializer(wb_serializers.ModelSerializer):
    # Extra fields to accommodate the multi level tree view with the CheckedIncidentRelationship class
    status_icon = wb_serializers.IconSelectField(read_only=True)
    _group_key = wb_serializers.CharField(read_only=True)
    checked_date = wb_serializers.DateField(read_only=True)
    object_repr = wb_serializers.CharField(read_only=True)
    threshold_repr = wb_serializers.CharField(read_only=True, required=False)
    breached_value = wb_serializers.TextField(read_only=True, default="Open to see details")
    report = wb_serializers.TextField(read_only=True, default="Open to see details")

    _resolved_by = PersonRepresentationSerializer(source="resolved_by")
    _breached_content_type = ContentTypeRepresentationSerializer(source="breached_content_type")
    _rule = RiskRuleRepresentationSerializer(source="rule")
    _severity = RiskIncidentTypeRepresentationSerializer(source="severity")
    date_range = wb_serializers.DateRangeField(outward_bounds_transform="[]")
    ignore_until = wb_serializers.DateField(
        read_only=True, label="Ignore Until (Included)", help_text=_("Ignore until this date (included)")
    )
    ignore_duration_in_days = wb_serializers.IntegerField(
        required=False,
        label=_("Ignore for X days"),
        help_text=_(
            "If set to a value different than 0, will ignore the forthcoming incidents for the specified number of days"
        ),
    )

    @wb_serializers.register_resource()
    def additional_resources(self, instance, request, user):
        res = {}
        if instance.checked_object_relationships.exists():
            res["relationships"] = reverse(
                "wbcompliance:riskincident-relationship-list",
                args=[instance.id],
                request=request,
            )
        return res

    def validate(self, data):
        if (ignore_duration_in_days := data.get("ignore_duration_in_days", None)) is not None:
            data["ignore_duration"] = timedelta(days=ignore_duration_in_days)
        return data

    class Meta:
        model = RiskIncident
        only_fsm_transition_on_instance = True

        fields = (
            "id",
            "status_icon",
            "date_range",
            "last_ignored_date",
            "ignore_until",
            "rule",
            "_rule",
            "breached_content_type",
            "_breached_content_type",
            "breached_object_id",
            "breached_object_repr",
            "ignore_duration",
            "ignore_duration_in_days",
            "status",
            "severity",
            "comment",
            "resolved_by",
            "_resolved_by",
            "_severity",
            "severity",
            "is_notified",
            "_additional_resources",
            "_group_key",
            "checked_date",
            "object_repr",
            "threshold_repr",
            "breached_value",
            "report",
        )
        read_only_fields = (
            "id",
            "date_range",
            "last_ignored_date",
            "ignore_until",
            "rule",
            "breached_content_type",
            "breached_object_id",
            "breached_object_repr",
            "status",
            "severity",
            "resolved_by",
            "_severity",
            "severity",
            "is_notified",
        )


class CheckedObjectIncidentRelationshipModelSerializer(wb_serializers.ModelSerializer):
    _resolved_by = PersonRepresentationSerializer(source="resolved_by")
    _incident = RiskIncidentRepresentationSerializer(source="incident")
    _rule_check = RiskCheckRepresentationSerializer(source="rule_check")
    _severity = RiskIncidentTypeRepresentationSerializer(source="severity")
    breached_value = wb_serializers.TextField()
    # extra annotation to play properly with the tree table
    checked_date = wb_serializers.DateField(read_only=True, required=False)
    # rule = wb_serializers.PrimaryKeyRelatedField()
    # _rule = RiskRuleRepresentationSerializer(source="rule")
    object_repr = wb_serializers.CharField(read_only=True, required=False)
    date_range = wb_serializers.DateRangeField(read_only=True, outward_bounds_transform="[]", required=False)
    threshold_repr = wb_serializers.CharField(read_only=True, required=False)

    class Meta:
        model = CheckedObjectIncidentRelationship
        read_only_fields = (
            "computed_str",
            "incident",
            "status",
            "severity",
            "rule_check",
            "report",
            "_severity",
            "resolved_by",
            "checked_date",
            "rule",
            "_rule",
            "object_repr",
            "date_range",
            "breached_value",
        )
        fields = (
            "id",
            "computed_str",
            "rule_check",
            "_rule_check",
            "incident",
            "_incident",
            "report",
            "status",
            "comment",
            "resolved_by",
            "_resolved_by",
            "_severity",
            "severity",
            "_additional_resources",
            "checked_date",
            # "rule",
            # "_rule",
            "object_repr",
            "date_range",
            "threshold_repr",
            "breached_value",
        )
