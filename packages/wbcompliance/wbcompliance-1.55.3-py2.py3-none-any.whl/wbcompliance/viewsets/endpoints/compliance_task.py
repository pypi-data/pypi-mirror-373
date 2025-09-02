from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig

from wbcompliance.models import ComplianceType, ReviewComplianceTask


class ComplianceTaskGroupEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        if ComplianceType.is_administrator(self.request.user):
            return super().get_endpoint()
        return None


class ComplianceTaskEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        if ComplianceType.is_administrator(self.request.user):
            return super().get_endpoint()
        return None


class ComplianceTaskComplianceTaskGroupEndpointConfig(ComplianceTaskEndpointConfig):
    def get_endpoint(self, **kwargs):
        if group_id := self.view.kwargs.get("group_id", None):
            return reverse(
                "wbcompliance:compliancetaskgroup-compliancetask-list", args=[group_id], request=self.request
            )
        return None


class ComplianceTaskInstanceEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        if ComplianceType.is_administrator(self.request.user):
            return super().get_endpoint()
        return None

    def get_create_endpoint(self, **kwargs):
        return None

    def get_delete_endpoint(self, **kwargs):
        if self.request.user.is_superuser:
            return super().get_delete_endpoint()
        return None


class ComplianceTaskInstanceComplianceTaskEndpointConfig(ComplianceTaskInstanceEndpointConfig):
    def get_endpoint(self, **kwargs):
        if ComplianceType.is_administrator(self.request.user):
            return reverse(
                "wbcompliance:compliancetask-compliancetaskinstance-list",
                args=[self.view.kwargs["task_id"]],
                request=self.request,
            )
        return None


class ComplianceTaskMatrixEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        if ComplianceType.is_administrator(self.request.user):
            return reverse("wbcompliance:compliancetaskmatrix-list", [], request=self.request)
        return None

    def get_create_endpoint(self, **kwargs):
        return None

    def get_instance_endpoint(self, **kwargs):
        return None


class ComplianceActionEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        if ComplianceType.is_administrator(self.request.user):
            return super().get_endpoint()
        return None


class ComplianceEventEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return super().get_endpoint()

    def get_instance_endpoint(self, **kwargs):
        if self.instance:
            obj = self.view.get_object()
            if not ComplianceType.is_administrator(self.request.user) and obj.creator != self.request.user.profile:
                return None
        return super().get_instance_endpoint()

    def get_delete_endpoint(self, **kwargs):
        if ComplianceType.is_administrator(self.request.user):
            return super().get_delete_endpoint()
        return None


class ReviewComplianceTaskEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        if ComplianceType.is_administrator(self.request.user):
            return super().get_endpoint()
        return None

    def get_instance_endpoint(self, **kwargs):
        if self.instance:
            if not ComplianceType.is_administrator(self.request.user):
                return None
            if obj_id := self.view.kwargs.get("pk", None):
                obj = ReviewComplianceTask.objects.get(id=obj_id)
                if obj.status != ReviewComplianceTask.Status.DRAFT:
                    return None
        return super().get_instance_endpoint()

    def get_delete_endpoint(self, **kwargs):
        if not ComplianceType.is_administrator(self.request.user):
            return None
        if obj_id := self.view.kwargs.get("pk", None):
            obj = ReviewComplianceTask.objects.get(id=obj_id)
            if obj.status != ReviewComplianceTask.Status.DRAFT or obj.is_instance:
                return None
        return super().get_delete_endpoint()


class AbstractComplianceTaskReviewEndpointConfig(EndpointViewConfig):
    def get_instance_endpoint(self, **kwargs):
        if self.instance:
            if not ComplianceType.is_administrator(self.request.user):
                return None
            if review_id := self.view.kwargs.get("review_id", None):
                obj = ReviewComplianceTask.objects.get(id=review_id)
                if obj.status != ReviewComplianceTask.Status.DRAFT:
                    return None
        return super().get_instance_endpoint()

    def get_create_endpoint(self, **kwargs):
        if not ComplianceType.is_administrator(self.request.user):
            return None
        if review_id := self.view.kwargs.get("review_id", None):
            obj = ReviewComplianceTask.objects.get(id=review_id)
            if obj.status != ReviewComplianceTask.Status.DRAFT:
                return None
        return super().get_create_endpoint()

    def get_delete_endpoint(self, **kwargs):
        if not ComplianceType.is_administrator(self.request.user):
            return None
        if review_id := self.view.kwargs.get("review_id", None):
            obj = ReviewComplianceTask.objects.get(id=review_id)
            if obj.status != ReviewComplianceTask.Status.DRAFT:
                return None
        return super().get_delete_endpoint()


class ComplianceTaskReviewNoGroupEndpointConfig(AbstractComplianceTaskReviewEndpointConfig):
    def get_endpoint(self, **kwargs):
        if ComplianceType.is_administrator(self.request.user):
            if review_id := self.view.kwargs.get("review_id", None):
                return reverse(
                    "wbcompliance:review-compliancetasknogroup-list", args=[review_id], request=self.request
                )
        return None


class ComplianceTaskReviewGroupEndpointConfig(AbstractComplianceTaskReviewEndpointConfig):
    def get_endpoint(self, **kwargs):
        if (
            ComplianceType.is_administrator(self.request.user)
            and (review_id := self.view.kwargs.get("review_id", None))
            and (group_id := self.view.kwargs.get("group_id", None))
        ):
            return reverse(
                "wbcompliance:review-compliancetaskgroup-list", args=[review_id, group_id], request=self.request
            )
        return None


class ComplianceTaskInstanceReviewNoGroupEndpointConfig(ComplianceTaskInstanceEndpointConfig):
    def get_endpoint(self, **kwargs):
        if ComplianceType.is_administrator(self.request.user) and (
            review_id := self.view.kwargs.get("review_id", None)
        ):
            return reverse(
                "wbcompliance:review-compliancetaskinstancenogroup-list", args=[review_id], request=self.request
            )
        return None


class ComplianceTaskInstanceReviewGroupEndpointConfig(ComplianceTaskInstanceEndpointConfig):
    def get_endpoint(self, **kwargs):
        if ComplianceType.is_administrator(self.request.user):
            if (review_id := self.view.kwargs.get("review_id", None)) and (
                group_id := self.view.kwargs.get("group_id", None)
            ):
                return reverse(
                    "wbcompliance:review-compliancetaskinstancegroup-list",
                    args=[review_id, group_id],
                    request=self.request,
                )
        return None
