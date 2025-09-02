from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from django.db.models import (
    BooleanField,
    Case,
    Count,
    F,
    OuterRef,
    QuerySet,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from rest_framework.reverse import reverse
from wbcore.contrib.icons import WBIcon
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.enums import RequestType
from wbcore.markdown.utils import custom_url_fetcher
from wbcore.metadata.configs.buttons import ActionButton, ButtonDefaultColor
from wbcore.models import WBModel
from wbcore.permissions.shortcuts import get_internal_users
from weasyprint import HTML

from .compliance_type import ComplianceDocumentMixin, ComplianceType, can_active_request

User = get_user_model()


class ComplianceFormType(WBModel):
    class Type(models.TextChoices):
        TEXT = "TEXT", "Text"
        FORM = "FORM", "Form"

    class Meta:
        verbose_name = "Compliance Form Type"
        verbose_name_plural = "Compliance Form Types"

    name = models.CharField(max_length=255, verbose_name=_("Name"))
    type = models.CharField(
        max_length=32,
        default=Type.TEXT,
        choices=Type.choices,
        verbose_name=_("Type"),
    )

    def __str__(self) -> str:
        return "{}".format(self.name)

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcompliance:complianceformtype"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcompliance:complianceformtyperepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{name}}"


class ComplianceForm(ComplianceDocumentMixin, WBModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVATION_REQUESTED = "ACTIVATION_REQUESTED", "Activation Requested"
        ACTIVE = "ACTIVE", "Active"

    class Meta:
        verbose_name = "Compliance Form"
        verbose_name_plural = "Compliance Forms"

        notification_types = [
            create_notification_type(
                code="wbcompliance.complianceform.notify",
                title="Compliance Form Notification",
                help_text="Sends out a notification when something happens with a compliance form",
                email=True,
                web=False,
                mobile=False,
                is_lock=True,
            )
        ]

    creator = models.ForeignKey(
        to="directory.Person",
        null=True,
        blank=True,
        verbose_name=_("Creator"),
        related_name="compliance_forms",
        on_delete=models.deletion.SET_NULL,
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    changer = models.ForeignKey(
        "directory.Person", null=True, blank=True, verbose_name=_("Changer"), on_delete=models.deletion.SET_NULL
    )
    changed = models.DateTimeField(auto_now=True, verbose_name=_("Changed"))
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    policy = models.TextField(default="", null=True, blank=True, verbose_name=_("Policy"))
    start = models.DateField(verbose_name=_("Start"))
    end = models.DateField(verbose_name=_("End"), null=True, blank=True)
    assigned_to = models.ManyToManyField(
        Group,
        related_name="forms_of_group",
        blank=True,
        verbose_name=_("Group to which the Form applies"),
    )
    only_internal = models.BooleanField(
        default=True, verbose_name=_("Only internal"), help_text=_("Send the Form only to internal users")
    )
    form_type = models.ForeignKey(to=ComplianceFormType, on_delete=models.PROTECT, verbose_name=_("Form Type"))

    compliance_type = models.ForeignKey(to=ComplianceType, on_delete=models.PROTECT, verbose_name=_("Type"))

    status = FSMField(
        default=Status.DRAFT,
        choices=Status.choices,
        verbose_name=_("Status"),
        help_text=_("The Compliance Form status (default to Draft)"),
    )
    version = models.IntegerField(default=0)

    def generate_pdf(self) -> bytes:
        html_content = ""
        if self.form_type.type == ComplianceFormType.Type.TEXT:
            html_content = self.policy
        elif self.form_type.type == ComplianceFormType.Type.FORM:
            html = get_template("compliance/compliance_form.html")
            html_content = html.render(
                {"form_type": self.form_type.type, "today": timezone.now(), "form": self, "is_signature": False}
            )
        return HTML(
            string=html_content, base_url=settings.BASE_ENDPOINT_URL, url_fetcher=custom_url_fetcher
        ).write_pdf()

    @transition(
        field=status,
        source=Status.DRAFT,
        target=Status.ACTIVATION_REQUESTED,
        permission=lambda instance, user: user.has_perm("wbcompliance.administrate_compliance"),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbcompliance:complianceform",),
                icon=WBIcon.EDIT.icon,
                key="activationrequested",
                label=_("Request Activation"),
                action_label=_("Request Activation"),
                description_fields=_(
                    "{{_form_type.name}} <p>Title: <b>{{title}}</b></p>\
                <p>Version: <b>{{version}}</b></p> <p>Status: <b>{{status}}</b></p> <p>Start: <b>{{start}}</b></p>\
                <p>End: <b>{{end}}</b></p> <p>Do you want to send this request for validation ?</p>"
                ),
            )
        },
    )
    def activationrequested(self, by=None, description=None, **kwargs):
        if self.compliance_type:
            # notify the compliance team without the current user
            if by:
                self.changer = by.profile
            current_profile = self.changer if self.changer else self.creator
            recipients = ComplianceType.get_administrators(self.compliance_type).exclude(profile=current_profile)
            msg = _("Validation Request from {} to activate a {} version <b>{}</b> : <b>{}</b>").format(
                str(current_profile), self.form_type, self.version, self.title
            )
            title = _("Validation Request {} : {}").format(self.form_type, self.title)
            self.notify(title, msg, recipients, admin_compliance=True)

    @transition(
        field=status,
        source=Status.ACTIVATION_REQUESTED,
        target=Status.ACTIVE,
        permission=can_active_request,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbcompliance:complianceform",),
                icon=WBIcon.SEND.icon,
                key="active",
                label=_("Activate"),
                action_label=_("Activate"),
                description_fields=_(
                    """
                <p> Title: <b> {{title}} </b></p> <p>Version: <b>{{version}}</b></p>
                <p>Start: <b>{{start}}</b></p><p>End: <b>{{end}}</b></p>
                <p>Do you want to activate this {{_form_type.name}} ?</p>
                """
                ),
            )
        },
    )
    def active(self, by=None, description=None, **kwargs):
        self.version += 1
        if by:
            self.changer = by.profile
        current_profile = self.changer if self.changer else self.creator
        self.create_compliance_form_signature()

        msg = _("<p>{} has activated a {} version <b>{}</b> : <b>{}</b></p>").format(
            str(current_profile), self.form_type, self.version, self.title
        )
        if self.policy and self.policy != "<p></p>" and self.policy != "null":
            msg += _("</br><p><b>Policy:</b></p><i>{}</i>").format(self.policy)
        title = _("Applying a {} : {}").format(self.form_type, self.title)
        self.notify(title, msg)
        self.save()

    @transition(
        field=status,
        source=[Status.ACTIVATION_REQUESTED, Status.ACTIVE],
        target=Status.DRAFT,
        permission=lambda instance, user: user.has_perm("wbcompliance.administrate_compliance"),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbcompliance:complianceform",),
                icon=WBIcon.EDIT.icon,
                key="draft",
                label=_("Return to Draft Mode"),
                action_label=_("Return to Draft Mode"),
                description_fields=_(
                    """
                {{_form_type.name}}<p>Title: <b> {{title}} </b></p><p>Version: <b>{{version}}</b></p>
                <p>Status: <b>{{status}}</b></p> <p>Start: <b>{{start}}</b></p>  <p>End: <b>{{end}}</b></p>
                <p>Do you want to return to draft mode this {{_form_type.name}}?</p>
                """
                ),
            )
        },
    )
    def draft(self, by=None, description=None, **kwargs):
        if self.compliance_type:
            if by:
                self.changer = by.profile
            current_profile = self.changer if self.changer else self.creator
            if self.status == ComplianceForm.Status.ACTIVE:
                msg = _("{} has disabled a {} version <b>{}</b> : <b>{}</b>").format(
                    str(current_profile), self.form_type, self.version, self.title
                )
                title = _("Disabled {} : {}").format(self.form_type, self.title)
            else:
                msg = _("{} has modified a {} version <b>{}</b> to Draft : <b>{}</b>").format(
                    str(current_profile), self.form_type, self.version, self.title
                )
                title = _("{} Drafted: {}").format(self.form_type, self.title)
            recipients = ComplianceType.get_administrators(self.compliance_type).exclude(profile=current_profile)
            self.notify(title, msg, recipients, admin_compliance=True)

    def get_signing_users(self) -> QuerySet["User"]:
        if self.only_internal:
            users = get_internal_users()
        else:
            users = User.objects.filter(is_active=True)
        if self.assigned_to.exists():
            users = users.filter(groups__in=self.assigned_to.all())
        return users.distinct()

    def create_compliance_form_signature(self) -> None:
        for user in self.get_signing_users():
            compliance_form_signature = ComplianceFormSignature.objects.create(
                compliance_form=self,
                version=self.version,
                policy=self.policy,
                start=self.start,
                end=self.end,
                person=user.profile,
            )
            sections = ComplianceFormSection.objects.filter(compliance_form=compliance_form_signature.compliance_form)
            for section in sections:
                signature_section = ComplianceFormSignatureSection.objects.create(
                    compliance_form_signature=compliance_form_signature, name=section.name
                )
                rules = ComplianceFormRule.objects.filter(section=section)
                for rule in rules:
                    ComplianceFormSignatureRule.objects.create(section=signature_section, text=rule.text)

    def notify(
        self, title: str, msg: str, recipients: QuerySet["User"] | None = None, admin_compliance: bool = False
    ) -> None:
        """
        param:
            recipients: list of users, if not set, we get all users assigned to the form
            admin_compliance: by default is false, allow to send the signature form to recipient, if true send rather the form to admin.
        """
        if admin_compliance:
            users = ComplianceType.get_administrators(self.compliance_type)
            if recipients:
                users = users.filter(id__in=[_user.id for _user in recipients])
        else:
            users = recipients if recipients else self.get_signing_users()
        for user in users:
            if admin_compliance:
                endpoint = reverse("wbcompliance:complianceform-detail", args=[self.id])
            else:
                endpoint = None
                if formsignature := (
                    ComplianceFormSignature.objects.filter(compliance_form=self, person=user.profile)
                    .order_by("version")
                    .last()
                ):
                    endpoint = reverse("wbcompliance:complianceformsignature-detail", args=[formsignature.id])

            if endpoint:
                send_notification(
                    code="wbcompliance.complianceform.notify",
                    title=title,
                    body=msg,
                    user=user,
                    endpoint=endpoint,
                )

    @classmethod
    def get_subquery_total_compliance_form_signature(cls, remaining_signed: bool = False) -> Subquery:
        if remaining_signed:
            compliance_form_signatures = ComplianceFormSignature.objects.filter(
                compliance_form=OuterRef("pk"),
                signed=None,
            ).order_by("-version")
        else:
            compliance_form_signatures = ComplianceFormSignature.objects.filter(
                compliance_form=OuterRef("pk"),
            ).order_by("-version")

        return Coalesce(
            Subquery(
                compliance_form_signatures.values("compliance_form__pk")
                .annotate(total_signed=Count("compliance_form__pk"))
                .values("total_signed")[:1]
            ),
            0,
        )

    @classmethod
    def get_subquery_compliance_form_signature(cls, person_signed) -> Subquery:
        compliance_form_signatures = ComplianceFormSignature.objects.filter(
            compliance_form=OuterRef("pk"), person=person_signed
        ).order_by("-version")
        return Coalesce(
            Subquery(
                compliance_form_signatures.values("compliance_form__pk")
                .annotate(
                    is_signed=Case(
                        When(signed=None, then=Value(False)),
                        default=Value(True),
                        output_field=BooleanField(),
                    )
                )
                .values("is_signed")[:1]
            ),
            None,
        )

    def __str__(self) -> str:
        return "{} {} ({} - {}) ".format(self.title, self.version, self.start, self.end)

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcompliance:complianceform"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcompliance:complianceformrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{title}}"


