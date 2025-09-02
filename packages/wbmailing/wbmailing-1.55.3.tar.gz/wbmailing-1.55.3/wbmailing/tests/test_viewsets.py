from unittest.mock import patch

import pytest
from django.core import mail
from rest_framework import status
from rest_framework.test import APIRequestFactory
from wbcore.contrib.directory.factories import EmailContactFactory
from wbcore.contrib.directory.viewsets import (
    CompanyModelViewSet,
    EntryModelViewSet,
    PersonModelViewSet,
)
from wbcore.signals.instance_buttons import add_instance_button
from wbcore.test.utils import get_kwargs, get_model_factory

from wbmailing.factories import (
    CustomMassMailFactory,
    MailEventFactory,
    MailFactory,
    MailingListEmailContactThroughModelFactory,
    MailingListFactory,
    MailingListSubscriberChangeRequestFactory,
    MassMailFactory,
    ToEmailMailFactory,
)
from wbmailing.models import (
    MailEvent,
    MailingListEmailContactThroughModel,
    MailingListSubscriberChangeRequest,
)
from wbmailing.viewsets import (
    EmailContactMailingListModelViewSet,
    MailingListEntryModelViewSet,
    MailingListSubscriberChangeRequestModelViewSet,
    MailModelViewSet,
    MailStatusMassMailModelViewSet,
    ManageMailingListSubscriptions,
    MassMailModelViewSet,
    UnsubscribeView,
)


