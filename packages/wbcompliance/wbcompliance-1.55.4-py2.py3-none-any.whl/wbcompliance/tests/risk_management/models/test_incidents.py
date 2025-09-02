from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from faker import Faker
from guardian.shortcuts import assign_perm
from guardian.utils import get_anonymous_user
from pandas.tseries.offsets import BDay

from wbcompliance.models.risk_management.incidents import (
    RiskIncident,
    resolve_all_incidents_as_task,
)
from wbcompliance.models.risk_management.rules import RiskRule

User = get_user_model()

fake = Faker()


@pytest.mark.django_db
class TestRiskIncidentFactory:
    def test_init(self, risk_incident):
        assert risk_incident.computed_str

    def test_closing_incident(self, risk_incident, checked_object_incident_relationship_factory):
        checked_object_incident_relationship_factory.create(incident=risk_incident)
        assert risk_incident.checked_object_relationships.filter(status=RiskIncident.Status.OPEN).exists()
        risk_incident.status = RiskIncident.Status.CLOSED
        risk_incident.save()
        assert not risk_incident.checked_object_relationships.filter(status=RiskIncident.Status.OPEN).exists()

    def test_incident_date_range(
        self,
        risk_incident,
        checked_object_incident_relationship_factory,
        risk_check_factory,
        rule_checked_object_relationship_factory,
    ):
        rel1 = checked_object_incident_relationship_factory.create(incident=risk_incident)
        checked_object_relationship = rule_checked_object_relationship_factory.create(rule=risk_incident.rule)
        for i in range(7):
            next_date = (rel1.incident_date + BDay(i)).date()
            check = risk_check_factory.create(
                evaluation_date=next_date, rule_checked_object_relationship=checked_object_relationship
            )
            checked_object_incident_relationship_factory.create(incident=risk_incident, rule_check=check)
            risk_incident.refresh_from_db()
            assert risk_incident.date_range.upper == next_date + timedelta(days=1)
            assert RiskIncident.objects.count() == 1

    def test_incident_always_max_severity(
        self,
        risk_incident_factory,
        checked_object_incident_relationship_factory,
        risk_incident_type_factory,
    ):
        minor_severity = risk_incident_type_factory.create(severity_order=0)
        major_severity = risk_incident_type_factory.create(severity_order=1)
        critical_severity = risk_incident_type_factory.create(severity_order=2)

        incident = risk_incident_factory.create(severity=minor_severity)
        assert incident.severity == minor_severity

        checked_object_incident_relationship_factory.create(incident=incident, severity=minor_severity)
        incident.save()
        assert incident.severity == minor_severity

        checked_object_incident_relationship_factory.create(incident=incident, severity=major_severity)
        incident.save()
        assert incident.severity == major_severity

        incident.severity = critical_severity
        incident.save()
        assert incident.severity == critical_severity

    @pytest.mark.parametrize(
        "evaluation_date, is_breached_object",
        [
            (fake.date_object(), True),
            (fake.date_object(), False),
        ],
    )
    def test_get_or_create_incident(self, risk_rule, risk_incident_type, evaluation_date, is_breached_object):
        if is_breached_object:
            breached_object = get_anonymous_user()
            breached_object_repr = str(get_anonymous_user())
        else:
            breached_object = None
            breached_object_repr = fake.text(max_nb_chars=125)

        assert not RiskIncident.objects.exists()
        risk_rule.get_or_create_incident(evaluation_date, risk_incident_type, breached_object, breached_object_repr)
        if breached_object:
            assert (
                RiskIncident.objects.filter(
                    rule=risk_rule,
                    date_range__contains=evaluation_date,
                    breached_content_type=ContentType.objects.get_for_model(breached_object),
                    breached_object_id=breached_object.id,
                ).count()
                == 1
            )
        else:
            assert (
                RiskIncident.objects.filter(
                    rule=risk_rule, date_range__contains=evaluation_date, breached_object_repr=breached_object_repr
                ).count()
                == 1
            )
        assert RiskIncident.objects.count() == 1
        # Check if we reevaluate this incident one business day later, the incident is consider the same
        risk_rule.get_or_create_incident(
            (evaluation_date + BDay(1)).date(), risk_incident_type, breached_object, breached_object_repr
        )
        assert RiskIncident.objects.count() == 1

        # Check if we reevaluate this incident three business day later, the incident is consider the discontinue, and then a new incident is created
        risk_rule.get_or_create_incident(
            (evaluation_date + BDay(3)).date(), risk_incident_type, breached_object, breached_object_repr
        )

        assert RiskIncident.objects.count() == 2

    def test_get_or_create_incident_with_resolve_incident(
        self, risk_incident, checked_object_incident_relationship_factory
    ):
        subincident = checked_object_incident_relationship_factory.create(incident=risk_incident)
        assert risk_incident.status == RiskIncident.Status.OPEN
        risk_incident.resolve()
        risk_incident.save()
        assert risk_incident.status == RiskIncident.Status.RESOLVED
        new_evaluation_date = subincident.rule_check.evaluation_date + timedelta(days=1)
        incident, created = risk_incident.rule.get_or_create_incident(
            new_evaluation_date,
            subincident.severity,
            risk_incident.breached_content_object,
            risk_incident.breached_object_repr,
        )
        assert incident == risk_incident
        assert incident.date_range.upper == new_evaluation_date

    @pytest.mark.parametrize("incident_report", [fake.paragraph()])
    def test_update_or_create_relationship(
        self, risk_incident_factory, risk_check, incident_report, risk_incident_type
    ):
        risk_incident = risk_incident_factory.create(rule=risk_check.rule)
        assert not risk_incident.checked_object_relationships.exists()
        risk_incident.update_or_create_relationship(
            risk_check, incident_report, dict(), fake.pyfloat(), risk_incident_type
        )
        assert risk_incident.checked_object_relationships.filter(
            rule_check=risk_check, severity=risk_incident_type
        ).exists()

    @pytest.mark.parametrize(
        "incident_report, override_incident",
        [
            (fake.paragraph(), True),
            (fake.paragraph(), False),
        ],
    )
    def test_update_or_create_relationship_already_existing(
        self, risk_incident_factory, risk_check_factory, incident_report, risk_incident_type, override_incident
    ):
        check1 = risk_check_factory.create()
        check2 = risk_check_factory.create(
            rule=check1.rule,
            checked_object_id=check1.checked_object_id,
            checked_object_content_type=check1.checked_object_content_type,
            evaluation_date=check1.evaluation_date,
        )
        risk_incident = risk_incident_factory.create(rule=check1.rule)

        # We check the first time
        initial_breached_value = str(fake.pyfloat())
        risk_incident.update_or_create_relationship(
            check1, incident_report, dict(), initial_breached_value, risk_incident_type
        )
        # verify that the relationship was created
        assert risk_incident.checked_object_relationships.count() == 1
        assert (
            risk_incident.checked_object_relationships.filter(rule_check=check1, severity=risk_incident_type).count()
            == 1
        )

        # Closing incident because open incident are override by default
        risk_incident.status = RiskIncident.Status.CLOSED
        risk_incident.save()
        breached_value = str(fake.pyfloat())
        risk_incident.update_or_create_relationship(
            check2, incident_report, dict(), breached_value, risk_incident_type, override_incident
        )
        subincidents = risk_incident.checked_object_relationships.all()
        if not override_incident:
            assert subincidents.get(rule_check=check1).breached_value == initial_breached_value
            assert subincidents.get(rule_check=check2).breached_value == breached_value
        else:
            assert subincidents.get(rule_check=check1).breached_value == breached_value
            assert not subincidents.filter(rule_check=check2).exists()
        # asser the parent incident were reopened
        risk_incident.refresh_from_db()
        if not override_incident:
            assert risk_incident.status == RiskIncident.Status.OPEN
        else:
            assert risk_incident.status == RiskIncident.Status.CLOSED

        if not override_incident:
            risk_incident.status = RiskIncident.Status.CLOSED
            risk_incident.save()
            # we submit a new check the next day with the same breached value. We test if the parent incident remains close because of it
            check3 = risk_check_factory.create(
                rule=check1.rule,
                checked_object_id=check1.checked_object_id,
                checked_object_content_type=check1.checked_object_content_type,
                evaluation_date=check1.evaluation_date + timedelta(days=1),
            )
            risk_incident.update_or_create_relationship(
                check3, incident_report, dict(), breached_value, risk_incident_type
            )
            risk_incident.refresh_from_db()
            assert risk_incident.status == RiskIncident.Status.CLOSED
            assert (
                subincidents.get(rule_check=check3, breached_value=breached_value).status == RiskIncident.Status.CLOSED
            )

    @patch.object(RiskIncident, "resolve_all_incidents")
    @pytest.mark.parametrize("reviewer_comment", [(fake.paragraph())])
    def test_resolve_all_incidents_as_task(self, mock_function, risk_incident, user, reviewer_comment):
        resolve_all_incidents_as_task(user.id, reviewer_comment, risk_incident.id)
        assert mock_function.call_count == 1

    @pytest.mark.parametrize(
        "is_superuser, is_admin",
        [
            (True, True),
            (False, True),
            (False, False),
            (True, False),
            (False, False),
        ],
    )
    def test_can_manage_without_incident(self, user, is_superuser, is_admin):
        if is_superuser:
            user.is_superuser = True
            user.save()
        if is_admin:
            admin_perm = Permission.objects.get(codename="administrate_riskrule")
            user.user_permissions.add(admin_perm)
        res = RiskIncident.can_manage(user)
        assert res == (is_admin or is_superuser)

    def test_can_manage_with_incident(self, user, risk_incident):
        assert not RiskIncident.can_manage(user, risk_incident.rule)
        assign_perm(RiskRule.change_perm_str, user, risk_incident.rule)
        assert RiskIncident.can_manage(user, risk_incident.rule)

    @pytest.mark.parametrize("risk_rule__automatically_close_incident", [True, False])
    def test_post_workflow_change_status(self, risk_incident_factory, risk_rule):
        risk_incident = risk_incident_factory.create(rule=risk_rule)
        assert not risk_incident.status == RiskIncident.Status.CLOSED
        risk_incident.post_workflow()
        assert (
            risk_incident.status == RiskIncident.Status.CLOSED
            if risk_incident.rule.automatically_close_incident
            else RiskIncident.Status.OPEN
        )

    def test_post_workflow_elevate_incident(self, risk_incident, rule_threshold_factory):
        current_threshold = risk_incident.threshold
        current_threshold.upgradable_after_days = risk_incident.business_days - 1
        current_threshold.save()
        next_threshold_1 = rule_threshold_factory.create(
            rule=risk_incident.rule, upgradable_after_days=risk_incident.business_days - 1
        )
        assert next_threshold_1.severity.severity_order == 1
        next_threshold_2 = rule_threshold_factory.create(rule=risk_incident.rule)
        assert next_threshold_2.severity.severity_order == 2
        assert risk_incident.threshold == current_threshold
        risk_incident.post_workflow()
        assert risk_incident.threshold == next_threshold_1
        risk_incident.post_workflow()
        assert risk_incident.threshold == next_threshold_2
        risk_incident.post_workflow()
        assert risk_incident.threshold == next_threshold_2


