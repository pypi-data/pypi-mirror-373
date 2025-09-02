from django.utils.translation import gettext as _
from wbcore.metadata.configs.titles import TitleViewConfig

from wbhuman_resources.models import EmployeeHumanResource


class AbsenceRequestPlannerTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Absence Graph")


class AbsenceTypeCountEmployeeTitleConfig(TitleViewConfig):
    def get_list_title(self):
        employee = EmployeeHumanResource.objects.get(id=self.view.kwargs["employee_id"])
        return _("Absence for {employee}").format(employee=str(employee))


class AbsenceRequestEmployeeBalanceTitleConfig(TitleViewConfig):
    def get_list_title(self):
        employee = EmployeeHumanResource.objects.get(id=self.view.kwargs["employee_id"])
        return _("Absence Requests for {employee}").format(employee=str(employee))

    def get_create_title(self):
        employee = EmployeeHumanResource.objects.get(id=self.view.kwargs["employee_id"])
        return _("Absence Request for {employee}").format(employee=str(employee))


class AbsenceTablePandasTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Weekly Presence Table")
