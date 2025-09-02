import pytest
from django.contrib.auth.models import Permission
from faker import Faker
from wbcore.contrib.authentication.factories import UserFactory

from wbmailing.models.mailing_lists import (
    MailingList,
    MailingListEmailContactThroughModel,
    MailingListSubscriberChangeRequest,
)

fake = Faker()


@pytest.mark.django_db
class TestMailingListSubscriberChangeRequest:
    @pytest.fixture
    def user_admin(self):
        user = UserFactory.create()
        perm = Permission.objects.get(codename="administrate_mailinglistsubscriberchangerequest")
        user.user_permissions.add(perm)
        return user

    def test_init(self, mailing_list_subscriber_change_request):
        """
        Test basics creation logic:
        - relationship creation from email contact and mailing list
        """
        assert mailing_list_subscriber_change_request
        assert mailing_list_subscriber_change_request.status == MailingListSubscriberChangeRequest.Status.PENDING
        rel = mailing_list_subscriber_change_request.relationship
        assert rel.email_contact == mailing_list_subscriber_change_request.email_contact
        assert rel.mailing_list == mailing_list_subscriber_change_request.mailing_list
        assert rel.status == MailingListEmailContactThroughModel.Status.UNSUBSCRIBED

    @pytest.mark.parametrize("mailing_list__is_public", [True, False])
    def test_init_public_mailing_list(self, mailing_list_subscriber_change_request_factory, mailing_list):
        """
        Test if a request subscription creation to a public mailing list is automatically approved
        """
        request = mailing_list_subscriber_change_request_factory.create(mailing_list=mailing_list)
        assert request.type == MailingListSubscriberChangeRequest.Type.SUBSCRIBING
        if mailing_list.is_public:
            assert request.status == MailingListSubscriberChangeRequest.Status.APPROVED
        else:
            assert request.status == MailingListSubscriberChangeRequest.Status.PENDING

    @pytest.mark.parametrize(
        "mailing_list_subscriber_change_request__type, description",
        [
            (MailingListSubscriberChangeRequest.Type.SUBSCRIBING, fake.sentence()),
            (MailingListSubscriberChangeRequest.Type.UNSUBSCRIBING, fake.sentence()),
        ],
    )
    def test_approve(self, mailing_list_subscriber_change_request, user, description):
        mailing_list_subscriber_change_request.approve(by=user, description=description)
        if mailing_list_subscriber_change_request.type == MailingListSubscriberChangeRequest.Type.SUBSCRIBING:
            assert (
                mailing_list_subscriber_change_request.relationship.status
                == MailingListEmailContactThroughModel.Status.SUBSCRIBED
            )
        else:
            assert (
                mailing_list_subscriber_change_request.relationship.status
                == MailingListEmailContactThroughModel.Status.UNSUBSCRIBED
            )
        assert mailing_list_subscriber_change_request.approver == user.profile
        assert mailing_list_subscriber_change_request.reason == description

    @pytest.mark.parametrize("description", [fake.sentence()])
    def test_deny(self, mailing_list_subscriber_change_request, user, description):
        """
        Coverage test and unit test on description and approver from action trigerer
        """
        mailing_list_subscriber_change_request.deny(by=user, description=description)
        mailing_list_subscriber_change_request.save()
        assert mailing_list_subscriber_change_request.approver == user.profile
        assert mailing_list_subscriber_change_request.reason == description

    @pytest.mark.parametrize(
        "mailing_list_email_contact_through_model__status, type, res",
        [
            (
                MailingListEmailContactThroughModel.Status.SUBSCRIBED,
                MailingListSubscriberChangeRequest.Type.UNSUBSCRIBING,
                False,
            ),
            (
                MailingListEmailContactThroughModel.Status.SUBSCRIBED,
                MailingListSubscriberChangeRequest.Type.SUBSCRIBING,
                False,
            ),
            (
                MailingListEmailContactThroughModel.Status.UNSUBSCRIBED,
                MailingListSubscriberChangeRequest.Type.UNSUBSCRIBING,
                False,
            ),
            (
                MailingListEmailContactThroughModel.Status.UNSUBSCRIBED,
                MailingListSubscriberChangeRequest.Type.SUBSCRIBING,
                True,
            ),
        ],
    )
    def test_subscribing(
        self, mailing_list_email_contact_through_model, mailing_list_subscriber_change_request_factory, type, res
    ):
        """
        Basic property result check
        """
        request = mailing_list_subscriber_change_request_factory.create(
            type=type,
            relationship=mailing_list_email_contact_through_model,
            email_contact=mailing_list_email_contact_through_model.email_contact,
            mailing_list=mailing_list_email_contact_through_model.mailing_list,
        )
        assert request.subscribing == res

    def test_get_expired_date_subquery(
        self, email_contact, mailing_list, mailing_list_subscriber_change_request_factory
    ):
        """
        Check that expired date is the last approved and subscribing mailing change request
        """
        mailing_list_subscriber_change_request_factory.create(
            type=MailingListSubscriberChangeRequest.Type.SUBSCRIBING,
            status=MailingListSubscriberChangeRequest.Status.APPROVED,
            mailing_list=mailing_list,
            email_contact=email_contact,
            expiration_date=fake.date_object(),
        )  # oldest valid request
        req = mailing_list_subscriber_change_request_factory.create(
            type=MailingListSubscriberChangeRequest.Type.SUBSCRIBING,
            status=MailingListSubscriberChangeRequest.Status.APPROVED,
            mailing_list=mailing_list,
            email_contact=email_contact,
            expiration_date=fake.date_object(),
        )  # expected expiration time request
        mailing_list_subscriber_change_request_factory.create(
            type=MailingListSubscriberChangeRequest.Type.UNSUBSCRIBING,
            status=MailingListSubscriberChangeRequest.Status.APPROVED,
            mailing_list=mailing_list,
            email_contact=email_contact,
            expiration_date=fake.date_object(),
        )  # Unvalid request because not subscribing
        mailing_list_subscriber_change_request_factory.create(
            type=MailingListSubscriberChangeRequest.Type.SUBSCRIBING,
            status=MailingListSubscriberChangeRequest.Status.PENDING,
            mailing_list=mailing_list,
            email_contact=email_contact,
            expiration_date=fake.date_object(),
        )  # Unvalid request because pending
        assert (
            MailingListEmailContactThroughModel.objects.annotate(
                expiration_date=MailingListEmailContactThroughModel.get_expired_date_subquery()
            )
            .filter(mailing_list=mailing_list, email_contact=email_contact)
            .values_list("expiration_date", flat=True)[0]
            == req.expiration_date
        )

    def test_get_approvers(self, user, user_admin):
        """
        Test that approvers are the proper user with admin rights
        """
        assert set(MailingListSubscriberChangeRequest.get_approvers()) == {user_admin}
        assert not MailingListSubscriberChangeRequest.get_approvers().filter(id=user.id).exists()


