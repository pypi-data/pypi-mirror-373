from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import (
    BooleanField,
    Case,
    CharField,
    ExpressionWrapper,
    F,
    Q,
    Value,
    When,
)
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from rest_framework import filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from reversion.views import RevisionMixin
from wbcore import viewsets
from wbcore.contrib.authentication.authentication import JWTCookieAuthentication
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.filters import DjangoFilterBackend

from wbcompliance.filters import ComplianceFormFilter, ComplianceFormSignatureFilter
from wbcompliance.models import (
    ComplianceForm,
    ComplianceFormRule,
    ComplianceFormSection,
    ComplianceFormSignature,
    ComplianceFormSignatureRule,
    ComplianceFormSignatureSection,
    ComplianceFormType,
    update_or_create_compliance_document,
)
from wbcompliance.serializers import (
    ComplianceFormModelSerializer,
    ComplianceFormRepresentationSerializer,
    ComplianceFormRuleModelSerializer,
    ComplianceFormSectionModelSerializer,
    ComplianceFormSectionRepresentationSerializer,
    ComplianceFormSignatureModelSerializer,
    ComplianceFormSignatureRuleModelSerializer,
    ComplianceFormSignatureSectionRepresentationSerializer,
    ComplianceFormTypeModelSerializer,
    ComplianceFormTypeRepresentationSerializer,
)

from .buttons import ComplianceFormButtonConfig, ComplianceFormSignatureButtonConfig
from .compliance_type import ComplianceType
from .display import (
    ComplianceFormDisplayConfig,
    ComplianceFormRuleDisplayConfig,
    ComplianceFormSectionDisplayConfig,
    ComplianceFormSignatureDisplayConfig,
    ComplianceFormSignatureSectionRuleDisplayConfig,
    ComplianceFormTypeDisplayConfig,
)
from .endpoints import (
    CFComplianceFormSectionEndpointConfig,
    CFComplianceFormSignatureEndpointConfig,
    ComplianceFormEndpointConfig,
    ComplianceFormRuleEndpointConfig,
    ComplianceFormSectionRuleEndpointConfig,
    ComplianceFormSignatureEndpointConfig,
    ComplianceFormSignatureSectionRuleEndpointConfig,
    ComplianceFormTypeEndpointConfig,
)
from .titles import (
    ComplianceFormSectionRuleTitleConfig,
    ComplianceFormSectionTitleConfig,
    ComplianceFormSignatureSectionRuleTitleConfig,
    ComplianceFormSignatureTitleConfig,
    ComplianceFormTitleConfig,
)

User = get_user_model()


class ComplianceFormRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbcompliance:complianceformrepresentation"

    queryset = ComplianceForm.objects.all()
    serializer_class = ComplianceFormRepresentationSerializer


class ComplianceFormSectionRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbcompliance:complianceformsectionrepresentation"

    queryset = ComplianceFormSection.objects.all()
    serializer_class = ComplianceFormSectionRepresentationSerializer


class ComplianceFormSignatureSectionRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbcompliance:complianceformsignaturesectionrepresentation"

    queryset = ComplianceFormSignatureSection.objects.all()
    serializer_class = ComplianceFormSignatureSectionRepresentationSerializer


# TYPE OF THE COMPLIANCE FORM
class ComplianceFormTypeRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbcompliance:complianceformtyperepresentation"
    queryset = ComplianceFormType.objects.all()
    serializer_class = ComplianceFormTypeRepresentationSerializer


class ComplianceFormTypeViewSet(RevisionMixin, viewsets.ModelViewSet):
    endpoint_config_class = ComplianceFormTypeEndpointConfig
    display_config_class = ComplianceFormTypeDisplayConfig

    ordering_fields = ["name"]

    serializer_class = ComplianceFormTypeModelSerializer
    queryset = ComplianceFormType.objects.all()

    def get_queryset(self):
        if ComplianceType.is_administrator(self.request.user):
            return super().get_queryset()
        return ComplianceFormType.objects.none()


# SECTION OF THE COMPLIANCE FORM
class ComplianceFormSectionViewSet(RevisionMixin, viewsets.ModelViewSet):
    title_config_class = ComplianceFormSectionTitleConfig
    display_config_class = ComplianceFormSectionDisplayConfig

    search_fields = ["name"]
    ordering_fields = ["name"]
    queryset = ComplianceFormSection.objects.all()
    serializer_class = ComplianceFormSectionModelSerializer

    def get_queryset(self):
        if ComplianceType.is_administrator(self.request.user):
            return ComplianceFormSection.objects.select_related("compliance_form")
        return ComplianceFormSection.objects.none()


class ComplianceFormSectionComplianceFormViewSet(ComplianceFormSectionViewSet):
    endpoint_config_class = CFComplianceFormSectionEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(compliance_form__id=self.kwargs["compliance_form_id"])


# RULES
class ComplianceFormRuleViewSet(RevisionMixin, viewsets.ModelViewSet):
    IDENTIFIER = "wbcompliance:complianceformrule"
    display_config_class = ComplianceFormRuleDisplayConfig
    endpoint_config_class = ComplianceFormRuleEndpointConfig

    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )

    serializer_class = ComplianceFormRuleModelSerializer

    queryset = ComplianceFormRule.objects.select_related("section")


