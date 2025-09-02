import re
from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Count, Max, Q, QuerySet
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from pandas.tseries.offsets import MonthEnd, YearEnd
from wbcore.contrib.color.enums import WBColor
from wbcore.contrib.icons import WBIcon
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.enums import RequestType
from wbcore.markdown.utils import custom_url_fetcher
from wbcore.metadata.configs.buttons import ActionButton, ButtonDefaultColor
from wbcore.models import WBModel
from wbcore.models.fields import YearField
from wbcore.utils.models import ComplexToStringMixin
from weasyprint import HTML

from .compliance_type import ComplianceDocumentMixin, ComplianceType, can_active_request
from .enums import IncidentSeverity

User = get_user_model()


def can_draft_request(instance, user: "User") -> bool:
    if instance.is_instance:
        return False
    return user.has_perm("wbcompliance.administrate_compliance")


class ComplianceTaskGroup(WBModel):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    order = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Order"))

    class Meta:
        verbose_name = "Compliance Task Group"
        verbose_name_plural = "Compliance Task Groups"

    def __str__(self) -> str:
        return "{}".format(self.name)

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcompliance:compliancetaskgroup"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcompliance:compliancetaskgrouprepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{name}}"


class ComplianceTask(WBModel):
    class Occurrence(models.TextChoices):
        YEARLY = "YEARLY", "Yearly"
        QUARTERLY = "QUARTERLY", "Quarterly"
        MONTHLY = "MONTHLY", "Monthly"
        NEVER = "NEVER", "Never"

        @classmethod
        def get_color_map(cls) -> list:
            colors = [WBColor.GREEN_LIGHT.value, WBColor.YELLOW_LIGHT.value, WBColor.RED_LIGHT.value]
            return [choice for choice in zip(cls, colors)]

    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(default="", blank=True, verbose_name=_("Description"))
    occurrence = models.CharField(
        max_length=32,
        default=Occurrence.MONTHLY,
        choices=Occurrence.choices,
        verbose_name=_("Occurrence"),
    )
    active = models.BooleanField(default=True)
    group = models.ForeignKey(
        to="wbcompliance.ComplianceTaskGroup",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="tasks_related",
        verbose_name=_("Group"),
    )
    review = models.ManyToManyField(
        "wbcompliance.ReviewComplianceTask",
        related_name="tasks",
        blank=True,
        verbose_name=_("Review"),
        help_text=_("list of reviews that contain this task"),
    )
    risk_level = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        choices=IncidentSeverity.choices,
        verbose_name=_("Risk Level"),
    )
    remarks = models.TextField(null=True, blank=True, verbose_name=_("Remarks"))
    type = models.ForeignKey(
        to=ComplianceType, on_delete=models.PROTECT, related_name="tasks_of_type", verbose_name=_("Type")
    )

    class Meta:
        verbose_name = "Compliance Task"
        verbose_name_plural = "Compliance Tasks"

    def generate_compliance_task_instance(self, occured: date | None = None, link_instance_review: bool = False):
        kwargs = {"task": self}
        if _instance := ComplianceTaskInstance.objects.filter(task=self).last():
            kwargs.update({"status": _instance.status, "text": _instance.text, "summary_text": _instance.summary_text})
        new_instance = ComplianceTaskInstance.objects.create(**kwargs)

        if occured:
            new_instance.occured = occured
            new_instance.save()

        if link_instance_review:
            for review in self.review.filter(Q(is_instance=False) & Q(review_task=None)):
                qs = ReviewComplianceTask.objects.filter(review_task=review, is_instance=True)
                if review_instance := qs.filter(occured=new_instance.occured).last():
                    new_instance.review.add(review_instance)
        return new_instance

    def __str__(self):
        return "{}".format(self.title)

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcompliance:compliancetask"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcompliance:compliancetaskrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{title}}"


