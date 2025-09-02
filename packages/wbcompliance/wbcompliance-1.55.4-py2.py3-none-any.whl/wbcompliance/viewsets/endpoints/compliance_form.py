from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig

from wbcompliance.models import ComplianceForm, ComplianceFormSection, ComplianceType


# Compliance Form
class ComplianceFormEndpointConfig(EndpointViewConfig):
    def get_instance_endpoint(self, **kwargs):
        if self.instance:
            obj = self.view.get_object()
            if (
                not ComplianceType.is_administrator(self.request.user)
                or obj.status == ComplianceForm.Status.ACTIVATION_REQUESTED
            ):
                return None
        return super().get_instance_endpoint()

    def get_create_endpoint(self, **kwargs):
        if ComplianceType.is_administrator(self.request.user):
            return super().get_create_endpoint()
        return None

    def get_delete_endpoint(self, **kwargs):
        if self.instance:
            obj = self.view.get_object()
            if (
                not ComplianceType.is_administrator(self.request.user)
                or obj.status == ComplianceForm.Status.ACTIVATION_REQUESTED
            ):
                return None
        return super().get_delete_endpoint()


class ComplianceFormSignatureEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None

    def get_instance_endpoint(self, **kwargs):
        if self.instance:
            obj = self.view.get_object()
            if obj.person != self.request.user.profile or obj.signed:
                return None
        return reverse(f"{self.view.get_model().get_endpoint_basename()}-list", request=self.request)


class CFComplianceFormSignatureEndpointConfig(ComplianceFormSignatureEndpointConfig):
    pass


# SECTION OF THE COMPLIANCE FORM
class CFComplianceFormSectionEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbcompliance:complianceform-sections-list",
            args=[self.view.kwargs["compliance_form_id"]],
            request=self.request,
        )

    def get_instance_endpoint(self, **kwargs):
        if self.instance and not ComplianceType.is_administrator(self.request.user):
            return None
        if self.instance and "compliance_form_id" in self.view.kwargs:
            obj = ComplianceForm.objects.get(id=self.view.kwargs.get("compliance_form_id"))
            if obj.status == ComplianceForm.Status.ACTIVATION_REQUESTED:
                return None
        return super().get_instance_endpoint()

    def get_create_endpoint(self, **kwargs):
        if not ComplianceType.is_administrator(self.request.user):
            return None
        if "compliance_form_id" in self.view.kwargs:
            obj = ComplianceForm.objects.get(id=self.view.kwargs.get("compliance_form_id"))
            if obj.status == ComplianceForm.Status.ACTIVATION_REQUESTED:
                return None
        return super().get_create_endpoint()

    def get_delete_endpoint(self, **kwargs):
        if not ComplianceType.is_administrator(self.request.user):
            return None
        if "compliance_form_id" in self.view.kwargs:
            obj = ComplianceForm.objects.get(id=self.view.kwargs.get("compliance_form_id"))
            if obj.status == ComplianceForm.Status.ACTIVATION_REQUESTED:
                return None
        if "pk" in self.view.kwargs:
            return f'{self.get_endpoint()}{self.view.kwargs["pk"]}/'
        return super().get_delete_endpoint()


# RULES OF THE SECTION
class ComplianceFormRuleEndpointConfig(EndpointViewConfig):
    def get_instance_endpoint(self, **kwargs):
        if self.instance and not ComplianceType.is_administrator(self.request.user):
            return None
        return super().get_instance_endpoint()

    def get_create_endpoint(self, **kwargs):
        if ComplianceType.is_administrator(self.request.user):
            return super().get_create_endpoint()
        return None

    def get_delete_endpoint(self, **kwargs):
        if ComplianceType.is_administrator(self.request.user):
            return super().get_delete_endpoint()
        return None


class ComplianceFormSectionRuleEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbcompliance:complianceformsection-rules-list",
            args=[self.view.kwargs["section_id"]],
            request=self.request,
        )

    def get_instance_endpoint(self, **kwargs):
        if self.instance and not ComplianceType.is_administrator(self.request.user):
            return None
        if self.instance and "section_id" in self.view.kwargs:
            obj = ComplianceFormSection.objects.get(id=self.view.kwargs.get("section_id"))
            if obj.compliance_form.status == ComplianceForm.Status.ACTIVATION_REQUESTED:
                return None
        return super().get_instance_endpoint()

    def get_create_endpoint(self, **kwargs):
        if not ComplianceType.is_administrator(self.request.user):
            return None
        if "section_id" in self.view.kwargs:
            obj = ComplianceFormSection.objects.get(id=self.view.kwargs.get("section_id"))
            if obj.compliance_form.status == ComplianceForm.Status.ACTIVATION_REQUESTED:
                return None
        return super().get_create_endpoint()

    def get_delete_endpoint(self, **kwargs):
        if not ComplianceType.is_administrator(self.request.user):
            return None
        if "section_id" in self.view.kwargs:
            obj = ComplianceFormSection.objects.get(id=self.view.kwargs.get("section_id"))
            if obj.compliance_form.status == ComplianceForm.Status.ACTIVATION_REQUESTED:
                return None
        if "pk" in self.view.kwargs:
            return f'{self.get_endpoint()}{self.view.kwargs["pk"]}/'
        return super().get_delete_endpoint()


class ComplianceFormSignatureSectionRuleEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None

    def get_instance_endpoint(self, **kwargs):
        if self.instance:
            obj = self.view.get_object()
            if (
                obj.section.compliance_form_signature.person != self.request.user.profile
                or obj.section.compliance_form_signature.signed
            ):
                return None
        return reverse(
            "wbcompliance:complianceformsignaturesection-rules-list",
            args=[self.view.kwargs["section_id"]],
            request=self.request,
        )


class ComplianceFormTypeEndpointConfig(EndpointViewConfig):
    def get_instance_endpoint(self, **kwargs):
        if self.instance and not ComplianceType.is_administrator(self.request.user):
            return None
        return super().get_instance_endpoint()

    def get_create_endpoint(self, **kwargs):
        if ComplianceType.is_administrator(self.request.user):
            return super().get_create_endpoint()
        return None

    def get_delete_endpoint(self, **kwargs):
        if ComplianceType.is_administrator(self.request.user):
            return super().get_delete_endpoint()
        return None
