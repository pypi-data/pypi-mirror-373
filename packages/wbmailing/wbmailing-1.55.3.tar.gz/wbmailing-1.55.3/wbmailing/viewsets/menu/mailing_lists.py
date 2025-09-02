from django.utils.translation import gettext as _
from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

from wbmailing.models.mailing_lists import MailingListSubscriberChangeRequest

MAILINGLIST_MENUITEM = MenuItem(
    label=_("Mailing Lists"),
    endpoint="wbmailing:mailinglist-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbmailing.view_mailinglist"]
    ),
    add=MenuItem(
        label=_("Create Mailing List"),
        endpoint="wbmailing:mailinglist-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbmailing.add_mailinglist"]
        ),
    ),
)

MAILINGLISTSUBSCRIPTIONCHANGEREQUEST_MENUITEM = MenuItem(
    label=_("Subscription Requests"),
    endpoint="wbmailing:mailinglistsubscriberchangerequest-list",
    endpoint_get_parameters={"status": MailingListSubscriberChangeRequest.Status.PENDING.value},
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user),
        permissions=["wbmailing.view_mailinglistsubscriberchangerequest"],
    ),
    add=MenuItem(
        label=_("Create Subscription Request"),
        endpoint="wbmailing:mailinglistsubscriberchangerequest-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user),
            permissions=["wbmailing.add_mailinglistsubscriberchangerequest"],
        ),
    ),
)
