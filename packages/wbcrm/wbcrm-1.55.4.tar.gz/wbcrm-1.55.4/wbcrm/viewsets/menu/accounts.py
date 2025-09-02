from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

ACCOUNT_MENUITEM = MenuItem(
    label="Accounts",
    endpoint="wbcrm:account-list",
    endpoint_get_parameters={"parent__isnull": True},
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbcrm.view_account"]
    ),
    add=MenuItem(
        label="Create Account",
        endpoint="wbcrm:account-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbcrm.add_account"]
        ),
    ),
)