class ComplianceTaskInstance(models.Model):
    class Status(models.TextChoices):
        NOT_CHECKED = "NOT_CHECKED", "Not Checked"
        WARNING = "WARNING", "Warning"
        FOR_INFO = "FOR_INFO", "For Info"
        NOTHING_TO_REPORT = "NOTHING_TO_REPORT", "Nothing to Report"
        BREACH = "BREACH", "Breach"

        @classmethod
        def get_color_map(cls) -> list:
            colors = [
                WBColor.GREY.value,
                WBColor.YELLOW_LIGHT.value,
                WBColor.YELLOW.value,
                WBColor.BLUE_LIGHT.value,
                WBColor.RED_LIGHT.value,
            ]
            return [choice for choice in zip(cls, colors)]

    task = models.ForeignKey(
        on_delete=models.CASCADE,
        to="wbcompliance.ComplianceTask",
        related_name="task_instances_related",
        verbose_name=_("Compliance Task"),
    )
    occured = models.DateField(auto_now_add=True, verbose_name=_("Occured"))
    status = models.CharField(
        max_length=32,
        default=Status.NOT_CHECKED,
        choices=Status.choices,
        verbose_name=_("Status"),
    )
    text = models.TextField(default="", blank=True, verbose_name=_("Text"))
    summary_text = models.TextField(null=True, blank=True, verbose_name=_("Summary Text"))
    review = models.ManyToManyField(
        "wbcompliance.ReviewComplianceTask",
        related_name="task_instances",
        blank=True,
        verbose_name=_("Review"),
        help_text=_("list of reviews that contain this task instance"),
    )

    class Meta:
        verbose_name = "Compliance Task Instance"
        verbose_name_plural = "Compliance Task Instances"

    @classmethod
    def get_max_depth(cls) -> int | None:
        return cls.objects.all().values("task").annotate(dcount=Count("task")).aggregate(max=Max("dcount")).get("max")

    @classmethod
    def get_dict_max_count_task(cls) -> dict:
        if cls.get_max_depth():
            return cls.objects.all().values("task").annotate(dcount=Count("task")).latest("dcount")
        return {}

    def __str__(self) -> str:
        return "{}".format(self.task.title)

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcompliance:compliancetaskinstance"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{task__title}} : {{id}}"


class ComplianceAction(models.Model):
    class Status(models.TextChoices):
        TO_BE_DONE = "TO_BE_DONE", "To be done"
        WORK_IN_PROGRESS = "WORK_IN_PROGRESS", "Work in Progress"
        DONE = "DONE", "Done"

        @classmethod
        def get_color_map(cls) -> list:
            colors = [WBColor.GREY.value, WBColor.YELLOW_LIGHT.value, WBColor.GREEN_LIGHT.value]
            return [choice for choice in zip(cls, colors)]

    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(
        default="",
        null=True,
        blank=True,
        verbose_name=_("Description"),
    )
    summary_description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Summary Description"),
    )
    deadline = models.DateField(null=True, blank=True, verbose_name=_("Deadline"))
    progress = models.FloatField(
        default=0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], verbose_name=_("Progress")
    )
    status = models.CharField(
        max_length=32,
        default=Status.TO_BE_DONE,
        choices=Status.choices,
        verbose_name=_("Status"),
    )
    type = models.ForeignKey(
        to=ComplianceType, on_delete=models.PROTECT, related_name="actions_of_type", verbose_name=_("Type")
    )
    active = models.BooleanField(default=True, verbose_name=_("Active"))
    creator = models.ForeignKey(
        to="directory.Person",
        null=True,
        blank=True,
        related_name="compliance_actions",
        verbose_name=_("Creator"),
        on_delete=models.SET_NULL,
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    changer = models.ForeignKey(
        to="directory.Person",
        null=True,
        blank=True,
        verbose_name=_("Changer"),
        related_name="updated_actions",
        on_delete=models.SET_NULL,
    )
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_("Last modified"))

    class Meta:
        verbose_name = "Compliance Action"
        verbose_name_plural = "Compliance Actions"

    def __str__(self) -> str:
        return "{}".format(self.title)

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcompliance:complianceaction"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{title}}"


