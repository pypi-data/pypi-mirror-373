import itertools
import json
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from dynamic_preferences.registries import global_preferences_registry
from rest_framework.test import APIRequestFactory
from wbcore.permissions.registry import user_registry

from wbcrm.factories import ActivityFactory
from wbcrm.models import Activity, ActivityParticipant
from wbcrm.synchronization.activity.shortcuts import get_backend
from wbcrm.typings import User as UserDTO

from .fixtures import TestOutlookSyncFixture, msgraph_fixture

User = get_user_model()


@pytest.mark.django_db
class TestInitController:
    def test_init(self):
        global_preferences_registry.manager()["wbactivity_sync__sync_backend_calendar"] = ""
        controller = get_backend()
        assert controller is None

        global_preferences_registry.manager()["wbactivity_sync__sync_backend_calendar"] = (
            "wbcrm.synchronization.activity.backends.outlook.backend.OutlookSyncBackend"
        )
        controller2 = get_backend()
        assert controller2.backend


@pytest.mark.django_db
class TestController(TestOutlookSyncFixture):
    def setup_method(self):
        global_preferences_registry.manager()["wbactivity_sync__sync_backend_calendar"] = (
            "wbcrm.synchronization.activity.backends.outlook.backend.OutlookSyncBackend"
        )

    @pytest.fixture()
    @patch("wbcrm.synchronization.activity.backends.outlook.backend.MicrosoftGraphAPI")
    def controller(self, mock_msgraph):
        controller = get_backend()
        controller.backend.open()
        controller.backend.msgraph = msgraph_fixture()
        return controller

    @pytest.mark.parametrize("type_request", [None, "validationToken", "admin_consent"])
    def test_handle_inbound_validation_response(self, controller, type_request):
        request1 = APIRequestFactory().get("")
        if type_request:
            request1.GET = request1.GET.copy()
            request1.GET[type_request] = "fake_info"
            assert controller.handle_inbound_validation_response(request1).content.decode("UTF-8") == "fake_info"
        else:
            assert controller.handle_inbound_validation_response(request1) is None

    @pytest.mark.parametrize("client_state", ["secret1", "secret2"])
    @patch("wbcrm.synchronization.activity.backends.outlook.backend.MicrosoftGraphAPI")
    def test_get_events_from_inbound_request(
        self, mock_msgraph, controller, client_state, notification_fixture, teams_event_fixture
    ):
        notification_fixture["client_state"] = client_state
        global_preferences_registry.manager()["wbactivity_sync__outlook_sync_client_state"] = "secret2"
        api_factory = APIRequestFactory()
        request1 = api_factory.post("", data={})
        request2 = api_factory.post(
            "", data=json.dumps({"value": [notification_fixture]}), content_type="application/json"
        )

        mock_msgraph.return_value = controller.backend.msgraph
        controller.backend.msgraph.event = teams_event_fixture
        controller.backend.msgraph.event_by_uid = teams_event_fixture
        events1 = controller.get_events_from_inbound_request(request1)
        events2 = controller.get_events_from_inbound_request(request2)
        assert events1 == []
        if client_state != global_preferences_registry.manager()["wbactivity_sync__outlook_sync_client_state"]:
            assert events1 == events2 == []
        else:
            assert events1 == []
            assert len(events2) == 1
            expected_result = {
                "change_type": notification_fixture["change_type"],
                "resource": notification_fixture["resource"],
                "subscription_id": notification_fixture["subscription_id"],
                "organizer_resource": notification_fixture["resource"],
                **teams_event_fixture,
            }
            assert set(events2[0].keys()) == set(expected_result.keys())

    @patch("wbcrm.synchronization.activity.backends.outlook.backend.MicrosoftGraphAPI")
    def test_user_for_handle_inbound(
        self, mock_msgraph, controller, notification_fixture, teams_event_fixture, user_factory
    ):
        event = {
            "change_type": notification_fixture["change_type"],
            "resource": notification_fixture["resource"],
            "subscription_id": notification_fixture["subscription_id"],
            **teams_event_fixture,
        }
        metadata = {"outlook": {"subscription": {"id": notification_fixture["subscription_id"]}}}
        _, _, user_dto = controller.backend._deserialize(event)
        user_result = UserDTO(metadata=metadata, id=None)
        assert user_dto.id is None
        assert user_dto.metadata == user_result.metadata

        assert controller.get_activity_participant(user_dto) is None
        user = user_factory(is_active=True, is_superuser=True, metadata=metadata)
        assert controller.get_activity_participant(user_dto) == user.profile

    def _get_user_and_activities(self, notification_fixture, user_factory, teams_event_fixture):
        user1 = user_factory(is_active=True)
        user2 = user_factory(
            is_active=True, metadata={"outlook": {"subscription": {"id": notification_fixture["subscription_id"]}}}
        )

        other1_activity = ActivityFactory(creator=user1.profile, participants=(user2.profile,))
        other2_activity = ActivityFactory(
            creator=user1.profile,
            participants=(user2.profile,),
            metadata={"outlook": {"event_id": 1, "event_uid": 2, "resources": ["Users/1/events/1"]}},
        )
        metadata = {
            "outlook": {
                "resources": [notification_fixture["resource"]],
                "organizer_resource": notification_fixture["resource"],
                "event_uid": teams_event_fixture["uid"],
                "event_id": teams_event_fixture["id"],
            }
        }
        activity = ActivityFactory(creator=user1.profile, participants=(user2.profile,))
        Activity.objects.filter(id=activity.id).update(metadata=metadata)
        return {"activities": (other1_activity, other2_activity, activity), "users": (user1, user2)}

    @pytest.mark.parametrize(
        "is_internal_creator, cancel_activity, delete_notification", list(itertools.product([True, False], repeat=3))
    )
    def test_delete_activity(
        self,
        cancel_activity,
        is_internal_creator,
        controller,
        notification_fixture,
        user_factory,
        teams_event_fixture,
        delete_notification,
    ):
        global_preferences_registry.manager()["wbactivity_sync__sync_cancelled_activity"] = cancel_activity

        data = self._get_user_and_activities(notification_fixture, user_factory, teams_event_fixture)
        other1_activity, other2_activity, activity = data["activities"]
        user1, user2 = data["users"]
        if is_internal_creator:
            permission = Permission.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(User), codename="is_internal_user"
            )[0]
            user1.user_permissions.add(permission)
            user_registry.reset_cache()
        activity.refresh_from_db()
        activity_dto = activity._build_dto()
        activity_dto.delete_notification = delete_notification

        user1_dto = UserDTO(metadata=user1.metadata, id=None)
        user2_dto = UserDTO(metadata=user2.metadata, id=None)

        assert set(Activity.objects.all()) == {other1_activity, other2_activity, activity}

        controller.delete_activity(activity_dto, user1_dto)
        assert set(Activity.objects.all()) == {other1_activity, other2_activity, activity}

        controller.delete_activity(
            activity_dto, user2_dto
        )  # user 2 is not the creator of the activity. it's a participant
        assert set(Activity.objects.all()) == {other1_activity, other2_activity, activity}
        if is_internal_creator:
            user2_status = (
                ActivityParticipant.ParticipationStatus.CANCELLED
                if delete_notification
                else ActivityParticipant.ParticipationStatus.PENDING_INVITATION
            )
            assert activity.activity_participants.get(participant=user2.profile).participation_status == user2_status

        controller.delete_activity(
            activity_dto, user1_dto
        )  # user 1 is the creator of the activity but doesn't have an active subscription
        assert set(Activity.objects.all()) == {other1_activity, other2_activity, activity}
        user1.metadata = user2.metadata
        user1.save()
        user2.metadata = {}
        user2.metadata = {"outlook": {"subscription": {"id": "new_subscription1"}}}
        user2.save()
        user1.refresh_from_db()
        user1_dto = UserDTO(metadata=user1.metadata, id=None)

        controller.delete_activity(
            activity_dto, user1_dto
        )  # user 1 is the creator of the activity with an active subscription
        if delete_notification and is_internal_creator and not cancel_activity:
            assert set(Activity.objects.all()) == {other1_activity, other2_activity}
        else:
            assert set(Activity.objects.all()) == {other1_activity, other2_activity, activity}
        assert set(Activity.all_objects.all()) == {other1_activity, other2_activity, activity}

    @pytest.mark.parametrize(
        "cancel_external_creator_activity, cancel_activity, delete_notification",
        list(itertools.product([True, False], repeat=3)),
    )
    def test_cancel_no_participant_external_creator_activity(
        self,
        cancel_external_creator_activity,
        cancel_activity,
        controller,
        notification_fixture,
        user_factory,
        teams_event_fixture,
        delete_notification,
    ):
        global_preferences_registry.manager()["wbactivity_sync__sync_cancelled_activity"] = cancel_activity
        global_preferences_registry.manager()["wbactivity_sync__sync_cancelled_external_activity"] = (
            cancel_external_creator_activity
        )

        data = self._get_user_and_activities(notification_fixture, user_factory, teams_event_fixture)
        other1_activity, other2_activity, activity = data["activities"]
        user1, user2 = data["users"]
        permission = Permission.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(User), codename="is_internal_user"
        )[0]
        user2.user_permissions.add(permission)
        user_registry.reset_cache()
        user2_dto = UserDTO(metadata=user2.metadata, id=None)
        Activity.objects.filter(id=activity.id).update(creator=user1.profile)
        activity.refresh_from_db()
        activity_dto = activity._build_dto()
        activity_dto.delete_notification = delete_notification

        assert set(Activity.objects.all()) == {other1_activity, other2_activity, activity}

        # user 1 is an external user and it's the creator of the activity without an active subscription
        # user 2 is a internal participant
        controller.delete_activity(activity_dto, user2_dto)
        if delete_notification and cancel_external_creator_activity and not cancel_activity:
            assert set(Activity.objects.all()) == {other1_activity, other2_activity}
        else:
            assert set(Activity.objects.all()) == {other1_activity, other2_activity, activity}
