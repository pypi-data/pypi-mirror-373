from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.authentication.serializers import GroupRepresentationSerializer
from wbcore.contrib.directory.models import Person
from wbcore.contrib.directory.serializers import PersonRepresentationSerializer
from wbcore.permissions.shortcuts import get_internal_groups

from wbcompliance.models import (
    ComplianceForm,
    ComplianceFormRule,
    ComplianceFormSection,
    ComplianceFormSignature,
    ComplianceFormSignatureRule,
    ComplianceFormSignatureSection,
    ComplianceFormType,
    ComplianceType,
)

from .compliance_type import ComplianceTypeRepresentationSerializer


class ComplianceFormTypeRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = ComplianceFormType
        fields = ("id", "name", "type")


class ComplianceFormTypeModelSerializer(wb_serializers.ModelSerializer):
    class Meta:
        model = ComplianceFormType
        fields = ("id", "name", "type")


# COMPLIANCE FORM
class ComplianceFormRepresentationSerializer(wb_serializers.RepresentationSerializer):
    # _detail = wb_serializers.HyperlinkField(reverse_name="wbcompliance:complianceform-detail")
    class Meta:
        model = ComplianceForm
        fields = (
            "id",
            "title",
            "form_type",
            "version",
            "status",
            "start",
            "end",
        )


class ComplianceFormModelSerializer(wb_serializers.ModelSerializer):
    creator = wb_serializers.PrimaryKeyRelatedField(
        default=wb_serializers.CurrentUserDefault("profile"),
        many=False,
        read_only=True,
    )
    start = wb_serializers.DateField(default=timezone.now().date(), label=_("Start"))
    _creator = PersonRepresentationSerializer(source="creator")
    _changer = PersonRepresentationSerializer(source="changer")
    current_signed = wb_serializers.CharField(
        label=_("Current Signed"),
        read_only=True,
        help_text=_("The number of signatures of the compliance form over the number of total to be signed"),
    )
    is_signed = wb_serializers.BooleanField(required=False, read_only=True)
    _assigned_to = GroupRepresentationSerializer(source="assigned_to", many=True)
    _form_type = ComplianceFormTypeRepresentationSerializer(source="form_type")
    compliance_type = wb_serializers.PrimaryKeyRelatedField(
        label=_("Administrator"), queryset=ComplianceType.objects.all()
    )
    _compliance_type = ComplianceTypeRepresentationSerializer(source="compliance_type")

    @cached_property
    def user_profile(self) -> Person | None:
        if request := self.context.get("request"):
            return request.user.profile
        return None

    class Meta:
        model = ComplianceForm
        fields = (
            "id",
            "creator",
            "_creator",
            "created",
            "changer",
            "_changer",
            "changed",
            "title",
            "policy",
            "status",
            "version",
            "_additional_resources",
            "assigned_to",
            "_assigned_to",
            "is_signed",
            "current_signed",
            "only_internal",
            "start",
            "end",
            "form_type",
            "_form_type",
            "compliance_type",
            "_compliance_type",
        )

        read_only_fields = ("creator", "created", "changer", "changed", "version")

    def create(self, validated_data):
        validated_data["creator"] = self.user_profile
        if len(validated_data["assigned_to"]) == 0:
            validated_data["assigned_to"] = get_internal_groups()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        profile = self.user_profile
        validated_data["changer"] = profile
        validated_data.pop("creator", None)
        validated_data.pop("created", None)
        persons = validated_data.pop("assigned_to", None)

        instance = super().update(instance, validated_data)

        # now update manytomany field assigned_to
        if persons is not None:
            instance.assigned_to.clear()
            for person in persons:
                instance.assigned_to.add(person)
            instance.save()

        return instance

    def validate(self, data):
        obj = self.instance
        start = data.get("start", obj.start if obj else None)
        end = data.get("end", obj.end if obj else None)
        title = data.get("title", obj.start if obj else None)
        errors = {}
        if not title:
            errors["title"] = ["This field is required."]
        if start and end:
            if start > end:
                errors["start"] = ["end date cannot be before start date"]
                errors["end"] = ["end date cannot be before start date"]

        if len(errors.keys()) > 0:
            raise serializers.ValidationError(errors)

        return data

    @wb_serializers.register_resource()
    def list_additional_resources(self, instance, request, user):
        return {
            "signatures": reverse(
                "wbcompliance:complianceform-signatures-list",
                args=[instance.id],
                request=request,
            ),
            "sections": reverse(
                "wbcompliance:complianceform-sections-list",
                args=[instance.id],
                request=request,
            ),
        }

    @wb_serializers.register_only_instance_resource()
    def instance_additional_resources(self, instance, request, user, view, **kwargs):
        additional_resources = dict()
        for section in ComplianceFormSection.objects.filter(compliance_form=instance.id).order_by("id"):
            additional_resources[f"rules{section.id}"] = reverse(
                "wbcompliance:complianceformsection-rules-list",
                args=[section.id],
                request=request,
            )

        if (
            view.user_has_compliance_admin_permission
            and instance.status == ComplianceForm.Status.ACTIVE
            and hasattr(instance, "is_signed")
        ):
            if not instance.is_signed:
                additional_resources["send_compliance_form_notification"] = reverse(
                    "wbcompliance:complianceform-sendcomplianceformnotification",
                    args=[instance.id],
                    request=request,
                )
        if view.user_has_compliance_admin_permission:
            additional_resources["regenerate_document"] = reverse(
                "wbcompliance:complianceform-regenerate-document", args=[instance.id], request=request
            )
        return additional_resources