class ComplianceEvent(models.Model):
    class Type(models.TextChoices):
        INCIDENT = "INCIDENT", "Incident"
        INFO = "INFO", "Info"

        @classmethod
        def get_color_map(cls) -> list:
            colors = [WBColor.GREY.value, WBColor.BLUE_LIGHT.value]
            return [choice for choice in zip(cls, colors)]

    type_event = models.CharField(
        max_length=32,
        default=Type.INCIDENT,
        choices=Type.choices,
        verbose_name=_("Type Event"),
    )
    level = models.CharField(
        max_length=32,
        default=IncidentSeverity.LOW,
        choices=IncidentSeverity.choices,
        verbose_name=_("Level"),
    )
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    exec_summary = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Executive Summary"),
    )
    exec_summary_board = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Executive Summary for the Board"),
    )
    description = models.TextField(default="", blank=True, verbose_name=_("Description"))
    actions_taken = models.TextField(default="", blank=True, verbose_name=_("Actions Taken"))
    consequences = models.TextField(default="", blank=True, verbose_name=_("Consequences"))
    future_suggestions = models.TextField(default="", blank=True, verbose_name=_("Future Suggestions"))
    type = models.ForeignKey(
        to=ComplianceType, on_delete=models.PROTECT, related_name="events_of_type", verbose_name=_("Type")
    )
    active = models.BooleanField(default=True)
    creator = models.ForeignKey(
        to="directory.Person",
        null=True,
        blank=True,
        related_name="compliance_events",
        verbose_name=_("Creator"),
        on_delete=models.SET_NULL,
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    changer = models.ForeignKey(
        to="directory.Person",
        null=True,
        blank=True,
        related_name="updated_events",
        verbose_name=_("Changer"),
        on_delete=models.SET_NULL,
    )
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_("Last modified"))
    confidential = models.BooleanField(default=False, verbose_name=_("Confidential"))

    class Meta:
        verbose_name = "Compliance Event"
        verbose_name_plural = "Compliance Events"

        notification_types = [
            create_notification_type(
                code="wbcompliance.complianceevent.notify",
                title="Compliance Event Notification",
                help_text="Sends out a notification when a new compliance event was created.",
                email=True,
                web=False,
                mobile=False,
                is_lock=True,
            )
        ]

    def __str__(self) -> str:
        return "{}".format(self.title)

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcompliance:complianceevent"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{title}}"


