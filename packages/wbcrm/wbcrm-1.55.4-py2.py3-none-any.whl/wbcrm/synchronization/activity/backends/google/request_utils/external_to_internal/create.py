from datetime import timedelta

from celery import shared_task
from dynamic_preferences.registries import global_preferences_registry
from googleapiclient.discovery import Resource
from psycopg.types.range import TimestamptzRange
from wbcore.contrib.authentication.models import User
from wbcrm.models import Activity

from ...typing_informations import GoogleEventType
from ...utils import GoogleSyncUtils
from .update import update_activity_participant


@shared_task(queue="synchronization")
def create_internal_activity_based_on_google_event(
    event: GoogleEventType, user: User, service: Resource, parent_occurrence: Activity | None = None, is_instance=False
):
    """
    A method for creating a "Workbench" activity based on a "Google" event. If the google event is a recurring event, this method will also create the corresponding workbench activities.

    :param event:           A google event body.
    :param user:            The current workbench user.
    :param service:         Thee google Resource.
    :param parent_occurrence: The parent activity. This is only used when the activity is part of a recurring chain. Per default it is None.
    :param is_instance:     True, when the event is a google instance (A instance is an event that is part of a recurring chain)
    """

    external_id = event["id"]
    if event.get("status") == "cancelled" or Activity.objects.filter(external_id=event["id"]).exists():
        return

    event_creator = event.get("organizer", {})
    event_creator_mail = event_creator.get("email", "")
    event_creator_displayed_name = event_creator.get("displayName", "")
    creator = GoogleSyncUtils.get_or_create_person(event_creator_mail, event_creator_displayed_name)
    event_start, event_end = GoogleSyncUtils.get_start_and_end(event)
    if event_start == event_end:
        event_end = event_end + timedelta(seconds=1)
    period = TimestamptzRange(event_start, event_end)  # type: ignore
    all_day: bool = True if event["start"].get("date") else False
    metadata = {"google_backend": {"instance": event}} if is_instance else {"google_backend": {"event": event}}

    act = Activity.objects.create(
        external_id=external_id,
        title=event.get("summary", "(No Subject)"),
        assigned_to=creator,
        creator=creator,
        description=event.get("description", ""),
        start=event_start,
        end=event_end,
        period=period,
        all_day=all_day,
        location=event.get("location"),
        visibility=GoogleSyncUtils.convert_event_visibility_to_activity_visibility(event.get("visibility", "")),
        metadata=metadata,
        parent_occurrence=parent_occurrence,
    )

    update_activity_participant(event, act)

    if event.get("recurrence") and not is_instance:
        instances: dict = service.events().instances(calendarId=user.email, eventId=event["id"]).execute()
        instance_items: list[GoogleEventType] = instances["items"]
        global_preferences = global_preferences_registry.manager()
        max_list_length: int = global_preferences["wbcrm__recurrence_maximum_count"]
        instance_items = instance_items[:max_list_length]

        for item in instance_items:
            if item["start"] == act.metadata["google_backend"].get("event", {}).get("start"):
                updated_metadata: dict = act.metadata
                updated_metadata["google_backend"] |= {"instance": item}
                Activity.objects.filter(id=act.id).update(metadata=updated_metadata)
            else:
                create_internal_activity_based_on_google_event(item, user, service, act, True)
