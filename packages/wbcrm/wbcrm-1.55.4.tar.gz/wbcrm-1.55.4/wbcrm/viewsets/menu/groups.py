from django.utils.translation import gettext as _
from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

GROUPS_MENUITEM = MenuItem(
    label=_("Groups"),
    endpoint="wbcrm:group-list",
    permission=ItemPermission(method=lambda request: is_internal_user(request.user), permissions=["wbcrm.view_group"]),
    add=MenuItem(
        label=_("Create Groups"),
        endpoint="wbcrm:group-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbcrm.add_group"]
        ),
    ),
)
