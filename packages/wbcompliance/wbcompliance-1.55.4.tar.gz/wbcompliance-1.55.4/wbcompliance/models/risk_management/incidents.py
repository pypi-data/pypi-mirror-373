from datetime import date, timedelta
from typing import TYPE_CHECKING, Any, Optional

import pandas as pd
from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as BaseUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import DateRangeField
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Value
from django.db.models.functions import TruncDate
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _
from django_fsm import FSMField, transition
from guardian.core import ObjectPermissionChecker
from psycopg.types.range import DateRange
from wbcore.content_type.utils import get_ancestors_content_type
from wbcore.contrib.color.enums import WBColor
from wbcore.contrib.directory.models import Person
from wbcore.contrib.icons import WBIcon
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.enums import RequestType
from wbcore.metadata.configs.buttons import ActionButton, ButtonDefaultColor
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)
from wbcore.models import WBModel
from wbcore.utils.models import ComplexToStringMixin

User: BaseUser = get_user_model()

if TYPE_CHECKING:
    from wbcompliance.models import RiskCheck


class RiskIncidentType(models.Model):
    name = models.CharField(max_length=128)
    severity_order = models.PositiveIntegerField(default=0, unique=True)

    color = models.CharField(max_length=20, verbose_name=_("Color"), default=WBColor.YELLOW_LIGHT.value)
    is_ignorable = models.BooleanField(default=True, verbose_name=_("Can be ignored"))
    is_automatically_closed = models.BooleanField(default=False, verbose_name=_("Automatically closed"))
    is_informational = models.BooleanField(
        default=False,
        verbose_name=_("Only Informational"),
        help_text=_("If true, the associated rule is not considered an incident"),
    )

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if (
            self.pk
            and RiskIncidentType.objects.exclude(id=self.pk).filter(severity_order=self.severity_order).exists()
        ):
            self.severity_order += 1
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("severity_order",)
        verbose_name = "Risk Incident Type"
        verbose_name_plural = "Risk Incidents Type"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcompliance:riskincidenttyperepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{name}}"


class RiskIncidentMixin(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"  # Newly created incidents
        RESOLVED = "RESOLVED", "Resolved"
        IGNORED = "IGNORED", "Ignored"
        CLOSED = "CLOSED", "Closed"

    severity = models.ForeignKey(
        "wbcompliance.RiskIncidentType",
        on_delete=models.CASCADE,
        verbose_name=_("Severity"),
        related_name="%(class)s",
    )
    comment = models.TextField(blank=True, null=True, verbose_name=_("Comment"))

    resolved_by = models.ForeignKey(
        "directory.Person",
        on_delete=models.SET_NULL,
        verbose_name=_("Handled by"),
        help_text=_("The person that resolved or ignored this incident"),
        related_name="%(class)s_handled",
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True


class CheckedObjectIncidentRelationship(ComplexToStringMixin, RiskIncidentMixin, WBModel):
    incident = models.ForeignKey(
        to="wbcompliance.RiskIncident",
        related_name="checked_object_relationships",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    rule_check = models.ForeignKey(
        "wbcompliance.RiskCheck",
        on_delete=models.CASCADE,
        verbose_name=_("Check"),
        help_text=_("The check that opened this incident"),
        related_name="incidents",
    )
    breached_value = models.CharField(
        blank=True,
        null=True,
        verbose_name=_("Breached Value"),
        max_length=128,
        help_text="The value that breached the rule threshold, can be None",
    )

    report = models.TextField(blank=True, null=True, verbose_name=_("Report"))
    report_details = models.JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)

    # A user can mark an incident as resolved, if the necessary actions were taken
    status = FSMField(
        default=RiskIncidentMixin.Status.OPEN, choices=RiskIncidentMixin.Status.choices, verbose_name=_("Status")
    )

    @transition(
        status,
        [RiskIncidentMixin.Status.OPEN],
        RiskIncidentMixin.Status.RESOLVED,
        permission=lambda instance, user: RiskIncident.can_manage(user, instance.rule),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcompliance:riskincident",),
                icon=WBIcon.APPROVE.icon,
                color=ButtonDefaultColor.SUCCESS,
                key="resolve",
                label=_("Resolve"),
                action_label=_("Resolve"),
                description_fields=_("<p>Are you sure you want to resolve the incident {{computed_str}}"),
                instance_display=create_simple_display([["comment"]]),
            )
        },
    )
    def resolve(self, by=None, **kwargs):
        if by:
            self.resolved_by = by.profile

    @transition(
        status,
        [RiskIncidentMixin.Status.OPEN],
        RiskIncidentMixin.Status.IGNORED,
        permission=lambda instance, user: RiskIncident.can_manage(user, instance.rule),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcompliance:riskincident",),
                icon=WBIcon.IGNORE.icon,
                color=ButtonDefaultColor.WARNING,
                key="ignore",
                label=_("Ignore"),
                action_label=_("Ignore"),
                description_fields=_("<p>Are you sure you want to ignore the incident {{computed_str}}"),
                instance_display=create_simple_display([["severity"], ["comment"]]),
            )
        },
    )
    def ignore(self, by=None, **kwargs):
        if by:
            self.resolved_by = by.profile

    def can_ignore(self):
        if not self.severity.is_ignorable:
            return {"severity": [_("Incident type {} is not ignorable").format(self.severity)]}
        return dict()

    @property
    def incident_date(self) -> date:
        return self.rule_check.evaluation_date

    @property
    def rule(self) -> Any:
        if self.incident:
            return self.incident.rule
        return self.rule_check.rule

    @property
    def checked_object(self) -> models.Model:
        return self.rule_check.checked_object

    def clean(self):
        allowed_checked_object_content_type = self.rule.rule_backend.allowed_checked_object_content_type
        if not self.checked_object:
            raise ValidationError("Checked Object cannot be null")
        checked_object_content_type = ContentType.objects.get_for_model(self.checked_object)
        if allowed_checked_object_content_type and (
            allowed_checked_object_content_type not in list(get_ancestors_content_type(checked_object_content_type))
        ):
            raise ValidationError(
                _(
                    "The relationship content type ({}) needs to match the incident rule backend allowed content type ({})"
                ).format(self.checked_object, allowed_checked_object_content_type)
            )
        super().clean()

    class Meta:
        verbose_name = "Incident to Checked Object relationship"
        verbose_name_plural = "Incident to Checked Object relationships"
        unique_together = ("incident", "rule_check")
        indexes = [
            models.Index(fields=["incident", "rule_check"]),
        ]

    def compute_str(self) -> str:
        return _("{} {} Sub Incident for checked_object {}").format(self.status, self.severity, self.rule_check)

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcompliance:checkedobjectincidentrelationshiprepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcompliance:checkedobjectincidentrelationship"


class RiskIncidentDefaultManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                ignore_until_time=models.F("last_ignored_date")
                + models.F("ignore_duration")
                + Value(timedelta(days=1)),
                ignore_until=TruncDate("ignore_until_time"),
            )
        )


class RiskIncident(ComplexToStringMixin, RiskIncidentMixin, WBModel):
    """
    Instance defining the incident that has happened during a check initiated by a certain rule
    """

    date_range = DateRangeField(blank=True, null=True, help_text=_("The incident spans date interval"))
    rule = models.ForeignKey(
        "wbcompliance.RiskRule",
        on_delete=models.CASCADE,
        verbose_name=_("Rule"),
        help_text=_("The rule that opened this incident"),
        related_name="incidents",
    )

    breached_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    breached_object_id = models.PositiveIntegerField(null=True, blank=True)
    breached_content_object = GenericForeignKey("breached_content_type", "breached_object_id")
    breached_object_repr = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name=_("Breached Object Representation"),
        help_text=_("String Representation of the breached object"),
    )

    status = FSMField(
        default=RiskIncidentMixin.Status.OPEN, choices=RiskIncidentMixin.Status.choices, verbose_name=_("Status")
    )
    is_notified = models.BooleanField(
        default=False, verbose_name=_("Notified"), help_text=_("True if the incident is already notified to the users")
    )

    last_ignored_date = models.DateField(blank=True, null=True)
    ignore_duration = models.DurationField(
        blank=True, null=True, help_text=_("If set, will ignore the forthcoming incidents for the specified duration")
    )

    def get_ignore_until_date(self) -> date | None:
        if self.last_ignored_date and self.ignore_duration:
            return self.last_ignored_date + self.ignore_duration

    @transition(
        status,
        [RiskIncidentMixin.Status.OPEN],
        RiskIncidentMixin.Status.RESOLVED,
        permission=lambda instance, user: RiskIncident.can_manage(user, instance.rule),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcompliance:riskincident",),
                icon=WBIcon.APPROVE.icon,
                color=ButtonDefaultColor.SUCCESS,
                key="resolve",
                label=_("Resolve"),
                action_label=_("Resolve"),
                description_fields=_(
                    "<p>Are you sure you want to resolve the incident {{computed_str}} and its relationships?"
                ),
                instance_display=create_simple_display([["comment"]]),
            )
        },
    )
    def resolve(self, by=None, **kwargs):
        if by:
            self.resolved_by = by.profile
            self.checked_object_relationships.filter(status=self.Status.OPEN).update(
                status=self.status, resolved_by=self.resolved_by
            )

    @transition(
        status,
        [RiskIncidentMixin.Status.OPEN],
        RiskIncidentMixin.Status.IGNORED,
        permission=lambda instance, user: RiskIncident.can_manage(user, instance.rule),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcompliance:riskincident",),
                icon=WBIcon.IGNORE.icon,
                color=ButtonDefaultColor.WARNING,
                key="ignore",
                label=_("Ignore"),
                action_label=_("Ignore"),
                description_fields=_(
                    "<p>Are you sure you want to ignore the incident {{computed_str}} and its relationships? If you set a days greater than 0, the forthcoming incident will be automatically ignore"
                ),
                instance_display=create_simple_display(
                    [["severity", "ignore_duration_in_days"], ["comment", "comment"]]
                ),
            )
        },
    )
    def ignore(self, by=None, **kwargs):
        if by:
            self.last_ignored_date = self.date_range.upper  # type: ignore
            self.resolved_by = by.profile
            self.checked_object_relationships.filter(status=self.Status.OPEN).update(
                status=self.status, resolved_by=self.resolved_by
            )

    def can_ignore(self):
        if not self.severity.is_ignorable:
            return {"severity": [_("Incident type {} is not ignorable").format(self.severity)]}
        return dict()

    objects = RiskIncidentDefaultManager()

    class Meta:
        verbose_name = "Risk Incident"
        verbose_name_plural = "Risk Incidents"

        notification_types = [
            create_notification_type(
                code="wbcompliance.riskincident.notify",
                title="Risk Incident Notification",
                help_text="Notifies you when an incident is triggered.",
                email=True,
                web=False,
                mobile=False,
                is_lock=True,
            )
        ]

    def save(self, *args, **kwargs):
        if not self.breached_object_repr:
            self.breached_object_repr = str(self.breached_content_object)

        if self.id and self.checked_object_relationships.exists():
            # If this global incident is closed, we close all opened incident relationships
            if self.status != self.Status.OPEN:
                self.checked_object_relationships.filter(status=self.Status.OPEN).update(status=self.status)

            existing_severity_orders = list(
                self.checked_object_relationships.values_list("severity__severity_order", flat=True)
            )
            self.severity = RiskIncidentType.objects.get(
                severity_order=max([self.severity.severity_order, *existing_severity_orders])
            )
            self.date_range = DateRange(
                lower=self.checked_object_relationships.earliest("rule_check__evaluation_date").incident_date,
                upper=self.checked_object_relationships.latest("rule_check__evaluation_date").incident_date
                + timedelta(days=1),
            )  # type: ignore
        super().save(*args, **kwargs)

    @property
    def date_range_lower_repr(self) -> str:
        return f"[{self.date_range.lower:%Y-%m-%d}" if self.date_range.lower else "]-∞"  # type: ignore

    @property
    def date_range_upper_repr(self) -> str:
        return f"{self.date_range.upper - timedelta(days=1):%Y-%m-%d}]" if self.date_range.upper else "+∞["  # type: ignore

    @property
    def automatically_close_incident(self) -> bool:
        return self.rule.automatically_close_incident or self.severity.is_automatically_closed

    def compute_str(self) -> str:
        if self.severity:
            return _("({}) {} Incident for breached object {} during {},{}").format(
                self.status,
                self.severity,
                self.breached_content_object,
                self.date_range_lower_repr,
                self.date_range_upper_repr,
            )
        return _("({}) Incident for breached object {} during {}").format(
            self.status, self.breached_content_object, self.date_range_lower_repr, self.date_range_upper_repr
        )

    def update_or_create_relationship(
        self,
        check: "RiskCheck",
        incident_report: str,
        incident_report_details: dict[str, Any],
        breached_value: str | None,
        incident_severity: "RiskIncidentType",
        override_incident: bool | None = False,
    ):
        # We assume that if the incident was not created and its status is other than opened, then it is a recheck and this incident was already handled.
        checked_object = check.checked_object
        similar_incidents_relationships = CheckedObjectIncidentRelationship.objects.filter(
            incident=self,
            rule_check__checked_object_content_type=ContentType.objects.get_for_model(checked_object),
            rule_check__checked_object_id=checked_object.id,
        ).distinct()
        defaults = {
            "report": incident_report,
            "report_details": incident_report_details,
            "breached_value": breached_value,
            "severity": incident_severity,
        }
        if self.rule.automatically_close_incident:
            defaults["status"] = RiskIncident.Status.CLOSED
        # if a previous check created an incident with the same breached value, we don't reopen it
        if override_incident or (
            (previous_check := check.previous_check)
            and similar_incidents_relationships.filter(rule_check=previous_check, breached_value=breached_value)
        ):
            defaults["status"] = self.status

        potential_existing_incidents_relationships = similar_incidents_relationships.filter(
            rule_check__evaluation_date=check.evaluation_date
        )
        if not potential_existing_incidents_relationships.exists() or not override_incident:
            rel, _ = CheckedObjectIncidentRelationship.objects.update_or_create(
                incident=self, rule_check=check, defaults=defaults
            )
            rel.full_clean()

        else:
            potential_existing_incidents_relationships.update(**defaults)

    @property
    def threshold(self) -> Any:
        return self.rule.thresholds.get(severity=self.severity)

    @property
    def notifiable(self) -> bool:
        """
        Property for wether the incident can fire notification
        Returns:
            True if the incident can fire notification
        """
        return not self.rule.is_silent and self.threshold.get_notifiable_users().exists()

    @property
    def business_days(self) -> int:
        """
        Property to get the number of days this incident span

        Returns:
            The number of business days
        """
        return len(pd.date_range(self.date_range.lower, self.date_range.upper, freq="B", inclusive="left"))  # type: ignore

    def post_workflow(self):
        """
        Post save method to check the extra mechanisms

        """

        # Check if the incident is automatically closed
        if self.automatically_close_incident:
            self.status = RiskIncident.Status.CLOSED
        # Check if the incident needs to be elevated
        if (
            (upgradable_after_days := self.threshold.upgradable_after_days)
            and (next_threshold := self.threshold.next_threshold)
            and (self.business_days > upgradable_after_days)
        ):
            self.severity = next_threshold.severity

        self.save()

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcompliance:riskincident"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcompliance:riskincidentrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def resolve_all_incidents(
        cls,
        resolved_by: "Person",
        reviewer_comment: str,
        is_resolved: Optional[bool] = True,
        rule_id: Optional[int] = None,
    ):
        """
        Utility methods to close all incidents that were created during an optional check and/or triggered by an optional rule
        Args:
            resolved_by: The user (Person) resolving all incidents.
            reviewer_comment: The resolver's comment.
            is_resolved: True if incident state becomes "RESOLVED", "IGNORED" otherwise. Defaults to True.
            risk_check_id: Optional check id. Defaults to None (Closing all incidents from any check).
            rule_id: Optional Rule id. Defaults to None (Closing all incidents from any rule).
        """
        qs = RiskIncident.objects.filter(status=RiskIncident.Status.OPEN)
        if rule_id:
            qs = qs.filter(rule__id=rule_id)
        for incident in qs.iterator():
            if is_resolved:
                incident.resolve(by=resolved_by)
            else:
                incident.ignore(by=resolved_by)
            incident.comment = reviewer_comment
            incident.save()

    @classmethod
    def can_manage(cls, user: "User", rule: Optional[models.Model] = None) -> bool:
        """
        Utility function to check wether the given user can manage|edit all incidents (manager) or on optional incident
        Args:
            user: The user whose permission is checked.
            incident: Optional Incident. If none, assume global permission check. Defaults to None.

        Returns:
            True if user can manage
        """
        from .rules import RiskRule

        if rule:
            checker = ObjectPermissionChecker(user)
            return checker.has_perm(RiskRule.change_perm_str, rule) or checker.has_perm(RiskRule.admin_perm_str, rule)
        return user.has_perm(RiskRule.admin_perm_str)


