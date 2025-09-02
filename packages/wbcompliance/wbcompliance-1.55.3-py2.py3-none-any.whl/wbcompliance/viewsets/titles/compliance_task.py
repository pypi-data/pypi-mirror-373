from django.utils.translation import gettext as _
from wbcore.metadata.configs.titles import TitleViewConfig

from wbcompliance.models import ComplianceTaskGroup


class ComplianceTaskMatrixPandasTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Indicator Matrix")


class ComplianceTaskComplianceTaskGroupTitleConfig(TitleViewConfig):
    def get_list_title(self):
        if group_id := self.view.kwargs.get("group_id"):
            group = ComplianceTaskGroup.objects.get(id=group_id)
            return _("Indicators of Group: {}").format(group.name)
        return self.get_list_title()


class ComplianceTaskTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Indicator: {{title}}")

    def get_list_title(self):
        return _("Indicators")

    def get_create_title(self):
        return _("New Indicator")


class ComplianceTaskGroupTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Group Indicator: {{name}}")

    def get_list_title(self):
        return _("Groups Indicator")

    def get_create_title(self):
        return _("New Group Indicator")


class ComplianceTaskInstanceTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Instance Indicator: {{_task.title}} -  {{occured}}")

    def get_list_title(self):
        return _("Instances Indicator")

    def get_create_title(self):
        return _("New Instance Indicator")


class ReviewComplianceTaskTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Report Indicator: {{computed_str}}")

    def get_list_title(self):
        return _("Reports Indicator")

    def get_create_title(self):
        return _("New Report Indicator")
