from datetime import timedelta

from anymail.backends.mailgun import EmailBackend as AnymailMailgunBackend
from anymail.backends.mailjet import EmailBackend as AnymailMailjetBackend
from anymail.backends.mandrill import EmailBackend as AnymailMandrillBackend
from anymail.backends.postmark import EmailBackend as AnymailPostmarkBackend
from anymail.backends.sendgrid import EmailBackend as AnymailSendgridBackend
from anymail.backends.sendinblue import EmailBackend as AnymailSendinblueBackend
from anymail.exceptions import AnymailError
from django.conf import settings
from django.core.mail.backends.console import EmailBackend as ConsoleBackend
from django.utils import timezone
from sentry_sdk import capture_message
from wbcore.utils.html import convert_html2text

from wbmailing.models import Mail, MailEvent


class SendMessagesMixin:
    def _process_msg(self, message):
        mail = message.mail if hasattr(message, "mail") else None
        mass_mail = message.mass_mail if hasattr(message, "mass_mail") else None
        if mail:
            event_type = MailEvent.EventType.RESENT
        else:
            if not hasattr(message, "silent_mail") or (hasattr(message, "silent_mail") and not message.silent_mail):
                mail = Mail.create_mail_from_mailmessage(message, user=getattr(message, "user", None))
            event_type = MailEvent.EventType.CREATED
        if mass_mail:
            message.tags = [f"massmail-{mass_mail.id}"]
        else:
            message.tags = [f"mail-{mail.id}"]
        if mail and mail.body:
            # We reset the body text and html field with what might have been computed in create_mail_from_mailmessage
            message.body = convert_html2text(mail.body)
            message.alternatives = []
            message.attach_alternative(mail.body, "text/html")
        return event_type, mail

    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        # This API is specified by Django's core BaseEmailBackend
        # (so you can't change it to, e.g., return detailed status).
        # Subclasses shouldn't need to override.
        from wbmailing.models import MailEvent

        num_sent = 0
        if not email_messages:
            return num_sent

        created_session = self.open()

        try:
            for message in email_messages:
                try:
                    event_type, mail = self._process_msg(message)
                    sent = self._send(message)
                    if mail:
                        MailEvent.objects.create(
                            mail=mail, event_type=event_type, timestamp=timezone.now() - timedelta(seconds=1)
                        )
                        mail.message_ids.append(message.anymail_status.message_id)
                        mail.last_send = timezone.now()
                        mail.save()
                except AnymailError as e:
                    capture_message(e)
                    if self.fail_silently:
                        sent = False
                    else:
                        raise
                if sent:
                    num_sent += 1
        finally:
            if created_session:
                self.close()

        return num_sent


class PostmarkEmailBackend(SendMessagesMixin, AnymailPostmarkBackend):
    def send_messages(self, email_messages):
        if settings.WBMAILING_POSTMARK_BROADCAST_STREAM_ID:
            for msg in email_messages:
                if hasattr(msg, "mass_mail") and msg.mass_mail:
                    msg.esp_extra = {"MessageStream": settings.WBMAILING_POSTMARK_BROADCAST_STREAM_ID}

        return super().send_messages(email_messages)


class SendgridEmailBackend(SendMessagesMixin, AnymailSendgridBackend):
    pass


class MailgunEmailBackend(SendMessagesMixin, AnymailMailgunBackend):
    pass


class MailjetEmailBackend(SendMessagesMixin, AnymailMailjetBackend):
    pass


class MandrillEmailBackend(SendMessagesMixin, AnymailMandrillBackend):
    pass


class SendinblueEmailBackend(SendMessagesMixin, AnymailSendinblueBackend):
    pass


class ConsoleEmailBackend(SendMessagesMixin, ConsoleBackend):
    def send_messages(self, email_messages):
        """Write all messages to the stream in a thread-safe way."""
        if not email_messages:
            return
        msg_count = 0
        with self._lock:
            try:
                stream_created = self.open()
                for message in email_messages:
                    self._process_msg(message)
                    self.write_message(message)
                    self.stream.flush()  # flush after each message
                    msg_count += 1
                if stream_created:
                    self.close()
            except Exception:
                if not self.fail_silently:
                    raise
        return msg_count
