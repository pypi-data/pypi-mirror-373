import re
import warnings
from uuid import uuid4

from dateutil.rrule import rrule, rrulestr
from googleapiclient.discovery import Resource
from wbcrm.models import Activity

from ...utils import GoogleSyncUtils


def update_single_event(creator_mail: str, google_service: Resource, internal_activity: Activity, updates: dict):
    """
    Updates a single Google-Event.

    After the external event has been updated, the metadata field of the internal activity is also updated with the information of the external event.

    Note: Do not use for recurring events.

    :param creator_mail:        The e-mail address of the activities creator.
    :param google_service:      The google service to interact with googles resources.
    :param internal_activity:   The internal workbench activity that corresponds to the external google event.
    :param updates:             The update information.
    :returns:                   None
    """

    updated_external_event = (
        google_service.events()
        .update(calendarId=creator_mail, eventId=internal_activity.external_id, body=updates)
        .execute()
    )
    metadata = internal_activity.metadata | {"google_backend": {"event": updated_external_event}}
    Activity.objects.filter(id=internal_activity.id).update(metadata=metadata)


def update_single_recurring_event(
    creator_mail: str, google_service: Resource, internal_activity: Activity, updates: dict
):
    """
    Updates a single recurring Google-Event.

    After the external event has been updated, the metadata field of the internal activity is also updated with the information of the external event.

    Note: Do not use for not recurring events.

    :param creator_mail:        The e-mail address of the activities creator.
    :param google_service:      The google service to interact with googles resources.
    :param internal_activity:   The internal workbench activity that corresponds to the external google event.
    :param updates:             The update information.
    :returns:                   None
    """
    is_parent = Activity.objects.filter(parent_occurrence=internal_activity).exists()
    external_id = (
        internal_activity.metadata["google_backend"]["instance"].get("id")
        if is_parent
        else internal_activity.external_id
    )
    updated_event = google_service.events().patch(calendarId=creator_mail, eventId=external_id, body=updates).execute()
    metadata = internal_activity.metadata
    metadata["google_backend"] |= {"instance": updated_event}
    Activity.objects.filter(id=internal_activity.id).update(metadata=metadata)


def update_all_recurring_events_from_parent(
    creator_mail: str, google_service: Resource, internal_activity: Activity, updates: dict
):
    """
    Updates all Google-Event-Instances belonging to the same recurring event chain.

    After the external event instances have been updated, the metadata fields of the internal activities is also updated with the information of the corresponding external event instance.

    Note: Do not use when creating a new parent activity from an existing child.

    :param creator_mail:        The e-mail address of the activities creator.
    :param google_service:      The google service to interact with googles resources.
    :param internal_activity:   The internal workbench parent activity that corresponds to the external google event.
    :param updates:             The update information.
    :returns:                   None
    """
    updated_event = (
        google_service.events()
        .patch(calendarId=creator_mail, eventId=internal_activity.external_id, body=updates)
        .execute()
    )
    metadata = internal_activity.metadata | {"google_backend": {"event": updated_event}}
    instances = google_service.events().instances(calendarId=creator_mail, eventId=updated_event["id"]).execute()
    google_event_items = instances["items"]
    GoogleSyncUtils.add_instance_metadata(internal_activity, google_event_items, metadata)


def update_all_recurring_events_from_new_parent(
    creator_mail: str, google_service: Resource, internal_activity: Activity, updates: dict
):
    """
    Updates all Google-Event-Instances belonging to the same parent event.

    After the external event instances have been updated, the metadata fields of the internal activities is also updated with the information of the corresponding external event instance.

    Note: Do not use when updating from the original event chain parent.

    :param creator_mail:        The e-mail address of the activities creator.
    :param google_service:      The google service to interact with googles resources.
    :param internal_activity:   The internal workbench parent activity that corresponds to the external google event.
    :param updates:             The update information.
    :returns:                   None
    """

    # If the old parent does not exist anymore, we cannot update the child.
    if not (
        current_parent_occurrence := Activity.objects.filter(
            id=internal_activity.metadata.get("old_parent_id")
        ).first()
    ):
        return warnings.warn(
            "Could not update the recurring events on google, because the old parent activity was already deleted."
        )

    # Get the current parent event from google
    current_google_parent_event: dict = (
        google_service.events().get(calendarId=creator_mail, eventId=current_parent_occurrence.external_id).execute()
    )

    # Get the current recurrence rules. We need to modify them for both the current parent event and the new parent event.
    current_parent_rrule_str: str = "\n".join(current_google_parent_event["recurrence"])

    # We need to adjust the rrules to mimic the current status on the workbench. So we replace any until or count value with the current number of child activities.
    current_parent_child_count = Activity.objects.filter(parent_occurrence=current_parent_occurrence).count()
    new_parent_child_count = Activity.objects.filter(parent_occurrence=internal_activity).count()
    current_parent_new_rrule: rrule = rrulestr(current_parent_rrule_str).replace(  # type: ignore
        count=current_parent_child_count + 1, until=None
    )
    new_parent_rrule: rrule = rrulestr(current_parent_rrule_str).replace(count=new_parent_child_count + 1, until=None)  # type: ignore

    # Converting the rrule back to str. Since the .__str__() method adds a DTSTART value, we need to remove this by using regex.
    current_parent_new_rrule_str: str = re.sub("[DTSTART].*[\n]", "", current_parent_new_rrule.__str__()).split("T0")[
        0
    ]
    new_parent_rrule_str: str = re.sub("[DTSTART].*[\n]", "", new_parent_rrule.__str__()).split("T0")[0]

    # Updating the current parent with the new rrules. This will remove all the child events on google that are not in the scope of the changed rrules anymore.
    current_google_parent_event |= {"recurrence": [current_parent_new_rrule_str]}
    updated_current_parent_event: dict = (
        google_service.events()
        .update(calendarId=creator_mail, eventId=current_google_parent_event["id"], body=current_google_parent_event)
        .execute()
    )

    # Updating the corresponding metadata
    current_parent_metadata = current_parent_occurrence.metadata | {
        "google_backend": {"event": updated_current_parent_event}
    }
    Activity.objects.filter(id=current_parent_occurrence.id).update(metadata=current_parent_metadata)
    current_instances = (
        google_service.events()
        .instances(calendarId=creator_mail, eventId=updated_current_parent_event["id"])
        .execute()
    )
    current_instances_google_event_items = current_instances["items"]
    current_parent_occurrence.refresh_from_db()
    GoogleSyncUtils.add_instance_metadata(
        current_parent_occurrence, current_instances_google_event_items, current_parent_metadata
    )

    # Updating the new parent with the created rrules. This will create the child events in google which are in the scope of the newly created rrules.

    internal_activity_query = Activity.objects.filter(id=internal_activity.id)
    external_id = uuid4().hex
    updates |= {"recurrence": [new_parent_rrule_str], "id": external_id}
    internal_activity_query.update(external_id=external_id)
    new_parent_event: dict = google_service.events().insert(calendarId=creator_mail, body=updates).execute()

    # Updating the corresponding metadata
    metadata = internal_activity.metadata | {"google_backend": {"event": new_parent_event}, "old_parent_id": None}
    internal_activity_query.update(metadata=metadata)
    new_instances = (
        google_service.events().instances(calendarId=creator_mail, eventId=new_parent_event["id"]).execute()
    )
    new_google_event_items = new_instances["items"]
    internal_activity.refresh_from_db()
    GoogleSyncUtils.add_instance_metadata(internal_activity, new_google_event_items, metadata, True)
