import json
import warnings
from datetime import datetime
from typing import Dict

from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from dynamic_preferences.registries import global_preferences_registry
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import Resource, build
from wbcore.contrib.authentication.models import User
from wbcore.contrib.directory.models import Person

from wbcrm.models import Activity, ActivityParticipant

from .request_utils import (
    create_internal_activity_based_on_google_event,
    delete_recurring_activity,
    delete_single_activity,
    update_activities_from_new_parent,
    update_all_activities,
    update_all_recurring_events_from_new_parent,
    update_all_recurring_events_from_parent,
    update_single_activity,
    update_single_event,
    update_single_recurring_event,
)
from .typing_informations import GoogleEventType
from .utils import GoogleSyncUtils


class GoogleCalendarBackend:
    error_messages = {
        "missing_google_credentials": _(
            "The Google credentials are not set. You cannot use the Google Calendar Backend without the Google credentials."
        ),
        "service_build_error": _("Could not create the Google service. Exception: "),
        "create_error": gettext("Could not create the external google event. Exception: "),
        "delete_error": _("Could not delete a corresponding external event. Exception: "),
        "update_error": gettext("Could not update the external google-event. Exception: "),
        "send_participant_response_error": gettext(
            "Could not update the participation status on the google-event. Exception: "
        ),
        "could_not_sync": _("Couldn't sync with google calendar. Exception:"),
        "could_not_set_webhook": _("Could not set the google web hook for the user: "),
    }

    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    API_SERVICE_NAME = "calendar"
    API_VERSION = "v3"

    @classmethod
    def _get_service_account_file(cls) -> Dict:
        global_preferences = global_preferences_registry.manager()
        google_credentials = global_preferences.get("wbactivity_sync__google_sync_credentials")
        if google_credentials and (serivce_account_file := json.loads(google_credentials)):
            return serivce_account_file
        else:
            raise ValueError(cls.error_messages["missing_google_credentials"])

    @classmethod
    def _get_service_account_url(cls) -> str:
        serivce_account_file = cls._get_service_account_file()
        return serivce_account_file.get("url", "")

    @classmethod
    def _get_service_user_email(cls, activity: Activity) -> str:
        """
        This methods returns the email of the first activity participant with an active google-subscription.
        If no participant with an active subscrition is found, the return value will be an empty string.
        """

        now = timezone.now().replace(tzinfo=None)
        primary_email_contact: str = ""

        def get_email_str(person: Person) -> str:
            if user_profile := User.objects.filter(profile=person).first():
                user_google_backend: Dict = user_profile.metadata.get("google_backend", {})
                expiration: str | None = user_google_backend.get("watch", {}).get("expiration")
                if expiration and datetime.fromtimestamp(int(expiration) / 1000) > now:
                    return str(user_profile.email)
            return ""

        primary_email_contact = get_email_str(activity.creator) if activity.creator else ""
        if not primary_email_contact and (
            internal_participants := activity.participants.filter(
                id__in=Person.objects.filter_only_internal().exclude(
                    id=activity.creator.id if activity.creator else None
                )
            )
        ):
            for participant in internal_participants:
                if primary_email_contact := get_email_str(participant):
                    return primary_email_contact
        return primary_email_contact

    @classmethod
    def _build_service(cls, user_email: str) -> Resource:
        serivce_account_file = cls._get_service_account_file()
        try:
            credentials = Credentials.from_service_account_info(serivce_account_file, scopes=cls.SCOPES)
            return build(cls.API_SERVICE_NAME, cls.API_VERSION, credentials=credentials.with_subject(user_email))
        except Exception as e:
            raise ValueError("{msg}{exception}".format(msg=cls.error_messages["service_build_error"], exception=e))

    @classmethod
    def create_external_activity(cls, activity: Activity) -> None:
        now = timezone.now()
        can_sync_past_activities: bool = global_preferences_registry.manager()["wbactivity_sync__sync_past_activity"]
        if (
            activity.parent_occurrence
            or not (service_user_mail := cls._get_service_user_email(activity))
            or not (service := cls._build_service(user_email=service_user_mail))
            or (not can_sync_past_activities and now > activity.period.lower)  # type: ignore
        ):
            return
        try:
            event_body = GoogleSyncUtils.convert_activity_to_event(activity, True)
            event = service.events().insert(calendarId=service_user_mail, body=event_body).execute()
            metadata = activity.metadata | {"google_backend": {"event": event}}
            Activity.objects.filter(id=activity.id).update(external_id=event["id"], metadata=metadata)
            if Activity.objects.filter(parent_occurrence=activity).exists():
                instances = service.events().instances(calendarId=service_user_mail, eventId=event["id"]).execute()
                google_event_items = instances["items"]
                GoogleSyncUtils.add_instance_metadata(activity, google_event_items, metadata, True)

        except Exception as e:
            raise ValueError("{msg}{exception}".format(msg=cls.error_messages["create_error"], exception=e))

    @classmethod
    def delete_external_activity(cls, activity: Activity) -> None:
        now = timezone.now()
        can_sync_past_activities: bool = global_preferences_registry.manager()["wbactivity_sync__sync_past_activity"]

        if (
            not (service_user_mail := cls._get_service_user_email(activity))
            or not (service := cls._build_service(user_email=service_user_mail))
            or (not can_sync_past_activities and now > activity.period.lower)  # type: ignore
        ):
            return

        try:
            external_id = activity.external_id
            if (
                Activity.objects.filter(parent_occurrence=activity).exists()
                and not not activity.propagate_for_all_children
                and (google_backend := activity.metadata.get("google_backend"))
            ):
                # This step must be done if you want to remove a parent activity without deleting the whole recurring chain.
                # Therefore we use the instance ID instead of the event ID.
                external_id = google_backend.get("instance", {}).get("id")
            service.events().delete(calendarId=service_user_mail, eventId=external_id).execute()
        except Exception as e:
            warnings.warn("{msg}{exception}".format(msg=cls.error_messages["delete_error"], exception=e))

    @classmethod
    def update_external_activity(cls, activity: Activity) -> None:
        if not activity.metadata.get("google_backend"):
            cls.create_external_activity(activity)
            activity.refresh_from_db()

        if not (service_user_mail := cls._get_service_user_email(activity)) or not (
            service := cls._build_service(user_email=service_user_mail)
        ):
            return

        updated_event_body = GoogleSyncUtils.convert_activity_to_event(activity)
        try:
            is_parent = Activity.objects.filter(parent_occurrence=activity).exists()

            def update_all_recurring_events():
                if activity.metadata.get("old_parent_id"):
                    update_all_recurring_events_from_new_parent(
                        service_user_mail, service, activity, updated_event_body
                    )
                else:
                    update_all_recurring_events_from_parent(service_user_mail, service, activity, updated_event_body)

            if is_parent or activity.parent_occurrence:
                if activity.propagate_for_all_children:
                    update_all_recurring_events()
                else:
                    update_single_recurring_event(service_user_mail, service, activity, updated_event_body)
            else:
                update_single_event(service_user_mail, service, activity, updated_event_body)
        except Exception as e:
            raise ValueError("{msg}{exception}".format(msg=cls.error_messages["update_error"], exception=e))

    @classmethod
    def send_participant_response_external_activity(
        cls, activity_participant: ActivityParticipant, response_status: str
    ):
        participant: Person | None = Person.objects.filter(id=activity_participant.participant.id).first()
        activity: Activity | None = Activity.objects.filter(id=activity_participant.activity.id).first()
        if not participant or not activity:
            return
        if Activity.objects.filter(parent_occurrence=activity).exists():
            google_backend = activity.metadata.get("google_backend", {})
            external_id: str | None = google_backend.get("instance", google_backend.get("event", {})).get("id", None)
        else:
            external_id: str | None = activity.external_id

        creator_mail = str(activity.creator.primary_email_contact()) if activity.creator else ""
        participant_mail = str(participant.primary_email_contact())
        service: Resource = cls._build_service(user_email=creator_mail)

        if not service or not external_id:
            return
        try:
            google_status = GoogleSyncUtils.convert_participant_status_to_attendee_status(response_status)
            instance: Dict = service.events().get(calendarId=creator_mail, eventId=external_id).execute()
            attendees_list: list[Dict] = instance.get("attendees", [])

            for index, attendee in enumerate(attendees_list):
                if attendee.get("email") == participant_mail:
                    attendees_list[index]["responseStatus"] = google_status
                    break
            metadata = activity.metadata
            google_backend = metadata.get("google_backend", {})
            event_metadata = google_backend.get("event", google_backend.get("instance", {"instance": {}}))
            event_metadata |= instance
            Activity.objects.filter(id=activity.id).update(metadata=metadata)

            service.events().patch(calendarId=creator_mail, eventId=instance["id"], body=instance).execute()

        except Exception as e:
            raise ValueError(
                "{msg}{exception}".format(msg=cls.error_messages["send_participant_response_error"], exception=e)
            )

    @classmethod
    def sync_with_external_calendar(cls, request: HttpRequest) -> HttpResponse:
        if (
            request.headers
            and (channel_id := request.headers.get("X-Goog-Channel-Id"))
            and User.objects.filter(pk=channel_id).exists()
        ):
            pass  # TODO handle_changes_as_task.delay(channel_id)
        return HttpResponse({})

    @classmethod
    def get_sync_token(cls, user: User) -> str | None:
        if google_backend := user.metadata.get("google_backend"):
            return google_backend.get("sync_token")

    @classmethod
    def delete_internal_activity(cls, activity: Activity, **kwargs) -> None:
        event = kwargs.get("event", {})
        user_email = kwargs.get("user_email", "")
        service = kwargs.get("service")
        if Activity.objects.filter(parent_occurrence=activity).exists() or activity.parent_occurrence:
            delete_recurring_activity(activity, event, user_email, service)
        else:
            delete_single_activity(activity)

    @classmethod
    def update_internal_activity(cls, activity: Activity, **kwargs) -> None:
        event: GoogleEventType = kwargs.get("event", {})
        user_email = kwargs.get("user_email", "")
        service = kwargs.get("service")
        if event.get("recurringEventId"):
            update_single_activity(event, activity)
        elif event.get("recurrence"):
            update_all_activities(activity, event, user_email, service)
        else:
            update_single_activity(event, activity)

    @classmethod
    def create_internal_activity(cls, **kwargs) -> None:
        event = kwargs.get("event", {})
        user = kwargs.get("user")
        service = kwargs.get("service")
        create_internal_activity_based_on_google_event.si(event, user, service)

    @classmethod
    def handle_changes(cls, user_id: int) -> None:
        user = User.objects.get(id=user_id)
        user_email = user.email
        can_sync_past_activities: bool = global_preferences_registry.manager()["wbactivity_sync__sync_past_activity"]
        service = cls._build_service(user_email=user_email)
        now = timezone.now()
        if not service:
            return
        external_event_list = []
        page_token = None
        while True:
            request = service.events().list(
                calendarId=user_email, pageToken=page_token, syncToken=cls.get_sync_token(user)
            )
            events = {}
            try:
                events: Dict = request.execute()
            except Exception as e:
                warnings.warn("{msg}{exception}".format(msg=cls.error_messages["could_not_sync"], exception=e))
            external_event_list += events.get("items", [])
            page_token = events.get("nextPageToken")
            if not page_token:
                user.metadata.setdefault("google_backend", {})
                user.metadata["google_backend"]["sync_token"] = events.get("nextSyncToken")
                user.save()
                break

        for event in external_event_list:
            if event.get("start") and not event.get("recurrence"):
                event_start, _ = GoogleSyncUtils.get_start_and_end(event)
                is_all_day_event = True if event["start"].get("date") else False
                starts_in_past = now.date() > event_start.date() if is_all_day_event else now > event_start
                if not can_sync_past_activities and starts_in_past:
                    return
            external_id = event["id"]
            # Note about how Google assigns IDs for events: A single, non-recurring event has an ID consisting of a unique string.
            # As soon as an event has recurring subsequent events, this string is extended by the start date of the respective subsequent event. these two parts are connected by "_R".
            # So if you look at the part before _R you get the ID for the parent event.
            first_part_of_id = external_id.split("_R")[0] if "_R" in external_id else None
            if (
                (activity := Activity.objects.filter(external_id=external_id).first())
                or (activity := Activity.objects.filter(metadata__google_backend__instance__id=external_id).first())
                or (activity := Activity.objects.filter(metadata__google_backend__event__id=external_id).first())
            ):
                # There are two ways we know an event was deleted. Either we receive the event-status "cancelled", or when the "recurrence" field changes.
                # The second one can also indicate that an event was altered. But at this point we don't know if it was deleted or updated. If it was updated we can restore it later.
                google_backend: Dict = activity.metadata["google_backend"]
                metadata_event: Dict = google_backend.get("event", google_backend.get("instance", {}))
                metadata_event_reccurence: list[str] | None = metadata_event.get("recurrence")

                if event.get("status") == "cancelled" or (
                    event.get("recurrence") and event.get("recurrence") != metadata_event_reccurence
                ):
                    cls.delete_internal_activity(activity, event=event, user_email=user_email, service=service)
                else:
                    cls.update_internal_activity(activity, event=event, user_email=user_email, service=service)
            elif first_part_of_id and (
                parent_occurrence := Activity.objects.filter(external_id=first_part_of_id).first()
            ):
                update_activities_from_new_parent(event, parent_occurrence, user_email, service)
            else:
                cls.create_internal_activity(event=event, user=user, service=service)

    @classmethod
    def get_external_activity(cls, activity: Activity):
        pass

    @classmethod
    def forward_external_activity(cls, activity: Activity, participants: list):
        cls.update_external_activity(activity)

    @classmethod
    def set_web_hook(cls, user: User, expiration_in_ms: int = 0) -> None:
        user_email = user.email
        service = cls._build_service(user_email=user_email)
        if service:
            try:
                watch_body = {
                    "id": user.id,  # type: ignore
                    "type": "web_hook",
                    "address": cls._get_service_account_url(),
                }
                if expiration_in_ms > 0.0:
                    watch_body |= {"expiration": str(expiration_in_ms)}
                response = service.events().watch(calendarId=user_email, body=watch_body).execute()
                user.metadata.setdefault("google_backend", {})
                user.metadata["google_backend"]["watch"] = response
                user.save()
            except Exception as e:
                raise ValueError(
                    "{msg}{user}. Eception: {exception}".format(
                        msg=cls.error_messages["could_not_set_webhook"],
                        user=user.profile.computed_str,
                        exception=e,  # type: ignore
                    )
                )

    @classmethod
    def stop_web_hook(cls, user: User) -> None:
        user_email = user.email
        service = cls._build_service(user_email=user_email)
        if service:
            body = {
                "id": user.metadata["google_backend"]["watch"]["id"],
                "resourceId": user.metadata["google_backend"]["watch"]["resourceId"],
            }
            service.channels().stop(body=body).execute()
            del user.metadata["google_backend"]["watch"]
            user.save()

    @classmethod
    def check_web_hook(cls, user: User) -> None:
        now = timezone.now().replace(tzinfo=None)
        user_google_backend: Dict = user.metadata.get("google_backend", {})
        expiration: str | None = user_google_backend.get("watch", {}).get("expiration")
        if expiration and datetime.fromtimestamp(int(expiration) / 1000) > now:
            warnings.warn(_("Timestamp valid until:") + str(datetime.fromtimestamp(int(expiration) / 1000)))
        else:
            raise Exception(_("No valid web hook found"))

    def _get_webhook_inconsistencies(self) -> str: ...

    def webhook_resubscription(self) -> None: ...
