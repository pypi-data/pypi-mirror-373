import factory
import pytz
from wbcore.contrib.directory.factories import EmailContactFactory

from wbmailing.models import (
    Mail,
    MailEvent,
    MailingList,
    MailingListEmailContactThroughModel,
    MailingListSubscriberChangeRequest,
    MailTemplate,
    MassMail,
)


class MailingListSubscriberChangeRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MailingListSubscriberChangeRequest

    expiration_date = factory.Faker("date_object")
    status = MailingListSubscriberChangeRequest.Status.PENDING
    type = MailingListSubscriberChangeRequest.Type.SUBSCRIBING
    email_contact = factory.SubFactory("wbcore.contrib.directory.factories.EmailContactFactory")
    mailing_list = factory.SubFactory("wbmailing.factories.MailingListFactory")
    requester = factory.SubFactory("wbcore.contrib.authentication.factories.AuthenticatedPersonFactory")
    approver = factory.SubFactory("wbcore.contrib.authentication.factories.AuthenticatedPersonFactory")
    reason = factory.Faker("text", max_nb_chars=256)


class ApprovedMailingListSubscriberChangeRequest(MailingListSubscriberChangeRequestFactory):
    status = MailingListSubscriberChangeRequest.Status.APPROVED


class MailingListFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MailingList

    title = factory.Faker("text", max_nb_chars=64)
    is_public = False

    @factory.post_generation
    def email_contacts(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for email_contact in extracted:
                MailingListEmailContactThroughModel.objects.create(
                    mailing_list=self,
                    email_contact=email_contact,
                    status=MailingListEmailContactThroughModel.Status.SUBSCRIBED,
                )


class EmailContactMailingListFactory(MailingListFactory):
    @factory.post_generation
    def email_contacts(self, create, extracted, **kwargs):
        mlscr = MailingListSubscriberChangeRequestFactory()
        self.email_contacts.add(mlscr.email_contact)


class MailingListEmailContactFactory(EmailContactFactory):
    @factory.post_generation
    def subscriptions(self, create, extracted, **kwargs):
        ml = MailingListFactory()
        MailingListEmailContactThroughModel.objects.create(
            mailing_list=ml, email_contact=self, status=MailingListEmailContactThroughModel.Status.SUBSCRIBED
        )


class UnsubscribedMailingListEmailContactFactory(EmailContactFactory):
    @factory.post_generation
    def subscriptions(self, create, extracted, **kwargs):
        ml = MailingListFactory()
        MailingListEmailContactThroughModel.objects.create(
            mailing_list=ml, email_contact=self, status=MailingListEmailContactThroughModel.Status.UNSUBSCRIBED
        )


class MailingListEmailContactThroughModelFactory(factory.django.DjangoModelFactory):
    email_contact = factory.SubFactory("wbcore.contrib.directory.factories.EmailContactFactory")
    mailing_list = factory.SubFactory("wbmailing.factories.MailingListFactory")
    status = MailingListEmailContactThroughModel.Status.SUBSCRIBED

    class Meta:
        model = MailingListEmailContactThroughModel


class MassMailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MassMail

    # status =  #defaut = DRAFT
    from_email = factory.Faker("email")
    template = factory.SubFactory("wbmailing.factories.MailTemplateFactory")

    @factory.post_generation
    def mailing_lists(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for mailing_list in extracted:
                self.mailing_lists.add(mailing_list)

    subject = factory.Faker("text", max_nb_chars=64)
    body = factory.Faker("paragraph", nb_sentences=5)

    @factory.post_generation
    def attachments(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for attachment in extracted:
                self.attach_document(attachment)

    # body_json = #JSONField(null=True, blank=True)
    created = factory.Faker("date_time", tzinfo=pytz.utc)
    creator = factory.SubFactory("wbcore.contrib.directory.factories.PersonFactory")
    send_at = factory.Faker("date_time_between", start_date="now", end_date="+30y", tzinfo=pytz.utc)


class CustomMassMailFactory(MassMailFactory):
    @factory.post_generation
    def mailing_lists(self, create, extracted, **kwargs):
        ml = MailingListFactory()
        self.mailing_lists.add(ml)


class CustomMassMailEmailContactFactory(EmailContactFactory):
    @factory.post_generation
    def subscriptions(self, create, extracted, **kwargs):
        ml = MailingListFactory.create()
        ml.add_to_mailinglist(self)
        MassMailFactory.create(mailing_lists=[ml])


class MailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Mail

    created = factory.Faker("date_time", tzinfo=pytz.utc)
    last_send = factory.Faker("date_time", tzinfo=pytz.utc)
    template = factory.SubFactory("wbmailing.factories.MailTemplateFactory")
    message_ids = factory.List([factory.Faker("pystr")])
    mass_mail = factory.SubFactory("wbmailing.factories.MassMailFactory")
    from_email = factory.Faker("email")

    @factory.post_generation
    def to_email(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for email in extracted:
                self.to_email.add(email)

    @factory.post_generation
    def cc_email(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for email in extracted:
                self.cc_email.add(email)

    @factory.post_generation
    def bcc_email(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for email in extracted:
                self.bcc_email.add(email)

    subject = factory.Faker("text", max_nb_chars=64)
    body = factory.Faker("paragraph", nb_sentences=5)
    # body_json =  # JSONField(null=True, blank=True)

    @factory.post_generation
    def attachments(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for attachment in extracted:
                self.attach_document(attachment)


class ToEmailMailFactory(MailFactory):
    @factory.post_generation
    def to_email(self, create, extracted, **kwargs):
        ec = EmailContactFactory.create()
        self.to_email.add(ec)


class MailEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MailEvent

    mail = factory.SubFactory("wbmailing.factories.MailFactory")
    timestamp = factory.Faker("date_time", tzinfo=pytz.utc)
    # event_type =  # default=EventType.CREATED
    reject_reason = ""  # default=null   # RejectReason.choices
    description = factory.Faker("paragraph", nb_sentences=2)
    recipient = factory.Faker("email")
    click_url = factory.Faker("image_url")
    ip = factory.Faker("ipv4")
    user_agent = factory.Faker("first_name")
    # raw_data =   JSONField(default=dict, null=True, blank=True, verbose_name="Raw Data")


class MailTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MailTemplate

    title = factory.Faker("text", max_nb_chars=64)
    template = factory.Faker("paragraph", nb_sentences=5)
