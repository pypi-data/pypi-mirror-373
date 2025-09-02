from datetime import timedelta

import pandas as pd
import pytest
from faker import Faker
from pandas.tseries.offsets import BDay

fake = Faker()


@pytest.mark.django_db
class TestChecks:
    def test_init(self, risk_check):
        assert risk_check

    @pytest.mark.parametrize("evaluation_date", [fake.date_object()])
    def test_previous_check(self, risk_rule, risk_check_factory, rule_checked_object_relationship, evaluation_date):
        check1 = risk_check_factory.create(
            rule_checked_object_relationship=rule_checked_object_relationship, evaluation_date=evaluation_date
        )
        assert not check1.previous_check
        check2 = risk_check_factory.create(
            rule_checked_object_relationship=rule_checked_object_relationship, evaluation_date=evaluation_date
        )
        check3 = risk_check_factory.create(
            rule_checked_object_relationship=rule_checked_object_relationship,
            evaluation_date=evaluation_date + timedelta(days=1),
        )

        assert check2.previous_check is None
        assert check3.previous_check == check2
        # Shouldn't include this check in the queryset
        other_check = risk_check_factory.create(
            rule_checked_object_relationship=rule_checked_object_relationship,
            evaluation_date=evaluation_date + timedelta(days=1),
        )
        assert other_check.previous_check == check2

    def test_get_unchecked_dates(
        self, weekday, risk_rule, risk_check_factory, rule_checked_object_relationship_factory
    ):
        rel = rule_checked_object_relationship_factory.create(rule=risk_rule)
        maximum_day_interval = 10
        assert list(rel.get_unchecked_dates(to_date=weekday, maximum_day_interval=maximum_day_interval)) == list(
            map(lambda _d: _d.date(), pd.date_range(weekday - timedelta(days=maximum_day_interval), weekday, freq="B"))
        )
        risk_check = risk_check_factory.create(rule_checked_object_relationship=rel, evaluation_date=weekday)

        assert list(rel.get_unchecked_dates()) == [(risk_check.evaluation_date + BDay(1)).date()]
        assert list(rel.get_unchecked_dates(to_date=risk_check.evaluation_date)) == list()

        risk_check2 = risk_check_factory.create(
            rule_checked_object_relationship=rel, evaluation_date=risk_check.evaluation_date + BDay(1)
        )
        assert list(rel.get_unchecked_dates()) == [(risk_check2.evaluation_date + BDay(1)).date()]
