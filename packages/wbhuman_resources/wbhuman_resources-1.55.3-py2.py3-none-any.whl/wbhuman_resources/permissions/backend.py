from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet
from wbcore.permissions.backend import UserBackend as BaseUserBackend

from wbhuman_resources.models.employee import EmployeeHumanResource

User = get_user_model()


class UserBackend(BaseUserBackend):
    """
    The UserBackend proposed by the human resources module
    """

    def get_internal_users(self) -> "QuerySet[User]":
        """
        Get internal users defined by the human resources module

        Returns:
            A queryset of users
        """
        internal_employee_profiles = EmployeeHumanResource.active_internal_employees.all()
        base_internal_users = super().get_internal_users()
        return User.objects.filter(
            Q(profile__in=internal_employee_profiles.values("profile")) | Q(id__in=base_internal_users.values("id"))
        )