# RULES OF THE SECTION OF THE COMPLIANCE FORM
class ComplianceFormSectionRuleViewSet(ComplianceFormRuleViewSet):
    IDENTIFIER = "wbcompliance:complianceformsection-rules"
    title_config_class = ComplianceFormSectionRuleTitleConfig
    endpoint_config_class = ComplianceFormSectionRuleEndpointConfig

    def get_queryset(self):
        if ComplianceType.is_administrator(self.request.user):
            return super().get_queryset().filter(section__id=self.kwargs["section_id"])
        return ComplianceFormRule.objects.none()


# RULES OF THE SECTION OF THE COMPLIANCE FORM SIGNATURE
class ComplianceFormSignatureSectionRuleViewSet(RevisionMixin, viewsets.ModelViewSet):
    IDENTIFIER = "wbcompliance:complianceformsignaturesection-signaturerules"
    title_config_class = ComplianceFormSignatureSectionRuleTitleConfig
    display_config_class = ComplianceFormSignatureSectionRuleDisplayConfig
    endpoint_config_class = ComplianceFormSignatureSectionRuleEndpointConfig

    serializer_class = ComplianceFormSignatureRuleModelSerializer

    queryset = ComplianceFormSignatureRule.objects.all()

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(section__id=self.kwargs["section_id"])
            .annotate(
                expected_result=ComplianceFormSignatureRule.get_subquery_expected_ticked(),
                same_answer=ExpressionWrapper(
                    Q(ticked__exact=F("expected_result")),
                    output_field=BooleanField(),
                ),
            )
        )