class ComplianceFormSignature(ComplianceDocumentMixin, models.Model):
    class Meta:
        verbose_name = "Compliance Form Signature"
        verbose_name_plural = "Compliance Signatures"

        notification_types = [
            create_notification_type(
                code="wbcompliance.complianceformsignature.signed",
                title="Compliance Form Signature Confirmation",
                help_text="Send a notification as a confirmation that a compliance form has been signed",
                email=True,
                web=False,
                mobile=False,
                is_lock=True,
            )
        ]

    compliance_form = models.ForeignKey(
        to="wbcompliance.ComplianceForm",
        verbose_name=_("Form"),
        related_name="complianceforms",
        on_delete=models.CASCADE,
    )
    version = models.IntegerField(default=0, verbose_name=_("Version"))
    start = models.DateField(verbose_name=_("Start"))
    end = models.DateField(verbose_name=_("End"), null=True, blank=True)
    policy = models.TextField(default="", null=True, blank=True, verbose_name=_("Policy"))
    signed = models.DateTimeField(null=True, blank=True, verbose_name=_("Signed"))
    person = models.ForeignKey(
        to="directory.Person",
        verbose_name=_("Signer"),
        related_name="signed_compliance_forms",
        on_delete=models.CASCADE,
    )
    remark = models.TextField(null=True, blank=True, default="", verbose_name=_("Remark"))

    def __str__(self) -> str:
        return "{} {} ({} - {})".format(self.compliance_form.title, self.version, self.start, self.end)

    def generate_pdf(self) -> bytes:
        html_content = ""
        html = get_template("compliance/compliance_form.html")
        html_content = html.render(
            {
                "form_type": self.compliance_form.form_type.type,
                "today": timezone.now(),
                "form": self,
                "is_signature": True,
            }
        )
        return HTML(
            string=html_content, base_url=settings.BASE_ENDPOINT_URL, url_fetcher=custom_url_fetcher
        ).write_pdf()

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcompliance:complianceformsignature"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{compliance_form.title}} {{self.version}} ({{start}} - {{end}})"


