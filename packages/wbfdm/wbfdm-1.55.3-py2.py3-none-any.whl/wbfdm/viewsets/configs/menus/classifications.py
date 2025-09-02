from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

ClassificationMenuItem = MenuItem(
    label="Classification",
    endpoint="wbfdm:classification-list",
    permission=ItemPermission(
        permissions=["wbfdm.view_classification"],
        method=lambda request: is_internal_user(request.user),
    ),
)
ClassificationGroupMenuItem = MenuItem(
    label="Classification Group",
    endpoint="wbfdm:classificationgroup-list",
    permission=ItemPermission(
        permissions=["wbfdm.view_classificationgroup"],
        method=lambda request: is_internal_user(request.user),
    ),
)
