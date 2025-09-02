from datetime import datetime, timedelta
from typing import Dict, List
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db import models
from dynamic_preferences.registries import global_preferences_registry
from wbcore.contrib.agenda.models import CalendarItem
from wbcore.contrib.directory.models import EmailContact, Person

from wbcrm.models import Activity, ActivityParticipant
from wbcrm.synchronization.activity.preferences import (
    can_synchronize_activity_description,
)

from .typing_informations import GoogleEventType, TimeInfo

global_preferences = global_preferences_registry.manager()


class GoogleSyncUtils:
    @classmethod
    def convert_event_visibility_to_activity_visibility(cls, event_visiblity: str):
        if event_visiblity == "public":
            return CalendarItem.Visibility.PUBLIC
        return CalendarItem.Visibility.PRIVATE

    @classmethod
    def convert_activity_participants_to_attendees(cls, activity: Activity, event: GoogleEventType | None = None):
        """
        A method for converting the participants of a "Workbench" activity to a list of dictionaries, that can be used to create "Google Event" attendees.

        :param activity:    The activity from which the participants needs to be converted.
        :return:            The list with the dictionaries of attendees. Can be empty if no participant is in the original activity.
        """
        attendees_list = []
        event_attendees = cls.get_or_create_participants(event, activity.creator) if event else []

        event_attendees = [Person.all_objects.get(id=person_dict["person_id"]) for person_dict in event_attendees]
        can_sync_external_participants: bool = global_preferences["wbactivity_sync__sync_external_participants"]
        allowed_participants: models.QuerySet["ActivityParticipant"] = activity.activity_participants.filter(
            participant__in=event_attendees,
        ).union(activity.activity_participants.filter(participant__id__in=Person.objects.filter_only_internal()))
        activity_participants: models.QuerySet["ActivityParticipant"] = (
            activity.activity_participants.all() if can_sync_external_participants else allowed_participants
        )
        for activity_participant in activity_participants:
            participant = activity_participant.participant
            status = cls.convert_participant_status_to_attendee_status(activity_participant.participation_status)
            attendees_list.append(
                {
                    "displayName": participant.computed_str,
                    "email": str(participant.primary_email_contact()),
                    "responseStatus": status,
                }
            )
        return attendees_list

    @classmethod
    def convert_activity_to_event(cls, activity: Activity, created=False):
        """
        Converts a "Workbench" activity into a dict, that can be used to create a "Google Event" instance.

        :param activity:    A "Workbench" activity. The activity that is converted to a dict.
        :param created:     A boolean. This should be True if the activity is created, in every other case it should be False. Per default it is False.
        :returns:           A dictionary which can be used to create a google event.
        """
        # If the activity instance is to be created (e.g. pre_save when creating the activity) we cannot interact with the activity_participants.
        participants_list = cls.convert_activity_participants_to_attendees(activity=activity)
        timezone = ZoneInfo(settings.TIME_ZONE)
        recurrence = []
        if not created:
            if (google_backend := activity.metadata.get("google_backend")) and (event := google_backend.get("event")):
                recurrence = event.get("recurrence", [])
            elif wb_recurrence := activity.metadata.get("recurrence"):
                recurrence = [wb_recurrence]
        else:
            if wb_recurrence := activity.metadata.get("recurrence"):
                recurrence = [wb_recurrence]
            else:
                recurrence = []
        event_body = {
            "summary": activity.title,
            "creator": str(activity.creator.primary_email_contact()) if activity.creator else "",
            "organizer": str(activity.assigned_to.primary_email_contact()) if activity.assigned_to else "",
            "attendees": participants_list,
            "description": activity.description if can_synchronize_activity_description else "",
            "start": {
                "dateTime": activity.period.lower.astimezone(timezone).isoformat(),  # type: ignore
                "timeZone": settings.TIME_ZONE,
            },
            "end": {
                "dateTime": activity.period.upper.astimezone(timezone).isoformat(),  # type: ignore
                "timeZone": settings.TIME_ZONE,
            },
            "recurrence": recurrence,
            "location": activity.location,
            "visibility": cls.convert_activity_visibility_to_event_visibility(activity.visibility),
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {
                        "method": "email",
                        "minutes": Activity.ReminderChoice.get_minutes_correspondance(activity.reminder_choice),
                    }
                ],
            },
        }
        return event_body

    @classmethod
    def get_start_and_end(cls, event: GoogleEventType):
        """
        Converts the google start & end times to a datetime format.

        A google event dict contains either a dateTime-key or a date-key. If a date-key is present, this indicates that the event is an all day event.

        :param event: A google event dictionary from which the start & and end time will be extracted and converted.

        :note: If a google event takes place all day, the start date and end date will not be the same date.
        For example, an event that will take place on the 01.06.2020 will have "2020-06-01" as the start date value and "2020-06-02" as the end date value.
        A workbench activity will work with "datetime" values, even when the activity is an all-day activity.
        Therefor the start date will be converted in a "datetime" object like "2020-06-01-00-00-00" and the end date will be converted to "2020-06-01-23-59-59"
        """
        event_start, event_end = None, None
        start, end = event["start"], event["end"]
        if start_datetime := start.get("dateTime"):
            event_start = datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%S%z")
        else:
            event_start = datetime.strptime(start["date"], "%Y-%m-%d")
        if end_datetime := end.get("dateTime"):
            event_end = datetime.strptime(end_datetime, "%Y-%m-%dT%H:%M:%S%z")
        else:
            event_end = datetime.strptime(end["date"], "%Y-%m-%d") - timedelta(seconds=1)
        return event_start, event_end

    @classmethod
    def add_instance_metadata(
        cls, parent_occurrence: Activity, google_event_items: List[GoogleEventType], new_metadata: Dict, created=False
    ) -> None:
        """
        Adds the information of google event instances to the corresponding activities metadata field.

        :param parent_occurrence: The "Workbench" parent activity. It is used to retrieve the child activities.
        :google_event_items: The corresponding google event instances.
        :new_metadata: The newly created metadata for the parent_occurrence
        """

        def compare_instances_and_activity(activity: Activity, is_parent=False):
            for google_child in google_event_items:
                if created:
                    google_start, _ = cls.get_start_and_end(google_child)
                    activity_start = activity.period.lower  # type: ignore
                else:
                    original_start_dict: TimeInfo = google_child.get("originalStartTime", {})
                    activity_start_dict: Dict = (
                        activity.metadata.get("google_backend", {}).get("instance", {}).get("originalStartTime", {})
                    )
                    google_start = original_start_dict.get("dateTime", original_start_dict.get("date"))
                    activity_start = activity_start_dict.get("dateTime", original_start_dict.get("date"))
                if google_start == activity_start:
                    if is_parent:
                        new_metadata["google_backend"] |= {"instance": google_child}
                        external_id = new_metadata["google_backend"]["event"].get("id")
                        Activity.objects.filter(id=activity.id).update(external_id=external_id, metadata=new_metadata)
                    else:
                        metadata = activity.metadata | {"google_backend": {"instance": google_child}}
                        Activity.objects.filter(id=activity.id).update(
                            external_id=google_child["id"], metadata=metadata
                        )
                    google_event_items.remove(google_child)
                    break

        compare_instances_and_activity(parent_occurrence, True)
        child_activities = Activity.objects.filter(parent_occurrence=parent_occurrence)
        for wb_child in child_activities:
            compare_instances_and_activity(wb_child)

    @classmethod
    def get_or_create_participants(cls, event: GoogleEventType, creator: Person | None):
        """
        Converts the participants of an event into person objects by using the email address of the participants to search for the corresponding person entries in the "Workbench" database.
        If no person with the right email address is found, a new person entry will automatically be created with the email address or, if possible, with the displayed name as last name.

        :param event:       A google event body.
        :param creator:     The creator of the event.

        :return:            A list of dicts with the following structure: {"person_id": int, "status":str}. Can be empty if the event has no attendees.
        """

        participants = (
            [{"person_id": creator.id, "status": ActivityParticipant.ParticipationStatus.ATTENDS}] if creator else []
        )
        if attendees := event.get("attendees"):
            for attendee in attendees:
                mail = attendee.get("email")
                mail_query = Person.objects.filter(
                    id__in=EmailContact.objects.filter(address__iexact=mail, primary=True).values_list(
                        "entry_id", flat=True
                    )
                )
                if mail and mail_query.exists():
                    person = mail_query.first()
                else:
                    if display_name := attendee.get("displayName"):
                        person = Person.objects.create(last_name=display_name, is_draft_entry=True)
                    else:
                        person = Person.objects.create(last_name=mail, is_draft_entry=True)
                    EmailContact.objects.create(entry=person, address=mail, primary=True)
                if not creator or person.id != creator.id:
                    person_obj = {
                        "person_id": person.id,
                        "status": cls.convert_attendee_status_to_participant_status(attendee.get("responseStatus")),
                    }
                    participants.append(person_obj)

        return participants
