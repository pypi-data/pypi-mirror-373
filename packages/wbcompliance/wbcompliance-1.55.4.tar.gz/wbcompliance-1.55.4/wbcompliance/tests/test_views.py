import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.test import APIRequestFactory
from wbcore.contrib.authentication.factories import InternalUserFactory, UserFactory
from wbcore.contrib.authentication.models import User
from wbcore.test.utils import (
    get_data_from_factory,
    get_kwargs,
    get_model_factory,
    get_or_create_superuser,
)

from wbcompliance.factories import (
    ComplianceFormSectionFactory,
    ComplianceFormSignatureRuleFactory,
    ComplianceFormSignatureSectionFactory,
    ComplianceFormTypeFactory,
)
from wbcompliance.models import (
    ComplianceForm,
    ComplianceFormRule,
    ComplianceFormSection,
    ComplianceFormSignature,
    ComplianceFormType,
)
from wbcompliance.viewsets import (
    CFComplianceFormSignatureModelViewSet,
    ComplianceFormModelViewSet,
    ComplianceFormRuleViewSet,
    ComplianceFormSectionComplianceFormViewSet,
    ComplianceFormSectionRuleViewSet,
    ComplianceFormSignatureModelViewSet,
    ComplianceFormTypeViewSet,
    ComplianceTaskMatrixPandasViewSet,
)

from .mixins import UserTestMixin


