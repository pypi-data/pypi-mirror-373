from unittest.mock import patch

import pytest
from django.contrib.admin import AdminSite
from django.core import mail
from django.forms.models import model_to_dict
from django.template import Context, Template
from rest_framework import status
from rest_framework.serializers import ValidationError
from rest_framework.test import APIRequestFactory
from wbcore.contrib.directory.factories import EmailContactFactory
from wbcore.test import GenerateTest, default_config
from wbcore.test.utils import get_kwargs, get_model_factory

from wbmailing.admin import MailAdmin, MassMailAdmin
from wbmailing.factories import ToEmailMailFactory
from wbmailing.models import Mail, MailingListSubscriberChangeRequest, MassMail
from wbmailing.models.mails import send_mail_as_task
from wbmailing.serializers import MailingListSubscriberChangeRequestModelSerializer
from wbmailing.templatetags.mailing_tags import strip, stripAndsplit
from wbmailing.viewsets import MailingListSubscriberChangeRequestModelViewSet

config = {}
for key, value in default_config.items():
    config[key] = list(
        filter(
            lambda x: x.__module__.startswith("wbmailing")
            and x.__name__
            not in [
                "ClientsBarChartViewSet",
                "CountryBarChartViewSet",
                "RegionBarChartViewSet",
                "MailStatusBarChartViewSet",
                "MailClickBarChartViewSet",
                "AbstractRawDataChartViewSet",
            ],
            value,
        )
    )


@pytest.mark.django_db
@GenerateTest(config)
class TestProject:
    pass


@pytest.mark.django_db
class TestSpecificAdmin:
    def test_send_test_mail(self, mass_mail_factory, user):
        request = APIRequestFactory().get("")
        request.user = user
        EmailContactFactory(address=request.user.email)
        mass_mail_factory()
        qs = MassMail.objects.all()
        mma = MassMailAdmin(MassMail, AdminSite())
        nb_mail_send = len(mail.outbox)
        mma.send_test_mail(request, qs)
        assert len(mail.outbox) == nb_mail_send + 1

    @patch("wbmailing.models.mails.send_mail_as_task.delay")
    def test_MailAdmin(self, send_mail_as_task, user):
        request = APIRequestFactory().get("")
        request.user = user
        ToEmailMailFactory()
        qs = Mail.objects.all()

        ma = MailAdmin(Mail, AdminSite())
        ma.send_mails(request, qs)
        send_mail_as_task.assert_called()
        assert send_mail_as_task.call_count == 1

    def test_send_mail_as_task(self):
        obj = ToEmailMailFactory.create()
        context = {}
        if obj.to_email.count() == 1:
            context = {"salutation": obj.to_email.first().entry.salutation}
        rendered_subject = Template(obj.subject).render(Context(context))
        msg = {
            "subject": rendered_subject,
            "body": obj.body,
            "from_email": obj.from_email,
            "to": list(obj.to_email.values_list("address", flat=True)),
            "bcc": list(obj.bcc_email.values_list("address", flat=True)),
            "cc": list(obj.cc_email.values_list("address", flat=True)),
            "mail_id": obj.id,
        }
        if obj.mass_mail:
            msg["mass_mail_id"] = obj.mass_mail.id
        assert len(mail.outbox) == 0
        send_mail_as_task(**msg)
        assert len(mail.outbox) == 1

    def test_stripAndsplit(self):
        string = "diego loic is the best man"
        result = stripAndsplit(string, " ")
        assert len(result) == 6

    def test_strip(self):
        string = "diego/loic/is/the/best/man"
        string = strip(string)
        result = stripAndsplit(string, " ")
        assert len(result) == 1

    def test_validate_email_contact(self, mailing_list, mailing_list_subscriber_change_request_factory, user):
        request = APIRequestFactory().post("")
        request.user = user
        request.parser_context = {}
        request.data = {"crm_profile": request.user.profile.id}
        serializer = MailingListSubscriberChangeRequestModelSerializer(
            mailing_list_subscriber_change_request_factory(mailing_list=mailing_list), context={"request": request}
        )
        data = model_to_dict(mailing_list_subscriber_change_request_factory.build(mailing_list=mailing_list))
        del data["email_contact"]
        assert serializer.validate(data)  # this is fine because the instance is still in the serializer

        serializer = MailingListSubscriberChangeRequestModelSerializer(context={"request": request})
        with pytest.raises((ValidationError)):
            serializer.validate(data)

    @pytest.mark.parametrize("mvs", [MailingListSubscriberChangeRequestModelViewSet])
    def test_approveall(self, mvs, user):
        request = APIRequestFactory().get("")
        request.user = user
        factory = get_model_factory(mvs().get_serializer_class().Meta.model)
        for i in range(2):
            obj = factory()
        kwargs = get_kwargs(obj, mvs, request)
        assert (
            MailingListSubscriberChangeRequest.objects.filter(
                status=MailingListSubscriberChangeRequest.Status.PENDING
            ).count()
            == 2
        )
        response = mvs(kwargs=kwargs).approveall(request=request)
        assert response.status_code == status.HTTP_200_OK
        assert response.data
        assert (
            MailingListSubscriberChangeRequest.objects.filter(
                status=MailingListSubscriberChangeRequest.Status.APPROVED
            ).count()
            == 2
        )
