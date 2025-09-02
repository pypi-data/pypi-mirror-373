import json
from unittest.mock import patch

import pytest
from dynamic_preferences.registries import global_preferences_registry
from rest_framework.test import APIRequestFactory
from wbcore.contrib.authentication.factories import UserFactory

from wbcrm.models.activities import Activity
from wbcrm.synchronization.activity.backends.outlook.backend import OutlookSyncBackend

from .fixtures import TestOutlookSyncFixture, msgraph_fixture


@pytest.mark.django_db
class TestOutlookSyncBackend(TestOutlookSyncFixture):
    backend = OutlookSyncBackend()

    def test_attribute(self):
        assert OutlookSyncBackend.METADATA_KEY == "outlook"

    def test_open(self):
        preferences = global_preferences_registry.manager()
        preferences["wbactivity_sync__outlook_sync_credentials"] = ""
        assert hasattr(self.backend, "msgraph") is False
        self.backend.open()
        assert self.backend.msgraph

    @pytest.mark.parametrize("type_request", [None, "validationToken", "admin_consent"])
    def test_validation_response(self, type_request):
        request1 = APIRequestFactory().get("")
        if type_request:
            request1.GET = request1.GET.copy()
            request1.GET[type_request] = "fake_info"
            assert self.backend._validation_response(request1).content.decode("UTF-8") == "fake_info"
        else:
            assert self.backend._validation_response(request1) is None

    @pytest.mark.parametrize("client_state", [False, True])
    def test_is_inbound_request_valid(
        self, client_state, notification_created_fixture, notification_call_record_fixture
    ):
        api_factory = APIRequestFactory()
        request1 = api_factory.post("", data={})
        request2 = api_factory.post(
            "", data=json.dumps({"value": [notification_call_record_fixture]}), content_type="application/json"
        )
        request3 = api_factory.post(
            "", data=json.dumps({"value": [notification_created_fixture]}), content_type="application/json"
        )
        preferences = global_preferences_registry.manager()
        preferences["wbactivity_sync__outlook_sync_client_state"] = ""
        if client_state:
            preferences["wbactivity_sync__outlook_sync_client_state"] = notification_created_fixture["client_state"]

        assert self.backend._is_inbound_request_valid(request1) is False
        assert self.backend._is_inbound_request_valid(request2) is False
        assert self.backend._is_inbound_request_valid(request3) == client_state

    @pytest.mark.parametrize("event_found, is_organizer", [(False, True), (True, True), (True, False)])
    @patch("wbcrm.synchronization.activity.backends.outlook.backend.MicrosoftGraphAPI")
    def test_get_events_from_request(
        self,
        mock_msgraph,
        event_found,
        is_organizer,
        notification_created_fixture,
        organizer_event_fixture_parsed,
        invitation_event_fixture_parsed,
    ):
        api_factory = APIRequestFactory()
        request1 = api_factory.post(
            "", data=json.dumps({"value": [notification_created_fixture]}), content_type="application/json"
        )
        self.backend.open()
        self.backend.msgraph = msgraph_fixture()
        if event_found:
            if is_organizer:
                msgraph_fixture.event = organizer_event_fixture_parsed
                msgraph_fixture.tenant_id = "fake_tenant_id"
            else:
                msgraph_fixture.event = invitation_event_fixture_parsed
                msgraph_fixture.event_by_uid = organizer_event_fixture_parsed
        events = self.backend._get_events_from_request(request1)
        self.backend.close()
        assert len(events) == 1
        if event_found:
            assert {"change_type", "resource", "subscription_id"}.issubset(set(events[0].keys()))
            assert events[0].get("id")
        else:
            assert {"change_type", "resource", "subscription_id"} == set(events[0].keys())

    def test_deserialize(self, organizer_event_fixture_parsed, organizer_master_event_fixture_parsed):
        self.backend.open()
        activity_dto0, is_deleted0, user_dto0 = self.backend._deserialize(
            organizer_event_fixture_parsed, include_metadata=False
        )
        activity_dto, is_deleted, user_dto = self.backend._deserialize(organizer_event_fixture_parsed)
        activity_dto2, is_deleted2, user_dto2 = self.backend._deserialize(organizer_master_event_fixture_parsed)
        self.backend.close()

        assert is_deleted0 == is_deleted == is_deleted2 is False
        assert user_dto0 == user_dto == user_dto2
        assert user_dto0.metadata == {"outlook": {"subscription": {"id": None}}}
        assert activity_dto0.metadata == {}
        assert activity_dto.metadata == {
            self.backend.METADATA_KEY: {
                "event_uid": organizer_event_fixture_parsed["uid"],
                "event_id": organizer_event_fixture_parsed["id"],
            }
        }
        assert activity_dto2.metadata == {
            self.backend.METADATA_KEY: {
                "event_uid": organizer_master_event_fixture_parsed["uid"],
                "event_id": organizer_master_event_fixture_parsed["id"],
            }
        }
        assert activity_dto.period
        assert activity_dto.repeat_choice == "NEVER"
        assert activity_dto2.repeat_choice != "NEVER"

    def test_serialize(self, activity_factory):
        activity_dto = activity_factory(preceded_by=None)._build_dto()
        act_dto = activity_factory(
            repeat_choice=Activity.ReoccuranceChoice.DAILY, recurrence_count=3, preceded_by=None
        )._build_dto()
        activity_dict = self.backend._serialize(activity_dto)
        activity_dict1 = self.backend._serialize(activity_dto, created=True)
        act_dict = self.backend._serialize(act_dto)
        act_dict1 = self.backend._serialize(act_dto, created=True)
        keys = {
            "subject",
            "start",
            "end",
            "body",
            "attendees",
            "sensitivity",
            "isReminderOn",
            "reminderMinutesBeforeStart",
            "isAllDay",
            "responseRequested",
            "location",
            "locations",
        }
        assert set(activity_dict.keys()) == set(act_dict.keys()) == set(activity_dict1.keys()) == keys
        assert set(act_dict1.keys()) == keys.union({"recurrence"})

    @pytest.mark.parametrize(
        "metadata, master_event",
        [
            ({}, False),
            ({}, True),
            ({"organizer_resource": "fake_resource"}, False),
            ({"organizer_resource": "fake_resource"}, True),
            ({"event_id": "fake_event_id"}, False),
            ({"event_id": "fake_event_id"}, True),
            ({"event_uid": "fake_event_uid"}, False),
            ({"event_uid": "fake_event_uid"}, True),
            ({"occurrence_resource": "fake_resource"}, False),
            ({"occurrence_resource": "fake_resource"}, True),
            ({"occurrence_id": "fake_occurrence_id"}, False),
            ({"occurrence_id": "fake_occurrence_id"}, True),
        ],
    )
    def test_get_external_event(self, metadata, master_event, activity_factory):
        activity_dto = activity_factory(preceded_by=None)._build_dto()
        activity_dto2 = activity_factory(preceded_by=None, metadata={self.backend.METADATA_KEY: metadata})._build_dto()
        self.backend.open()
        self.backend.msgraph = msgraph_fixture()
        msgraph_fixture.tenant_id = "fake_tenant_id"
        msgraph_fixture.event_by_uid = msgraph_fixture.event = {"id": "event_id"}
        assert (
            self.backend.get_external_event(activity_dto, master_event)
            == self.backend.get_external_event(activity_dto, master_event)
            is None
        )
        if metadata:
            event_result = self.backend.get_external_event(activity_dto2, master_event)
            if master_event or not activity_dto2.is_recurrent:
                if metadata.get("event_uid") or metadata.get("event_id") or metadata.get("organizer_resource"):
                    assert event_result == {"id": "event_id"}
                else:
                    assert event_result is None
            else:
                if metadata.get("occurrence_resource") or metadata.get("occurrence_id"):
                    assert event_result == {"id": "event_id"}
                else:
                    assert event_result is None
        else:
            assert self.backend.get_external_event(activity_dto2, master_event) is None

    def test_get_external_participants(self, activity_factory, person_factory):
        person = person_factory()
        activity_dto = activity_factory(preceded_by=None, participants=(person,))._build_dto()
        activity_dto2 = activity_factory(
            preceded_by=None,
            participants=(person,),
            metadata={self.backend.METADATA_KEY: {"organizer_resource": "fake_resource"}},
        )._build_dto()
        self.backend.open()
        self.backend.msgraph = msgraph_fixture()
        msgraph_fixture.tenant_id = "fake_tenant_id"
        msgraph_fixture.event_by_uid = msgraph_fixture.event = {
            "id": "event_id",
            "attendees": [{"emailAddress": {"address": person._build_dto().email}}],
        }
        assert len(self.backend.get_external_participants(activity_dto, [])) == 0
        assert len(self.backend.get_external_participants(activity_dto2, [])) == 1
        assert len(self.backend.get_external_participants(activity_dto2, activity_dto2.participants)) == 0

    @patch("wbcrm.synchronization.activity.backends.outlook.backend.MicrosoftGraphAPI")
    def test_is_participant_valid(self, mock_msgraph):
        user = UserFactory(is_superuser=True)
        user2 = UserFactory(is_superuser=True)
        user2.metadata = {self.backend.METADATA_KEY: {"subscription": {"id": "fake_subscription_id"}}}
        user2.save()
        msgraph_fixture._subscription = {"id": "fake_subscription_id"}
        mock_msgraph.return_value = msgraph_fixture()
        assert self.backend._is_participant_valid(user2) is True
        assert self.backend._is_participant_valid(user) is False

    def test_generate_event_metadata(self):
        event = {"id": "fake_id", "uid": "fake_uid"}
        occurrence_event = {"id": "fake_id", "uid": "fake_uid"}
        resource = f"Users/fake_tenant_id/Events/{event['id']}"
        result = {
            "resources": [resource],
            "organizer_resource": resource,
            "event_uid": event["uid"],
            "event_id": event["id"],
        }
        metadata = self.backend._generate_event_metadata("fake_tenant_id", event)
        metadata2 = self.backend._generate_event_metadata("fake_tenant_id", event, occurrence_event)
        assert metadata == {self.backend.METADATA_KEY: result}
        assert metadata2 == {
            self.backend.METADATA_KEY: {**result, **{"occurrence_id": event["id"], "occurrence_resource": resource}}
        }

    def test_get_metadata_from_event(
        self, activity_factory, organizer_event_fixture_parsed, organizer_master_event_fixture_parsed
    ):
        self.backend.open()
        self.backend.msgraph = msgraph_fixture()
        msgraph_fixture.tenant_id = "fake_tenant_id"
        activity_dto = activity_factory(preceded_by=None)._build_dto()
        metadata_list = self.backend._get_metadata_from_event(activity_dto, organizer_event_fixture_parsed)
        # self.backend._get_metadata_from_event()
        resource = f"Users/fake_tenant_id/Events/{organizer_event_fixture_parsed['id']}"
        assert len(metadata_list) == 1
        assert metadata_list[0][0] == activity_dto
        assert metadata_list[0][1] == {
            self.backend.METADATA_KEY: {
                "resources": [resource],
                "organizer_resource": resource,
                "event_uid": organizer_event_fixture_parsed["uid"],
                "event_id": organizer_event_fixture_parsed["id"],
            }
        }

    @patch("wbcrm.synchronization.activity.backends.outlook.backend.MicrosoftGraphAPI")
    def test_renew_web_hooks(self, mock_msgraph):
        msgraph_fixture._subscription = {"id": "fake_id_new"}
        mock_msgraph.return_value = msgraph_fixture()

        user1 = UserFactory(is_superuser=True)
        user2 = UserFactory(is_superuser=True)
        user2.metadata = {self.backend.METADATA_KEY: {"subscription": {"id": "fake_id"}}}
        user2.save()

        self.backend.renew_web_hooks()
        user1.refresh_from_db()
        user2.refresh_from_db()
        assert user1.metadata == {}
        assert user2.metadata == {self.backend.METADATA_KEY: {"subscription": {"id": "fake_id_new"}}}
