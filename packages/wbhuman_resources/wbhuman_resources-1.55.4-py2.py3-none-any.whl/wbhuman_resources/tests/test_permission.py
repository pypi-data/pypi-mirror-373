import pytest
from django.contrib.auth import get_user_model
from dynamic_preferences.registries import global_preferences_registry
from faker import Faker
from rest_framework.test import APIRequestFactory
from wbcore.contrib.authentication.factories import UserFactory
from wbcore.permissions.shortcuts import is_internal_user

from wbhuman_resources.factories.employee import EmployeeHumanResourceFactory
from wbhuman_resources.models.employee import EmployeeHumanResource

User = get_user_model()
fake = Faker()


@pytest.mark.django_db
class TestPermissionTasks:
    @pytest.fixture
    def request_user_external(self):
        request = APIRequestFactory()
        user = UserFactory()
        EmployeeHumanResourceFactory.create(
            profile=user.profile, contract_type=EmployeeHumanResource.ContractType.EXTERNAL
        )
        request.user = user
        return request

    @pytest.fixture
    def request_user_active_internal(self):
        request = APIRequestFactory()
        user = UserFactory()
        EmployeeHumanResourceFactory.create(
            profile=user.profile, contract_type=EmployeeHumanResource.ContractType.INTERNAL
        )
        request.user = user
        return request

    @pytest.fixture
    def request_user_inactive_internal(self):
        request = APIRequestFactory()
        user = UserFactory()
        EmployeeHumanResourceFactory.create(
            profile=user.profile, contract_type=EmployeeHumanResource.ContractType.INTERNAL, is_active=False
        )
        request.user = user
        return request

    def test_permission_active_internal(self, request_user_active_internal):
        assert is_internal_user(request_user_active_internal.user) is True

    def test_permission_inactive_internal(self, request_user_inactive_internal):
        assert is_internal_user(request_user_inactive_internal.user) is False

    def test_permission_external(self, request_user_external):
        assert is_internal_user(request_user_external.user) is False

    def test_permission_external_but_considered_internal(self, request_user_external):
        from wbcore.permissions.registry import user_registry

        user = request_user_external.user
        global_preferences_registry.manager()["wbhuman_resources__is_external_considered_as_internal"] = True
        user = User.objects.get(id=user.id)  # reload to reset cached property
        user_registry.reset_cache()
        assert is_internal_user(user) is True
