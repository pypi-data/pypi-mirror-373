from datetime import timedelta

import factory
from faker import Faker
from psycopg.types.range import DateRange

from wbcompliance.models.risk_management import (
    CheckedObjectIncidentRelationship,
    RiskIncident,
    RiskIncidentType,
)

from .checks import RiskCheckFactory
from .rules import RuleCheckedObjectRelationshipFactory

fake = Faker()


def _generate_date_range():
    d1 = fake.date_object()
    return DateRange(lower=d1, upper=d1 + timedelta(days=fake.pyint(min_value=1, max_value=100)))


def _extract_date_range_from_incident(incident):
    return fake.date_between_dates(incident.date_range.lower, incident.date_range.upper)


class RiskIncidentMixinFactory:
    status = RiskIncident.Status.OPEN.value
    comment = factory.Faker("paragraph")
    resolved_by = factory.SubFactory("wbcore.contrib.authentication.factories.AuthenticatedPersonFactory")


def get_severity_order(o):
    types = RiskIncidentType.objects.all()
    if types.exists():
        return types.last().severity_order + 1
    return 0


def _get_severity(o):
    if o.rule.thresholds.exists():
        return o.rule.thresholds.first().severity
    return RiskIncidentTypeFactory.create()


class RiskIncidentTypeFactory(factory.django.DjangoModelFactory):
    name = "LOW"
    severity_order = factory.LazyAttribute(lambda o: get_severity_order(o))
    is_ignorable = True
    is_automatically_closed = False
    is_informational = False

    class Meta:
        model = RiskIncidentType


class RiskIncidentFactory(RiskIncidentMixinFactory, factory.django.DjangoModelFactory):
    rule = factory.SubFactory("wbcompliance.factories.risk_management.rules.RiskRuleFactory")
    severity = factory.LazyAttribute(lambda x: x.rule.thresholds.first().severity)
    date_range = factory.LazyAttribute(lambda o: _generate_date_range())

    breached_content_type = None
    breached_object_id = None
    breached_object_repr = factory.Faker("text", max_nb_chars=32)

    class Meta:
        model = RiskIncident


def _create_risk_check(incident):
    rel = RuleCheckedObjectRelationshipFactory.create(rule=incident.rule)
    return RiskCheckFactory.create(
        rule=rel.rule,
        checked_object_content_type=rel.checked_object_content_type,
        checked_object_id=rel.checked_object_id,
    )


class CheckedObjectIncidentRelationshipFactory(RiskIncidentMixinFactory, factory.django.DjangoModelFactory):
    severity = factory.LazyAttribute(lambda x: x.incident.rule.thresholds.first().severity)
    rule_check = factory.LazyAttribute(lambda x: _create_risk_check(x.incident))
    incident = factory.SubFactory("wbcompliance.factories.risk_management.incidents.RiskIncidentFactory")
    # rule_check = factory.SubFactory("wbcompliance.factories.risk_management.checks.RiskCheckFactory")
    report = factory.Faker("paragraph")
    report_details = factory.LazyAttribute(lambda x: dict(a="b"))

    class Meta:
        model = CheckedObjectIncidentRelationship
