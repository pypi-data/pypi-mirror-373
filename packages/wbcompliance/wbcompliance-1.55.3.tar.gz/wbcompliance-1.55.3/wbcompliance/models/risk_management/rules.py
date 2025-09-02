from contextlib import suppress
from datetime import date, datetime, timedelta
from importlib import import_module
from typing import Any, Dict, Generator, Iterable, Iterator, Optional, Type

import pandas as pd
from celery import shared_task
from dateutil import rrule
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.models import User as BaseUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import DecimalRangeField
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Exists, OuterRef, Q
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.template.loader import get_template
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from pandas.tseries.offsets import BDay
from psycopg.types.range import DateRange
from rest_framework.reverse import reverse
from wbcore.contrib.directory.models import Person
from wbcore.contrib.guardian.models.mixins import PermissionObjectModelMixin
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.models import WBModel
from wbcore.utils.models import ComplexToStringMixin
from wbcore.utils.rrules import convert_rrulestr_to_dict

from .backend import AbstractRuleBackend
from .checks import RiskCheck
from .incidents import CheckedObjectIncidentRelationship, RiskIncident, RiskIncidentType

User: BaseUser = get_user_model()


class RuleGroup(models.Model):
    key = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.key.title()
        super().save(*args, **kwargs)

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcompliance:rulegrouprepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{name}}"


class RuleCheckedObjectRelationship(ComplexToStringMixin, models.Model):
    rule = models.ForeignKey(
        to="wbcompliance.RiskRule", related_name="checked_object_relationships", on_delete=models.CASCADE
    )
    checked_object_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="risk_management_checked_objects"
    )
    checked_object_id = models.PositiveIntegerField()
    checked_object = GenericForeignKey("checked_object_content_type", "checked_object_id")
    checked_object_repr = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        verbose_name = "Checked Object to Rule relationship"
        verbose_name_plural = "Checked Object to Rule relationships"
        indexes = [
            models.Index(fields=["rule", "checked_object_content_type", "checked_object_id"]),
        ]
        unique_together = [("rule", "checked_object_content_type", "checked_object_id")]

    @property
    def checks(self) -> "models.QuerySet[RiskCheck]":
        return RiskCheck.objects.filter(
            checked_object_id=self.checked_object_id,
            checked_object_content_type=self.checked_object_content_type,
            rule=self.rule,
        )

    def clean(self):
        allowed_checked_object_content_type = self.rule.rule_backend.allowed_checked_object_content_type
        if allowed_checked_object_content_type and (
            allowed_checked_object_content_type != self.checked_object_content_type
        ):
            raise ValidationError(
                _(
                    "The relationship content type ({}) needs to match the rule's backend allowed content type ({})"
                ).format(self.checked_object_content_type, allowed_checked_object_content_type)
            )
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        self.checked_object_repr = str(self.checked_object)
        super().save(*args, **kwargs)

    def compute_str(self) -> str:
        return _("Rule Relationship {} -> {} {}").format(
            self.rule, self.checked_object_content_type.name, self.checked_object
        )

    def process_rule(self, evaluation_date: date, override_incident: bool = False) -> bool:
        """
        Trigger the check between the rule and the checked object attached to this relationship
        """
        rule_backend = self.rule.rule_backend.backend(
            evaluation_date, self.checked_object, self.rule.parameters, self.rule.thresholds.all()
        )
        incident_detected = False
        if rule_backend.is_passive_evaluation_valid():
            check = RiskCheck.objects.create(
                rule=self.rule,
                checked_object_id=self.checked_object_id,
                checked_object_content_type=self.checked_object_content_type,
                evaluation_date=evaluation_date,
            )
            # we create the check but the rule might not be allowed to be processed on that particular date (e.g. wrong frequency)
            if self.rule.is_evaluation_date_valid(evaluation_date):
                for incident in check.evaluate(override_incident=override_incident):
                    incident_detected = True
                    incident.post_workflow()
        return incident_detected

    def get_unchecked_dates(
        self, from_date: Optional[date] = None, to_date: Optional[date] = None, maximum_day_interval: int = 30
    ) -> Iterator[date]:
        """
        if a checks exists it generates all dates between it and the specified to_date (if exists, otherwise, return just the next day after the last check
        if checks does not exist but to_date is specified, generates a unique date

        Args:
            to_date: The limit at which we want to check the next expected check date. Defaults None (no upper bound).

        Returns:
            A list of date to be checked
        """

        if not from_date:
            if self.checks.exists():
                from_date = (self.checks.latest("evaluation_date").evaluation_date + BDay(1)).date()
            elif to_date:
                from_date = to_date - timedelta(days=maximum_day_interval)
            if to_date:
                minimum_allowed_from_date = to_date - timedelta(days=maximum_day_interval)
                from_date = max([from_date, minimum_allowed_from_date])
        if not to_date:
            to_date = from_date
        if not from_date and not to_date:
            raise ValueError("Either from or To date needs to be provided")
        for evaluation_date in pd.date_range(from_date, to_date, freq="B"):
            if not self.checks.filter(evaluation_date=evaluation_date.date()).exists():
                yield evaluation_date.date()

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcompliance:rulechecked_objectrelationshiprepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"