@pytest.mark.django_db
class TestMailingListEmailContactThroughModel:
    def test_init(self, mailing_list_email_contact_through_model):
        assert mailing_list_email_contact_through_model

    def test_change_state(self, mailing_list_email_contact_through_model):
        initial_status = mailing_list_email_contact_through_model.status
        mailing_list_email_contact_through_model.change_state()
        assert mailing_list_email_contact_through_model.status == initial_status
        assert (
            mailing_list_email_contact_through_model.requests.filter(
                status=MailingListSubscriberChangeRequest.Status.PENDING
            ).count()
            == 1
        )
        mailing_list_email_contact_through_model.change_state(automatically_approve=True)
        mailing_list_email_contact_through_model.refresh_from_db()
        assert not mailing_list_email_contact_through_model.requests.filter(
            status=MailingListSubscriberChangeRequest.Status.PENDING
        ).exists()
        assert mailing_list_email_contact_through_model.status != initial_status


@pytest.mark.django_db
class TestMailingList:
    def test_init(self, mailing_list):
        assert mailing_list

    @pytest.mark.parametrize(
        "mailing_list_email_contact_through_model__status", [MailingListEmailContactThroughModel.Status.SUBSCRIBED]
    )
    def test_unsubscription(self, mailing_list_email_contact_through_model):
        """
        Test unsubscription
        """
        email_contact = mailing_list_email_contact_through_model.email_contact
        mailing_list = mailing_list_email_contact_through_model.mailing_list

        mailing_list.unsubscribe(email_contact)
        req = mailing_list_email_contact_through_model.requests.get(
            status=MailingListSubscriberChangeRequest.Status.PENDING
        )
        assert (
            mailing_list_email_contact_through_model.status == MailingListEmailContactThroughModel.Status.SUBSCRIBED
        )  # We expect the contact to still be subscribed because the unsubscription request is still pending
        req.approve()
        mailing_list_email_contact_through_model.refresh_from_db()
        assert (
            mailing_list_email_contact_through_model.status == MailingListEmailContactThroughModel.Status.UNSUBSCRIBED
        )

    @pytest.mark.parametrize(
        "mailing_list_email_contact_through_model__status", [MailingListEmailContactThroughModel.Status.SUBSCRIBED]
    )
    def test_unsubscription_automatically_approve(self, mailing_list_email_contact_through_model):
        """
        Test automatically approved unsubscription change request
        """
        email_contact = mailing_list_email_contact_through_model.email_contact
        mailing_list = mailing_list_email_contact_through_model.mailing_list

        mailing_list.unsubscribe(email_contact, automatically_approve=True)
        mailing_list_email_contact_through_model.refresh_from_db()
        assert (
            mailing_list_email_contact_through_model.status == MailingListEmailContactThroughModel.Status.UNSUBSCRIBED
        )

    @pytest.mark.parametrize(
        "mailing_list_email_contact_through_model__status", [MailingListEmailContactThroughModel.Status.UNSUBSCRIBED]
    )
    def test_subscription(self, mailing_list_email_contact_through_model):
        """
        Test subscription change request
        """
        email_contact = mailing_list_email_contact_through_model.email_contact
        mailing_list = mailing_list_email_contact_through_model.mailing_list

        mailing_list.subscribe(email_contact)
        req = mailing_list_email_contact_through_model.requests.get(
            status=MailingListSubscriberChangeRequest.Status.PENDING
        )
        assert (
            mailing_list_email_contact_through_model.status == MailingListEmailContactThroughModel.Status.UNSUBSCRIBED
        )  # We expect the contact to still be subscribed because the unsubscription request is still pending
        req.approve()
        mailing_list_email_contact_through_model.refresh_from_db()
        assert mailing_list_email_contact_through_model.status == MailingListEmailContactThroughModel.Status.SUBSCRIBED

    @pytest.mark.parametrize(
        "mailing_list_email_contact_through_model__status", [MailingListEmailContactThroughModel.Status.UNSUBSCRIBED]
    )
    def test_subscription_automatically_approve(self, mailing_list_email_contact_through_model):
        """
        Test automatically approved subscription change request
        """
        email_contact = mailing_list_email_contact_through_model.email_contact
        mailing_list = mailing_list_email_contact_through_model.mailing_list

        mailing_list.subscribe(email_contact, automatically_approve=True)
        mailing_list_email_contact_through_model.refresh_from_db()
        assert mailing_list_email_contact_through_model.status == MailingListEmailContactThroughModel.Status.SUBSCRIBED

    def test_get_subscribed_mailing_lists(self, mailing_list_email_contact_through_model_factory):
        """
        Test subscribed mailing list for a email contact.
        """
        rel_e1_ml1_subscribed = mailing_list_email_contact_through_model_factory.create(
            status=MailingListEmailContactThroughModel.Status.SUBSCRIBED
        )
        e1 = rel_e1_ml1_subscribed.email_contact
        m1 = rel_e1_ml1_subscribed.mailing_list

        rel_e1_rel_ml2_unsubscribed = mailing_list_email_contact_through_model_factory.create(
            email_contact=e1, status=MailingListEmailContactThroughModel.Status.UNSUBSCRIBED
        )  # We expect e1 to not show up in the valid emails queryset
        m2 = rel_e1_rel_ml2_unsubscribed.mailing_list

        rel_e2_ml1_subscribed = mailing_list_email_contact_through_model_factory.create(
            mailing_list=m1, status=MailingListEmailContactThroughModel.Status.SUBSCRIBED
        )
        e2 = rel_e2_ml1_subscribed.email_contact
        mailing_list_email_contact_through_model_factory.create(
            email_contact=e2, mailing_list=m2, status=MailingListEmailContactThroughModel.Status.SUBSCRIBED
        )

        assert set(MailingList.get_subscribed_mailing_lists(e1)) == {
            m1,
        }
        assert set(MailingList.get_subscribed_mailing_lists(e2)) == {m1, m2}
