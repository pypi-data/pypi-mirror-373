import json
import re
import time
from datetime import date, timedelta
from typing import Any

from dateutil import parser
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.utils.translation import gettext, gettext_lazy
from dynamic_preferences.registries import global_preferences_registry
from psycopg.types.range import TimestamptzRange

from wbcrm.synchronization.activity.backend import SyncBackend
from wbcrm.synchronization.activity.utils import flattened_dict_into_nested_dict
from wbcrm.typings import Activity as ActivityDTO
from wbcrm.typings import ParticipantStatus as ParticipantStatusDTO
from wbcrm.typings import User as UserDTO

from .msgraph import MicrosoftGraphAPI
from .parser import OutlookParser, parse

User = get_user_model()


class OutlookSyncBackend(SyncBackend):
    METADATA_KEY = "outlook"

    def open(self):
        self.msgraph = MicrosoftGraphAPI()

    def close(self):
        pass

    def _validation_response(self, request: HttpRequest) -> HttpResponse:
        # handle validation
        if token := request.GET.get("validationToken"):
            return HttpResponse(token, content_type="text/plain")
        # handle callback consent permision
        if _consent := request.GET.get("admin_consent"):
            return HttpResponse(_consent, content_type="text/plain")
        return super()._validation_response(request)

    def _is_inbound_request_valid(self, request: HttpRequest) -> bool:
        is_valid = False
        try:
            if request.body and (json_body := json.loads(request.body)) and (notifications := json_body.get("value")):
                # When many changes occur, MSGraph may send multiple notifications that correspond to different subscriptions in the same POST request.
                for notification in parse(notifications):
                    if (
                        notification.get("client_state")
                        == global_preferences_registry.manager()["wbactivity_sync__outlook_sync_client_state"]
                        and (resource_data := notification.get("resource_data"))
                        and (event_type := resource_data.get("@odata.type", "").lower())
                        and (event_type == "#microsoft.graph.event")
                    ):
                        is_valid = True
                    else:
                        return False
        except json.decoder.JSONDecodeError:
            return False
        return is_valid

    def _get_events_from_request(self, request: HttpRequest) -> list[dict[str, Any]]:
        events = []
        for notification in parse(json.loads(request.body)["value"]):
            event = {
                "change_type": notification["change_type"],
                "resource": notification["resource"],
                "subscription_id": notification["subscription_id"],
            }
            if data := self.msgraph.get_event_by_resource(notification["resource"]):
                # Try to get the organizer's event in case if it's an invitation event
                if data["is_organizer"] is True:
                    event["organizer_resource"] = notification["resource"]
                elif (
                    (tenant_id := self.msgraph.get_tenant_id(data["organizer.email_address.address"]))
                    and data["is_organizer"] is False
                    and (organizer_data := self.msgraph.get_event_by_uid(tenant_id, data["uid"]))
                ):
                    event["organizer_resource"] = f"Users/{tenant_id}/Events/{organizer_data['id']}"
                    data = organizer_data
                event.update(data)
            events.append(event)
        return events

    def _deserialize(self, event: dict[str, Any], include_metadata: bool = True) -> tuple[ActivityDTO, bool, UserDTO]:
        event_id = event.get("id")
        delete_notification = event.get("change_type") == "deleted"
        is_deleted = delete_notification or not event_id or event.get("is_cancelled") is True
        user_dto = UserDTO(metadata={self.METADATA_KEY: {"subscription": {"id": event.get("subscription_id")}}})
        if include_metadata:
            _metadata = {"event_uid": event["uid"], "event_id": event_id} if event_id else {}
            if resource := event.get("resource"):
                _metadata["resources"] = [resource]
            if organizer_resource := event.get("organizer_resource"):
                _metadata["organizer_resource"] = organizer_resource
            elif is_deleted and resource:
                _metadata["organizer_resource"] = resource
            metadata = {self.METADATA_KEY: _metadata}
        else:
            metadata = {}

        if event_id:
            start = OutlookParser.convert_string_to_datetime(event["start.date_time"], event["start.time_zone"])
            end = OutlookParser.convert_string_to_datetime(event["end.date_time"], event["end.time_zone"])
            if start == end:
                end += timedelta(seconds=1)
            period = TimestamptzRange(start, end)
            if event["is_all_day"] is True:
                period = OutlookParser.convert_to_all_day_period(period)
            participants, conference_room = OutlookParser.deserialize_participants(event)
            recurrence_dict = OutlookParser.deserialize_recurring_activities(event)
            if event.get("is_reminder_on"):
                reminder_choice = OutlookParser.convert_reminder_minutes_to_choice(
                    event.get("reminder_minutes_before_start")
                )
            else:
                reminder_choice = ActivityDTO.ReminderChoice.NEVER.name
            activity_dto = ActivityDTO(
                metadata=metadata,
                title=event["subject"] if event.get("subject") else "(No Subject)",
                period=period,
                description=event.get("body.content", ""),
                participants=participants,
                creator=OutlookParser.deserialize_person(
                    event["organizer.email_address.address"], event["organizer.email_address.name"]
                ),
                visibility=OutlookParser.convert_sensitivity_to_visibility(event.get("sensitivity")),
                reminder_choice=reminder_choice,
                is_cancelled=event.get("is_cancelled", False),
                all_day=event.get("is_all_day", False),
                online_meeting=event.get("is_online_meeting", False),
                location=event.get("location.display_name"),
                conference_room=conference_room[0] if conference_room else None,
                recurrence_end=recurrence_dict["recurrence_end"],
                recurrence_count=recurrence_dict["recurrence_count"],
                repeat_choice=recurrence_dict["repeat_choice"],
            )
            if (
                event["type"] == "seriesMaster"
                and (tenant_id := self.msgraph.get_tenant_id(activity_dto.creator.email))
                and (
                    occurrences := self.msgraph.get_instances_event(
                        tenant_id, event["id"], start.date(), end.date() + relativedelta(years=10)
                    )
                )
            ):
                recurring_activities = []
                for occurrence in occurrences:
                    instance_dto, *_ = self._deserialize(occurrence, include_metadata=False)
                    instance_dto.recurrence_end = activity_dto.recurrence_end
                    instance_dto.recurrence_count = activity_dto.recurrence_count
                    instance_dto.repeat_choice = activity_dto.repeat_choice
                    instance_dto.metadata = {
                        self.METADATA_KEY: {
                            **metadata[self.METADATA_KEY],
                            "occurrence_id": occurrence["id"],
                            "occurrence_resource": f"Users/{tenant_id}/Events/{occurrence['id']}",
                        }
                    }
                    if (extension := self.msgraph.get_extension_event(tenant_id, occurrence["id"])) and (
                        act_id := extension.get("activity_id")
                    ):
                        instance_dto.id = act_id
                    recurring_activities.append(instance_dto)
                activity_dto.recurring_activities = recurring_activities
        else:
            activity_dto = ActivityDTO(metadata=metadata, title=event.get("subject", "(No Subject)"))
        activity_dto.delete_notification = delete_notification
        return activity_dto, is_deleted, user_dto

    def _serialize(self, activity_dto: ActivityDTO, created: bool = False) -> dict[str, Any]:
        attendees = OutlookParser.serialize_participants(activity_dto.participants)
        if activity_dto.conference_room:
            attendees.append(OutlookParser.serialize_conference_room(activity_dto.conference_room))

        activity_dict = {
            "subject": activity_dto.title,
            "start": {
                "dateTime": activity_dto.period.lower.isoformat(),
                "timeZone": activity_dto.period.lower.tzname(),
            },
            "end": {
                "dateTime": activity_dto.period.upper.isoformat(),
                "timeZone": activity_dto.period.upper.tzname(),
            },
            "body": {
                "contentType": "HTML",
                "content": activity_dto.description,
            },
            "attendees": attendees,
            "sensitivity": OutlookParser.convert_visibility_to_sensitivity(activity_dto.visibility),
            "reminderMinutesBeforeStart": OutlookParser.convert_reminder_choice_to_minutes(
                activity_dto.reminder_choice
            ),
            "isReminderOn": False if activity_dto.reminder_choice == ActivityDTO.ReminderChoice.NEVER.name else True,
            "isAllDay": activity_dto.all_day,
            "responseRequested": True,
        }

        if activity_dto.online_meeting:
            activity_dict.update(
                {"allowNewTimeProposals": True, "isOnlineMeeting": True, "onlineMeetingProvider": "teamsForBusiness"}
            )
        if activity_dto.location:
            activity_dict["location"] = {
                "displayName": (
                    activity_dto.location if isinstance(activity_dto.location, str) else str(activity_dto.location)
                )
            }
        activity_dict["locations"] = [{"displayName": activity_dto.location}] if activity_dto.location else []
        if created and activity_dto.is_recurrent:
            activity_dict.update(OutlookParser.serialize_recurring_activities(activity_dto))
        return activity_dict

    def _stream_deletion(self, activity_dto: ActivityDTO):
        if event := self.get_external_event(activity_dto):
            if tenant_id := self.msgraph.get_tenant_id(activity_dto.creator.email):
                self.msgraph.delete_event(tenant_id, event["id"])

    def _stream_creation(
        self, activity_dto: ActivityDTO, activity_dict: dict[str, Any]
    ) -> list[tuple[ActivityDTO, dict[str, Any]]] | None:
        if not self.get_external_event(activity_dto) and (
            tenant_id := self.msgraph.get_tenant_id(activity_dto.creator.email)
        ):
            if event := self.msgraph.create_event(tenant_id, activity_dict):
                metadata_list = self._get_metadata_from_event(activity_dto, event)
                for act_dto, _metadata in metadata_list:
                    if act_dto.is_recurrent:
                        self._stream_extension_event(act_dto, _metadata)
                return metadata_list

    def _stream_update(
        self,
        activity_dto: ActivityDTO,
        activity_dict: dict[str, Any] | None = None,
        only_participants_changed: bool = False,
        external_participants: list = [],
        keep_external_description: bool = False,
    ) -> tuple[ActivityDTO, dict[str, Any]]:
        if old_event := self.get_external_event(activity_dto):
            if tenant_id := self.msgraph.get_tenant_id(activity_dto.creator.email):
                activity_dict = activity_dict or old_event
                # When a participant is removed, we send a complete update of the event to remove this person in outlook
                activity_dict["attendees"] += external_participants
                if only_participants_changed:
                    # An event update that includes only the attendees property in the request body sends a meeting update to only the attendees that have changed.
                    # An event update that removes an attendee specified as a member of a distribution list sends a meeting update to all the attendees.
                    activity_dict = {"attendees": activity_dict["attendees"]}
                elif keep_external_description:
                    # preserve body when description is not synchronized especially meeting blob for online meeting.
                    activity_dict["body"]["content"] = old_event.get("body.content", "")

                if (
                    activity_dto.is_recurrent
                    and activity_dto.propagate_for_all_children
                    and not activity_dto.is_leaf
                    and (old_master_event := self.get_external_event(activity_dto, master_event=True))
                ):
                    if activity_dto.is_root:
                        self.msgraph.update_event(tenant_id, old_master_event["id"], activity_dict)
                    else:
                        return self._stream_update_from_occurrence(activity_dto, old_master_event, activity_dict)
                else:
                    self.msgraph.update_event(tenant_id, old_event["id"], activity_dict)
        elif not activity_dto.metadata.get(self.METADATA_KEY):
            # creation of recurring activity is done only during the creation phase of the activity
            if activity_dto.is_recurrent and activity_dict.get("recurrence"):
                activity_dict.pop("recurrence")
            return self._stream_creation(activity_dto, activity_dict)

    def _stream_update_from_occurrence(self, activity_dto: ActivityDTO, old_master_event: dict, activity_dict: dict):
        if (tenant_id := self.msgraph.get_tenant_id(activity_dto.creator.email)) and (
            instances_dict := self._get_occurrences_from_master_event(
                old_master_event, start_date_as_key=True, from_date=activity_dto.period.lower.date()
            )
        ):
            # Update recurrence pattern from old root to new root
            remaining_old_recurrence = {
                "recurrence": flattened_dict_into_nested_dict(OutlookParser.serialize_event_keys(old_master_event))[
                    "recurrence"
                ]
            }
            last_start_old = activity_dto.period.lower - timedelta(days=1)
            if remaining_old_recurrence := OutlookParser.serialize_recurrence_range_with_end_date(
                remaining_old_recurrence, last_start_old
            ):
                self.msgraph.update_event(tenant_id, old_master_event["id"], remaining_old_recurrence)
            # Create recurrence from new root
            new_recurrence = OutlookParser.serialize_recurring_activities(activity_dto)
            last_start_new = sorted(instances_dict.keys()).pop()
            if new_recurrence := OutlookParser.serialize_recurrence_range_with_end_date(
                new_recurrence, last_start_new
            ):
                activity_dict.update(new_recurrence)
                if new_master_event := self.msgraph.create_event(tenant_id, activity_dict):
                    # delete occurrences that had been deleted in the past
                    if new_instances_dict := self._get_occurrences_from_master_event(
                        new_master_event, start_date_as_key=True
                    ):
                        for key, value in new_instances_dict.items():
                            if not instances_dict.get(key):
                                self.msgraph.delete_event(tenant_id, value["id"])
                    metadata_list = self._get_metadata_from_event(activity_dto, new_master_event)
                    for act_dto, _metadata in metadata_list:
                        if act_dto.is_recurrent:
                            self._stream_extension_event(act_dto, _metadata)
                    return metadata_list

    def _stream_update_only_attendees(self, activity_dto: ActivityDTO, participants_dto: list[ParticipantStatusDTO]):
        new_attendees = OutlookParser.serialize_participants(participants_dto)
        self._stream_update(
            activity_dto=activity_dto,
            external_participants=new_attendees,
            only_participants_changed=True,
        )

    def _stream_forward(self, activity_dto: ActivityDTO, participants_dto: list[ParticipantStatusDTO]):
        if (event := self.get_external_event(activity_dto)) and (
            tenant_id := self.msgraph.get_tenant_id(activity_dto.creator.email)
        ):
            new_attendees = []
            participants, _ = OutlookParser.deserialize_participants(event)
            external_emails_participants = [participant.person.email for participant in participants]
            for participant_dto in participants_dto:
                # forward if it is not the organizer or if it is not already part of the participants
                if (
                    participant_dto.person.email != activity_dto.creator.email
                    and participant_dto.person.email not in external_emails_participants
                ):
                    new_attendees.append(OutlookParser.serialize_person(participant_dto.person))
                    self.msgraph.forward_event(tenant_id, event["id"], new_attendees)

    def _stream_participant_change(
        self, participant_dto: ParticipantStatusDTO, is_deleted: bool = False, wait_before_changing: bool = False
    ):
        if (organizer_event := self.get_external_event(participant_dto.activity)) and (
            tenant_id := self.msgraph.get_tenant_id(participant_dto.person.email)
        ):
            if wait_before_changing:
                time.sleep(10)
            if invitation_event := self.msgraph.get_event_by_uid(tenant_id, organizer_event["uid"]):
                if participant_dto.person.email == participant_dto.activity.creator.email:
                    if is_deleted or participant_dto.status == ParticipantStatusDTO.ParticipationStatus.CANCELLED.name:
                        pass  # self.msgraph.cancel_event(tenant_id, invitation_event["id"]) # delete activity if organizer is removed of participants
                else:
                    if is_deleted or participant_dto.status == ParticipantStatusDTO.ParticipationStatus.CANCELLED.name:
                        self.msgraph.decline_event(tenant_id, invitation_event["id"])
                    elif participant_dto.status == ParticipantStatusDTO.ParticipationStatus.MAYBE.name:
                        self.msgraph.tentatively_accept_event(tenant_id, invitation_event["id"])
                    elif participant_dto.status in [
                        ParticipantStatusDTO.ParticipationStatus.ATTENDS.name,
                        ParticipantStatusDTO.ParticipationStatus.ATTENDS_DIGITALLY.name,
                    ]:
                        self.msgraph.accept_event(tenant_id, invitation_event["id"])

    def _stream_extension_event(self, activity_dto: ActivityDTO, metadata: dict | None = None) -> None:
        metadata = metadata if metadata else activity_dto.metadata
        if (
            (tenant_id := self.msgraph.get_tenant_id(activity_dto.creator.email))
            and (_metadata := metadata.get(self.METADATA_KEY))
            and (occurrence_id := _metadata.get("occurrence_id"))
        ):
            self.msgraph.update_or_create_extension_event(tenant_id, occurrence_id, {"activity_id": activity_dto.id})

    def _set_web_hook(self, user: "User") -> dict[str, dict[str, Any]]:
        response = {}
        self.open()
        if (
            (outlook := user.metadata.get(self.METADATA_KEY))
            and (subscription := outlook.get("subscription"))
            and (ms_subscription := self.msgraph.subscription(subscription.get("id")))
        ):
            response = self.msgraph._renew_subscription(ms_subscription.get("id"))
        elif tenant_id := self.msgraph.get_tenant_id(user.email):
            response = self.msgraph._subscribe(f"users/{tenant_id}/events/", "created, updated, deleted")
        else:
            raise Exception(gettext("Outlook TenantId not found for: ") + str(user))
        self.close()
        return {"subscription": response} if response else user.metadata.get(self.METADATA_KEY, {})

    def _stop_web_hook(self, user: "User") -> dict[str, dict[str, Any]]:
        if (
            (outlook_backend := user.metadata.get(self.METADATA_KEY))
            and (subscription := outlook_backend.get("subscription"))
            and (subscription_id := subscription.get("id"))
        ):
            self.open()
            self.msgraph._unsubscribe(subscription_id)
            self.close()
            del user.metadata[self.METADATA_KEY]["subscription"]
        else:
            raise ValueError(str(user) + gettext(" has no active webhook"))
        return user.metadata.get(self.METADATA_KEY)

    def check_web_hook(self, user: "User", raise_error: bool = True) -> bool:
        error = ""
        self.open()
        if (outlook := user.metadata.get(self.METADATA_KEY)) and (subscription := outlook.get("subscription")):
            if not self.msgraph.subscription(subscription.get("id")):
                error = gettext("Webhook is invalid, Remove or Stop it and Set again please. ")
        else:
            error = gettext("Webhook not found. ")
        if error and raise_error:
            if user_tenant_id := self.msgraph.get_tenant_id(user.email):
                tenant_ids = [
                    items[1]
                    for sub in self.msgraph.subscriptions()
                    if (resource := sub.get("resource")) and (items := resource.split("/")) and len(items) > 2
                ]
                error += gettext(
                    "Number of subscriptions found in outlook for {} out of the total number: {}/{}."
                ).format(user.email, tenant_ids.count(user_tenant_id), len(tenant_ids))
            else:
                error += gettext("TenantId not found for ") + str(user)
            raise Exception(error)
        self.close()
        return False if error else True

    def renew_web_hooks(self) -> None:
        self.open()
        lookup = {f"metadata__{self.METADATA_KEY}__subscription__id__isnull": False}
        for user in User.objects.filter(**lookup):
            if response := self.msgraph._renew_subscription(user.metadata[self.METADATA_KEY]["subscription"]["id"]):
                user.metadata[self.METADATA_KEY]["subscription"] = response
                user.save()
        self.close()

    def _get_webhook_inconsistencies(self) -> str:
        self.open()
        subscriptions = self.msgraph.subscriptions()
        calls = set(
            list(
                map(
                    lambda x: x["id"],
                    list(filter(lambda x: x["resource"] == "/communications/callRecords", subscriptions)),
                )
            )
        )
        calendars = set(
            list(
                map(
                    lambda x: x["id"],
                    list(filter(lambda x: bool(re.match(r"users\/.*\/events\/", x["resource"])), subscriptions)),
                )
            )
        )
        lookup = f"metadata__{self.METADATA_KEY}__subscription__id"
        stored_calendars = set(User.objects.filter(**{f"{lookup}__isnull": False}).values_list(lookup, flat=True))
        message = ""
        if len(calls) == 0:
            message += gettext_lazy("<li>No Call Record subscription found in Microsoft</li>")
        if calendars != stored_calendars:
            diff = calendars.difference(stored_calendars)
            diff_inv = stored_calendars.difference(calendars)
            message += gettext_lazy(
                """
                <li>Number of calendar subscription not found in our system : <b>{}</b></li>
                <p>{}</p>

                <li>Number of calendar subscription assumed to be active not found in outlook: <b>{}</b></li>
                <p>{}</p>
            """
            ).format(len(diff), diff, len(diff_inv), diff_inv)
        if message == "":
            for subscription in subscriptions:
                if expiration_date_time := subscription.get("expiration_date_time"):
                    date_time = parser.parse(expiration_date_time)
                    diff = date_time - timezone.now()
                    if diff.days < 1:
                        message += f"Resource: {subscription['resource']} expires on {date_time} (in {diff})"
        self.close()
        return message

    def get_external_event(self, activity_dto: ActivityDTO, master_event: bool = False) -> dict:
        event = None
        metadata = activity_dto.metadata.get(self.METADATA_KEY, {})
        if master_event or not activity_dto.is_recurrent:
            if resource := metadata.get("organizer_resource"):
                event = self.msgraph.get_event_by_resource(resource)
            if (creator := activity_dto.creator) and (tenant_id := self.msgraph.get_tenant_id(creator.email)):
                if not event and (event_id := metadata.get("event_id")):
                    event = self.msgraph.get_event(tenant_id, event_id)
                if not event and (event_uid := metadata.get("event_uid")):
                    event = self.msgraph.get_event_by_uid(tenant_id, event_uid)
        else:
            if resource := metadata.get("occurrence_resource"):
                event = self.msgraph.get_event_by_resource(resource)
            elif (
                not event
                and (creator := activity_dto.creator)
                and (tenant_id := self.msgraph.get_tenant_id(creator.email))
                and metadata.get("occurrence_id")
            ):
                event = self.msgraph.get_event(tenant_id, metadata["occurrence_id"])
        return event

    def get_external_participants(
        self, activity_dto: ActivityDTO, internal_participants_dto: list[ParticipantStatusDTO]
    ) -> list:
        external_participants = []
        if event := self.get_external_event(activity_dto):
            internal_emails = [
                participant_dto.person.email for participant_dto in internal_participants_dto if participant_dto.person
            ]
            for participant in event.get("attendees", []):
                if participant["emailAddress"]["address"] not in internal_emails:
                    external_participants.append(participant)
        return external_participants

    def _is_participant_valid(self, user: "User") -> bool:
        try:
            return super()._is_participant_valid(user) and self.check_web_hook(user, raise_error=False)
        except Exception:
            return False

    def _generate_event_metadata(self, tenant_id: str, master_event: dict, occurrence_event: dict = {}):
        resource = f"Users/{tenant_id}/Events/{master_event['id']}"
        metadata = {
            self.METADATA_KEY: {
                "resources": [resource],
                "organizer_resource": resource,
                "event_uid": master_event["uid"],
                "event_id": master_event["id"],
            }
        }
        if occurrence_event:
            metadata[self.METADATA_KEY].update(
                {
                    "occurrence_id": occurrence_event["id"],
                    "occurrence_resource": f"Users/{tenant_id}/Events/{occurrence_event['id']}",
                }
            )
        return metadata

    def _get_metadata_from_event(
        self, activity_dto: ActivityDTO, event: dict
    ) -> list[tuple[ActivityDTO, dict[str, Any]]]:
        metadata_list = []
        if tenant_id := self.msgraph.get_tenant_id(activity_dto.creator.email):
            if event.get("type") == "seriesMaster" and (
                instances_dict := self._get_occurrences_from_master_event(event, start_date_as_key=True)
            ):
                occurrence = instances_dict.get(activity_dto.period.lower.date(), {})
                metadata_list.append((activity_dto, self._generate_event_metadata(tenant_id, event, occurrence)))
                instances_dto = activity_dto.recurring_activities + activity_dto.invalid_recurring_activities
                for instance_dto in instances_dto:
                    if occurrence := instances_dict.get(instance_dto.period.lower.date()):
                        metadata_list.append(
                            (instance_dto, self._generate_event_metadata(tenant_id, event, occurrence))
                        )
            else:
                metadata_list.append((activity_dto, self._generate_event_metadata(tenant_id, event)))
        return metadata_list

    def _get_occurrences_from_master_event(
        self, event: dict, start_date_as_key: bool = False, from_date: date = None
    ) -> dict:
        """
        Dict of instances event whose key is id by default otherwise start date and the value is the occurrence event data.
        """
        start = (
            from_date
            if from_date
            else OutlookParser.convert_string_to_datetime(event["start.date_time"], event["start.time_zone"]).date()
        )
        end = OutlookParser.convert_string_to_datetime(
            event["end.date_time"], event["end.time_zone"]
        ).date() + relativedelta(years=10)
        tenant_id = self.msgraph.get_tenant_id(event["organizer.email_address.address"])
        occurrences_dict = {}
        if occurrences := self.msgraph.get_instances_event(tenant_id, event["id"], start, end):
            if start_date_as_key:
                occurrences_dict = {
                    OutlookParser.convert_string_to_datetime(
                        occurrence["start.date_time"], occurrence["start.time_zone"]
                    ).date(): occurrence
                    for occurrence in occurrences
                }
            else:
                occurrences_dict = {occurrence["id"]: occurrence for occurrence in occurrences}
        return occurrences_dict
