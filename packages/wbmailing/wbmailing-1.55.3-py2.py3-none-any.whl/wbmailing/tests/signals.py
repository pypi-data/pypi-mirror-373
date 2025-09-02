from django.dispatch import receiver
from wbcore.contrib.directory.models import EmailContact
from wbcore.test.signals import (
    custom_update_data_from_factory,
    custom_update_kwargs,
    get_custom_factory,
)

from wbmailing.factories import (
    CustomMassMailFactory,
    EmailContactFactory,
    MailEventFactory,
    MailFactory,
    MailingListFactory,
    MailingListSubscriberChangeRequestFactory,
    MassMailFactory,
    ToEmailMailFactory,
)
from wbmailing.models import MailingListSubscriberChangeRequest
from wbmailing.viewsets import (
    EmailContactMailingListModelViewSet,
    MailEventMassMailMailModelViewSet,
    MailingListEntryModelViewSet,
    MailingListSubscriberChangeRequestModelViewSet,
    MailingListSubscriberRequestEntryModelViewSet,
    MailingListSubscriberRequestMailingListModelViewSet,
    MailMailingListChartViewSet,
    MailModelViewSet,
    MailStatusMassMailModelViewSet,
    MassMailModelViewSet,
)

# =================================================================================================================
#                                              CUSTOM FACTORY
# =================================================================================================================


@receiver(get_custom_factory, sender=MassMailModelViewSet)
def receive_factory_mass_mail(sender, *args, **kwargs):
    return CustomMassMailFactory


@receiver(get_custom_factory, sender=MailModelViewSet)
def receive_factory_toemail(sender, *args, **kwargs):
    return ToEmailMailFactory


@receiver(get_custom_factory, sender=MailStatusMassMailModelViewSet)
def receive_factory_email(sender, *args, **kwargs):
    return EmailContactFactory


# =================================================================================================================
#                                              UPDATE DATA
# =================================================================================================================


@receiver(custom_update_data_from_factory, sender=MailingListSubscriberRequestMailingListModelViewSet)
@receiver(custom_update_data_from_factory, sender=MailingListSubscriberChangeRequestModelViewSet)
def receive_data_mailinglist_subscriber(sender, *args, **kwargs):
    if obj := kwargs.get("obj_factory"):
        obj.status = MailingListSubscriberChangeRequest.Status.APPROVED
        obj.save()
        # return {"mailing_list": obj.mailing_list.id }
    return {}


@receiver(custom_update_data_from_factory, sender=MailingListSubscriberRequestEntryModelViewSet)
def receive_data_mailinglistrequest_entry_subscriber(sender, *args, **kwargs):
    if obj := kwargs.get("obj_factory"):
        obj.status = MailingListSubscriberChangeRequest.Status.APPROVED
        obj.save()
        return {"entry_id": obj.email_contact.entry.id}
    return {}


@receiver(custom_update_data_from_factory, sender=EmailContactMailingListModelViewSet)
def receive_data_email_contact_mailinglist(sender, *args, **kwargs):
    if obj := kwargs.get("obj_factory"):
        mlscr = MailingListSubscriberChangeRequestFactory(
            status=MailingListSubscriberChangeRequest.Status.APPROVED, mailing_list=obj.mailing_list
        )
        return {"email_contact": mlscr.email_contact.id}
    return {}


# =================================================================================================================
#                                              UPDATE KWARGS
# =================================================================================================================


@receiver(custom_update_kwargs, sender=MailStatusMassMailModelViewSet)
def receive_kwargs_mass_mail_mail(sender, *args, **kwargs):
    if obj := kwargs.get("obj_factory"):
        ml = MailingListFactory.create(email_contacts=[obj])
        mass_mail = MassMailFactory.create(mailing_lists=[ml])
        MailEventFactory.create(recipient=obj.address)
        MailFactory.create(mass_mail=mass_mail, to_email=[obj])
        return {"mass_mail_id": mass_mail.id}
    return {}


@receiver(custom_update_kwargs, sender=MailEventMassMailMailModelViewSet)
def receive_kwargs_mail_event_massmail(sender, *args, **kwargs):
    if obj := kwargs.get("obj_factory"):
        return {"mass_mail_id": obj.mail.mass_mail.id}
    return {}


@receiver(custom_update_kwargs, sender=MailingListEntryModelViewSet)
def receive_kwargs_mailing_list_entry(sender, *args, **kwargs):
    if email_id := kwargs.get("email_contact_id", None):
        ec = EmailContact.objects.get(id=email_id)
        return {"entry_id": ec.entry.id}
    return {}


@receiver(custom_update_kwargs, sender=MailingListSubscriberRequestEntryModelViewSet)
def receive_kwargs_mailing_list_subscriber_entry(sender, *args, **kwargs):
    if kwargs.get("email_contact_id"):
        sec = kwargs.get("email_contact_id")
        ec = EmailContact.objects.filter(id=sec).first()
        return {"entry_id": ec.entry.id}
    return {}


@receiver(custom_update_kwargs, sender=MailMailingListChartViewSet)
def receive_kwargs_mail_mailing_list(sender, *args, **kwargs):
    if obj := kwargs.get("obj_factory"):
        ml = MailingListFactory()
        obj.mass_mail.mailing_lists.add(ml)
        return {"mailing_list_id": ml.id}
    return {}