class RuleBackend(models.Model):
    """
    Represent a rule backend  that links to a module where a RuleBackend class is defined.

    We expect this class to at least define the following interface:
    * check(evaluation_date, checked_object, **json_parameters) // Check for a given date, triggering object, a set of
    parameters and corresponding severity thresholds if a rule is in breach.

    Optionally, it can define the following methods:
    * is_passive_evaluation_valid(eval_date, evaluated_object)
    """

    name = models.CharField(max_length=128)
    backend_class_path = models.CharField(max_length=512)
    backend_class_name = models.CharField(max_length=128, default="RuleBackend")
    allowed_checked_object_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, blank=True, null=True
    )
    rule_group = models.ForeignKey(
        to="wbcompliance.RuleGroup", related_name="rules", null=True, blank=True, on_delete=models.SET_NULL
    )
    incident_report_template = models.TextField(
        default=get_template("risk_management/incident_report.html").template.source, verbose_name="Incident Template"
    )

    class Meta:
        verbose_name = "Rule Backend"
        verbose_name_plural = "Rule Backends"

    @cached_property
    def backend_class(self) -> type[AbstractRuleBackend]:
        """
        Return the imported backend class
        Returns:
            The backend class
        """
        return getattr(import_module(self.backend_class_path), self.backend_class_name)

    def backend(
        self,
        evaluation_date: date,
        evaluated_object: models.Model,
        json_parameters: Dict[str, Any],
        thresholds: "models.QuerySet[RuleThreshold]",
    ) -> AbstractRuleBackend:
        """
        Args:
            evaluation_date: The evaluation rule date
            evaluated_object: The object that needs evaluation
            json_parameters: Set of paramaters as dictionary. Might expect deserialization that will be handled within the backend
            thresholds: List of numerical range, severity pairs

        Return the instantiated backend imported through the specified dotted path and the passed parameters
        Returns:
            The instantiated backend
        """
        checked_object_content_type = ContentType.objects.get_for_model(evaluated_object)
        if self.allowed_checked_object_content_type and (
            checked_object_content_type != self.allowed_checked_object_content_type
        ):
            raise ValidationError(
                _("Passed content type {} does not match the allowed backend content type {}").format(
                    checked_object_content_type, self.allowed_checked_object_content_type
                )
            )
        return self.backend_class(
            evaluation_date, evaluated_object, json_parameters, thresholds.order_by("severity__severity_order")
        )

    def get_all_active_relationships(self) -> Iterable:
        try:
            return self.backend_class.get_all_active_relationships()
        except NotImplementedError:
            return []

    def __str__(self):
        return _("Rule Backend {}").format(self.name)

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcompliance:rulebackendrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{name}}"


