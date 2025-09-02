from datetime import timedelta

from django.utils import timezone
from dynamic_preferences.registries import global_preferences_registry
from googleapiclient.discovery import Resource
from psycopg.types.range import TimestamptzRange
from wbcore.contrib.directory.models import Person
from wbcrm.models import Activity, ActivityParticipant

from ...typing_informations import GoogleEventType
from ...utils import GoogleSyncUtils


def update_activity_participant(event: GoogleEventType, activity: Activity):
    """
    Used to update the participants in a workbench activity.

    :param event:   The Google event dict with the participant informations.
    :param activity:The corresponding activity.
    """

    can_sync_external_participants: bool = global_preferences_registry.manager()[
        "wbactivity_sync__sync_external_participants"
    ]
    event_participants = GoogleSyncUtils.get_or_create_participants(event, activity.creator)

    def update_or_add_participants():
        for event_participant in event_participants:
            if person := Person.objects.filter(id=event_participant["person_id"]).first():
                activity.participants.add(person.id)
                ActivityParticipant.objects.filter(activity=activity, participant=person).update(
                    participation_status=event_participant["status"]
                )

    if can_sync_external_participants or not activity.creator.is_internal:  # type: ignore
        update_or_add_participants()
    else:
        internal_activity_participants_set = set(
            activity.participants.filter(id__in=Person.objects.filter_only_internal())
        )
        event_participants_set = set(Person.objects.filter(id__in=[x["person_id"] for x in event_participants]))
        missing_activity_participants = internal_activity_participants_set - event_participants_set
        update_or_add_participants()
        if missing_activity_participants:
            ActivityParticipant.objects.filter(
                participant__in=missing_activity_participants, activity=activity
            ).update(participation_status=ActivityParticipant.ParticipationStatus.CANCELLED)


def update_single_activity(event: GoogleEventType, activity: Activity, change_status=False):
    """
    Updates a single workbench activity based on changes done in a google event.

    :param event:           The google event dict that was updated.
    :param activity:        The corresponding workbench activity.
    :param change_status:   Information wheter the status of the event was updated or not.
    """
    if activity.external_id is None:
        return
    if activity.status == Activity.Status.REVIEWED or activity.status == Activity.Status.FINISHED:
        metadata = activity.metadata
        metadata["google_backend"] |= {"event": event} if not event.get("recurringEventId") else {"instance": event}
        Activity.objects.filter(id=activity.id).update(
            external_id=event["id"] if "_" in activity.external_id else activity.external_id,
            metadata=metadata,
        )
        return
    event_organizer = event.get("organizer", {})
    event_organizer_mail = event_organizer.get("email", "")
    event_organizer_displayed_name = event_organizer.get("displayName", "")
    organizer = GoogleSyncUtils.get_or_create_person(event_organizer_mail, event_organizer_displayed_name)
    event_start, event_end = GoogleSyncUtils.get_start_and_end(event)
    if event_start == event_end:
        event_end = event_end + timedelta(seconds=1)
    period = TimestamptzRange(event_start, event_end)  # type: ignore
    all_day: bool = True if event["start"].get("date") else False

    metadata = activity.metadata
    metadata["google_backend"] |= {"event": event} if not event.get("recurringEventId") else {"instance": event}
    Activity.objects.filter(id=activity.id).update(
        title=event.get("summary", "(No Subject)"),
        assigned_to=organizer,
        description=event.get("description", ""),
        start=event_start,
        status=Activity.Status.PLANNED if change_status else activity.status,
        end=event_end,
        period=period,
        all_day=all_day,
        location=event.get("location"),
        visibility=GoogleSyncUtils.convert_event_visibility_to_activity_visibility(event.get("visibility")),
        metadata=metadata,
        external_id=event["id"] if "_" in activity.external_id else activity.external_id,
    )
    update_activity_participant(event, activity)


def update_all_activities(activity: Activity, event: GoogleEventType, user_mail: str, service: Resource):
    """
    Updates all workbench activities in a recurrence chain based on changes done in a google event.

    :param event:       The google event dict that was updated.
    :param activity:    The corresponding workbench activity.
    :param user_mail:   The e-mail address of the current user.
    :param service:     The google service to interact with googles resources.
    """

    activity_instance = activity.metadata["google_backend"].get(
        "instance", activity.metadata["google_backend"].get("event", {})
    )
    event_start, event_end = event["start"], event["end"]
    activity_start, activity_end = activity_instance.get("start"), activity_instance.get("end")
    event_instances: dict = service.events().instances(calendarId=user_mail, eventId=event["id"]).execute()
    instance_items = event_instances["items"]
    connected_activities = Activity.objects.filter(parent_occurrence=activity)
    connected_activities |= Activity.objects.filter(metadata__google_backend__instance__recurringEventId=event["id"])
    connected_activities |= Activity.objects.filter(id=activity.id)
    if event_start != activity_start or event_end != activity_end:
        # If the start/end time of the google event chain changes, google will also change the id of the event instances. That is why we need to handle this case seperatly
        connected_activities = connected_activities.order_by("external_id")
        activity_list = list(connected_activities)
        instance_items.sort(key=lambda x: x["start"].get("date", x["start"]["dateTime"]))
        for instance in instance_items:
            if len(activity_list) == 0:
                break
            activity_instance = activity_list.pop(0)
            update_single_activity(instance, activity_instance)
            activity_instance.refresh_from_db()
    else:
        for instance in instance_items:
            if activity_child := connected_activities.filter(external_id=instance["id"]).first() or (
                activity_child := Activity.objects.filter(
                    metadata__google_backend__instance__id=instance["id"]
                ).first()
            ):
                update_single_activity(instance, activity_child)


def update_activities_from_new_parent(event: dict, parent_occurrence: Activity, user_mail: str, service: Resource):
    """
    This methods updates child activities whose parent activity was altered.

    :param event:           The google event dict that was updated.
    :param parent_occurrence: The corresponding workbench parent activity.
    :param user_mail:       The e-mail address of the current user.
    :param service:         The google service to interact with googles resources.

    """
    now = timezone.now()
    canceled_child_activities = Activity.objects.filter(
        parent_occurrence=parent_occurrence, period__startswith__gt=now
    )
    event_instances: dict = service.events().instances(calendarId=user_mail, eventId=event["id"]).execute()
    for instance in event_instances["items"]:
        if activity := canceled_child_activities.filter(external_id=instance["id"]).first():
            update_single_activity(instance, activity, True)
