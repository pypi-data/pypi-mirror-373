from django.dispatch import receiver
from wbcore.test.signals import (
    custom_update_data_from_factory,
    custom_update_kwargs,
    get_custom_factory,
)

from wbcompliance.factories import (
    ComplianceTaskInstanceReviewFactory,
    ComplianceTaskInstanceReviewNoGroupFactory,
    ComplianceTaskReviewFactory,
    ComplianceTaskReviewNoGroupFactory,
)
from wbcompliance.viewsets import (
    CFComplianceFormSignatureModelViewSet,
    ComplianceFormSignatureModelViewSet,
    ComplianceFormSignatureSectionRuleViewSet,
    ComplianceTaskInstanceReviewGroupModelViewSet,
    ComplianceTaskInstanceReviewNoGroupModelViewSet,
    ComplianceTaskReviewGroupModelViewSet,
    ComplianceTaskReviewNoGroupModelViewSet,
)

# =================================================================================================================
#                                              CUSTOM FACTORY
# =================================================================================================================


@receiver(get_custom_factory, sender=ComplianceTaskReviewNoGroupModelViewSet)
def receive_factory_compliance_task_review_no_group(sender, *args, **kwargs):
    return ComplianceTaskReviewNoGroupFactory


@receiver(get_custom_factory, sender=ComplianceTaskReviewGroupModelViewSet)
def receive_factory_compliance_task_review(sender, *args, **kwargs):
    return ComplianceTaskReviewFactory


@receiver(get_custom_factory, sender=ComplianceTaskInstanceReviewNoGroupModelViewSet)
def receive_factory_compliance_task_instance_review_no_group(sender, *args, **kwargs):
    return ComplianceTaskInstanceReviewNoGroupFactory


@receiver(get_custom_factory, sender=ComplianceTaskInstanceReviewGroupModelViewSet)
def receive_factory_compliance_task_review_group(sender, *args, **kwargs):
    return ComplianceTaskInstanceReviewFactory


# =================================================================================================================
#                                              UPDATE DATA
# =================================================================================================================


@receiver(custom_update_data_from_factory, sender=ComplianceFormSignatureSectionRuleViewSet)
def receive_data_compliance_form_signature_section(sender, *args, **kwargs):
    if (obj := kwargs.get("obj_factory")) and (user := kwargs.get("user")):
        obj.section.compliance_form_signature.person = user.profile
        obj.section.compliance_form_signature.save()
    return {}


@receiver(custom_update_data_from_factory, sender=ComplianceFormSignatureModelViewSet)
@receiver(custom_update_data_from_factory, sender=CFComplianceFormSignatureModelViewSet)
def receive_data_compliance_form_signature(sender, *args, **kwargs):
    if (obj := kwargs.get("obj_factory")) and (user := kwargs.get("user")):
        obj.person = user.profile
        obj.signed = None
        obj.save()
    return {}


# =================================================================================================================
#                                              UPDATE KWARGS
# =================================================================================================================


@receiver(custom_update_kwargs, sender=ComplianceTaskInstanceReviewNoGroupModelViewSet)
@receiver(custom_update_kwargs, sender=ComplianceTaskReviewGroupModelViewSet)
@receiver(custom_update_kwargs, sender=ComplianceTaskReviewNoGroupModelViewSet)
def receive_kwargs_compliance_task_review(sender, *args, **kwargs):
    if (obj := kwargs.get("obj_factory")) and obj.review.exists():
        return {"review_id": obj.review.first().id}
    return {}


@receiver(custom_update_kwargs, sender=ComplianceTaskInstanceReviewGroupModelViewSet)
def receive_kwargs_compliance_task_instance_review(sender, *args, **kwargs):
    if (obj := kwargs.get("obj_factory")) and obj.review.exists():
        return {"review_id": obj.review.first().id, "group_id": obj.task.group.id}
    return {}