class RuleThreshold(ComplexToStringMixin, models.Model):
    """
    Represent the list of threshold and its associated severity link to a certain rule
    """

    rule = models.ForeignKey(to="wbcompliance.RiskRule", related_name="thresholds", on_delete=models.CASCADE)
    range = DecimalRangeField(
        verbose_name=_("Threshold range"),
        help_text=_("The range which triggers the specified severity. null bound represent infinity"),
    )

    severity = models.ForeignKey(
        "wbcompliance.RiskIncidentType",
        on_delete=models.CASCADE,
        verbose_name=_("Triggered Severity"),
        help_text=_("The Triggered Severity when the rule is within the threshold range"),
        related_name="thresholds",
    )
    upgradable_after_days = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Upgradable to next severity after X Days"),
        help_text=_(
            "If set to a positive integer, the resulting incident will be elevated to the next rule severity after an incident remains open this number of days"
        ),
    )

    notifiable_users = models.ManyToManyField(
        "directory.Person",
        related_name="notified_rule_thresholds",
        blank=True,
        verbose_name=_("Notifiable Persons"),
        help_text=_("Notified Persons for this rule and severity"),
    )
    notifiable_groups = models.ManyToManyField(
        Group,
        related_name="notified_rule_thresholds",
        blank=True,
        verbose_name=_("Notifiable Groups"),
        help_text=_("Notified Groups for this rule and severity"),
    )

    @property
    def next_threshold(self):
        """
        Property that hold the next higher severity order threshold

        Returns: The next Threshold in the severity order sense
        """
        higher_thresholds = (
            self.rule.thresholds.exclude(id=self.id)
            .filter(severity__severity_order__gt=self.severity.severity_order)
            .order_by("severity__severity_order")
        )

        if higher_thresholds.exists():
            return higher_thresholds.first()

    @property
    def numerical_range(self) -> tuple[float, float]:
        return float(self.range.lower) if self.range.lower is not None else float("-inf"), float(  # type: ignore
            self.range.upper  # type: ignore
        ) if self.range.upper is not None else float("inf")  # type: ignore

    @property
    def range_repr(self) -> str:
        upper_bound_repr = "{}]".format(self.range.upper) if self.range.upper is not None else "∞["  # type: ignore
        lower_bound_repr = "[{}".format(self.range.lower) if self.range.lower is not None else "]-∞"  # type: ignore
        return f"{lower_bound_repr}, {upper_bound_repr}"

    def is_inrange(self, value) -> bool:
        """
        Utility function to check whether is within this threshold range
        Args:
            value: The value to check against

        Returns:
            True if the value is in range
        """
        return value > self.numerical_range[0] and value < self.numerical_range[1]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def compute_str(self) -> str:
        return _("Range: {} (Severity {})").format(self.range_repr, self.severity)

    def get_notifiable_users(self) -> "models.QuerySet[Person]":
        """
        Returns the incident notifiable persons

        Returns:
            A queryset of Person
        """
        try:
            return User.objects.filter(
                models.Q(profile__in=self.notifiable_users.values("id"))
                | models.Q(groups__in=self.notifiable_groups.all())
            ).distinct()
        except ObjectDoesNotExist:
            return User.objects.none()

    class Meta:
        unique_together = ("rule", "severity")

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcompliance:rulethresholdrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"


class RiskRuleDefaultManager(models.Manager):
    def get_active_rules_for_object(self, obj: Type[models.Model]) -> models.QuerySet["RiskRule"]:
        return (
            self.get_queryset()
            .annotate(
                has_direct_relationship=Exists(
                    RuleCheckedObjectRelationship.objects.filter(
                        rule=OuterRef("pk"),
                        checked_object_content_type=ContentType.objects.get_for_model(obj),
                        checked_object_id=obj.id,
                    )
                )
            )
            .filter(
                Q(is_enable=True)
                & Q(only_passive_check_allowed=False)
                & (Q(apply_to_all_active_relationships=True) | Q(has_direct_relationship=True))
            )
        )


