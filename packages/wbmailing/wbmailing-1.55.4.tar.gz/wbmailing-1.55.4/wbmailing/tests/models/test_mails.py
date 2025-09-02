from unittest.mock import patch

import pytest
from anymail.signals import AnymailTrackingEvent, tracking
from django.core import mail
from django.test import override_settings
from rest_framework.test import APIRequestFactory
from wbcore.contrib.directory.factories import EmailContactFactory
from wbcore.contrib.documents.factories import DocumentFactory
from wbcore.test.utils import get_or_create_superuser

from wbmailing.backend import SendgridEmailBackend
from wbmailing.factories import ToEmailMailFactory
from wbmailing.models import MailEvent, MassMail
from wbmailing.models.mails import (
    can_administrate_mail,
    send_mail_task,
    send_mass_mail_as_task,
)


@pytest.mark.django_db
class TestSpecificModels:
    @patch("wbmailing.models.mails.send_mass_mail_as_task.delay")
    def test_send_mail_task(self, send_mass_mail_as_task, mass_mail_factory, mailing_list_factory):
        ec = EmailContactFactory()
        ml = mailing_list_factory(email_contacts=(ec,))
        mm = mass_mail_factory(mailing_lists=(ml,))

        send_mail_task(mm.id)
        send_mass_mail_as_task.assert_called()
        assert send_mass_mail_as_task.call_count == 1

    def test_send_mass_mail_as_task(self, mass_mail_factory, mailing_list_factory):
        ec = EmailContactFactory()
        ml = mailing_list_factory(email_contacts=(ec,))
        mass_mail = mass_mail_factory(mailing_lists=(ml,))
        assert len(mail.outbox) == 0
        for subscriber in mass_mail.get_mail_addresses():
            send_mass_mail_as_task(mass_mail.id, subscriber["address"])
        assert len(mail.outbox) == 1

    @pytest.mark.parametrize("status, expected", [("PENDING", "DENIED")])
    def test_deny(self, mailing_list_subscriber_change_request_factory, status, expected):
        mlscr = mailing_list_subscriber_change_request_factory()
        mlscr.deny(description="SPAM")
        assert mlscr.status == expected

    @pytest.mark.parametrize("status, expected", [("DRAFT", "PENDING")])
    def test_submit(self, mass_mail_factory, status, expected):
        ml = mass_mail_factory()
        ml.submit()
        assert ml.status == expected

    @pytest.mark.parametrize("status, expected", [("PENDING", "DENIED")])
    def test_deny2(self, mass_mail_factory, status, expected):
        ml = mass_mail_factory(status=MassMail.Status.PENDING)
        ml.deny()
        assert ml.status == expected

    @pytest.mark.parametrize("status, expected", [("PENDING", "DRAFT")])
    def test_revise(self, mass_mail_factory, status, expected):
        ml = mass_mail_factory(status=MassMail.Status.PENDING)
        ml.revise()
        assert ml.status == expected

    @patch("wbmailing.models.mails.send_mail_task.delay")
    def test_send(self, send_mail_task, mass_mail_factory):
        mm = mass_mail_factory(status=MassMail.Status.PENDING)
        mm.send()
        send_mail_task.assert_called()
        assert send_mail_task.call_count == 1

    def test_create_email(self, mass_mail_factory):
        request = APIRequestFactory().get("")
        request.user = get_or_create_superuser()
        mm = mass_mail_factory(attachments=(DocumentFactory(),))
        EmailContactFactory(address=request.user.email)
        mm.template = None
        mm.save()
        msg = mm.create_email(request.user.email)
        assert msg

    @patch("wbmailing.models.mails.send_mail_as_task.delay")
    def test_resend_no_massmail(self, send_mail_as_task):
        request = APIRequestFactory().get("")
        request.user = get_or_create_superuser()
        obj = ToEmailMailFactory(attachments=(DocumentFactory(),))
        obj.mass_mail = None
        obj.save()
        obj.resend()
        send_mail_as_task.assert_called()
        assert send_mail_as_task.call_count == 1

    @patch("wbmailing.models.mails.send_mail_as_task.delay")
    def test_resend_no_template(self, send_mail_as_task):
        request = APIRequestFactory().get("")
        request.user = get_or_create_superuser()
        obj = ToEmailMailFactory()
        obj.mass_mail.template = None
        obj.mass_mail.save()
        obj.resend()
        send_mail_as_task.assert_called()
        assert send_mail_as_task.call_count == 1

    @override_settings(EMAIL_BACKEND="anymail.backends.test.EmailBackend")
    @pytest.mark.parametrize(
        "exits_message_id, event_type, reject_reason",
        [
            ("YES", MailEvent.EventType.SENT, None),
            ("YES", MailEvent.EventType.SENT, MailEvent.RejectReason.SPAM),
            ("YES", "Other", "Unknow"),
            ("NO", "Other", None),
        ],
    )
    def test_handle_mail_tracking(self, exits_message_id, event_type, reject_reason, mail_factory, mail_event_factory):
        request = APIRequestFactory().get("")
        request.user = get_or_create_superuser()
        ml = ToEmailMailFactory()
        nb_mail_send = len(mail.outbox)
        esp_event = {}
        if reject_reason:
            mailevent = mail_event_factory(mail=ml, description="", reject_reason=reject_reason)
            if reject_reason == MailEvent.RejectReason.SPAM:
                esp_event["reason"] = "SPAM"
            else:
                esp_event["response"] = "Unknow"
        else:
            mailevent = mail_event_factory(mail=ml)

        to = list(ml.to_email.values_list("address", flat=True))
        msg = ml.get_mailmessage(ml.subject, ml.body, request.user.email, to, attachments=ml.documents.all())
        msg.send()
        assert len(mail.outbox) == nb_mail_send + 1
        assert msg.anymail_status.status == {"sent"}
        if exits_message_id == "YES":
            message_id = mailevent.mail.message_ids[0]
        else:
            message_id = msg.anymail_status.message_id

        esp_event["ip"] = mailevent.ip
        esp_event["useragent"] = mailevent.user_agent
        mevent = AnymailTrackingEvent(
            event_type=event_type,
            message_id=message_id,
            timestamp=mailevent.timestamp,
            event_id=mailevent.id,
            recipient=mailevent.recipient,
            reject_reason=mailevent.reject_reason,
            description=mailevent.description,
            user_agent=mailevent.user_agent,
            click_url=mailevent.click_url,
            esp_event=esp_event,
        )
        # sender(class) – The source of the event.  (One of theanymail.webhook.*Viewclasses, but you generally won’t examine this parameter; it’s required by Django’s signalmechanism.
        tracking.send(sender=msg, event=mevent, esp_name="SendGrid")

        if exits_message_id == "YES":
            assert MailEvent.objects.filter(mail=ml, recipient=mailevent.recipient).count() == 2
        else:
            assert MailEvent.objects.filter(mail=ml, recipient=mailevent.recipient).count() == 1

    @override_settings(EMAIL_BACKEND="anymail.backends.test.EmailBackend", ANYMAIL_SENDGRID_API_KEY="TEST")
    @patch("wbmailing.backend.SendgridEmailBackend._send")
    @pytest.mark.parametrize("resend, exit_document", [(False, False), (False, True), (True, False)])
    def test_SendgridEmailBackend_send_messages(self, mock_send, resend, exit_document):
        request = APIRequestFactory().get("")
        request.user = get_or_create_superuser()
        num_sent = SendgridEmailBackend().send_messages(None)
        assert num_sent == 0
        doc1 = DocumentFactory()
        ml = ToEmailMailFactory(cc_email=(EmailContactFactory(),), attachments=(doc1,))
        to = list(ml.to_email.values_list("address", flat=True))
        cc = list(ml.cc_email.values_list("address", flat=True))
        bcc = ["lemissan@atonra.ch"]
        if resend:
            msg = ml.get_mailmessage(
                ml.subject, ml.body, request.user.email, to, attachments=ml.documents.all(), mail=ml
            )
        else:
            msg = ml.get_mailmessage(
                ml.subject, ml.body, request.user.email, to, bcc=bcc, cc=cc, attachments=ml.documents.all()
            )
        msg.send()

        if exit_document:
            for name, payload, mimetype in msg.attachments:
                doc1.name = name
                doc1.save()

        email_messages = [msg]

        mock_send.return_value.status_code = 200
        mock_send.return_value.json.return_value = msg

        num_sent = SendgridEmailBackend().send_messages(email_messages)
        mock_send.assert_called()
        assert mock_send.call_count == 1
        assert num_sent == 1

    def test_can_administrate_mail(self, mass_mail_factory):
        request = APIRequestFactory().get("")
        request.user = get_or_create_superuser()
        obj = mass_mail_factory()
        result = can_administrate_mail(obj, request.user)
        assert result