class ReviewComplianceTask(ComplianceDocumentMixin, ComplexToStringMixin, WBModel):
    class Occurrence(models.TextChoices):
        YEARLY = "YEARLY", "Yearly"
        QUARTERLY = "QUARTERLY", "Quarterly"
        MONTHLY = "MONTHLY", "Monthly"
        NEVER = "NEVER", "Never"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        VALIDATION_REQUESTED = "VALIDATION_REQUESTED", "Validation Requested"
        VALIDATED = "VALIDATED", "Validated"

        @classmethod
        def get_color_map(cls) -> list:
            colors = [
                WBColor.BLUE_LIGHT.value,
                WBColor.YELLOW_LIGHT.value,
                WBColor.GREEN_LIGHT.value,
            ]
            return [choice for choice in zip(cls, colors)]

    class Meta:
        verbose_name = "Review Compliance Task"
        verbose_name_plural = "Review Compliance Tasks"

        notification_types = [
            create_notification_type(
                code="wbcompliance.reviewcompliancetask.notify",
                title="Compliance Task Review Notification",
                help_text="Notifies you when a compliance task can be reviewed",
                email=True,
                web=False,
                mobile=False,
                is_lock=True,
            )
        ]

    title = models.CharField(max_length=255, verbose_name=_("Title"))
    from_date = models.DateField(null=True, blank=True, verbose_name=_("From"))
    to_date = models.DateField(null=True, blank=True, verbose_name=_("To"))
    description = models.TextField(default="", blank=True, verbose_name=_("Description"))
    year = YearField(
        validators=[MinValueValidator(1000), MaxValueValidator(9999)], null=True, blank=True, verbose_name=_("Year")
    )
    creator = models.ForeignKey(
        to="directory.Person",
        null=True,
        blank=True,
        verbose_name=_("Creator"),
        related_name="author_review_compliane_tasks",
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    changer = models.ForeignKey(
        "directory.Person", null=True, blank=True, verbose_name=_("Changer"), on_delete=models.deletion.SET_NULL
    )
    changed = models.DateTimeField(auto_now=True, verbose_name=_("Changed"))
    status = FSMField(default=Status.DRAFT, choices=Status.choices, verbose_name=_("Status"))
    occurrence = models.CharField(
        max_length=32,
        default=Occurrence.MONTHLY,
        choices=Occurrence.choices,
        verbose_name=_("Occurrence"),
    )

    is_instance = models.BooleanField(default=False, verbose_name=_("Is occurrence"))
    review_task = models.ForeignKey(
        to="wbcompliance.ReviewComplianceTask",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="review_tasks",
        verbose_name=_("Parent Review"),
    )
    occured = models.DateField(null=True, blank=True, verbose_name=_("Occured Instance"))
    type = models.ForeignKey(
        to=ComplianceType,
        on_delete=models.PROTECT,
        related_name="reviewtask_of_type",
        verbose_name=_("Type"),
    )

    def notify(self, title, msg, recipients: QuerySet["User"]) -> None:
        for user in recipients:
            send_notification(
                code="wbcompliance.reviewcompliancetask.notify",
                title=title,
                body=msg,
                user=user,
                reverse_name="wbcompliance:reviewcompliancetask-detail",
                reverse_args=[self.id],
            )

    def _remove_styled_paragraph(self, html_content: str) -> str:
        tags = ["p", "span"]
        for tag in tags:
            reg_str = "<" + tag + "(.*?)" + ">"
            reg_style = '(style=".*?;")'
            _attributs = re.findall(reg_str, html_content)
            dict_attrs = {}
            for attribut in _attributs:
                dict_attrs[attribut] = re.sub(reg_style, "", attribut)

            for _key, _value in dict_attrs.items():
                html_content = re.sub(_key, _value, html_content)

        html_content = re.sub("<p>&nbsp;</p>", "", html_content)
        return html_content

    def generate_pdf(self) -> bytes:
        html = get_template("compliance/review_compliance_task_report.html")
        table = {}
        tasks = ComplianceTask.objects.filter(Q(review=self) & Q(active=True)).order_by("group__order")
        group_ids = tasks.values_list("group", flat=True).distinct()
        for group_id in group_ids:
            if group_id:
                group = ComplianceTaskGroup.objects.get(id=group_id)
                table[group.id] = {"name": group.name, "tasks": {}}
            else:
                group_id = ""
                group = None
                table[""] = {"name": "", "tasks": {}}

            for task in tasks.filter(group=group):
                table[group_id]["tasks"][task.id] = {
                    "title": task.title,
                    "description": self._remove_styled_paragraph(task.description),
                    "risk_level": task.risk_level,
                    "remarks": task.remarks,
                }
        html_content = html.render(
            {
                "today": timezone.now(),
                "review": self,
                "table": table,
            }
        )
        return HTML(
            string=html_content, base_url=settings.BASE_ENDPOINT_URL, url_fetcher=custom_url_fetcher
        ).write_pdf()

    def get_period_date(self, today: datetime | None = None):
        if today is None:
            today = timezone.now()
        if self.occurrence == self.Occurrence.YEARLY:
            from_date = date(today.year - 1, 1, 1)
            to_date = from_date + YearEnd(1)
        elif self.occurrence == self.Occurrence.QUARTERLY:
            from_date = (today - MonthEnd(4)).date() + timedelta(days=1)
            to_date = (today - MonthEnd(1)).date()
        elif self.occurrence == self.Occurrence.MONTHLY:
            from_date = (today - MonthEnd(2)).date() + timedelta(days=1)
            to_date = (today - MonthEnd(1)).date()
        else:
            return None, None
        return from_date, to_date

    def generate_review_compliance_task_instance(
        self, current_date: datetime | None = None, link_instance: bool = False, notify_admin: bool = False
    ) -> None:
        """
        allow to generate the occurrence of the Indicators Report.
        current_date: allow to find the year and the period date corresponding to the occurrence. we use today by default
        """
        if current_date is None:
            current_date = timezone.now()
        from_date, to_date = self.get_period_date(current_date)
        date_title = to_date if to_date else current_date
        kwargs = {
            "review_task": self,
            "year": current_date.year,
            "occured": current_date.date(),
            "is_instance": True,
            "status": ReviewComplianceTask.Status.DRAFT,
            "creator": self.creator,
            "changer": self.changer,
            "occurrence": ReviewComplianceTask.Occurrence.NEVER,
            "description": self.description,
            "title": "{} - {}".format(self.title, date_title.strftime("%b %Y")),
            "from_date": from_date,
            "to_date": to_date,
            "type": self.type,
        }
        if _instance := ReviewComplianceTask.objects.filter(Q(review_task=self) & Q(is_instance=True)).last():
            kwargs.update({"creator": _instance.changer, "description": _instance.description})
        new_review = ReviewComplianceTask.objects.create(**kwargs)

        if link_instance:
            for task in ComplianceTask.objects.filter(review__in=[self]):
                if instance := ComplianceTaskInstance.objects.filter(task=task).last():
                    instance.review.add(new_review)

        if notify_admin and (compliance_type := self.type):
            recipients = ComplianceType.get_administrators(compliance_type)
            msg = _("<b>{}</b> is available. You can now complete and validate it.").format(self.title)
            title = _("Instance Indicator Report: {}").format(self.title)
            self.notify(title, msg, recipients)

    def get_task_group_ids_from_review(self, through_task: bool = True, task_with_group: bool = True) -> set:
        if through_task:
            return set(
                self.tasks.filter(group__isnull=not (task_with_group))
                .order_by("group__order")
                .values_list("group", flat=True)
            )
        else:
            return set(
                self.task_instances.filter(task__group__isnull=not (task_with_group))
                .order_by("task__group__order")
                .values_list("task__group", flat=True)
            )

    @transition(
        field=status,
        source=Status.DRAFT,
        target=Status.VALIDATION_REQUESTED,
        permission=lambda _, user: user.has_perm("wbcompliance.administrate_compliance"),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbcompliance:reviewcompliancetask",),
                icon=WBIcon.SEND.icon,
                key="validationrequested",
                label="Request Validation",
                action_label=_("Request Validation"),
                description_fields=_(
                    "<p>Title: <b>{{title}}</b></p>\
                <p>Status: <b>{{status}}</b></p> <p>From: <b>{{from_date}}</b></p>\
                <p>To: <b>{{to_date}}</b></p> <p>Do you want to send this request for validation ?</p>"
                ),
            )
        },
    )
    def validationrequested(self, by=None, description=None, **kwargs):
        if compliance_type := self.type:
            # notify the compliance team without the current user
            if by:
                self.changer = by.profile
            current_user = self.changer if self.changer else self.creator
            recipients = ComplianceType.get_administrators(compliance_type).exclude(profile=current_user)
            msg = _("Validation Request from {} to validate a ompliance Risk Review: <b>{}</b>").format(
                str(current_user), self.title
            )
            title = _("Validation Requested Compliance Risk Review: {}").format(self.title)
            self.notify(title, msg, recipients)

    @transition(
        field=status,
        source=Status.VALIDATION_REQUESTED,
        target=Status.DRAFT,
        permission=lambda _, user: user.has_perm("wbcompliance.administrate_compliance"),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbcompliance:reviewcompliancetask",),
                icon=WBIcon.EDIT.icon,
                key="draft",
                label="Return to Draft Mode",
                action_label=_("Return to Draft Mode"),
                description_fields=_(
                    """
                <p>Title: <b> {{title}} </b></p>
                <p>Status: <b>{{status}}</b></p> <p>From: <b>{{from_date}}</b></p>  <p>To: <b>{{to_date}}</b></p>
                <p>Do you want to return to draft ?</p>
                """
                ),
            )
        },
    )
    def draft(self, by=None, description=None, **kwargs):
        if compliance_type := self.type:
            if by:
                self.changer = by.profile
            current_user = self.changer if self.changer else self.creator
            msg = _("{} has changed a Compliance Risk Review to Draft : <b>{}</b>").format(
                str(current_user), self.title
            )
            title = _("Compliance Risk Review : {}").format(self.title)
            recipients = ComplianceType.get_administrators(compliance_type).exclude(profile=current_user)
            self.notify(title, msg, recipients)

    @transition(
        field=status,
        source=Status.VALIDATION_REQUESTED,
        target=Status.VALIDATED,
        permission=can_active_request,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbcompliance:reviewcompliancetask",),
                icon=WBIcon.SEND.icon,
                key="validation",
                label="Validate",
                action_label=_("Validate"),
                description_fields=_(
                    """
                <p>Title: <b> {{title}} </b></p>
                <p>Status: <b>{{status}}</b></p> <p>From: <b>{{from_date}}</b></p>  <p>To: <b>{{to_date}}</b></p>
                <p>Do you want to validate?</p>
                """
                ),
            )
        },
    )
    def validation(self, by=None, description=None, **kwargs):
        if compliance_type := self.type:
            if by:
                self.changer = by.profile
            current_user = self.changer if self.changer else self.creator
            msg = _(
                """
                {} has validated a Compliance Risk Review : <b>{}</b>
            """
            ).format(str(current_user), self.title)
            title = _("Validation - Compliance Risk Review : {}").format(self.title)
            recipients = ComplianceType.get_administrators(compliance_type).exclude(profile=current_user)
            self.notify(title, msg, recipients)

    @transition(
        field=status,
        source=Status.VALIDATED,
        target=Status.DRAFT,
        permission=can_draft_request,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbcompliance:reviewcompliancetask",),
                icon=WBIcon.EDIT.icon,
                key="backtodraft",
                label="Back to draft",
                action_label=_("Back to draft"),
                description_fields=_(
                    """
                <p>Title: <b> {{title}} </b></p>
                <p>Status: <b>{{status}}</b></p> <p>From: <b>{{from_date}}</b></p>  <p>To: <b>{{to_date}}</b></p>
                <p>Do you want to return to the draft?</p>
                """
                ),
            )
        },
    )
    def backtodraft(self, by=None, description=None, **kwargs):
        if compliance_type := self.type:
            if by:
                self.changer = by.profile
            current_user = self.changer if self.changer else self.creator
            msg = _("{} has drafted a Compliance Indicators Report : <b>{}</b>").format(str(current_user), self.title)
            title = _("Compliance Indicators Report drafted: {}").format(self.title)
            recipients = ComplianceType.get_administrators(compliance_type)
            self.notify(title, msg, recipients)

    def compute_str(self) -> str:
        _str = "{}".format(self.title)
        if self.from_date or self.to_date:
            _str += " - ({} - {})".format(self.from_date, self.to_date)
        return _str

    def __str__(self) -> str:
        return self.computed_str

    def save(self, *args, **kwargs):
        self.computed_str = self.compute_str()
        super().save(*args, **kwargs)

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbcompliance:reviewcompliancetask"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbcompliance:reviewcompliancetaskrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{computed_str}}"


@receiver(post_save, sender=ComplianceEvent)
def post_save_compliance_event(sender, instance, created, **kwargs):
    """
    Send notification to administrators
    """
    if created and (compliance_type := instance.type):
        current_profile = instance.changer if instance.changer else instance.creator
        recipients = ComplianceType.get_administrators(compliance_type).exclude(profile=current_profile)
        title = "{}: {}".format(ComplianceEvent.Type[instance.type_event].label, instance.title)
        msg = _("<p>An {} Event was created by {} {} at {}</p>").format(
            ComplianceEvent.Type[instance.type_event].label,
            current_profile.first_name,
            current_profile.last_name,
            instance.last_modified.strftime("%d-%b-%y %H:%M:%S"),
        )
        if instance.exec_summary:
            msg += _("<p> Summary : {}</p>").format(instance.exec_summary)
        for recipient in recipients:
            send_notification(
                code="wbcompliance.complianceevent.notify",
                title=title,
                body=msg,
                user=recipient,
                reverse_name="wbcompliance:complianceevent-detail",
                reverse_args=[instance.id],
            )
