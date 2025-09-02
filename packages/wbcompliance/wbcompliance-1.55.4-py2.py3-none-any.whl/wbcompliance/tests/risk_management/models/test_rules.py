import random
from datetime import date, timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from faker import Faker
from guardian.utils import get_anonymous_user
from psycopg.types.range import NumericRange
from wbcore.permissions.utils import perm_to_permission

from wbcompliance.models import (
    RiskIncident,
    RiskRule,
    RuleCheckedObjectRelationship,
    RuleThreshold,
)
from wbcompliance.models.risk_management.rules import process_rule_as_task

fake = Faker()


@pytest.mark.django_db
class TestRuleCheckedObjectRelationship:
    def test_init(self, rule_checked_object_relationship):
        assert rule_checked_object_relationship

    def test_init_wrong_content_type(self, risk_rule, rule_checked_object_relationship_factory):
        risk_rule.rule_backend.allowed_checked_object_content_type = ContentType.objects.get_for_model(RuleThreshold)
        risk_rule.rule_backend.save()
        with pytest.raises(ValidationError):
            rule_checked_object_relationship_factory.create(
                rule=risk_rule,
                checked_object_content_type=ContentType.objects.get_for_model(RuleCheckedObjectRelationship),
            )


@pytest.mark.django_db
class TestRuleBackend:
    def test_init(self, rule_backend):
        assert rule_backend

    def test_backend_class(self, rule_backend):
        assert rule_backend.backend_class.__module__
        assert rule_backend.backend_class.__class__

    @pytest.mark.parametrize("evaluation_date", [fake.date_object()])
    def test_backend(self, rule_backend, risk_rule, evaluation_date):
        assert rule_backend.backend(evaluation_date, risk_rule, risk_rule.parameters, RuleThreshold.objects.none())


@pytest.mark.django_db
class TestRuleThreshold:
    def test_init(self, rule_threshold):
        assert rule_threshold

    @pytest.mark.parametrize(
        "lower,upper,value,result",
        [
            (0, 1, random.random(), True),
            (1, 2, random.random(), False),
            (-1, 0, random.random(), False),
            (None, 1, random.random(), True),
            (0, None, random.random(), True),
        ],
    )
    def test_is_inrange(self, rule_threshold_factory, lower, upper, value, result):
        threshold = rule_threshold_factory.create(range=NumericRange(lower=lower, upper=upper))
        assert threshold.is_inrange(value) == result

    def test_get_notifiable_users(self, rule_threshold, user_factory):
        assert not rule_threshold.get_notifiable_users().exists()
        user = user_factory.create()
        user_group = user_factory.create()
        group_test = Group.objects.create(name="test")
        user_group.groups.add(group_test)
        rule_threshold.notifiable_users.add(user.profile)  # Add user to threshold person group
        rule_threshold.notifiable_groups.add(group_test)  # Add user to threshold group
        users = rule_threshold.get_notifiable_users()
        assert set(users.values_list("id", flat=True)) == {user.id, user_group.id}


