from django.apps import apps
from django.db.models.signals import pre_migrate
from pytest_factoryboy import register
from wbcore.contrib.authentication.factories import UserFactory
from wbcore.contrib.directory.factories import EmailContactFactory, PersonFactory
from wbcore.contrib.geography.tests.signals import app_pre_migration
from wbmailing.factories import (
    MailEventFactory,
    MailFactory,
    MailingListEmailContactThroughModelFactory,
    MailingListFactory,
    MailingListSubscriberChangeRequestFactory,
    MailTemplateFactory,
    MassMailFactory,
)

register(EmailContactFactory)
register(PersonFactory)
register(UserFactory)
register(MailingListSubscriberChangeRequestFactory)
register(MailingListEmailContactThroughModelFactory)
register(MailingListFactory)
register(MassMailFactory)
register(MailFactory)
register(MailEventFactory)
register(MailTemplateFactory)

from .signals import *

pre_migrate.connect(app_pre_migration, sender=apps.get_app_config("wbmailing"))