@receiver(post_save, sender="wbcompliance.CheckedObjectIncidentRelationship")
def post_save_incident_relationship(sender, instance, created, raw, **kwargs):
    """
    Trigger notification on incident creation
    """
    if not raw and instance.incident:
        if (
            created
            and instance.status == RiskIncident.Status.OPEN
            and not instance.severity.is_informational  # do not reopen incident from informational severity
            and (
                instance.incident.status in [RiskIncident.Status.RESOLVED, RiskIncident.Status.CLOSED]
                or (
                    instance.incident.status == RiskIncident.Status.IGNORED
                    and (
                        not (ignore_until := instance.incident.get_ignore_until_date())
                        or ignore_until < instance.incident_date
                    )
                )
            )
        ):
            instance.incident.status = RiskIncident.Status.OPEN
            instance.incident.last_ignored_date = None
            instance.incident.ignore_duration = None

        instance.incident.save()


@shared_task
def resolve_all_incidents_as_task(
    resolved_by_id,
    reviewer_comment,
    is_resolved: Optional[bool] = True,
    rule_id: Optional[int] = None,
):
    """
    Async task to resolve all incidents
    """
    resolved_by = User.objects.get(id=resolved_by_id)
    RiskIncident.resolve_all_incidents(resolved_by, reviewer_comment, is_resolved, rule_id=rule_id)
