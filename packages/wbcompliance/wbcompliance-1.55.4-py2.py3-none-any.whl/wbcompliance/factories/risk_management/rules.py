import json
import random
from datetime import date

import factory
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from faker import Faker
from guardian.utils import get_anonymous_user
from psycopg.types.range import NumericRange
from wbcore.contrib.authentication.factories import UserFactory

from wbcompliance.models.risk_management.rules import (
    RiskRule,
    RuleBackend,
    RuleCheckedObjectRelationship,
    RuleThreshold,
)

fake = Faker()


class RuleBackendFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    backend_class_path = "wbcompliance.factories.risk_management.backends"
    backend_class_name = "RuleBackend"
    allowed_checked_object_content_type = None

    class Meta:
        model = RuleBackend


def _get_default_parameter():
    return json.loads(
        json.dumps(
            {
                "date": fake.date_object(),
                "name": fake.name(),
                "int": fake.pyint(),
                "anonymous_user": get_anonymous_user().id,
            },
            cls=DjangoJSONEncoder,
        )
    )


class RiskRuleFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    description = factory.Faker("paragraph")
    rule_backend = factory.SubFactory("wbcompliance.factories.risk_management.RuleBackendFactory")
    is_enable = True
    only_passive_check_allowed = True
    is_silent = False
    is_mandatory = True
    automatically_close_incident = False
    parameters = factory.LazyAttribute(lambda x: _get_default_parameter())
    activation_date = date.min

    @factory.post_generation
    def threshold(self, create, extracted, **kwargs):
        if not RuleThreshold.objects.filter(rule=self).exists():
            RuleThresholdFactory.create(rule=self, notifiable_users=[UserFactory.create().profile])

    class Meta:
        model = RiskRule


class RuleThresholdFactory(factory.django.DjangoModelFactory):
    rule = factory.SubFactory("wbcompliance.factories.risk_management.RiskRuleFactory")
    range = factory.LazyAttribute(lambda o: NumericRange(lower=random.uniform(0, 0.5), upper=random.uniform(0.5, 1)))
    severity = factory.SubFactory("wbcompliance.factories.risk_management.incidents.RiskIncidentTypeFactory")

    @factory.post_generation
    def notifiable_users(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for person in extracted:
                self.notifiable_users.add(person)

    @factory.post_generation
    def notifiable_groups(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for group in extracted:
                self.notifiable_groups.add(group)

    class Meta:
        model = RuleThreshold


class RuleCheckedObjectRelationshipFactory(factory.django.DjangoModelFactory):
    rule = factory.SubFactory("wbcompliance.factories.risk_management.RiskRuleFactory")
    checked_object_content_type = factory.LazyAttribute(lambda o: ContentType.objects.get_for_model(get_user_model()))
    checked_object_id = 1

    class Meta:
        model = RuleCheckedObjectRelationship
        django_get_or_create = ["rule", "checked_object_content_type", "checked_object_id"]
