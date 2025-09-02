from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

ExchangeMenuItem = MenuItem(
    label="Exchange",
    endpoint="wbfdm:exchange-list",
    permission=ItemPermission(
        permissions=["wbfdm.view_exchange"], method=lambda request: is_internal_user(request.user)
    ),
)