@pytest.mark.django_db
class TestCheckedObjectIncidentRelationshipFactory:
    def test_init(self, rule_checked_object_relationship):
        assert rule_checked_object_relationship

    def test_init_checked_object_not_valid(
        self,
        checked_object_incident_relationship_factory,
        rule_checked_object_relationship_factory,
        risk_incident_factory,
        risk_check_factory,
    ):
        rel_user = rule_checked_object_relationship_factory.create()
        rel_other = rule_checked_object_relationship_factory.create(
            checked_object_content_type=ContentType.objects.get_for_model(rel_user)
        )

        incident = risk_incident_factory.create(rule=rel_user.rule)
        check = risk_check_factory.create(rule_checked_object_relationship=rel_other)
        with pytest.raises(ValidationError):
            checked_rel = checked_object_incident_relationship_factory.create(incident=incident, rule_check=check)
            checked_rel.full_clean()

    def test_init_backend_allowed_content_type_not_valid(
        self,
        checked_object_incident_relationship_factory,
        rule_checked_object_relationship_factory,
        risk_incident_factory,
    ):
        rel_user = rule_checked_object_relationship_factory.create()
        rel_user.rule.rule_backend.allowed_checked_object_content_type = ContentType.objects.get_for_model(rel_user)
        rel_user.rule.rule_backend.save()
        incident = risk_incident_factory.create(rule=rel_user.rule)
        with pytest.raises(ValidationError):
            checked_rel = checked_object_incident_relationship_factory.create(incident=incident)
            checked_rel.full_clean()

    def test_checked_object(self, checked_object_incident_relationship):
        assert checked_object_incident_relationship.checked_object
        assert (
            checked_object_incident_relationship.checked_object
            == checked_object_incident_relationship.rule_check.checked_object
        )
