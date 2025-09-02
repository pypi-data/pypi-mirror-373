from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

INSTRUMENT_MENUITEM = MenuItem(
    label="Instrument",
    endpoint="wbfdm:instrument-list",
    endpoint_get_parameters={"parent__isnull": True},
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbfdm.view_instrument"]
    ),
)

INVESTABLE_UNIVERSE_MENUITEM = MenuItem(
    label="Investable Universe",
    endpoint="wbfdm:instrument-list",
    endpoint_get_parameters={"is_investable_universe": True},
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbfdm.view_instrument"]
    ),
)
