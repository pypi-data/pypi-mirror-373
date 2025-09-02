from collections import defaultdict
from datetime import date, datetime

from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from tqdm import tqdm

from wbcompliance.models import ComplianceTask, ReviewComplianceTask
from wbcompliance.models.risk_management.rules import (
    RiskRule,
    RuleCheckedObjectRelationship,
)


@shared_task
def check_passive_rules(
    from_date: date | None = None,
    to_date: date | None = None,
    override_incident: bool | None = False,
    extra_process_kwargs: dict | None = None,
    silent_notification: bool = False,
    debug: bool = False,
):
    """
    Periodic function that call all active passive rules and checked_object the check workflow
    """
    if not to_date:
        to_date = datetime.today().date()

    # cleanup relationship before continuing
    clean_dynamic_rule_relationships(debug=debug)

    process_kwargs = {
        "override_incident": override_incident,
    }
    if isinstance(extra_process_kwargs, dict):
        process_kwargs.update(extra_process_kwargs)

    res = []
    for rule in RiskRule.objects.filter(is_enable=True):
        for relationship in rule.checked_object_relationships.iterator():
            res.append((rule, relationship))
    gen = res
    if debug:
        gen = tqdm(gen, total=len(res))
    date_to_notify = defaultdict(set)
    for rule, relationship in gen:
        for evaluation_date in relationship.get_unchecked_dates(from_date=from_date, to_date=to_date):
            if relationship.process_rule(evaluation_date, **process_kwargs):
                date_to_notify[rule].add(evaluation_date)

    if not silent_notification:
        for rule, dates in date_to_notify.items():
            for checked_date in dates:
                rule.notify(checked_date)


@shared_task
def clean_dynamic_rule_relationships(debug: bool = False):
    """
    Periodic function to check reverse generic object that don't exist anymore. Furthermore, get the queryset representing all the active relationship for all backend and ensure that every object have a relationship (e.g. new object creation)
    """
    gen = RiskRule.objects.filter(apply_to_all_active_relationships=True)
    if debug:
        gen = tqdm(gen, total=gen.count())

    for rule in gen:
        leftover_relationships = rule.checked_object_relationships.all()
        for content_object in rule.rule_backend.get_all_active_relationships():
            rel, _ = RuleCheckedObjectRelationship.objects.get_or_create(
                rule=rule,
                checked_object_content_type=ContentType.objects.get_for_model(content_object),
                checked_object_id=content_object.id,
            )
            leftover_relationships = leftover_relationships.exclude(id=rel.id)

        for leftover_relationship in leftover_relationships.iterator():
            leftover_relationship.delete()


@shared_task
def periodic_quaterly_or_monthly_compliance_task():
    today = datetime.now()
    qs = ComplianceTask.objects.filter(active=True)
    qs_review = ReviewComplianceTask.objects.filter(
        Q(status=ReviewComplianceTask.Status.VALIDATED) & Q(is_instance=False)
    )
    if today.month == 1 and today.day == 1:
        qs = qs.filter(
            Q(occurrence=ComplianceTask.Occurrence.YEARLY) | Q(occurrence=ComplianceTask.Occurrence.MONTHLY)
        )
        qs_review = qs_review.filter(
            Q(occurrence=ReviewComplianceTask.Occurrence.YEARLY)
            | Q(occurrence=ReviewComplianceTask.Occurrence.MONTHLY)
        )
    elif today.month % 3 == 0:
        qs = qs.filter(
            Q(occurrence=ComplianceTask.Occurrence.QUARTERLY) | Q(occurrence=ComplianceTask.Occurrence.MONTHLY)
        )
        qs_review = qs_review.filter(
            Q(occurrence=ReviewComplianceTask.Occurrence.QUARTERLY)
            | Q(occurrence=ReviewComplianceTask.Occurrence.MONTHLY)
        )
    else:
        qs = qs.filter(occurrence=ComplianceTask.Occurrence.MONTHLY)
        qs_review = qs_review.filter(occurrence=ReviewComplianceTask.Occurrence.MONTHLY)

    for review_task in qs_review:
        review_task.generate_review_compliance_task_instance(notify_admin=True)

    for task in qs:
        task.generate_compliance_task_instance(link_instance_review=True)
