from django.urls import include, path
from wbcore.routers import WBCoreRouter

from wbmailing import viewsets

router = WBCoreRouter()
router.register(r"mailinglist", viewsets.MailingListModelViewSet)
router.register(r"mailrepresentation", viewsets.MailRepresentationViewSet, basename="mailrepresentation")
router.register(
    r"mailinglistrepresentation", viewsets.MailingListRepresentationViewSet, basename="mailinglistrepresentation"
)
router.register(
    r"mailtemplaterepresentation", viewsets.MailTemplateRepresentationViewSet, basename="mailtemplaterepresentation"
)
router.register(r"massmailrepresentation", viewsets.MassMailRepresentationViewSet, basename="massmailrepresentation")


router.register(r"massmail", viewsets.MassMailModelViewSet)
router.register(r"mailevent", viewsets.MailEventModelViewSet)
router.register(r"mail", viewsets.MailModelViewSet)
router.register(r"mailtemplate", viewsets.MailTemplateModelViewSet)
router.register(
    r"mailinglistsubscriberchangerequest",
    viewsets.MailingListSubscriberChangeRequestModelViewSet,
    basename="mailinglistsubscriberchangerequest",
)
router.register(
    "mailinglistemailcontact",
    viewsets.MailingListEmailContactThroughModelModelViewSet,
    basename="mailinglistemailcontact",
)

entry_router = WBCoreRouter()
entry_router.register(r"mailinglist", viewsets.MailingListEntryModelViewSet, basename="entry-mailinglist")


entry_router.register(
    r"mailinglistsubscriberchangerequest",
    viewsets.MailingListSubscriberRequestEntryModelViewSet,
    basename="entry-mailinglistsubscriberchangerequest",
)

mailinglist_router = WBCoreRouter()
mailinglist_router.register(
    r"mailinglistsubscriberchangerequest",
    viewsets.MailingListSubscriberRequestMailingListModelViewSet,
    basename="mailing_list-mailinglistsubscriberchangerequest",
)
mailinglist_router.register(
    r"email_contacts",
    viewsets.EmailContactMailingListModelViewSet,
    basename="mailing_list-email_contacts",
)
mailinglist_router.register(
    r"maileventchart", viewsets.MailMailingListChartViewSet, basename="mailing_list-maileventchart"
)


mail_router = WBCoreRouter()
mail_router.register(r"mailevent", viewsets.MailEventMailModelViewSet, basename="mail-mailevent")

massmail_router = WBCoreRouter()
massmail_router.register(r"mailstatus", viewsets.MailStatusMassMailModelViewSet, basename="massmail-mailstatus")
massmail_router.register(
    r"mailstatusbarchart", viewsets.MailStatusBarChartViewSet, basename="massmail-mailstatusbarchart"
)
massmail_router.register(
    r"mailclickbarchart", viewsets.MailClickBarChartViewSet, basename="massmail-mailclickbarchart"
)
massmail_router.register(r"clientsbarchart", viewsets.ClientsBarChartViewSet, basename="massmail-clientsbarchart")
massmail_router.register(r"countrybarchart", viewsets.CountryBarChartViewSet, basename="massmail-countrybarchart")
massmail_router.register(r"regionbarchart", viewsets.RegionBarChartViewSet, basename="massmail-regionbarchart")
massmail_router.register("mailevent", viewsets.MailEventMassMailMailModelViewSet, basename="massmail-mailevent")

urlpatterns = [
    path("", include(router.urls)),
    path("entry/<int:entry_id>/", include(entry_router.urls)),
    path("mailing_list/<int:mailing_list_id>/", include(mailinglist_router.urls)),
    path("mail/<int:mail_id>/", include(mail_router.urls)),
    path("massmail/<int:mass_mail_id>/", include(massmail_router.urls)),
    path(
        "manage_mailing_list_subscriptions/<int:email_contact_id>/",
        viewsets.ManageMailingListSubscriptions.as_view(),
        name="manage_mailing_list_subscriptions",
    ),
    path(
        "unsubscribe/<int:email_contact_id>/<int:mailing_list_id>/",
        viewsets.UnsubscribeView.as_view(),
        name="unsubscribe",
    ),
]
