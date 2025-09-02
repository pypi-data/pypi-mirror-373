from django.db.models import QuerySet
from dynamic_preferences.registries import global_preferences_registry
from googleapiclient.discovery import Resource
from wbcrm.models import Activity


def cancel_or_delete_activity(activity: "Activity") -> None:
    # Activity is cancelled rather than disable if global preference is True
    if global_preferences_registry.manager()["wbactivity_sync__sync_cancelled_activity"]:
        Activity.objects.filter(id=activity.id).update(status=Activity.Status.CANCELLED)
    else:
        activity.delete()


def cancel_or_delete_activity_queryset(activity_qs: QuerySet["Activity"]) -> None:
    # Activities are cancelled rather than delete if global preference is True
    if global_preferences_registry.manager()["wbactivity_sync__sync_cancelled_activity"]:
        activity_qs.update(status=Activity.Status.CANCELLED)
    else:
        activity_qs.delete()


def delete_single_activity(activity: Activity):
    """
    Deletes the activity that has the corresponding external ID
    """
    Activity.objects.filter(id=activity.id).update(external_id=None)
    cancel_or_delete_activity(activity)


def delete_recurring_activity(activity: Activity, event: dict, user_mail: str, service: Resource):
    """
    Handles the deletion of recurring activities (either a single activity, a certain number of activities or all activities),
    based on the changes done to the google event.

    :param event:           The google event dict that was deleted.
    :param activity:        The corresponding workbench activity.
    :param user_mail:       The e-mail address of the current user.
    :param service:         The google service to interact with googles resources.
    """

    parent_occurrence = activity.parent_occurrence if activity.parent_occurrence else activity
    metadata_event = parent_occurrence.metadata["google_backend"].get(
        "event", parent_occurrence.metadata["google_backend"].get("instance", {})
    )
    if event.get("recurringEventId"):
        # Delete single event in event chain
        if activity.status not in [Activity.Status.REVIEWED, Activity.Status.FINISHED]:
            cancel_or_delete_activity(activity)

    elif event.get("recurrence") != metadata_event.get("recurrence"):
        # Delete all events after a certain event in the event chain

        event_instances: dict = service.events().instances(calendarId=user_mail, eventId=event["id"]).execute()
        external_id_list: list = [instance["id"] for instance in event_instances["items"]]
        activities_to_remove = Activity.objects.filter(
            metadata__google_backend__instance__recurringEventId__startswith=event["id"],
            status=Activity.Status.PLANNED,
        ).exclude(metadata__google_backend__instance__id__in=external_id_list)
        first_in_list = activities_to_remove.order_by("start").first()
        metadata = parent_occurrence.metadata
        metadata["google_backend"] |= {"event": event}
        Activity.objects.filter(id=parent_occurrence.id).update(metadata=metadata)
        if (
            first_in_list
            and first_in_list.id == parent_occurrence.id
            and parent_occurrence.status not in [Activity.Status.REVIEWED, Activity.Status.FINISHED]
        ):
            cancel_or_delete_activity(parent_occurrence)
        cancel_or_delete_activity_queryset(activities_to_remove)

    else:
        # Delete all events in event chain
        activities_to_cancel = Activity.objects.filter(
            parent_occurrence=parent_occurrence, status=Activity.Status.PLANNED
        )
        cancel_or_delete_activity_queryset(activities_to_cancel)
        cancel_or_delete_activity(activity)
