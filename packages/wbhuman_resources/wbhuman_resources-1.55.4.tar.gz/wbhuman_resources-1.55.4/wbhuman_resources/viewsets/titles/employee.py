from django.utils.translation import gettext as _
from wbcore.metadata.configs.titles import TitleViewConfig


class EmployeeBalanceTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Balance & Usage: {{_profile.first_name}} {{_profile.last_name}}")

    def get_list_title(self):
        return _("Balance & Usage")


class EmployeeTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return _("Employee: {{_profile.first_name}} {{_profile.last_name}}")

    def get_list_title(self):
        return _("Employees")