class ComplianceFormSection(WBModel):
    """Model that represents a section of the Compliance Form"""

    compliance_form = models.ForeignKey(
        ComplianceForm, related_name="compliance_forms", verbose_name=_("Compliance Form"), on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255, verbose_name=_("Name section"))

    class Meta:
        verbose_name = "Section of the Compliance Form"
        verbose_name_plural = "Sections of the Compliance Form"

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcompliance:complianceformsection"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcompliance:complianceformsectionrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{name}}"


class ComplianceFormRule(models.Model):
    """Model that represents a rule in a Section of the Compliance Form"""

    section = models.ForeignKey(
        ComplianceFormSection, related_name="rules", verbose_name=_("Section"), on_delete=models.CASCADE
    )
    text = models.TextField(default="")
    ticked = models.BooleanField(
        default=False,
        verbose_name=_("Expected Answer"),
    )

    class Meta:
        verbose_name = "Rule of the section of the Compliance Form"
        verbose_name_plural = "Rules of the section of the Compliance Form"

    def __str__(self) -> str:
        return "{} {}".format(self.section, self.id)

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcompliance:complianceformrule"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{section}} {{id}}"


class ComplianceFormSignatureSection(models.Model):
    """Model that represents a section of the Compliance Form Signature"""

    compliance_form_signature = models.ForeignKey(
        ComplianceFormSignature,
        related_name="compliance_form_signatures",
        verbose_name=_("Compliance Form Signature"),
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255, verbose_name=_("Name section"))

    class Meta:
        verbose_name = "Section of the Compliance Form Signature"
        verbose_name_plural = "Sections of the Compliance Form Signature"

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcompliance:complianceformsignaturesectionrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{name}}"


