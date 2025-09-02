from datetime import date

import pytest
from dateutil.relativedelta import relativedelta
from rest_framework import status
from rest_framework.test import APIRequestFactory
from wbcore.test.utils import (
    get_data_from_factory,
    get_kwargs,
    get_model_factory,
    get_or_create_superuser,
)

from wbcompliance.viewsets import ComplianceFormModelViewSet

from .mixins import UserTestMixin


@pytest.mark.django_db
class TestSpecificSerializers(UserTestMixin):
    @pytest.mark.parametrize("mvs", [ComplianceFormModelViewSet])
    def test_update_compliance_form_model_serializer(self, mvs, user):
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        obj = factory(assigned_to=(user.groups.first(),))
        user = get_or_create_superuser()

        data = get_data_from_factory(obj, mvs, update=True, superuser=user)
        request = APIRequestFactory().put("", data)
        request.user = user

        kwargs = get_kwargs(obj, mvs, request)
        vs = mvs.as_view({"put": "update"})
        response = vs(request, **kwargs, pk=obj.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("instance")

    @pytest.mark.parametrize("mvs", [ComplianceFormModelViewSet])
    def test_validate_date_compliance_form(self, mvs):
        user = get_or_create_superuser()
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        now = date.today()
        obj = factory(start=now, end=now - relativedelta(months=+5))
        data = get_data_from_factory(obj, mvs, update=True, superuser=user)
        request = APIRequestFactory().post("", data)
        request.user = user
        kwargs = get_kwargs(obj, mvs, request)
        vs = mvs.as_view({"post": "create"})
        response = vs(request, **kwargs)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