@pytest.mark.django_db
class TestMailStatusMassMailViewSet:
    @pytest.fixture()
    def mass_mail(self, user):
        email = EmailContactFactory.create()
        ml = MailingListFactory.create(email_contacts=[email])
        mass_mail = MassMailFactory.create(mailing_lists=[ml], status="SENT")
        mail = MailFactory.create(mass_mail=mass_mail)
        MailEventFactory.create(mail=mail, event_type=MailEvent.EventType.BOUNCED, recipient=email.address)
        return mass_mail

    @patch("wbmailing.models.mails.send_mail_as_task.delay")
    @pytest.mark.parametrize("mvs", [MailStatusMassMailModelViewSet])
    def test_resendbouncedmails(self, send_mail_as_task, mvs, mass_mail, user):
        request = APIRequestFactory().get("")
        request.user = user
        kwargs = {"mass_mail_id": mass_mail.id}

        response = mvs(kwargs=kwargs).resendbouncedmails(request=request, mass_mail_id=mass_mail.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.data
        send_mail_as_task.assert_called()
        assert send_mail_as_task.call_count == 1

    @pytest.mark.parametrize("mvs", [MailStatusMassMailModelViewSet])
    def test_get_custom_buttons(self, mvs, mass_mail, user):
        request = APIRequestFactory().get("")
        request.user = user
        # obj = mail_factory()
        kwargs = {"mass_mail_id": mass_mail.id}
        mvs.kwargs = kwargs
        response = (
            mvs(kwargs=kwargs).button_config_class(view=mvs, request=request, instance=mass_mail).get_custom_buttons()
        )
        assert response


@pytest.mark.django_db
class TestSpecificViewsets:
    @pytest.mark.parametrize(
        "mvs, factory",
        [
            (EmailContactMailingListModelViewSet, MailingListEmailContactThroughModelFactory),
        ],
    )
    def test_delete(self, mvs, factory, user):
        request = APIRequestFactory().get("")
        request.user = user
        obj = factory()
        kwargs = get_kwargs(obj, mvs, request)
        response = mvs(kwargs=kwargs).delete(request=request, mailing_list_id=kwargs["mailing_list_id"], pk=obj.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data

    @pytest.mark.parametrize(
        "mvs, factory", [(MailingListEntryModelViewSet, MailingListEmailContactThroughModelFactory)]
    )
    def test_delete_unsubscriber_email_contacts(self, mvs, factory, mailing_list_factory, user):
        request = APIRequestFactory().get("")
        request.user = user
        mlscr = MailingListSubscriberChangeRequestFactory()
        obj = factory()
        kwargs = get_kwargs(obj, mvs, request)
        response = mvs(kwargs=kwargs).unsubscribe(
            request=request, entry_id=mlscr.email_contact.entry.id, pk=mlscr.mailing_list.pk
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data

    @pytest.mark.parametrize("myview", [PersonModelViewSet, CompanyModelViewSet, EntryModelViewSet])
    def test_entry_adding_instance_buttons(self, myview, user):
        remote_buttons = add_instance_button.send(myview, many=True)
        custom_instance_buttons = set([button for _, button in remote_buttons])
        assert custom_instance_buttons

    # @pytest.mark.parametrize("mvs", [(MassMailModelViewSet)])
    # def test_get_messages(self, mvs, mass_mail_factory, mail_factory, mail_event_factory, user):
    #     request = APIRequestFactory().get("")
    #     request.user = user
    #     obj = mass_mail_factory(status = MassMail.Status.SENT)
    #     qs = mvs().get_queryset()
    #     mail = mail_factory(mass_mail=qs[0])
    #     me = mail_event_factory(mail = mail, event_type=MailEvent.EventType.CLICKED)

    #     msg = mvs().get_messages(request, instance=qs[0])
    #     assert msg

    @pytest.mark.parametrize("mvs, factory", [(MassMailModelViewSet, CustomMassMailFactory)])
    def test_sendtestmail(self, mvs, factory, user):
        request = APIRequestFactory().get("")
        request.user = user
        obj = factory()
        EmailContactFactory(address=request.user.email)
        # request.POST = request.POST.copy()
        # request.POST['to_test_email'] = "lemissan@atonra.ch"
        nb_mail_send = len(mail.outbox)
        request.query_params = {}
        mvs.request = request
        mvs.kwargs = get_kwargs(obj, mvs, request)
        mvs.kwargs["pk"] = obj.pk
        response = mvs().sendtestmail(request)
        assert response.status_code == status.HTTP_200_OK
        assert response.data
        assert len(mail.outbox) == nb_mail_send + 1

    @pytest.mark.parametrize("mvs, factory", [(MailModelViewSet, ToEmailMailFactory)])
    def test_get_queryset_mail(self, mvs, factory, user):
        request = APIRequestFactory().get("")
        request.user = user
        request.user.is_superuser = False
        request.user.save()
        obj = factory()
        kwargs = get_kwargs(obj, mvs, request)
        vs = mvs.as_view({"get": "list"})
        response = vs(request, **kwargs)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("wbmailing.models.mails.send_mail_as_task.delay")
    def test_resend(self, send_mail_as_task, user):
        request = APIRequestFactory().get("")
        request.user = user
        obj = ToEmailMailFactory()
        request.query_params = {}
        MailModelViewSet.request = request
        MailModelViewSet.kwargs = get_kwargs(obj, MailModelViewSet, request)
        MailModelViewSet.kwargs["pk"] = obj.pk
        response = MailModelViewSet().resend(request)
        assert response.status_code == status.HTTP_200_OK
        assert response.data
        send_mail_as_task.assert_called()
        assert send_mail_as_task.call_count == 1

    @pytest.mark.parametrize("user__is_superuser", [True])
    def test_get_custom_buttons_approveall(self, user):
        request = APIRequestFactory().get("")
        request.user = user
        factory = get_model_factory(MailingListSubscriberChangeRequestModelViewSet().get_serializer_class().Meta.model)
        for i in range(2):
            obj = factory()
        kwargs = get_kwargs(obj, MailingListSubscriberChangeRequestModelViewSet, request)
        assert (
            MailingListSubscriberChangeRequest.objects.filter(
                status=MailingListSubscriberChangeRequest.Status.PENDING
            ).count()
            == 2
        )
        response = (
            MailingListSubscriberChangeRequestModelViewSet(kwargs=kwargs)
            .button_config_class(view=MailingListSubscriberChangeRequestModelViewSet, request=request, instance=obj)
            .get_custom_buttons()
        )
        assert response

    @pytest.mark.parametrize(
        "mvs, factory", [(ManageMailingListSubscriptions, MailingListEmailContactThroughModelFactory)]
    )
    def test_ManageMailingListSubscriptions(self, mvs, factory, user):
        request = APIRequestFactory().get("")
        request.user = user
        through_model = factory()
        response = mvs().get(request, through_model.email_contact.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.content

    @pytest.mark.parametrize("mvs, factory", [(UnsubscribeView, MailingListEmailContactThroughModelFactory)])
    def test_UnsubscribeView(self, mvs, factory, user):
        request = APIRequestFactory().get("")
        request.user = user
        through_model = factory()
        mailing_list = through_model.mailing_list
        response = mvs().get(request, through_model.email_contact.id, mailing_list.id)
        assert response.status_code == status.HTTP_302_FOUND
        assert response.url
        through_model.refresh_from_db()
        assert through_model.status == MailingListEmailContactThroughModel.Status.UNSUBSCRIBED
