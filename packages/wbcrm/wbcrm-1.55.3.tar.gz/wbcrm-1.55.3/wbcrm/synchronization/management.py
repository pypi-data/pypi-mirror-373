from django.apps import apps as global_apps
from django.db import DEFAULT_DB_ALIAS
from django_celery_beat.models import CrontabSchedule, PeriodicTask


def initialize_task(app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs):
    crontab1, _ = CrontabSchedule.objects.get_or_create(
        minute="0",
        hour="1",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
    )
    crontab2, _ = CrontabSchedule.objects.get_or_create(
        minute="0",
        hour="7",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
    )

    # Automatically register the utility periodic tasks
    PeriodicTask.objects.update_or_create(
        task="wbcrm.synchronization.activity.tasks.periodic_renew_web_hooks_task",
        defaults={
            "name": "Wbactivity_sync: Renewal of the Activity Sync webhook",
            "crontab": crontab1,
        },
    )
    PeriodicTask.objects.update_or_create(
        task="wbcrm.synchronization.activity.tasks.periodic_notify_admins_of_webhook_inconsistencies_task",
        defaults={
            "name": "Wbactivity_sync: Notification of webhook inconsistencies",
            "crontab": crontab2,
        },
    )