@pytest.mark.django_db
class TestSpecificViewsets(UserTestMixin):
    @pytest.mark.parametrize(
        "mvs",
        [
            ComplianceFormModelViewSet,
            ComplianceFormSignatureModelViewSet,
            ComplianceFormTypeViewSet,
            ComplianceFormSectionComplianceFormViewSet,
            ComplianceFormSectionRuleViewSet,
        ],
    )
    def test_get_queryset(self, mvs):
        request = APIRequestFactory().get("")
        request.user = UserFactory(is_active=True, is_superuser=False)
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        obj = factory()
        kwargs = get_kwargs(obj, mvs, request)
        vs = mvs.as_view({"get": "list"})
        response = vs(request, **kwargs)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        "mvs, signature", [(ComplianceFormModelViewSet, False), (ComplianceFormSignatureModelViewSet, True)]
    )
    def test_option_request_declaration_on_honour(self, mvs, signature, compliance_form_factory):
        request = APIRequestFactory().options("")
        request.user = UserFactory(is_active=True, is_superuser=True)
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        complianceformtype = ComplianceFormTypeFactory()
        complianceformtype.type = ComplianceFormType.Type.FORM
        complianceformtype.save()
        if signature:
            cf = compliance_form_factory(form_type=complianceformtype)
            obj = factory(compliance_form=cf)
            sign_section = ComplianceFormSignatureSectionFactory(compliance_form_signature=obj)
            ComplianceFormSignatureRuleFactory(section=sign_section)
        else:
            obj = factory(form_type=complianceformtype)
            ComplianceFormSectionFactory(compliance_form=obj)
        obj.save()
        kwargs = get_kwargs(obj, mvs, request)
        kwargs["pk"] = obj.pk
        vs = mvs.as_view({"options": "options"})
        response = vs(request, **kwargs)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        "mvs, model, codename, is_queryset_not_empty",
        [
            (ComplianceFormTypeViewSet, ComplianceFormType, "view_complianceformtype", False),
            (ComplianceFormRuleViewSet, ComplianceFormRule, "view_complianceformrule", True),
            (ComplianceFormSectionComplianceFormViewSet, ComplianceFormSection, "view_complianceformsection", False),
            (ComplianceFormSectionRuleViewSet, ComplianceFormRule, "view_complianceformrule", False),
        ],
    )
    def test_option_request_no_admin_section_rules(self, mvs, model, codename, is_queryset_not_empty):
        request = APIRequestFactory().options("")
        request.user = UserFactory(is_active=True)
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        obj = factory()
        kwargs = get_kwargs(obj, mvs, request)
        kwargs["pk"] = obj.pk
        content_type = ContentType.objects.get_for_model(model)
        permission = Permission.objects.get(
            codename=codename,
            content_type=content_type,
        )
        request.user.user_permissions.add(permission)
        # permission check caching. -> refetch your object
        request.user.refresh_from_db()
        request.user = User.objects.get(pk=request.user.pk)

        view = mvs()
        view.setup(request, **kwargs)

        assert view.get_queryset().exists() == is_queryset_not_empty

    @pytest.mark.parametrize("mvs", [ComplianceFormModelViewSet])
    def test_option_request_no_admin_compliance_form(self, mvs, compliance_form_factory):
        request = APIRequestFactory().options("")
        request.user = InternalUserFactory(is_active=True)
        obj = compliance_form_factory.create()
        kwargs = get_kwargs(obj, mvs, request)

        permission_view = Permission.objects.get(
            codename="view_complianceform",
            content_type=ContentType.objects.get_for_model(ComplianceForm),
        )
        permission_select = Permission.objects.get(
            codename="select_complianceform",
            content_type=ContentType.objects.get_for_model(ComplianceForm),
        )
        permission_internal_user = Permission.objects.get(
            codename="is_internal_user",
        )
        request.user.user_permissions.add(permission_view)
        request.user.user_permissions.add(permission_select)
        request.user.user_permissions.add(permission_internal_user)

        request.user = User.objects.get(pk=request.user.pk)  # reset cached property and permission cache
        vs = mvs.as_view({"options": "options"})
        response = vs(request, **kwargs)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        "mvs, model, codename, is_allowed",
        [
            (ComplianceFormTypeViewSet, ComplianceFormType, "change_complianceformtype", False),
            (ComplianceFormRuleViewSet, ComplianceFormRule, "change_complianceformrule", False),
            (ComplianceFormSectionComplianceFormViewSet, ComplianceFormSection, "change_complianceformsection", False),
            (ComplianceFormSectionRuleViewSet, ComplianceFormRule, "change_complianceformrule", False),
        ],
    )
    def test_get_instance_endpoint_no_admin_section_rules(self, mvs, model, codename, is_allowed):
        user = UserFactory(is_active=True)
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        obj = factory()
        data = get_data_from_factory(obj, mvs, update=True, superuser=user)
        request = APIRequestFactory().put("", data)
        request.user = user
        kwargs = get_kwargs(obj, mvs, request)

        content_type = ContentType.objects.get_for_model(model)
        permission = Permission.objects.get(
            codename=codename,
            content_type=content_type,
        )
        request.user.user_permissions.add(permission)
        # permission check caching. -> refetch your object
        request.user.refresh_from_db()
        request.user = User.objects.get(pk=request.user.pk)

        vs = mvs.as_view({"put": "update"})
        response = vs(request, **kwargs, pk=obj.pk)
        if is_allowed:
            assert response.status_code == status.HTTP_200_OK
        else:
            assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.parametrize("mvs", [ComplianceFormSignatureModelViewSet, CFComplianceFormSignatureModelViewSet])
    def test_get_create_endpoint_no_admin_compliance_form(self, mvs):
        user = UserFactory(is_active=True)
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        obj = factory()
        data = get_data_from_factory(obj, mvs, update=True, superuser=user)
        request = APIRequestFactory().post("", data)
        request.user = user
        kwargs = get_kwargs(obj, mvs, request)
        content_type = ContentType.objects.get_for_model(ComplianceFormSignature)
        permission = Permission.objects.get(
            codename="add_complianceformsignature",
            content_type=content_type,
        )
        request.user.user_permissions.add(permission)
        request.user.refresh_from_db()
        request.user = User.objects.get(pk=request.user.pk)
        vs = mvs.as_view({"post": "create"})
        response = vs(request, **kwargs)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.parametrize(
        "mvs, model, codename, is_allowed",
        [
            (ComplianceFormTypeViewSet, ComplianceFormType, "add_complianceformtype", False),
            (ComplianceFormRuleViewSet, ComplianceFormRule, "add_complianceformrule", False),
            (ComplianceFormSectionComplianceFormViewSet, ComplianceFormSection, "add_complianceformsection", False),
            (ComplianceFormSectionRuleViewSet, ComplianceFormRule, "add_complianceformrule", False),
        ],
    )
    def test_get_create_endpoint_no_admin_section_rules(self, mvs, model, codename, is_allowed):
        user = UserFactory(is_active=True)
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        obj = factory()
        data = get_data_from_factory(obj, mvs, update=True, superuser=user)
        request = APIRequestFactory().post("", data)
        request.user = user
        kwargs = get_kwargs(obj, mvs, request)

        content_type = ContentType.objects.get_for_model(model)
        permission = Permission.objects.get(
            codename=codename,
            content_type=content_type,
        )
        request.user.user_permissions.add(permission)
        request.user.refresh_from_db()
        request.user = User.objects.get(pk=request.user.pk)

        vs = mvs.as_view({"post": "create"})
        response = vs(request, **kwargs)
        if is_allowed:
            assert response.status_code == status.HTTP_201_CREATED
        else:
            assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.parametrize("mvs", [ComplianceFormSignatureModelViewSet, CFComplianceFormSignatureModelViewSet])
    def test_get_delete_endpoint_no_admin_compliance_form(self, mvs):
        request = APIRequestFactory().delete("")
        request.user = UserFactory(is_active=True)
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        obj = factory()
        kwargs = get_kwargs(obj, mvs, request)

        content_type = ContentType.objects.get_for_model(ComplianceFormSignature)
        permission = Permission.objects.get(
            codename="delete_complianceformsignature",
            content_type=content_type,
        )
        request.user.user_permissions.add(permission)
        request.user.refresh_from_db()

        # request.user = User.objects.get(pk=request.user.pk)
        vs = mvs.as_view({"delete": "destroy"})
        response = vs(request, **kwargs, pk=obj.pk)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    # TODO this should have never worked as Loic remove the delete endpoint excpliticlty, so the returned status code is 405 method not allowed and not 403.

    @pytest.mark.parametrize(
        "mvs, model, codename, is_allowed",
        [
            (ComplianceFormTypeViewSet, ComplianceFormType, "delete_complianceformtype", False),
            (ComplianceFormRuleViewSet, ComplianceFormRule, "delete_complianceformrule", False),
            (ComplianceFormSectionComplianceFormViewSet, ComplianceFormSection, "delete_complianceformsection", False),
            (ComplianceFormSectionRuleViewSet, ComplianceFormRule, "delete_complianceformrule", False),
        ],
    )
    def test_get_delete_endpoint_no_admin_section_rules(self, mvs, model, codename, is_allowed):
        request = APIRequestFactory().delete("")
        request.user = UserFactory(is_active=True)
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        obj = factory()
        kwargs = get_kwargs(obj, mvs, request)

        content_type = ContentType.objects.get_for_model(model)
        permission = Permission.objects.get(
            codename=codename,
            content_type=content_type,
        )
        request.user.user_permissions.add(permission)
        request.user.refresh_from_db()

        # request.user = User.objects.get(pk=request.user.pk)
        vs = mvs.as_view({"delete": "destroy"})
        response = vs(request, **kwargs, pk=obj.pk)
        if is_allowed:
            assert response.status_code == status.HTTP_204_NO_CONTENT
        else:
            assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.parametrize(
        "mvs, no_employee", [(ComplianceFormModelViewSet, True), (ComplianceFormModelViewSet, False)]
    )
    def test_sendcomplianceformnotification(self, mvs, no_employee, user):
        request = APIRequestFactory().get("")
        request.user = get_or_create_superuser()
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        obj = factory()
        if not no_employee:
            obj.assigned_to.add(user.groups.first())
            obj.activationrequested()
            obj.active()

        response = mvs().sendcomplianceformnotification(request, pk=obj.pk)
        assert response
        assert response.data

    @pytest.mark.parametrize("mvs", [ComplianceFormSignatureModelViewSet, CFComplianceFormSignatureModelViewSet])
    def test_signature(self, mvs, user_factory):
        request = APIRequestFactory().get("")
        user = user_factory.create(is_superuser=False)
        superuser = user_factory.create(is_superuser=True)
        request.user = user

        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        obj = factory(person=user.profile)
        obj2 = factory(person=superuser.profile)

        response = mvs().signature(request, pk=obj.pk)
        response2 = mvs().signature(request, pk=obj2.pk)
        assert response
        assert response.data
        assert response2.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize("mvs, changer", [(ComplianceFormModelViewSet, True), (ComplianceFormModelViewSet, False)])
    def test_active_compliance_form_viewset_admin(self, mvs, changer):
        request = APIRequestFactory().get("")
        request.user = get_or_create_superuser()
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        if changer:
            obj = factory()
        else:
            obj = factory(changer=None)
        obj.activationrequested()
        obj.active()
        kwargs = get_kwargs(obj, mvs, request)
        vs = mvs.as_view({"get": "list"})
        response = vs(request, **kwargs)
        assert response.status_code == status.HTTP_200_OK
        assert response.data
        assert response.data.get("results")

    @pytest.mark.parametrize("mvs", [ComplianceTaskMatrixPandasViewSet])
    def test_PandasAPIView(self, mvs, compliance_task_factory, compliance_task_instance_factory):
        request = APIRequestFactory().get("")
        request.user = get_or_create_superuser()

        compliance_task_instance_factory(task=compliance_task_factory())
        # kwargs = get_kwargs(obj, mvs, request)
        vs = mvs.as_view({"get": "list"})
        response = vs(request)
        assert response.status_code == status.HTTP_200_OK, str(response.status_code) + " == 200"
        assert response.data, str(response.data) + " should not be empty"
        assert response.data.get("results"), str(response.data.get("results")) + " should not be empty"

    def test_queryset_filtering_for_user(self, user_factory, compliance_form_signature_factory):
        request = APIRequestFactory().get("")
        user = user_factory.create(is_superuser=False)
        form_signature = compliance_form_signature_factory.create()
        form_signature2 = compliance_form_signature_factory.create()

        request.user = user
        viewset = ComplianceFormSignatureModelViewSet(request=request)
        queryset = viewset.get_queryset()
        assert queryset.count() == 0

        form_signature.person = user.profile
        form_signature.save()
        queryset = viewset.get_queryset()
        assert set(queryset) == {form_signature}

        user.is_superuser = True
        user.save()
        request.user = user
        viewset = ComplianceFormSignatureModelViewSet(request=request)
        queryset = viewset.get_queryset()
        assert set(queryset) == {form_signature, form_signature2}
