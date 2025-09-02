from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

INSTRUMENT_LIST_MENUITEM = MenuItem(
    label="Instrument Lists",
    endpoint="wbfdm:instrumentlist-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbfdm.view_instrumentlist"]
    ),
)
