from celery import shared_task
from django.db.utils import OperationalError
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from wbcrm.models.events import Event

from .shortcuts import get_backend


@shared_task(
    queue="synchronization",
    default_retry_delay=5,
    autoretry_for=(OperationalError,),
    max_retries=4,
    retry_backoff=True,
)
def handle_inbound_as_task(event: dict):
    """
    the events received from the webhook are handled in a task
    which will allow to create, modify or delete the activity without interrupting the main server
    """
    if controller := get_backend():
        event_object = Event.objects.create(data=event)
        controller.handle_inbound(event=event, event_object_id=event_object.id)


@csrf_exempt
def event_watch(request: HttpRequest) -> HttpResponse:
    # TODO this is unsecure as it is prone to DDOS attack
    status_code = 200
    try:
        if controller := get_backend():
            if response := controller.handle_inbound_validation_response(request):
                return response
            for event in controller.get_events_from_inbound_request(request):
                handle_inbound_as_task.delay(event)
    except Exception as e:
        print(e)  # noqa: T201
        status_code = 500
    return HttpResponse(status=status_code)
