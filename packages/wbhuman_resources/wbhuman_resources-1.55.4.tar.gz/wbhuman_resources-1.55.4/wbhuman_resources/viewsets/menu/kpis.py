from django.utils.translation import gettext as _
from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

KPI_MENUITEM = MenuItem(
    label=_("KPIs"),
    endpoint="wbhuman_resources:kpi-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.view_kpi"]
    ),
)
KPIEVALUATIONPANDAS_MENUITEM = MenuItem(
    label=_("KPI Evaluations"),
    endpoint="wbhuman_resources:kpievaluationpandas-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbhuman_resources.view_kpi"]
    ),
)
