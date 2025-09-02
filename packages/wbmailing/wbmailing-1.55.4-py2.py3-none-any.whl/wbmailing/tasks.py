from __future__ import absolute_import, unicode_literals

from datetime import datetime

from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from wbmailing.models import (
    MailingListEmailContactThroughModel,
    MailingListSubscriberChangeRequest,
    MassMail,
)


@shared_task
def check_and_remove_expired_mailinglist_subscription(date=None):
    """
    Shared tasks to expire contact in MailingList.
    """
    if not date:
        date = timezone.now().date()
    for request in MailingListSubscriberChangeRequest.objects.filter(
        relationship__status=MailingListEmailContactThroughModel.Status.SUBSCRIBED,
        expiration_date__isnull=False,
        expiration_date__lte=date,
    ).all():
        request.relationship.change_state(automatically_approve=True, reason="Expired mailing list subscription")
        request.expiration_date = None
        request.save()


@shared_task
def periodic_send_mass_mail_as_tasks():
    mass_mails = MassMail.objects.filter(Q(status=MassMail.Status.SEND_LATER) & Q(send_at__lte=datetime.now()))
    for mass_mail in mass_mails:
        mass_mail.send()
        mass_mail.save()
