import pytest
from django.core import mail
from rest_framework import status
from rest_framework.test import APIRequestFactory
from wbcore.contrib.directory.factories import EmailContactFactory
from wbcore.test.utils import get_kwargs

from wbmailing.factories import CustomMassMailFactory
from wbmailing.models import MassMail
from wbmailing.viewsets.mails import MassMailModelViewSet


@pytest.mark.django_db
class TestSpecificSerializers:
    @pytest.mark.parametrize("mvs, factory", [(MassMailModelViewSet, CustomMassMailFactory)])
    def test_serializers_mail(self, mvs, factory, user):
        request = APIRequestFactory().get("")
        request.user = user
        obj = factory(status=MassMail.Status.SENT)
        EmailContactFactory(address=request.user.email)
        nb_mail_send = len(mail.outbox)
        request.query_params = {}
        mvs.request = request
        mvs.kwargs = get_kwargs(obj, mvs, request)
        mvs.kwargs["pk"] = obj.pk
        response = mvs().sendtestmail(request)
        assert response.status_code == status.HTTP_200_OK
        assert response.data
        assert len(mail.outbox) == nb_mail_send + 1
