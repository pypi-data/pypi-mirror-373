import pytest
from wbcore.contrib.authentication.factories import UserFactory
from wbcore.permissions.shortcuts import get_internal_users

from wbcompliance.models import ComplianceForm, ComplianceFormSignature

from .mixins import UserTestMixin


@pytest.mark.django_db
class TestSpecificModels(UserTestMixin):
    @pytest.mark.parametrize("other_user", [True, False])
    def test_draft_activationrequested_active(self, compliance_form_factory, other_user):
        other_user = UserFactory() if other_user else None
        compliance_form = compliance_form_factory()
        assert compliance_form.status == ComplianceForm.Status.DRAFT
        compliance_form.activationrequested(by=other_user)
        assert compliance_form.status == ComplianceForm.Status.ACTIVATION_REQUESTED
        compliance_form.active(by=other_user)
        assert compliance_form.status == ComplianceForm.Status.ACTIVE
        compliance_form.draft(by=other_user)
        assert compliance_form.status == ComplianceForm.Status.DRAFT

    def test_create_compliance_form_signature(
        self,
        compliance_form_factory,
        user,
        compliance_form_section_factory,
        compliance_form_rule_factory,
    ):
        compliance_form = compliance_form_factory(
            assigned_to=(user.groups.filter(name="Compliance Position").first(),)
        )
        section = compliance_form_section_factory(compliance_form=compliance_form)
        compliance_form_rule_factory(section=section)

        compliance_form.activationrequested()
        compliance_form.active()
        assert ComplianceFormSignature.objects.count() == 1

        # test empty assigned_to
        compliance_form1 = compliance_form_factory(only_internal=True)
        compliance_form1.activationrequested()
        compliance_form1.active()
        assert (
            ComplianceFormSignature.objects.filter(compliance_form=compliance_form1).count()
            == get_internal_users().count()
        )

    # def test_only_internal(self, compliance_form_factory):
    #     employee.contract_type = EmployeeHumanResource.ContractType.EXTERNAL
    #     employee.save()
    #     compliance_form = compliance_form_factory(assigned_to=(user.groups.filter(name="Compliance Position").first(),), only_internal=True)
    #     assert compliance_form.get_signing_users().count() == 0
    #
    #     employee2 = EmployeeHumanResourceFactory(profile=person2)
    #     compliance_form2 = compliance_form_factory(assigned_to=(employee2.position,), only_internal=False)
    #     assert compliance_form2.get_signing_users().count() == 1
