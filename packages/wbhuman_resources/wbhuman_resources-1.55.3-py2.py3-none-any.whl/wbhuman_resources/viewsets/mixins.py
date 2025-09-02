from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property

from wbhuman_resources.models.employee import EmployeeHumanResource


class EmployeeViewMixin:
    @cached_property
    def employee(self):
        return get_object_or_404(EmployeeHumanResource, profile=self.request.user.profile)

    @cached_property
    def is_administrator(self):
        return EmployeeHumanResource.is_administrator(self.request.user)
