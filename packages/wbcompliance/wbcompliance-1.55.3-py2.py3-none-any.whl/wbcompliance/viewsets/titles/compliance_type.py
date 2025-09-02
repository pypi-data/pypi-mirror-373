from django.utils.translation import gettext as _
from wbcore.metadata.configs.titles import TitleViewConfig


class ComplianceTypeTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Compliance Administrator: {{name}}")

    def get_list_title(self):
        return _("Compliance Administrators")

    def get_create_title(self):
        return _("New Compliance Administrator")
