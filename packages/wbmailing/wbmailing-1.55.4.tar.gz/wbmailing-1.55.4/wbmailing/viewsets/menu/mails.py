from django.utils.translation import gettext as _
from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

MASSMAIL_MENUITEM = MenuItem(
    label=_("Mass Mail"),
    endpoint="wbmailing:massmail-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbmailing.view_massmail"]
    ),
    add=MenuItem(
        label=_("Create Mass Mail"),
        endpoint="wbmailing:massmail-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbmailing.add_massmail"]
        ),
    ),
)
MAIL_MENUITEM = MenuItem(
    label=_("Mails"),
    endpoint="wbmailing:mail-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbmailing.view_mail"]
    ),
)
