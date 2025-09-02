from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

INSTRUMENTMETRIC_MENUITEM = MenuItem(
    label="Metrics",
    endpoint="metric:instrumentmetric-list",
    endpoint_get_parameters={"parent_metric__isnull": True},
    permission=ItemPermission(
        permissions=["metric.view_instrumentmetric"], method=lambda request: is_internal_user(request.user)
    ),
)
