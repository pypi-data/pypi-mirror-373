from contextlib import suppress
from datetime import date
from typing import Any

from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy
from wbcore.contrib.notifications.dispatch import send_notification

from wbcrm.typings import Activity as ActivityDTO
from wbcrm.typings import ParticipantStatus as ParticipantStatusDTO
from wbcrm.typings import User as UserDTO

User = get_user_model()


class SyncBackend:
    METADATA_KEY = None

    def open(self):
        """
        Allows to perform primary operations or to open a communication channel for synchronization,
        such as defining the necessary configurations to send requests
        """
        pass

    def close(self):
        """
        Close the communication channel and unset configuration
        """
        pass

    def _validation_response(self, request: HttpRequest) -> HttpResponse:
        """
        send a response to the external calendar if necessary to validate the endpoint
        """
        return None

    def _is_inbound_request_valid(self, request: HttpRequest) -> bool:
        """
        Valid function to ensure that the request received meets expectations
        """
        raise NotImplementedError

    def _get_events_from_request(self, request: HttpRequest) -> list[dict[str, Any]]:
        """
        list of events following the notification received
        """
        raise NotImplementedError

    def _deserialize(self, event: dict[str, Any]) -> tuple[ActivityDTO, bool, UserDTO]:
        """
        convert the dictionary received to a valid format of an activity
        """
        raise NotImplementedError()

    def _serialize(self, activity_dto: ActivityDTO, created: bool = False) -> dict[str, Any]:
        """
        convert activity data transfer object to event dictionary
        """
        raise NotImplementedError()

    def _stream_deletion(self, activity_dto: ActivityDTO):
        """
        allow the deletion of the event in the external calendar
        we use the event_id stored in activity_dto's metadata to retrieve the event
        """
        raise NotImplementedError()

    def _stream_creation(
        self, activity_dto: ActivityDTO, activity_dict: dict[str, Any]
    ) -> tuple[ActivityDTO, dict[str, Any]]:
        """
        allow the creation of the event in the external calendar
        param: activity_dict: dictionary used to create the event

        we return a tuple of activity, metadata which contains the external id to be store in the activity
        """
        raise NotImplementedError()

    def _stream_update(
        self,
        activity_dto: ActivityDTO,
        activity_dict: dict[str, Any],
        only_participants_changed: bool = False,
        external_participants: list = [],
        keep_external_description: bool = False,
    ) -> tuple[ActivityDTO, dict[str, Any]]:
        """
        allow to update the event in the external calendar
        param: activity_dict: dictionary used to update the event
               activity_dto: we use the metadata of the activity to retrieve the event
               only_participants_changed: boolean to know if only the participants need to be update
               external_participants: list of external participants, that must be added to the current list of participants to avoid their deletion when the activity is updated
               keep_external_description: boolean to know if the description must be deleted or not before the update of the event
        """
        raise NotImplementedError()

    def _stream_update_only_attendees(self, activity_dto: ActivityDTO, participants_dto: list[ParticipantStatusDTO]):
        """
        allow to update only the attendees of the event in the external calendar
        """
        raise NotImplementedError()

    def _stream_extension_event(self, activity_dto: ActivityDTO) -> None:
        """
        Extend external event with custom data
        this allows us for example to add additional information to the event to easily identify it for a recurring activities
        """
        pass

    def _stream_forward(self, activity_dto: ActivityDTO, participants_dto: list[ParticipantStatusDTO]):
        """
        allow to forward an event to a new participant. the external calendar
        send an invitation to all participants and avoid sending an update of the activity to all participants
        """
        raise NotImplementedError()

    def _stream_participant_change(
        self, participant_dto: ParticipantStatusDTO, is_deleted: bool = False, wait_before_changing: bool = False
    ):
        """
        allow to update the status of an event participant
        """
        raise NotImplementedError()

    def _set_web_hook(self, user: "User") -> dict[str, dict[str, Any]]:
        """
        allows to activate the webhook for a user
        returns a dictionary that will be stored in the metadata of the ser
        """
        raise NotImplementedError()

    def _stop_web_hook(self, user: "User") -> dict[str, dict[str, Any]]:
        """
        allows to strop the webhook for a user and deletes the data stored in the metadata
        """
        raise NotImplementedError()

    def _check_web_hook(self, user: "User") -> bool:
        """
        return a boolean to know if a subscription is activated or not for a user
        """
        raise NotImplementedError()

    def set_web_hook(self, user: "User"):
        """
        allows to be sure that the metadata are saved by specifying the backend type.
        """
        new_metadata = self._set_web_hook(user)
        user.metadata.setdefault(self.METADATA_KEY, {})
        user.metadata[self.METADATA_KEY] = new_metadata
        user.save()

    def stop_web_hook(self, user: "User"):
        new_metadata = self._stop_web_hook(user)
        user.metadata.setdefault(self.METADATA_KEY, {})
        user.metadata[self.METADATA_KEY] = new_metadata
        user.save()

    def check_web_hook(self, user: "User") -> bool:
        try:
            return self._check_web_hook(user)
        except NotImplementedError:
            return False

    def renew_web_hooks(self) -> None:
        """
        Allows to renew existing webhooks of all users
        """
        pass

    def _get_webhook_inconsistencies(self) -> str:
        """
        return a message of anomalies that will be notified to the administrator/persons set in the preferences
        """
        raise NotImplementedError()

    def notify_admins_of_webhook_inconsistencies(self, emails: list) -> None:
        """
        the purpose is to make sure that the authorized persons receive the messages in case a webhook has been deactivated or not renewed correctly.
        """
        with suppress(NotImplementedError):
            if emails and (message := self._get_webhook_inconsistencies()):
                for recipient in User.objects.filter(email__in=emails):
                    send_notification(
                        code="wbcrm.activity_sync.admin",
                        title=gettext_lazy("Notify admins of event webhook inconsistencies - {}").format(date.today()),
                        body=f"<ul>{message}</ul>",
                        user=recipient,
                    )

    def get_external_event(self, activity_dto: ActivityDTO) -> dict:
        """
        Get an event of external calendar.
        """
        pass

    def get_external_participants(
        self, activity_dto: ActivityDTO, internal_participants_dto: list[ParticipantStatusDTO]
    ) -> list[str, Any]:
        """
        Get external participants of an external event
        """
        return []

    def _is_participant_valid(self, user: "User") -> bool:
        return user.is_active and user.is_register

    def is_valid(self, activity: ActivityDTO) -> bool:
        # Synchronize only if the creator or at least one participant has an active subscription
        participants = [activity.creator.email] if activity.creator else []
        participants.extend(list(map(lambda x: x.person.email, activity.participants)))
        return any([self._is_participant_valid(user) for user in User.objects.filter(email__in=set(participants))])
