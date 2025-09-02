from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django.db import DEFAULT_DB_ALIAS
from django.apps import apps as global_apps


def initialize_task(app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs):
    PeriodicTask.objects.update_or_create(
        task="wbmailing.tasks.periodic_send_mass_mail_as_tasks",
        defaults={
            "name": "Mailing: Periodically send scheduled mass mails",
            "interval": IntervalSchedule.objects.get_or_create(every=120, period=IntervalSchedule.SECONDS)[0],
            "crontab": None,
        },
    )
    PeriodicTask.objects.update_or_create(
        task="wbmailing.tasks.check_and_remove_expired_mailinglist_subscription",
        defaults={
            "name": "Mailing: Remove expired contact from mailing list",
            "interval": IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.DAYS)[0],
            "crontab": None,
        },
    )