class RiskRule(PermissionObjectModelMixin, WBModel):
    """
    Base class for rule management. All the data that defined the rule parameters.

    Expected to be inherited (Abstract)
    """

    name = models.CharField(max_length=512)
    description = models.CharField(max_length=516, default="", verbose_name=_("Quick Description"))
    rule_backend = models.ForeignKey(to="wbcompliance.RuleBackend", related_name="rules", on_delete=models.CASCADE)

    is_enable = models.BooleanField(default=True, verbose_name=_("Enabled"))
    only_passive_check_allowed = models.BooleanField(
        default=True,
        verbose_name=_("Passive Only"),
        help_text=_("If False, This rule can only be triggered passively"),
    )
    is_silent = models.BooleanField(
        default=True, help_text=_("If true, the notification won't be send through System nor Mail")
    )
    is_mandatory = models.BooleanField(
        default=False, help_text=_("A mandatory rule cannot be modified by anyone other than the administrators")
    )
    automatically_close_incident = models.BooleanField(
        default=False, help_text=_("If True, this rule will automatically close all encountered incidents")
    )

    apply_to_all_active_relationships = models.BooleanField(
        default=False,
        help_text=_("If True, will keep this rule syncrhonize with the backend definition of all active relationship"),
    )
    activation_date = models.DateField(null=True, blank=True, verbose_name="Activation Date")
    frequency = models.CharField(
        null=True,
        blank=True,
        max_length=56,
        verbose_name=_("Evaluation Frequency"),
        help_text=_("The Evaluation Frequency in RRULE format"),
    )
    parameters = models.JSONField(blank=True, default=dict, encoder=DjangoJSONEncoder)

    class Meta(PermissionObjectModelMixin.Meta):
        verbose_name = "Risk Rule"
        verbose_name_plural = "Risk Rules"

    objects = RiskRuleDefaultManager()

    @property
    def checked_object_representation(self) -> str:
        try:
            backend_class = self.rule_backend.backend_class
            checked_object_repr = getattr(backend_class, "OBJECT_FIELD_NAME").title()
        except AttributeError:
            checked_object_repr = "Object"
        return checked_object_repr

    @property
    def checked_objects(self) -> Generator[models.Model, None, None]:
        """
        All objects that share a relationship with this rule instance

        Returns:
            An generator of Object (any type)

        """
        for relation in self.checked_object_relationships.all():
            yield relation.checked_object

    @property
    def checks(self) -> "models.QuerySet[RiskCheck]":
        return RiskCheck.objects.filter(rule=self).distinct()

    def save(self, *args, **kwargs):
        serializer = self.rule_backend.backend_class.get_serializer_class()(data=self.parameters)
        if serializer.is_valid():
            self.parameters = serializer.data
        super().save(*args, **kwargs)

    def __str__(self):
        return _("Rule {}").format(self.name)

    def is_evaluation_date_valid(self, evaluation_date: date) -> bool:
        if self.frequency and self.activation_date:
            rrule_dict = convert_rrulestr_to_dict(self.frequency, dtstart=self.activation_date, until=evaluation_date)
            valid_dates = list(map(lambda o: o.date(), rrule.rrule(**rrule_dict)))
            return evaluation_date in valid_dates
        return self.activation_date is not None and self.activation_date <= evaluation_date

    def process_rule(self, evaluation_date: date, override_incident: bool = False, silent_notification: bool = False):
        """
        Wrapper function that calls the not implemented check_risk to evaluate the rule against a date and all linked risk management instances.

        Args:
            evaluation_date: The evaluation date
            override_incident: If True, the existing incidents will be reopened instead of being ignored
            silent_notification: If True, explicitly silent notification even if they are due
        """
        if not self.is_enable:
            raise ValueError("This rule cannot be triggered (disabled or active)")
        for relationship in self.checked_object_relationships.iterator():
            relationship.process_rule(evaluation_date, override_incident=override_incident)
        if not silent_notification:
            self.notify(evaluation_date)

    def get_permissions_for_user(self, user, created: datetime | None = None) -> dict[str, bool]:
        permissions = super().get_permissions_for_user(user, created)

        if user.has_perm(self.view_perm_str):
            permissions[self.view_perm_str] = False

        return permissions

    def get_or_create_incident(
        self,
        evaluation_date: date,
        incident_severity: "RiskIncidentType",
        breached_object: Any,
        breached_object_repr: str,
    ) -> tuple[RiskIncident, bool]:
        """
        Utility function to get or create incident base on the given breached object

        Args:
            rule:  The rule this incident happens
            evaluation_date: The incident date
            incident_severity: The incident severity
            breached_object: The breached object (i.e. the object that triggers the incident)
            breached_object_repr: Its string representation

        Returns:
            A tuple (incident, is_created)
        """

        # Consider that if an incident happens one business day in the future or past, it is continue
        date_range = DateRange(  # type: ignore
            (evaluation_date - BDay(1)).date(), (evaluation_date + BDay(1)).date(), "[]"
        )
        incidents = RiskIncident.objects.filter(rule=self, date_range__overlap=date_range)
        if breached_object:
            # If a breached_object is provided, we lookup over it
            incidents = incidents.filter(
                breached_content_type=ContentType.objects.get_for_model(breached_object),
                breached_object_id=breached_object.id,
            )
        else:
            # Otherwise, we lookup over its string representation. Might need to change as this is not very robust
            incidents = incidents.filter(
                breached_object_repr=breached_object_repr,
            )
        if incident := incidents.first():
            incident.date_range = DateRange(
                lower=incident.date_range.lower, upper=(evaluation_date + timedelta(days=1))
            )  # type: ignore
            if self.automatically_close_incident:
                incident.status = RiskIncident.Status.CLOSED
            incident.save()
            return incident, False
        else:
            return (
                RiskIncident.objects.create(
                    rule=self,
                    date_range=DateRange(lower=evaluation_date, upper=(evaluation_date + timedelta(days=1))),  # type: ignore
                    breached_content_type=ContentType.objects.get_for_model(breached_object)
                    if breached_object
                    else None,
                    breached_object_id=breached_object.id if breached_object else None,
                    breached_object_repr=breached_object_repr,
                    severity=incident_severity,
                    status=RiskIncident.Status.CLOSED
                    if self.automatically_close_incident
                    else RiskIncident.Status.OPEN,
                ),
                True,
            )

    def notify(self, evaluation_date: date):
        """
        Create the notification for this rule relationship and all implied persons
        """
        # Check if the incident needs to be notified
        incidents = RiskIncident.objects.filter(
            models.Q(checked_object_relationships__rule_check__evaluation_date=evaluation_date)
            & models.Q(rule=self)
            & (models.Q(status=RiskIncident.Status.OPEN) | models.Q(is_notified=False))
        )
        if not self.is_silent:
            for threshold in self.thresholds.filter(
                severity__is_informational=False
            ):  # ignore informational incident from being ignored
                threshold_incidents = incidents.filter(severity=threshold.severity)
                notified_users = threshold.get_notifiable_users()
                if notified_users.exists() and threshold_incidents.exists():
                    evaluation_date_sub_incidents = CheckedObjectIncidentRelationship.objects.filter(
                        incident__in=threshold_incidents,
                        rule_check__evaluation_date=evaluation_date,
                        severity=threshold.severity,
                    ).order_by("rule_check__checked_object_repr")
                    if evaluation_date_sub_incidents.exists():
                        breached_content_types = ContentType.objects.filter(
                            id__in=evaluation_date_sub_incidents.values("incident__breached_content_type")
                        )
                        breached_content_type_name = "Object"
                        if breached_content_types.count() == 1:
                            breached_content_type_name = breached_content_types.first().name
                        html = get_template("risk_management/incident_notification.html").render(
                            {
                                "evaluation_date_sub_incidents": evaluation_date_sub_incidents,
                                "rule": self,
                                "threshold": threshold,
                                "evaluation_date": evaluation_date,
                                "check_object_content_type_name": "Checked " + self.checked_object_representation,
                                "breached_content_type_name": breached_content_type_name,
                            }
                        )
                        for user in notified_users:
                            send_notification(
                                code="wbcompliance.riskincident.notify",
                                title=_("{} Broken Rule: {} as of {}").format(
                                    threshold.severity.name, self.name, evaluation_date.strftime("%d.%m.%Y")
                                ),
                                body=html,
                                user=user,
                                endpoint=reverse("wbcompliance:riskrule-detail", args=[self.id]),
                            )
        incidents.update(is_notified=True)

    @classmethod
    def get_rules_for_object(cls, obj) -> "models.QuerySet[RiskRule]":
        """
        Returns a Queryset of document linked to the passed object

        Args:
            obj: The related object

        Returns:
            A queryset of documents
        """
        rule_ids = RuleCheckedObjectRelationship.objects.filter(
            checked_object_content_type=ContentType.objects.get_for_model(obj), checked_object_id=obj.id
        ).values("rule")
        return cls.objects.filter(id__in=rule_ids)

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcompliance:riskrule"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcompliance:riskrulerepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{name}}"


@receiver(pre_save, sender="wbcompliance.RuleThreshold")
def pre_save_risk_threshold(sender, instance, **kwargs):
    with suppress(RuleThreshold.DoesNotExist):
        pre_save_instance = RuleThreshold.objects.get(id=instance.id)
        RiskIncident.objects.filter(rule=instance.rule, severity=pre_save_instance.severity).update(
            severity=instance.severity
        )
        CheckedObjectIncidentRelationship.objects.filter(
            incident__rule=instance.rule, severity=pre_save_instance.severity
        ).update(severity=instance.severity)


@receiver(pre_delete, sender="wbcompliance.RuleThreshold")
def pre_delete_risk_threshold(sender, instance, **kwargs):
    RiskIncident.objects.filter(rule=instance.rule, severity=instance.severity).delete()
    CheckedObjectIncidentRelationship.objects.filter(incident__rule=instance.rule, severity=instance.severity).delete()


@shared_task
def process_rule_as_task(rule_id: int, evaluation_date: date, override_incident: bool | None = False):
    """
    Async task to process rule
    """
    rule = RiskRule.objects.get(id=rule_id)
    rule.process_rule(evaluation_date, override_incident=override_incident)
