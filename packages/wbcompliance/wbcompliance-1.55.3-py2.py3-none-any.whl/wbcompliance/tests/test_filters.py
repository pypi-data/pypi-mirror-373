import pytest

from wbcompliance.viewsets import ComplianceFormSignatureModelViewSet

from .mixins import UserTestMixin


@pytest.mark.django_db
class TestSpecificFilters(UserTestMixin):
    def test_filter_version(self, compliance_form_factory, user):
        compliance_form = compliance_form_factory(assigned_to=(user.groups.first(),))
        compliance_form.activationrequested()
        compliance_form.active()
        compliance_form.draft()
        compliance_form.activationrequested()
        compliance_form.active()
        mvs = ComplianceFormSignatureModelViewSet()
        qs = mvs.get_serializer_class().Meta.model.objects.all()
        assert mvs.filterset_class().filter_version(qs, "", False) == qs
        assert mvs.filterset_class().filter_version(qs, "", False).count() == 2
        assert mvs.filterset_class().filter_version(qs, "", True).count() == 1

    def test_not_created_m2m_field_compliance_form_factory(self, compliance_form_factory):
        assert compliance_form_factory.build()
