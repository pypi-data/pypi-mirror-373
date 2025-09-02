from celery import shared_task

from .shortcuts import get_backend


@shared_task(queue="synchronization")
def periodic_notify_admins_of_webhook_inconsistencies_task(emails: list | None = None):
    """
    Periodic tasks to notify webhook inconsistencies
    """
    if emails and (controller := get_backend()):
        controller.backend.notify_admins_of_webhook_inconsistencies(emails)


@shared_task(queue="synchronization")
def periodic_renew_web_hooks_task():
    """
    Periodic tasks to renew active webhooks
    """
    if controller := get_backend():
        controller.backend.renew_web_hooks()
