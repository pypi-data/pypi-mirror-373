from django.utils.translation import gettext as _
from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

EMPLOYEEHUMANRESOURCE_MENUITEM = MenuItem(
    label=_("Balance & Usage"),
    endpoint="wbhuman_resources:employeebalance-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user),
        permissions=["wbhuman_resources.view_employeehumanresource"],
    ),
)

EMPLOYEE_MENUITEM = MenuItem(
    label=_("Employees"),
    endpoint="wbhuman_resources:employee-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user),
        permissions=["wbhuman_resources.view_employeehumanresource"],
    ),
    add=MenuItem(
        label=_("Add Employee"),
        endpoint="wbhuman_resources:employee-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user),
            permissions=["wbhuman_resources.add_employeehumanresource"],
        ),
    ),
)

POSITION_MENUITEM = MenuItem(
    label=_("Positions"),
    endpoint="wbhuman_resources:position-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.view_position"]
    ),
    add=MenuItem(
        label=_("Add Position"),
        endpoint="wbhuman_resources:position-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.add_position"]
        ),
    ),
)
