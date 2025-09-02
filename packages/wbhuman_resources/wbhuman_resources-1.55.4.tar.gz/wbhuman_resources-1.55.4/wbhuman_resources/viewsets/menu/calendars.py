from django.utils.translation import gettext as _
from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

DAYOFF_MENUITEM = MenuItem(
    label=_("Days Off"),
    endpoint="wbhuman_resources:dayoff-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.view_dayoff"]
    ),
    add=MenuItem(
        label=_("Add Day Off"),
        endpoint="wbhuman_resources:dayoff-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.add_dayoff"]
        ),
    ),
)

DAYOFFCALENDAR_MENUITEM = MenuItem(
    label=_("Calendars"),
    endpoint="wbhuman_resources:dayoffcalendar-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.view_dayoffcalendar"]
    ),
    add=MenuItem(
        label=_("Add Calendar"),
        endpoint="wbhuman_resources:dayoffcalendar-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.add_dayoffcalendar"]
        ),
    ),
)