# COMPLIANCE FORM
class ComplianceFormModelViewSet(RevisionMixin, viewsets.ModelViewSet):
    IDENTIFIER = "wbcompliance:complianceform"

    ordering_fields = [
        "title",
        "status",
        "creator",
        "changer",
        "changed",
        "start",
        "end",
        "version",
        "form_type",
        "compliance_type",
    ]
    ordering = ["-changed", "-created"]
    search_fields = ["title"]

    filterset_class = ComplianceFormFilter

    display_config_class = ComplianceFormDisplayConfig
    title_config_class = ComplianceFormTitleConfig
    button_config_class = ComplianceFormButtonConfig
    endpoint_config_class = ComplianceFormEndpointConfig

    serializer_class = ComplianceFormModelSerializer
    queryset = ComplianceForm.objects.select_related(
        "creator",
        "changer",
        "form_type",
        "compliance_type",
    ).prefetch_related("assigned_to")

    @cached_property
    def user_has_compliance_admin_permission(self):
        return self.request.user.has_perm("wbcompliance.administrate_compliance")

    def get_queryset(self):
        if ComplianceType.is_administrator(self.request.user):
            qs = super().get_queryset()
            qs = qs.annotate(
                # is_signed = ComplianceForm.get_subquery_compliance_form_signature(self.request.user.profile),
                total_compliance_form_signature=ComplianceForm.get_subquery_total_compliance_form_signature(),
                total_signed=F("total_compliance_form_signature")
                - ComplianceForm.get_subquery_total_compliance_form_signature(remaining_signed=True),
                current_signed=ExpressionWrapper(
                    Concat(
                        Value(" ("), F("total_signed"), Value("/"), F("total_compliance_form_signature"), Value(")")
                    ),
                    output_field=CharField(),
                ),
                is_signed=Case(
                    When(total_compliance_form_signature=F("total_signed"), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ),
            )
        else:
            qs = super().get_queryset().filter(status=ComplianceForm.Status.ACTIVE)
            qs = qs.annotate(
                is_signed=ComplianceForm.get_subquery_compliance_form_signature(self.request.user.profile),
            ).filter(is_signed__isnull=False)
        return qs

    @action(detail=True, methods=["PATCH"], permission_classes=[permissions.IsAuthenticated])
    def sendcomplianceformnotification(self, request, pk=None):
        compliance_form = ComplianceForm.objects.get(pk=pk)
        person_ids = ComplianceFormSignature.objects.filter(
            compliance_form=compliance_form, version=compliance_form.version, signed=None
        ).values_list("person", flat=True)

        if person_ids:
            msg = _("<p>{} has activated a {} {} version {} </p>").format(
                str(compliance_form.changer), compliance_form.title, compliance_form.form_type, compliance_form.version
            )
            if compliance_form.policy and compliance_form.policy != "<p></p>" and compliance_form.policy != "null":
                msg += _("</br><p><b>User's ComplianceForm:</b></p><i>{}</i>").format(compliance_form.policy)
            title = _("Unsigned Compliance Form - {} Reminder : {} ").format(
                compliance_form.form_type, compliance_form.title
            )
            compliance_form.notify(title, msg, recipients=User.objects.filter(profile__id__in=person_ids))

            return Response(
                {
                    "__notification": {
                        "compliance_form": compliance_form.id,
                        "status": "Compliance Form notification sent",
                        "person_signed": person_ids,
                    }
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "__notification": {
                    "compliance_form": compliance_form.id,
                    "status": "Compliance Form notification not sent",
                    "person_signed": None,
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=["PATCH"], authentication_classes=[JWTCookieAuthentication])
    def regenerate_document(self, request, pk):
        if not request.user.has_perm("wbcompliance.administrate_compliance"):
            return Response(status=status.HTTP_403_FORBIDDEN)
        content_type = ContentType.objects.get_for_model(ComplianceForm)
        send_email = request.POST.get("send_email", "false") == "true"
        update_or_create_compliance_document.delay(request.user.id, content_type.id, pk, send_email=send_email)

        return Response(
            {"__notification": {"title": "PDF is going to be created and sent to you."}},
            status=status.HTTP_200_OK,
        )


# COMPLIANCE FORM SIGNATURE
class ComplianceFormSignatureModelViewSet(RevisionMixin, viewsets.ModelViewSet):
    IDENTIFIER = "wbcompliance:complianceformsignature"
    display_config_class = ComplianceFormSignatureDisplayConfig
    title_config_class = ComplianceFormSignatureTitleConfig
    button_config_class = ComplianceFormSignatureButtonConfig
    endpoint_config_class = ComplianceFormSignatureEndpointConfig

    search_fields = ["compliance_form__title"]

    ordering_fields = ["version", "signed", "start", "end", "person"]
    ordering = ["-version", "-signed"]

    filterset_class = ComplianceFormSignatureFilter

    serializer_class = ComplianceFormSignatureModelSerializer
    queryset = ComplianceFormSignature.objects.select_related("compliance_form", "person")

    def get_queryset(self):
        if ComplianceType.is_administrator(self.request.user):
            qs = super().get_queryset()
        else:
            qs = super().get_queryset().filter(person=self.request.user.profile)
        return qs.annotate(
            is_signed=Case(
                When(signed=None, then=Value(False)),
                default=Value(True),
                output_field=BooleanField(),
            )
        )

    @action(detail=True, methods=["PATCH"], permission_classes=[permissions.IsAuthenticated])
    def signature(self, request, pk=None):
        compliance_form_signature = get_object_or_404(ComplianceFormSignature, pk=pk)
        if request.user.profile != compliance_form_signature.person:
            return Response(status=status.HTTP_403_FORBIDDEN)
        compliance_form_signature.signed = timezone.now()
        compliance_form_signature.remark = request.POST.get("remark")
        compliance_form_signature.save()

        ComplianceFormSignature.objects.filter(
            Q(compliance_form=compliance_form_signature.compliance_form)
            & Q(version__lt=compliance_form_signature.version)
            & Q(signed__isnull=True)
            & Q(person=request.user.profile)
        ).update(signed=timezone.now())

        if hasattr(compliance_form_signature.person, "user_account"):
            msg = _("<p><b>{}</b> {} version <b>{} </b> has been signed</p>").format(
                compliance_form_signature.compliance_form.title,
                compliance_form_signature.compliance_form.form_type,
                compliance_form_signature.version,
            )
            if (
                compliance_form_signature.policy
                and compliance_form_signature.policy != "<p></p>"
                and compliance_form_signature.policy != "null"
            ):
                msg += _("</br><p><b>{}:</b></p> <i>{}</i>").format(
                    compliance_form_signature.compliance_form.form_type, compliance_form_signature.policy
                )
            send_notification(
                code="wbcompliance.complianceformsignature.signed",
                title=_("Confirmation : {} {} version {} has been signed").format(
                    compliance_form_signature.compliance_form.title,
                    compliance_form_signature.compliance_form.form_type,
                    compliance_form_signature.version,
                ),
                body=msg,
                user=compliance_form_signature.person.user_account,
                reverse_name="wbcompliance:complianceformsignature-detail",
                reverse_args=[compliance_form_signature.id],
            )

        return Response(
            {
                "__notification": {
                    str(compliance_form_signature.signed): "Compliance Form signed",
                    "person_signed": compliance_form_signature.person.id,
                }
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["PATCH"], authentication_classes=[JWTCookieAuthentication])
    def regenerate_document(self, request, pk):
        compliance_form_signature = get_object_or_404(ComplianceFormSignature, pk=pk)
        if (
            not request.user.has_perm("wbcompliance.administrate_compliance")
            and request.user.profile != compliance_form_signature.person
        ):
            return Response(status=status.HTTP_403_FORBIDDEN)
        content_type = ContentType.objects.get_for_model(ComplianceFormSignature)
        send_email = request.POST.get("send_email", "false") == "true"
        update_or_create_compliance_document.delay(request.user.id, content_type.id, pk, send_email=send_email)

        return Response(
            {"__notification": {"title": "PDF is going to be created and sent to you."}},
            status=status.HTTP_200_OK,
        )


class CFComplianceFormSignatureModelViewSet(ComplianceFormSignatureModelViewSet):
    endpoint_config_class = CFComplianceFormSignatureEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(compliance_form__id=self.kwargs["compliance_form_id"])
