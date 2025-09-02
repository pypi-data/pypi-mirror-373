import logging
from typing import TypeVar

from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from slugify import slugify
from wbcore.contrib.documents.models import Document, DocumentType
from wbcore.contrib.documents.models.mixins import DocumentMixin
from wbcore.models import WBModel

User = get_user_model()
SelfComplianceType = TypeVar("SelfComplianceType", bound="ComplianceType")


def can_active_request(instance, user: "User") -> bool:
    if instance.changer:
        current_profile = instance.changer
    else:
        current_profile = instance.creator

    return user.is_superuser or (
        user.profile != current_profile and user.has_perm("wbcompliance.administrate_compliance")
    )


class ComplianceType(WBModel):
    class Meta:
        verbose_name = "Compliance Type"
        verbose_name_plural = "Compliance Types"
        permissions = [("administrate_compliance", "Can Administrate Compliance")]

    name = models.CharField(max_length=255, verbose_name=_("Name"), unique=True)
    description = models.TextField(default="", blank=True, verbose_name=_("Description"))
    in_charge = models.ManyToManyField(
        Group,
        related_name="compliance_types",
        blank=True,
        verbose_name=_("Group of administrators"),
        help_text=_("groups responsible for managing this type of compliance"),
    )

    def __str__(self) -> str:
        return "{}".format(self.name)

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcompliance:compliancetype"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcompliance:compliancetyperepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{name}}"

    @classmethod
    def get_administrators(cls, type: SelfComplianceType | None = None) -> models.QuerySet["User"]:
        administrators = (
            get_user_model()
            .objects.filter(
                Q(groups__permissions__codename="administrate_compliance")
                | Q(user_permissions__codename="administrate_compliance")
            )
            .distinct()
        )
        if type:
            administrators = administrators.filter(groups__in=type.in_charge.all())
        return administrators

    @classmethod
    def is_administrator(cls, user) -> bool:
        return user.has_perm("wbcompliance.administrate_compliance")


@shared_task
def update_or_create_compliance_document(user_id: int, content_type_id: int, object_id: int, send_email: bool = True):
    user = get_user_model().objects.get(id=user_id)
    content_type = ContentType.objects.get(id=content_type_id)
    content_object = content_type.model_class().objects.get(id=object_id)

    filename = "{}.pdf".format(slugify(str(content_object)))
    logging.getLogger("weasyprint").setLevel(logging.CRITICAL)
    pdf_content = content_object.generate_pdf()
    logging.getLogger("weasyprint").setLevel(logging.INFO)
    content_file = ContentFile(pdf_content, name=filename)

    document_type, _ = DocumentType.objects.get_or_create(name="Compliance")
    document, _ = Document.objects.update_or_create(
        document_type=document_type,
        system_created=True,
        system_key="{}-{}-{}".format(content_type.model, content_object.id, filename),
        defaults={
            "file": content_file,
            "name": filename,
            "permission_type": Document.PermissionType.PRIVATE,
            "creator": user,
        },
    )
    document.link(content_object)
    if send_email:
        document.send_email(
            to_emails=user.email,
            as_link=True,
            subject="Compliance PDF - {}".format(str(content_object)),
        )


class ComplianceDocumentMixin(DocumentMixin):
    def get_permissions_for_user_and_document(self, user, view, created):
        """
        allows user to access the document associated with this object
        :return:     The tuple list permission for the corresponding user

        :note: Core implements a signal that automatically calls this function when instantiating the view
        """
        if ComplianceType.is_administrator(user):
            return [
                ("document.view_document", False),
                ("document.change_document", False),
                ("document.delete_document", False),
            ]
        return []
