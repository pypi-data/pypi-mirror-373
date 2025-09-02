from django.utils.translation import gettext_lazy
from wbcore import serializers as wb_serializers
from wbcore.contrib.authentication.serializers import GroupRepresentationSerializer
from wbcore.contrib.directory.serializers import PersonRepresentationSerializer

from wbcompliance.models import ComplianceType


class ComplianceTypeRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = ComplianceType
        fields = (
            "id",
            "name",
        )


class ComplianceTypeModelSerializer(wb_serializers.ModelSerializer):
    _in_charge = GroupRepresentationSerializer(source="in_charge", many=True)
    administrators = wb_serializers.PrimaryKeyRelatedField(
        label=gettext_lazy("Administrator"), many=True, read_only=True
    )
    _administrators = PersonRepresentationSerializer(many=True, source="administrators")

    class Meta:
        model = ComplianceType
        fields = ("id", "name", "description", "in_charge", "_in_charge", "administrators", "_administrators")
