from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from django.db.models import Q
from django.utils import timezone
from faker import Faker

from wbmailing.factories import MailingListSubscriberChangeRequestFactory
from wbmailing.models import MassMail
from wbmailing.models.mailing_lists import MailingListEmailContactThroughModel
from wbmailing.tasks import (
    check_and_remove_expired_mailinglist_subscription,
    periodic_send_mass_mail_as_tasks,
)

fake = Faker()


@pytest.mark.django_db
class TestSpecificTasks:
    @pytest.mark.parametrize("expiration_date", [fake.past_date()])
    def test_check_and_remove_expired_mailinglist_subscription(self, expiration_date, mailing_list, email_contact):
        request = MailingListSubscriberChangeRequestFactory(
            expiration_date=expiration_date, email_contact=email_contact, mailing_list=mailing_list
        )
        request.approve()
        request.save()
        assert request.relationship.status == MailingListEmailContactThroughModel.Status.SUBSCRIBED

        check_and_remove_expired_mailinglist_subscription()
        request.refresh_from_db()
        assert request.relationship.status == MailingListEmailContactThroughModel.Status.UNSUBSCRIBED
        request.refresh_from_db()
        assert request.expiration_date is None

    @patch("wbmailing.models.mails.send_mail_task.delay")
    def test_periodic_tasks(self, send_mail_task, mass_mail_factory):
        mass_mail_factory(status=MassMail.Status.PENDING, send_at=None)
        send_date = timezone.now() - timedelta(minutes=15)
        mass_mail_factory(status=MassMail.Status.SEND_LATER, send_at=send_date)
        assert (
            MassMail.objects.filter(Q(status=MassMail.Status.SEND_LATER) & Q(send_at__lte=datetime.now())).count() == 1
        )
        periodic_send_mass_mail_as_tasks()
        send_mail_task.assert_called()
        assert send_mail_task.call_count == 1
        assert (
            MassMail.objects.filter(Q(status=MassMail.Status.SEND_LATER) & Q(send_at__lte=datetime.now())).count() == 0
        )
