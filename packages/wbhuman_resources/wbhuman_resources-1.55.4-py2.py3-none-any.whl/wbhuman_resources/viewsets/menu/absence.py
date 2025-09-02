from django.utils.translation import gettext as _
from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

ABSENCEPLANNER_MENUITEM = MenuItem(
    label=_("Absence Graph"),
    endpoint="wbhuman_resources:absenceplanner-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.view_absencerequest"]
    ),
)

ABSENCETABLE_MENUITEM = MenuItem(
    label=_("Presence Table"),
    endpoint="wbhuman_resources:absencetable-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.view_absencerequest"]
    ),
)

ABSENCEREQUEST_MENUITEM = MenuItem(
    label=_("Requests"),
    endpoint="wbhuman_resources:absencerequest-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.view_absencerequest"]
    ),
    add=MenuItem(
        label=_("Add Requests"),
        endpoint="wbhuman_resources:absencerequest-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.add_absencerequest"]
        ),
    ),
)

ABSENCEREQUESTTYPE_MENUITEM = MenuItem(
    label=_("Request Types"),
    endpoint="wbhuman_resources:absencerequesttype-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.view_absencerequesttpe"]
    ),
    add=MenuItem(
        label=_("Add Request Types"),
        endpoint="wbhuman_resources:absencerequesttype-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user),
            permissions=["wbhuman_resources.add_absencerequesttype"],
        ),
    ),
)
