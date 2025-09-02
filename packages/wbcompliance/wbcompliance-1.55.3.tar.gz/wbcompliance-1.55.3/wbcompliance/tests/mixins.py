import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from faker import Faker
from wbcore.contrib.authentication.factories import InternalUserFactory

fake = Faker()
User = get_user_model()


class UserTestMixin:
    @pytest.fixture()
    def user(self):
        user = InternalUserFactory.create()
        group = Group.objects.create(name="Compliance Position")
        user.groups.add(group)
        return user
