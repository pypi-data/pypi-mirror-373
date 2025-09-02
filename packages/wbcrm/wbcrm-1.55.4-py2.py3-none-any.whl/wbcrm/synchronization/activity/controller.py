import copy
import dataclasses
import operator
from functools import reduce
from typing import Any

from django.conf import settings
from django.db import transaction
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from wbcore.contrib.agenda.models import Building, ConferenceRoom
from wbcore.contrib.directory.models import EmailContact, Person

from wbcrm.models import Activity, ActivityParticipant, ActivityType, Event
from wbcrm.synchronization.activity.utils import flattened_metadata_lookup
from wbcrm.typings import Activity as ActivityDTO
from wbcrm.typings import ConferenceRoom as ConferenceRoomDTO
from wbcrm.typings import ParticipantStatus as ParticipantStatusDTO
from wbcrm.typings import Person as PersonDTO
from wbcrm.typings import User as UserDTO

from .backend import SyncBackend
from .preferences import (
    can_sync_cancelled_activity,
    can_sync_cancelled_external_activity,
    can_sync_create_new_activity_on_replanned_reviewed_activity,
    can_sync_past_activity,
    can_synchronize_activity_description,
    can_synchronize_external_participants,
)


class ActivityController:
    update_fields = [
        "title",
        "period",
        "visibility",
        "creator",
        "conference_room",
        "reminder_choice",
        "is_cancelled",
        "all_day",
        "online_meeting",
        "location",
        "description",
    ]

    def __init__(self, backend: SyncBackend):
        if settings.DEBUG:
            raise ValueError("DEBUG Mode -> activity sync disabled")
        self.backend = backend()

    def _is_valid(self, activity_dto: ActivityDTO) -> bool:
        """
        Check if the activity can be synchronized or not.
        - Past activity is not synchronized if global preference is False
        - Activity is synchronized if at least one of the participants has an active webhook
        """
        if period := activity_dto.period:
            if period.upper < timezone.now() and not can_sync_past_activity():
                return False
            else:
                return self.backend.is_valid(activity_dto)
        else:
            qs_activities = self.get_activities(activity_dto)
            with transaction.atomic():
                return qs_activities.exists() and any(
                    [self._is_valid(act._build_dto()) for act in qs_activities if act.period]
                )

    def handle_inbound_validation_response(self, request: HttpRequest) -> HttpResponse:
        """
        allows to send a response to the external calendar if it is required before receiving the events in the webhook
        """
        return self.backend._validation_response(request)

    def get_events_from_inbound_request(self, request: HttpRequest) -> list[dict[str, Any]]:
        """
        allows to get list of event following the notification
        """
        events = []
        self.backend.open()
        if self.backend._is_inbound_request_valid(request):
            for event in self.backend._get_events_from_request(request):
                events.append(event)
        self.backend.close()
        return events

    def handle_inbound(self, event: dict, event_object_id: int) -> None:
        """
        Each event received in the webhook is processed here, it allows to delete or create/update the corresponding activity
        """
        self.backend.open()
        activity_dto, is_deleted, user_dto = self.backend._deserialize(event)
        if activity_dto.is_recurrent or self._is_valid(activity_dto):
            if is_deleted:
                self.delete_activity(activity_dto, user_dto, event_object_id)
            else:
                self.update_or_create_activity(activity_dto, event_object_id)
        self.backend.close()

    def _handle_outbound_data_preferences(self, activity_dto: ActivityDTO) -> tuple[ActivityDTO, list]:
        """
        Activity data is parsed to take into account the company's preferences
        this allows you to exclude the description or exclude external participants from the data if global preference is True
        """
        if not can_synchronize_activity_description():
            activity_dto.description = ""
        valid_participants = []
        internal_participants = []
        for participant_dto in activity_dto.participants:
            # External person are removed of the list if global preference is True
            if (
                Person.all_objects.get(id=participant_dto.person.id).is_internal
                or can_synchronize_external_participants()
            ):
                internal_participants.append(participant_dto)
                if participant_dto.status != ActivityParticipant.ParticipationStatus.CANCELLED:
                    valid_participants.append(participant_dto)

        activity_dto.participants = valid_participants

        # list of external participants present in the external event, they will be added to the participants before updating the event to avoid deleting them
        external_participants = (
            self.backend.get_external_participants(activity_dto, internal_participants)
            if not can_synchronize_external_participants()
            else []
        )
        return activity_dto, external_participants

    def handle_outbound(
        self, activity_dto: ActivityDTO, old_activity_dto: ActivityDTO = None, is_deleted: bool = False
    ):
        """
        Requests sent to the external calendar are processed here
        It allows to send requests to delete, modify or create the event in the external calendar corresponding to the activity
        """
        if not self._is_valid(activity_dto):
            return
        self.backend.open()
        if is_deleted or activity_dto.is_cancelled:
            self.backend._stream_deletion(activity_dto)
        else:
            activities_metadata = []
            created = True if not old_activity_dto else False
            # dataclasses.replace returns a new copy of the object without passing in any changes, return a copy with no modification
            activity_dto_preference, external_participants = self._handle_outbound_data_preferences(
                dataclasses.replace(activity_dto)
            )
            activity_dict = self.backend._serialize(activity_dto_preference, created=created)
            if created:  # then it's a creation
                activities_metadata = self.backend._stream_creation(activity_dto, activity_dict)
            elif self._has_changed(activity_dto, old_activity_dto):
                keep_external_description = not can_synchronize_activity_description()
                only_participants_changed = self._has_changed(
                    activity_dto, old_activity_dto, update_fields=["participants"]
                ) and not self._has_changed(activity_dto, old_activity_dto, exclude_fields=["participants"])
                activities_metadata = self.backend._stream_update(
                    activity_dto,
                    activity_dict,
                    only_participants_changed,
                    external_participants,
                    keep_external_description,
                )

            if activities_metadata:
                for act_dto, act_metadata in activities_metadata:
                    self.update_activity_metadata(act_dto, act_metadata)
        self.backend.close()

    def handle_outbound_participant(
        self,
        participant_dto: ParticipantStatusDTO,
        old_participant_dto: ParticipantStatusDTO = None,
        is_deleted: bool = False,
    ):
        """
        allows to update the status of the event in the external calendar to match the one updated in the internal activity
        """
        # check if activity creator is internal or activity is not passed according to global preference
        if not self._is_valid(participant_dto.activity):
            return

        # check if participant is internal or can sync external participant is allowed according to global preference
        if not (
            Person.all_objects.get(id=participant_dto.person.id).is_internal or can_synchronize_external_participants()
        ):
            return

        self.backend.open()
        was_cancelled = False
        status_changed = False
        if old_participant_dto and old_participant_dto.status != participant_dto.status:
            was_cancelled = old_participant_dto.status == ActivityParticipant.ParticipationStatus.CANCELLED
            status_changed = participant_dto.status not in [
                ActivityParticipant.ParticipationStatus.NOTRESPONDED,
                ActivityParticipant.ParticipationStatus.PENDING_INVITATION,
            ]

        wait_before_changing_status = False
        if (not is_deleted and not old_participant_dto) or was_cancelled:
            # self.backend._stream_forward(participant_dto.activity, [participant_dto])
            # forward event doesn't work when user is an external, following the documentation it's recommended to only include the attendees property in the request body
            # It will only send notifications to newly added attendees.
            self.backend._stream_update_only_attendees(
                activity_dto=participant_dto.activity, participants_dto=[participant_dto]
            )
            wait_before_changing_status = status_changed
        if is_deleted or status_changed:
            self.backend._stream_participant_change(
                participant_dto, is_deleted, wait_before_changing=wait_before_changing_status
            )
        self.backend.close()

    def handle_outbound_external_participants(self, activity_dto, participants_dto: list[ParticipantStatusDTO]):
        """
        allows to update the status of the event in the external calendar to match the one updated in the internal activity
        """
        # check if activity creator is internal or activity is not passed according to global preference
        if not self._is_valid(activity_dto):
            return

        self.backend.open()
        self.backend._stream_update_only_attendees(activity_dto=activity_dto, participants_dto=participants_dto)
        self.backend.close()

    def _changed_participants(
        self, participants: list[ParticipantStatusDTO], old_participants: list[ParticipantStatusDTO]
    ) -> bool:
        """
        Comparison of 2 lists of participants, returns false if they are identical
        """
        d1 = {elt.person.email: elt.status for elt in participants}
        d2 = {elt.person.email: elt.status for elt in old_participants}
        if set(d1.keys()) == set(d2.keys()):
            return any([d1[key] != d2[key] for key in d1.keys()])
        return True

    def _has_changed(
        self,
        activity_dto: ActivityDTO,
        old_activity_dto: ActivityDTO,
        update_fields: list = [],
        exclude_fields: list = [],
    ) -> bool:
        """
        Comparison of 2 activities, returns false if they are identical

        :param update_fields: allows to specify the list of fields taken into account in the comparison,
        if not specified we use the list of the controller

        :param exclude_fields: allows you to exclude fields from the comparison list
        """
        if not can_synchronize_activity_description():
            exclude_fields.append("description")
        update_fields = (
            update_fields
            if update_fields
            else (
                self.update_fields + ["propagate_for_all_children", "exclude_from_propagation"]
                if self.update_fields
                else activity_dto.__dataclass_fields__
            )
        )
        fields = list(set(update_fields) - set(exclude_fields))
        if "participants" in fields:
            fields.remove("participants")
            participants_changed = self._changed_participants(activity_dto.participants, old_activity_dto.participants)
        else:
            participants_changed = False
        is_new_activity = True if activity_dto and not old_activity_dto else False
        return (
            participants_changed
            or is_new_activity
            or (
                activity_dto
                and old_activity_dto
                and any(
                    [getattr(activity_dto, field, None) != getattr(old_activity_dto, field, None) for field in fields]
                )
            )
        )

    def get_activities(self, activity_dto: ActivityDTO, _operator: operator = operator.or_) -> QuerySet["Activity"]:
        """
        Received events are deserialized into data transfer object of activity,
        we use the metadata construct to identify the activity
        the operator allows to know which operation combination to perform during the filter
        """
        if conditions := [
            Q(**{key: value}) for key, value in flattened_metadata_lookup(activity_dto.metadata, key_string="metadata")
        ]:
            return Activity.all_objects.select_for_update().filter(reduce(_operator, conditions))
        return Activity.objects.none()

    def get_activity_participant(self, user_dto: UserDTO) -> Person:
        """
        Attendees of the external event are deserialized into person data transfer objects
        we use the metadata construct to identify the person
        """
        if conditions := [
            Q(**{key: value})
            for key, value in flattened_metadata_lookup(user_dto.metadata, key_string="user_account__metadata")
        ]:
            try:
                return Person.objects.get(reduce(operator.and_, conditions))
            except Exception:
                return None
        return None

    def _get_data_from_activity_dto(self, activity_dto: ActivityDTO, parent_occurrence: Activity = None) -> dict:
        """
        Data transfer object of activity obtained from the external event is parsed into a dict to allow the creation or update of the object in the database
        """
        activity_data = {}
        fields = self.update_fields if self.update_fields else activity_dto.__dataclass_fields__
        if not can_synchronize_activity_description() and "description" in fields:
            fields.remove("description")

        for field in fields:
            activity_data[field] = getattr(activity_dto, field)
        if activity_data.get("creator"):
            activity_data["creator"] = self.get_or_create_person(activity_dto.creator)
        if activity_data.get("conference_room"):
            activity_data["conference_room"] = self.get_or_create_conference_room(activity_dto.conference_room)
        if activity_dto.is_recurrent:
            activity_data.update(
                {
                    "recurrence_end": activity_dto.recurrence_end,
                    "recurrence_count": activity_dto.recurrence_count,
                    "repeat_choice": activity_dto.repeat_choice,
                }
            )
            if parent_occurrence:
                activity_data["parent_occurrence"] = parent_occurrence
        return activity_data

    def _create_activity(self, activity_dto: ActivityDTO, parent_occurrence: Activity = None) -> Activity:
        """
        Uses the Data transfer object obtained from the external event to create the activity in the database
        """
        activity_data = self._get_data_from_activity_dto(activity_dto, parent_occurrence)
        activity_type, created = ActivityType.objects.get_or_create(
            slugify_title="meeting", defaults={"title": "Meeting"}
        )
        activity = Activity(**activity_data, type=activity_type)
        activity.save(synchronize=False)
        if activity.period.lower < activity.created:
            # A created past event should not appear at the top of the list.
            Activity.objects.filter(id=activity.id).update(created=activity.period.lower, edited=activity.period.lower)
        self.update_or_create_participants(activity, activity_dto.participants)
        self.update_activity_metadata(activity._build_dto(), activity_dto.metadata)
        return activity

    def _update_activity(
        self, activity: Activity, activity_dto: ActivityDTO, parent_occurrence: Activity = None
    ) -> tuple[Activity, str]:
        """
        Convert the data transfer object obtained from the external event into a dict to update the activity in the database.
        """
        activity_data = self._get_data_from_activity_dto(activity_dto, parent_occurrence)
        if has_changed := self._has_changed(activity_dto, activity._build_dto(), update_fields=activity_data.keys()):
            # When previously canceled by the only internal participant is finally accepted by the latter
            if (
                (creator := activity.creator)
                and not creator.is_internal
                and activity.status == Activity.Status.CANCELLED
            ):
                activity_data["status"] = Activity.Status.PLANNED
            Activity.objects.filter(id=activity.id).update(**activity_data)
            activity.refresh_from_db()
            activity.save(synchronize=False)
        _, participant_changed = self.update_or_create_participants(activity, activity_dto.participants)
        self.update_activity_metadata(activity._build_dto(), activity_dto.metadata)
        return activity, f"activity_changes: {has_changed}, participants_changes: {participant_changed or False}; "

    @transaction.atomic
    def update_or_create_activity(self, activity_dto: ActivityDTO, event_object_id: int | None = None) -> None:
        """
        allows you to create or update a single or recurring activity from a data transfer object obtained from an external event
        """
        qs_activities = self.get_activities(activity_dto)
        if activity_dto.is_recurrent:
            event_result = {"action_type": "update or create recurring activities", "action": ""}
            ids_dto_dict = {}
            dates_dto_dict = {}
            for _dto in activity_dto.recurring_activities:
                if _dto.id:
                    ids_dto_dict[_dto.id] = _dto
                dates_dto_dict[_dto.period.lower.date()] = _dto
            ids_dto_list = set(ids_dto_dict.keys())
            dates_dto_list = set(dates_dto_dict.keys())

            for act in qs_activities.exclude(Q(id__in=ids_dto_list) | Q(period__startswith__date__in=dates_dto_list)):
                act.delete(synchronize=False)
            for act in qs_activities.filter(Q(id__in=ids_dto_list) | Q(period__startswith__date__in=dates_dto_list)):
                act_dto = (
                    _act_dto if (_act_dto := ids_dto_dict.get(act.id)) else dates_dto_dict[act.period.lower.date()]
                )
                activity_updated, _ = self._update_activity(act, act_dto)
                if not act_dto.id:
                    self.backend._stream_extension_event(activity_updated._build_dto())

            dates_act_dict = {act.period.lower.date(): act for act in qs_activities}
            if dates_to_create := dates_dto_list.difference(set(dates_act_dict.keys())):
                parent_start = sorted(dates_dto_list)[0]
                if dates_act_dict.get(parent_start):
                    parent_act = dates_act_dict[parent_start]
                else:
                    parent_dto = dates_dto_dict[parent_start]
                    if parent_dto.id and (instance := Activity.all_objects.filter(id=parent_dto.id).first()):
                        Activity.all_objects.filter(id=parent_dto.id).update(parent_occurrence=None, is_active=True)
                        parent_act, _ = self._update_activity(instance, parent_dto)
                    else:
                        if parent_act := self._create_activity(parent_dto):
                            qs_activities.exclude(id=parent_act.id).update(parent_occurrence=parent_act)
                            self.backend._stream_extension_event(parent_act._build_dto())
                if parent_start in dates_to_create:
                    dates_to_create.remove(parent_start)
                for _start_date in sorted(dates_to_create):
                    instance_dto = dates_dto_dict[_start_date]
                    if (instance_dto.id and (instance := Activity.all_objects.filter(id=instance_dto.id).first())) or (
                        instance := parent_act.child_activities.filter(period__startswith__date=_start_date).first()
                    ):
                        new_activity, _ = self._update_activity(instance, instance_dto, parent_occurrence=parent_act)
                    else:
                        new_activity = self._create_activity(instance_dto, parent_occurrence=parent_act)
                        self.backend._stream_extension_event(new_activity._build_dto())
        else:
            if qs_activities.exists():
                event_result = {"action_type": "update", "action": ""}
                for activity in qs_activities:
                    previous_status = activity.status
                    if not (
                        previous_status == Activity.Status.REVIEWED
                        and can_sync_create_new_activity_on_replanned_reviewed_activity()
                        and activity._build_dto().period != activity_dto.period
                    ):
                        activity_updated, participant_updates_info = self._update_activity(activity, activity_dto)
                        msg = f"{activity.id} => {previous_status} activity, {participant_updates_info} -> {activity_updated.status} activity; "
                        event_result["action"] += msg
                    else:
                        new_activity = self._create_activity(activity_dto)
                        event_result["action"] += (
                            f"reviewed activity {activity.id} replanned to {new_activity.id} -> new activity {new_activity.status} created"
                        )
                        # remove metadata since the old activity is not sync anymore
                        Activity.objects.filter(id=activity.id).update(
                            metadata={
                                self.backend.METADATA_KEY: {
                                    "info": f"reviewed activity has been replanned to {new_activity.id}"
                                }
                            }
                        )
            else:
                new_activity = self._create_activity(activity_dto)
                event_result = {
                    "action_type": "create",
                    "action": f"{new_activity.id} -> new activity {new_activity.status} created",
                }
        Event.objects.filter(id=event_object_id).update(result=event_result)

    def update_activity_metadata(self, activity_dto: ActivityDTO, new_metadata):
        """
        allows to update the metadata used to save the external event id which is used to retrieve the event/activity
        """
        old_metadata = activity_dto.metadata.get(self.backend.METADATA_KEY, {})
        metadata = copy.deepcopy(old_metadata)
        new_metadata = new_metadata.get(self.backend.METADATA_KEY, {})
        for key, new_value in new_metadata.items():
            if old_value := metadata.get(key):
                if isinstance(old_value, list):
                    values = set(new_value) if isinstance(new_value, list) else {new_value}
                    if new_values := [_value for _value in values if _value not in old_value]:
                        metadata[key] = sorted(old_value + new_values)
                else:
                    metadata[key] = new_value
            else:
                metadata[key] = new_value
        if old_metadata != metadata:
            activity_dto.metadata[self.backend.METADATA_KEY] = metadata
            Activity.objects.filter(id=activity_dto.id).update(metadata=activity_dto.metadata)

    def _cancel_or_delete_activity(self, activity: "Activity") -> None:
        """
        when an event is deleted in the external calendar, we cancel or delete the activity according to global preferences
        """
        if can_sync_cancelled_activity():
            if activity.status != Activity.Status.CANCELLED:
                activity.cancel()
                activity.save(synchronize=False)
        else:
            activity.delete(synchronize=False)

    def _delete_activity(self, activity: Activity, participant: Person, exact_match: bool):
        previous_status = activity.status
        internal_activity = activity.creator.is_internal if activity.creator else False
        is_internal_creator = internal_activity and activity.creator == participant
        if exact_match and is_internal_creator:
            if activity.parent_occurrence:
                # delete instance activity if it's not the parent of recurring activities
                activity.delete(synchronize=False)
            else:
                # single activity or first parent of recurring activity
                self._cancel_or_delete_activity(activity)
            msg = f"{activity.id} => {previous_status} activity {activity.status}; "
        else:
            activity.activity_participants.filter(participant=participant).update(
                participation_status=ActivityParticipant.ParticipationStatus.CANCELLED
            )
            msg = f"{activity.id} => participant status cancelled; "

        # Handle external creator activity cancellation if no internal participants exist
        internal_participants_exist = (
            activity.activity_participants.exclude(
                participation_status=ActivityParticipant.ParticipationStatus.CANCELLED
            )
            .exclude(participant=participant)
            .filter(participant__in=Person.objects.filter_only_internal())
            .exists()
        )
        if not internal_activity and can_sync_cancelled_external_activity() and not internal_participants_exist:
            self._cancel_or_delete_activity(activity)
            msg += f"external {previous_status} activity {activity.status}; "

        return msg

    @transaction.atomic
    def delete_activity(
        self, activity_dto: ActivityDTO, user_dto: UserDTO, event_object_id: int | None = None
    ) -> None:
        event_result = {"action_type": "delete", "action": ""}

        # Try to get the participant, return if not found
        participant = self.get_activity_participant(user_dto)
        if not participant:
            Event.objects.filter(id=event_object_id).update(result=event_result)
            return

        # Prepare query sets for activities deletion
        qs_activities = self.get_activities(activity_dto, operator.and_)  # activities deleted by the organizer
        qs_invitation_activities = self.get_activities(activity_dto)  # activities deleted by a participant

        # skip deletion when notification received is not a deletion
        if not activity_dto.delete_notification:
            activities_ids = list(qs_invitation_activities.values_list("id", "status"))
            event_result["action"] += f"{activities_ids} => skip deletion; wait for delete notification"
            Event.objects.filter(id=event_object_id).update(result=event_result)
            return

        # Handle activities deleted by organizer
        if qs_activities.exists():
            for activity in qs_activities:
                event_result["action"] += self._delete_activity(activity, participant, exact_match=True)

        # Handle activities with participant invitation
        elif qs_invitation_activities.exists():
            for activity in qs_invitation_activities:
                event_result["action"] += self._delete_activity(activity, participant, exact_match=False)

        event_result["participant"] = participant.id
        Event.objects.filter(id=event_object_id).update(result=event_result)

    def get_or_create_person(self, person_dto: PersonDTO) -> Person:
        """
        A method to get or create the internal person of a "External" event. Returns a Person objects of the internal database.

        :param mail: person mail.
        """
        potential_persons = Person.objects.filter(emails__address=person_dto.email.lower()).order_by(
            "-emails__primary"
        )
        if potential_persons.exists():
            person = potential_persons.first()  # TODO change with owner feature
        else:
            person = Person.objects.create(
                last_name=person_dto.last_name, first_name=person_dto.first_name, is_draft_entry=True
            )
            if (
                potential_contact := EmailContact.objects.filter(entry__isnull=True, address=person_dto.email.lower())
                .order_by("-primary")
                .first()
            ):
                EmailContact.objects.filter(id=potential_contact.id).update(entry=person)
            else:
                EmailContact.objects.create(entry=person, address=person_dto.email, primary=True)
        return person

    def get_or_create_conference_room(self, conference_room: ConferenceRoomDTO) -> ConferenceRoom:
        if ConferenceRoom.objects.filter(email=conference_room.email).exists():
            conference_room = ConferenceRoom.objects.get(email=conference_room.email)
        else:
            name_building = conference_room.name_building if conference_room.name_building else conference_room.email
            name_conference_room = conference_room.name if conference_room.name else conference_room.email
            building, _ = Building.objects.get_or_create(name=name_building)
            conference_room = ConferenceRoom.objects.create(
                name=name_conference_room, email=conference_room.email, building=building
            )
        return conference_room

    def update_or_create_participants(
        self, activity: Activity, participants_dto: list[ParticipantStatusDTO]
    ) -> tuple[list[ActivityParticipant], str]:
        """
        allows to create or update the status of the participants of an activity
        """
        activity_participants = []
        participants_changed = ""
        for participant_dto in participants_dto:
            person = self.get_or_create_person(participant_dto.person)
            kwargs = {"participation_status": participant_dto.status} if participant_dto.status else {}

            if activity_participant := ActivityParticipant.objects.filter(
                activity=activity, participant=person
            ).first():
                if activity_participant.participation_status != participant_dto.status:
                    ActivityParticipant.objects.filter(activity=activity, participant=person).update(**kwargs)
                    participants_changed += (
                        f"- {person}: {activity_participant.participation_status} -> {participant_dto.status}"
                    )
            else:
                activity_participant = ActivityParticipant.objects.create(
                    activity=activity, participant=person, **kwargs
                )
                participants_changed += f"- new participant {person}: {participant_dto.status}"
            activity_participants.append(activity_participant)
        return activity_participants, participants_changed
