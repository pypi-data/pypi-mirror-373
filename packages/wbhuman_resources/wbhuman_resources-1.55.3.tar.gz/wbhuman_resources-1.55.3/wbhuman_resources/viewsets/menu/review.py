from django.utils.translation import gettext as _
from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

REVIEWGROUP_MENUITEM = MenuItem(
    label=_("Groups"),
    endpoint="wbhuman_resources:reviewgroup-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.view_reviewgroup"]
    ),
    add=MenuItem(
        label=_("Add Group"),
        endpoint="wbhuman_resources:reviewgroup-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.add_reviewgroup"]
        ),
    ),
)


REVIEW_MENUITEM = MenuItem(
    label=_("Employee Reviews"),
    endpoint="wbhuman_resources:review-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.view_review"]
    ),
    add=MenuItem(
        label=_("Add Review"),
        endpoint="wbhuman_resources:review-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.add_review"]
        ),
    ),
)

REVIEWTEMPLATE_MENUITEM = MenuItem(
    label=_("Templates"),
    endpoint="wbhuman_resources:reviewtemplate-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.add_review"]
    ),
    add=MenuItem(
        label=_("Add Template"),
        endpoint="wbhuman_resources:reviewtemplate-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.add_review"]
        ),
    ),
)

REVIEWQUESTIONCATEFORY_MENUITEM = MenuItem(
    label=_("Categories"),
    endpoint="wbhuman_resources:reviewquestioncategory-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user),
        permissions=["wbhuman_resources.view_reviewquestioncategory"],
    ),
    add=MenuItem(
        label=_("Add Question Category"),
        endpoint="wbhuman_resources:reviewquestioncategory-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user),
            permissions=["wbhuman_resources.add_reviewquestioncategory"],
        ),
    ),
)

REVIEWQUESTION_MENUITEM = MenuItem(
    label=_("Questions"),
    endpoint="wbhuman_resources:reviewquestion-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.view_reviewquestion"]
    ),
    add=MenuItem(
        label=_("Add Question"),
        endpoint="wbhuman_resources:reviewquestion-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.add_reviewquestion"]
        ),
    ),
)


REVIEWANDWER_MENUITEM = MenuItem(
    label=_("Answers"),
    endpoint="wbhuman_resources:reviewanswer-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.view_reviewanswer"]
    ),
    add=MenuItem(
        label=_("Add Review"),
        endpoint="wbhuman_resources:reviewanswer-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.add_reviewanswer"]
        ),
    ),
)