class ComplianceFormSignatureRule(models.Model):
    """Model that represents a rule in a Section of the Compliance Form Signature"""

    section = models.ForeignKey(
        ComplianceFormSignatureSection, related_name="rules", verbose_name=_("Section"), on_delete=models.CASCADE
    )
    text = models.TextField(default="")
    ticked = models.BooleanField(
        default=False,
        verbose_name=_("Answer"),
    )
    comments = models.TextField(default="")

    class Meta:
        verbose_name = "Rule of the section of the Compliance Form Signature"
        verbose_name_plural = "Rules of the section of the Compliance Form Signature"

    def __str__(self) -> str:
        return "{} {}".format(self.section, self.id)

    @classmethod
    def get_subquery_expected_ticked(cls) -> Subquery:
        return Coalesce(
            Subquery(
                ComplianceFormRule.objects.filter(
                    section__compliance_form=OuterRef("section__compliance_form_signature__compliance_form"),
                    section__name=OuterRef("section__name"),
                    text=OuterRef("text"),
                )
                .values("ticked")
                .annotate(exp=F("ticked"))
                .values("exp")[:1]
            ),
            None,
        )

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{section}} {{id}}"


if apps.is_installed("wbhuman_resources"):

    @receiver(post_save, sender="wbhuman_resources.EmployeeHumanResource")
    def post_save_compliance_form_employee(sender, instance, created, **kwargs):
        if created:
            for compliance_form in ComplianceForm.objects.filter(status=ComplianceForm.Status.ACTIVE):
                if compliance_form.get_signing_users().filter(profile_id=instance.profile.id).exists():
                    compliance_form_signature, created = ComplianceFormSignature.objects.get_or_create(
                        compliance_form=compliance_form,
                        version=compliance_form.version,
                        policy=compliance_form.policy,
                        start=compliance_form.start,
                        end=compliance_form.end,
                        person=instance.profile,
                    )
                    sections = ComplianceFormSection.objects.filter(
                        compliance_form=compliance_form_signature.compliance_form
                    )
                    for section in sections:
                        signature_section = ComplianceFormSignatureSection.objects.create(
                            compliance_form_signature=compliance_form_signature, name=section.name
                        )
                        rules = ComplianceFormRule.objects.filter(section=section)
                        for rule in rules:
                            ComplianceFormSignatureRule.objects.create(section=signature_section, text=rule.text)
                    if _user := getattr(instance.profile, "user_account", None):
                        msg = _("<p>{} has activated a <b>{}</b> policy version <b>{} </b></p>").format(
                            str(compliance_form.changer), compliance_form.title, compliance_form.version
                        )
                        if (
                            compliance_form.policy
                            and compliance_form.policy != "<p></p>"
                            and compliance_form.policy != "null"
                        ):
                            msg += _("</br><p><b>Policy:</b></p><i>{}</i>").format(compliance_form.policy)
                        title = _("Applying a {} : {}").format(compliance_form.form_type, compliance_form.title)
                        compliance_form.notify(title, msg, recipients=[_user])
