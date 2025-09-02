from django.utils.translation import gettext as _
from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

PRODUCT_MENUITEM = MenuItem(
    label=_("Products"),
    endpoint="wbcrm:product-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user),
        permissions=["wbcrm.view_product"],
    ),
    add=MenuItem(
        label=_("Create Product"),
        endpoint="wbcrm:product-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user),
            permissions=["wbcrm.add_product"],
        ),
    ),
)
