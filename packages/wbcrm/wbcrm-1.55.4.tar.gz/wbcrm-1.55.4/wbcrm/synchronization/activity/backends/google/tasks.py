from datetime import datetime, timedelta

from celery import shared_task
from wbcore.contrib.authentication.models import User


@shared_task(queue="synchronization")
def google_webhook_resubscription() -> None:
    """
    A task to renew the google webhook subscriptions. The expiration date will be increased by 8 days.
    Only the subscriptions of users who still have a valid subscription will be renewed.
    """

    from .google import GoogleCalendarBackend

    user: User
    for user in User.objects.filter(metadata__google_backend__watch__isnull=False):
        GoogleCalendarBackend.stop_web_hook(user)
        user.refresh_from_db()
        new_timestamp_ms = round((datetime.now() + timedelta(days=8)).timestamp() * 1000)
        GoogleCalendarBackend.set_web_hook(user, new_timestamp_ms)
