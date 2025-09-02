from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

INSTRUMENTFAVORITEGROUP_MENUITEM = MenuItem(
    label="Favorite Group",
    endpoint="wbfdm:favoritegroup-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbfdm.view_instrumentfavoritegroup"]
    ),
)

CLASSIFIEDINSTRUMENTS_MENUITEM = MenuItem(
    label="Classified Instruments",
    endpoint="wbfdm:classifiedinstrument-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbfdm.view_instrument"]
    ),
)

INSTRUMENT_REQUEST_MENUITEM = MenuItem(
    label="Instrument Requests",
    endpoint="wbfdm:instrumentrequest-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbfdm.view_instrumentrequest"]
    ),
    add=MenuItem(
        label="Create Instrument Request",
        endpoint="wbfdm:instrumentrequest-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbfdm.add_instrumentrequest"]
        ),
    ),
)