# COMPLIANCE FORM SIGNATURE
class ComplianceFormSignatureModelSerializer(wb_serializers.ModelSerializer):
    compliance_form = wb_serializers.PrimaryKeyRelatedField(read_only=True)
    _compliance_form = ComplianceFormRepresentationSerializer(source="compliance_form")
    person = wb_serializers.PrimaryKeyRelatedField(read_only=True)
    _person = PersonRepresentationSerializer(source="person")
    is_signed = wb_serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = ComplianceFormSignature
        fields = (
            "id",
            "compliance_form",
            "_compliance_form",
            "version",
            "start",
            "end",
            "policy",
            "signed",
            "person",
            "_person",
            "remark",
            "is_signed",
            "_additional_resources",
        )

        read_only_fields = ("compliance_form", "version", "policy", "person", "signed", "start", "end")

    @wb_serializers.register_only_instance_resource()
    def additional_resources(self, instance, request, user, **kwargs):
        additional_resources = dict()
        if not instance.signed and instance.person == user.profile:
            additional_resources["signature"] = reverse(
                "wbcompliance:complianceformsignature-signature",
                args=[instance.id],
                request=request,
            )
        for section in ComplianceFormSignatureSection.objects.filter(compliance_form_signature=instance.id).order_by(
            "id"
        ):
            additional_resources[f"rules{section.id}"] = reverse(
                "wbcompliance:complianceformsignaturesection-rules-list",
                args=[section.id],
                request=request,
            )
        if user.has_perm("wbcompliance.administrate_compliance") or user.profile == instance.person:
            additional_resources["regenerate_document"] = reverse(
                "wbcompliance:complianceformsignature-regenerate-document", args=[instance.id], request=request
            )
        return additional_resources


# SECION OF THE COMPLIANCE FORM
class ComplianceFormSectionRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = ComplianceFormSection
        fields = ("id", "name")


class ComplianceFormSectionModelSerializer(wb_serializers.ModelSerializer):
    compliance_form = wb_serializers.PrimaryKeyRelatedField(
        queryset=ComplianceForm.objects.all(), read_only=lambda view: not view.new_mode
    )
    _compliance_form = ComplianceFormRepresentationSerializer(many=False, source="compliance_form")

    class Meta:
        model = ComplianceFormSection
        fields = ("id", "name", "compliance_form", "_compliance_form", "_additional_resources")

    @wb_serializers.register_resource()
    def additional_resources(self, instance, request, user):
        additional_resources = dict()
        additional_resources["rules"] = reverse(
            "wbcompliance:complianceformsection-rules-list",
            args=[instance.id],
            request=request,
        )
        return additional_resources


# RULES OF THE SECTION OF THE COMPLIANCE
class ComplianceFormRuleModelSerializer(wb_serializers.ModelSerializer):
    section = wb_serializers.PrimaryKeyRelatedField(
        queryset=ComplianceFormSection.objects.all(), read_only=lambda view: not view.new_mode
    )
    _section = ComplianceFormSectionRepresentationSerializer(many=False, source="section")
    text = wb_serializers.TextField(allow_null=False)

    class Meta:
        model = ComplianceFormRule
        fields = ("id", "text", "ticked", "section", "_section")


# REPRESENTATION SECTION OF THE COMPLIANCE FORM SIGNATURE
class ComplianceFormSignatureSectionRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = ComplianceFormSignatureSection
        fields = ("id", "name")


# RULES OF THE SECTION OF THE COMPLIANCE FORM SIGNATURE
class ComplianceFormSignatureRuleModelSerializer(wb_serializers.ModelSerializer):
    _section = ComplianceFormSignatureSectionRepresentationSerializer(many=False, source="section")
    comments = wb_serializers.TextAreaField(label=_("Comments"), allow_blank=True, allow_null=True)

    expected_result = wb_serializers.BooleanField(read_only=True)
    same_answer = wb_serializers.BooleanField(read_only=True)

    class Meta:
        model = ComplianceFormSignatureRule
        fields = ("id", "text", "ticked", "comments", "section", "_section", "expected_result", "same_answer")

        read_only_fields = ("section", "text")