@pytest.mark.django_db
class TestRiskRule:
    def test_init(self, risk_rule):
        assert risk_rule

    def test_checked_objects(self, risk_rule_factory, rule_threshold_factory):
        rule = risk_rule_factory.create()
        other_rule = risk_rule_factory.create()
        threshold1 = rule_threshold_factory.create()
        threshold2 = rule_threshold_factory.create()
        RuleCheckedObjectRelationship.objects.create(checked_object=threshold1, rule=rule)
        RuleCheckedObjectRelationship.objects.create(checked_object=get_anonymous_user(), rule=rule)
        RuleCheckedObjectRelationship.objects.create(checked_object=threshold2, rule=other_rule)
        assert set(rule.checked_objects) == {threshold1, get_anonymous_user()}

    def test_checks(self, risk_rule_factory, rule_checked_object_relationship_factory, risk_check_factory):
        rule = risk_rule_factory.create()
        other_rule = risk_rule_factory.create()
        rel1 = rule_checked_object_relationship_factory.create(rule=rule)
        rel2 = rule_checked_object_relationship_factory.create(rule=rule)
        other_rel = rule_checked_object_relationship_factory.create(rule=other_rule)
        check1 = risk_check_factory.create(rule_checked_object_relationship=rel1)
        check2 = risk_check_factory.create(rule_checked_object_relationship=rel2)
        risk_check_factory.create(rule_checked_object_relationship=other_rel)
        assert set(rule.checks.values_list("id", flat=True)) == {check1.id, check2.id}

    @pytest.mark.parametrize(
        "risk_rule__automatically_close_incident, evaluation_date, expected_incident_status",
        [
            (True, fake.date_object(), RiskIncident.Status.CLOSED),
            (False, fake.date_object(), RiskIncident.Status.OPEN),
        ],
    )
    def test_process_rule(
        self,
        risk_rule,
        rule_checked_object_relationship_factory,
        rule_threshold_factory,
        evaluation_date,
        expected_incident_status,
    ):
        rule_threshold_factory.create(rule=risk_rule)
        rule_checked_object_relationship_factory.create(rule=risk_rule)

        risk_rule.process_rule(evaluation_date)
        incident = RiskIncident.objects.get(rule=risk_rule, status=expected_incident_status)
        assert incident.checked_object_relationships.count() == 1

    def test_get_permissions_for_user(self, risk_rule, user_factory):
        user_with_permission = user_factory.create()
        user_without_permission = user_factory.create()
        user_with_permission.user_permissions.add(perm_to_permission(RiskRule.view_perm_str))
        assert risk_rule.get_permissions_for_user(user_with_permission)[RiskRule.view_perm_str] is False
        assert not risk_rule.get_permissions_for_user(user_without_permission)

    def test_get_rules_for_object(self, risk_rule_factory, rule_checked_object_relationship_factory):
        rule1 = risk_rule_factory.create()
        rule2 = risk_rule_factory.create()

        rule_checked_object_relationship_factory.create(rule=rule1)
        rule_checked_object_relationship_factory.create(rule=rule2)

        res = RiskRule.get_rules_for_object(get_anonymous_user())
        assert res.exists()
        assert set(res.values_list("id", flat=True)) == {rule1.id, rule2.id}

    @patch.object(RiskRule, "process_rule")
    @pytest.mark.parametrize(
        "evaluation_date, override_incident",
        [(fake.date_object(), fake.pybool())],
    )
    def test_process_rule_as_task(self, mock_function, risk_rule, evaluation_date, override_incident):
        process_rule_as_task(risk_rule.id, evaluation_date, override_incident)
        assert mock_function.call_count == 1

    @patch("wbcompliance.models.risk_management.rules.send_notification")
    def test_do_not_notify_no_open_incidents(
        self,
        mock_fct,
        risk_incident_factory,
        rule_checked_object_relationship,
        risk_check_factory,
        checked_object_incident_relationship_factory,
    ):
        risk_rule = rule_checked_object_relationship.rule
        risk_incident = risk_incident_factory.create(rule=risk_rule)
        sub_incident = checked_object_incident_relationship_factory.create(incident=risk_incident)

        incident_date = sub_incident.incident_date
        risk_rule.notify(incident_date)
        assert mock_fct.call_count == 1

        risk_incident.refresh_from_db()
        assert risk_incident.is_notified is True

        # renotifying this incident still triggers the method because the incident (even marked as notified) is still open
        risk_rule.notify(incident_date)
        assert mock_fct.call_count == 2

        risk_incident.ignore()
        risk_incident.save()
        risk_rule.notify(incident_date)
        assert mock_fct.call_count == 2

        tomorrow = incident_date + timedelta(days=1)
        tomorrow_risk_check = risk_check_factory.create(
            rule_checked_object_relationship=rule_checked_object_relationship, evaluation_date=tomorrow
        )
        tomorrow_sub_incident = checked_object_incident_relationship_factory.create(  # noqa
            rule_check=tomorrow_risk_check, incident=risk_incident
        )

        risk_incident.refresh_from_db()
        assert risk_incident.status == RiskIncident.Status.OPEN
        # the incident was already notified and is closed, so another subincident will mark the incident as open and retrigger notification
        risk_rule.notify(tomorrow)
        assert mock_fct.call_count == 3

        after_tomorrow = tomorrow + timedelta(days=1)
        risk_incident.ignore()
        risk_incident.last_ignored_date = tomorrow
        risk_incident.ignore_duration = timedelta(days=1)
        risk_incident.save()

        # this shoudn't reopen the incident
        after_tomorrow_risk_check = risk_check_factory.create(
            rule_checked_object_relationship=rule_checked_object_relationship, evaluation_date=after_tomorrow
        )
        after_tomorrow_sub_incident = checked_object_incident_relationship_factory.create(  # noqa
            rule_check=after_tomorrow_risk_check, incident=risk_incident
        )
        risk_incident.refresh_from_db()
        assert risk_incident.status == RiskIncident.Status.IGNORED
        # then notify shouldn't happen
        risk_rule.notify(after_tomorrow)
        assert mock_fct.call_count == 3

    def test_is_evaluation_date_valid(self, risk_rule):
        risk_rule.activation_date = None
        risk_rule.save()
        assert risk_rule.is_evaluation_date_valid(fake.date_object()) is False

        activation_date = fake.date_object()
        risk_rule.activation_date = activation_date
        risk_rule.save()
        assert (
            risk_rule.is_evaluation_date_valid(
                fake.date_between(activation_date, activation_date + timedelta(days=365))
            )
            is True
        )
        assert (
            risk_rule.is_evaluation_date_valid(
                fake.date_between(activation_date - timedelta(days=365), activation_date - timedelta(days=1))
            )
            is False
        )

        # enable a rule to be checked every week on monday (i.e. every monday)
        activation_date = date(2024, 11, 25)  # Monday
        risk_rule.activation_date = activation_date
        risk_rule.frequency = "RRULE:FREQ=WEEKLY"
        risk_rule.save()

        assert risk_rule.is_evaluation_date_valid(date(2024, 11, 25)) is True
        assert risk_rule.is_evaluation_date_valid(date(2024, 11, 26)) is False
        assert risk_rule.is_evaluation_date_valid(date(2024, 11, 27)) is False
        assert risk_rule.is_evaluation_date_valid(date(2024, 11, 28)) is False
        assert risk_rule.is_evaluation_date_valid(date(2024, 11, 29)) is False
        assert risk_rule.is_evaluation_date_valid(date(2024, 11, 30)) is False
        assert risk_rule.is_evaluation_date_valid(date(2024, 12, 1)) is False
        assert risk_rule.is_evaluation_date_valid(date(2024, 12, 2)) is True
