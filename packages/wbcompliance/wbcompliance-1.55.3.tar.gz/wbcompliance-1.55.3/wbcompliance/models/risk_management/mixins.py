from datetime import date
from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.utils.functional import cached_property

from .checks import RiskCheck, evaluate_as_task
from .rules import RiskRule


class RiskCheckMixin(models.Model):
    """
    A utility mixin to inherit from when a model proposes a risk check workflow on one of its field
    """

    id: int

    @property
    def checked_object(self) -> Any:
        raise NotImplementedError()

    @property
    def check_evaluation_date(self) -> Any:
        raise NotImplementedError()

    @cached_property
    def checked_object_content_type(self) -> ContentType:
        return ContentType.objects.get_for_model(self.checked_object)

    @cached_property
    def activator_id(self) -> int:
        return self.id

    @cached_property
    def activator_content_type(self) -> ContentType:
        return ContentType.objects.get_for_model(self)

    @property
    def checks(self) -> models.QuerySet[RiskCheck]:
        """
        Returned the check triggered by this object (self)
        Returns: A queryset of RiskCheck
        """
        return RiskCheck.all_objects.filter(
            activator_id=self.activator_id,
            activator_content_type=self.activator_content_type,
            checked_object_content_type=self.checked_object_content_type,
            checked_object_id=self.checked_object.id,
            evaluation_date=self.check_evaluation_date,
        )

    @property
    def has_non_successful_checks(self) -> bool:
        """
        Return True if checks are available and they all succeed
        """
        return (
            self.checks.exists()
            and self.checks.exclude(status__in=[RiskCheck.CheckStatus.SUCCESS, RiskCheck.CheckStatus.WARNING]).exists()
        )

    @property
    def has_all_check_completed(self) -> bool:
        """
        Return True if checks are available and they all succeed
        """
        return (
            self.checks.exists()
            and not self.checks.filter(
                status__in=[RiskCheck.CheckStatus.RUNNING, RiskCheck.CheckStatus.PENDING]
            ).exists()
        )

    def get_worst_check_status(self) -> RiskCheck.CheckStatus:
        status_ordered = [
            RiskCheck.CheckStatus.FAILED,
            RiskCheck.CheckStatus.WARNING,
            RiskCheck.CheckStatus.RUNNING,
            RiskCheck.CheckStatus.PENDING,
        ]
        for status in status_ordered:
            if self.checks.filter(status=status).exists():
                return status
        return RiskCheck.CheckStatus.SUCCESS

    def evaluate_active_rules(self, evaluation_date: date, *dto, asynchronously: bool = True):
        for rule in RiskRule.objects.get_active_rules_for_object(self.checked_object):
            check = RiskCheck.all_objects.update_or_create(
                rule=rule,
                evaluation_date=evaluation_date,
                checked_object_content_type=self.checked_object_content_type,
                checked_object_id=self.checked_object.id,
                activator_id=self.activator_id,
                activator_content_type=self.activator_content_type,
                defaults={"status": RiskCheck.CheckStatus.PENDING},
            )[0]
            if asynchronously:
                transaction.on_commit(
                    lambda: evaluate_as_task.delay(
                        check.id, *dto, override_incident=True, ignore_informational_threshold=True
                    )
                )
            else:
                check.evaluate(*dto, override_incident=True, ignore_informational_threshold=True)

    class Meta:
        abstract = True
