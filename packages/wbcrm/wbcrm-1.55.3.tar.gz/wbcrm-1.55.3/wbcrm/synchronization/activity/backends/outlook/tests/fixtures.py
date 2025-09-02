import copy

import pytest
from django.contrib.messages import storage
from rest_framework.test import APIRequestFactory


class msgraph_fixture:
    token = None
    _subscriptions = []
    _subscription = None
    tenant_id = None
    event = None
    event_by_uid = None
    instances_event = []
    extension_event = None

    def _get_access_token(self):
        return self.token

    def applications(self):
        return None

    def subscriptions(self):
        return self._subscriptions

    def subscription(self, subscription_id: str):
        return self._subscription

    def _renew_subscription(self, subscription_id: str):
        return self._subscription

    def get_tenant_id(self, email: str):
        return self.tenant_id

    def _subscribe(self, resource: str, change_type: str):
        return self._subscription

    def _unsubscribe(self, subscription_id: str):
        return None

    def get_event_by_resource(self, resource: str):
        return self.event

    def get_event(self, tenant_id: str, external_id: str):
        return self.event

    def get_event_by_uid(self, tenant_id: str, uid: str):
        return self.event_by_uid

    def get_instances_event(self, tenant_id: str, external_id: str, start: str, end: str):
        return self.instances_event

    def get_extension_event(self, tenant_id: str, extension_id: str):
        return self.extension_event


@pytest.mark.django_db
class TestOutlookSyncFixture:
    @pytest.fixture()
    def fixture_request(self):
        request = APIRequestFactory().get("")
        request.session = {}  # for sessions middleware
        request._messages = storage.default_storage(request)  # for messages middleware
        return request

    @pytest.fixture()
    def credentials_fixture(self):
        return '{"notification_url": "https://test.com/api/crm/sync/activity/event_watch", "authority": "https://test.com/fake_app_tenant_id", "client_id": "fake_client_id", "client_secret": "fake_client_secret", "token_endpoint": "/fake_token", "graph_url": "https://fake_url"}'

    @pytest.fixture()
    def notification_created_fixture(self):
        return {
            "subscription_id": "fake_subscription_id",
            "subscription_expiration": "2022-12-11T09:05:13+00:00",
            "change_type": "created",
            "resource": "Users/fake_user_id/Events/fake_event_id",
            "resource_data": {
                "@odata.etag": "fake_etag",
                "@odata.id": "Users/fake_user_id/Events/fake_event_id",
                "@odata.type": "#Microsoft.Graph.Event",
                "id": "unique_id",
            },
            "client_state": "secretClientValue",
            "tenant_id": "fake_tenant_id",
        }

    @pytest.fixture()
    def notification_fixture(self, notification_created_fixture):
        _fixture = copy.deepcopy(notification_created_fixture)
        _fixture["change_type"] = "deleted"
        return _fixture

    @pytest.fixture()
    def notification_call_record_fixture(self, notification_created_fixture):
        notification_call_record_fixture = copy.deepcopy(notification_created_fixture)
        notification_call_record_fixture["resource_data"]["@odata.type"] = "/communications/callRecords"
        return notification_call_record_fixture

    @pytest.fixture()
    def organizer_event_fixture(self):
        return {
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users('cd209b0b-3f83-4c35-82d2-d88a61820480')/events/$entity",
            "@odata.etag": 'W/"ZlnW4RIAV06KYYwlrfNZvQAALfZeRQ=="',
            "id": "AAMkAGI1AAAt9AHjAAA=",
            "createdDateTime": "2017-04-15T03:00:50.7579581Z",
            "lastModifiedDateTime": "2017-04-15T03:00:51.245372Z",
            "changeKey": "ZlnW4RIAV06KYYwlrfNZvQAALfZeRQ==",
            "categories": [],
            "originalStartTimeZone": "Pacific Standard Time",
            "originalEndTimeZone": "Pacific Standard Time",
            "iCalUId": "040000008200E00074C5B7101A82E00800000000DA2B357D94B5D201000000000000000010000000EC4597557F0CB34EA4CC2887EA7B17C3",
            "reminderMinutesBeforeStart": 15,
            "isReminderOn": True,
            "hasAttachments": False,
            "hideAttendees": False,
            "subject": "Let's go brunch",
            "bodyPreview": "Does noon work for you?",
            "importance": "normal",
            "sensitivity": "normal",
            "isAllDay": False,
            "isCancelled": False,
            "isDraft": False,
            "isOrganizer": True,
            "responseRequested": True,
            "seriesMasterId": None,
            "transactionId": "7E163156-7762-4BEB-A1C6-729EA81755A7",
            "showAs": "busy",
            "type": "singleInstance",
            "webLink": "https://outlook.office365.com/owa/?itemid=AAMkAGI1AAAt9AHjAAA%3D&exvsurl=1&path=/calendar/item",
            "onlineMeetingUrl": None,
            "isOnlineMeeting": True,
            "onlineMeetingProvider": "unknown",
            "onlineMeeting": None,
            "allowNewTimeProposals": True,
            "responseStatus": {"response": "organizer", "time": "0001-01-01T00:00:00Z"},
            "body": {
                "contentType": "html",
                "content": "<html><head></head><body>Does late morning work for you?</body></html>",
            },
            "start": {"dateTime": "2017-04-15T11:00:00.0000000", "timeZone": "Pacific Standard Time"},
            "end": {"dateTime": "2017-04-15T12:00:00.0000000", "timeZone": "Pacific Standard Time"},
            "location": {
                "displayName": "Harry's Bar",
                "locationType": "default",
                "uniqueId": "Harry's Bar",
                "uniqueIdType": "private",
            },
            "locations": [{"displayName": "Harry's Bar", "locationType": "default", "uniqueIdType": "unknown"}],
            "recurrence": None,
            "attendees": [
                {
                    "type": "required",
                    "status": {"response": "none", "time": "0001-01-01T00:00:00Z"},
                    "emailAddress": {"name": "Samantha Booth", "address": "samanthab@contoso.onmicrosoft.com"},
                }
            ],
            "organizer": {"emailAddress": {"name": "Dana Swope", "address": "danas@contoso.onmicrosoft.com"}},
        }

    @pytest.fixture()
    def invitation_event_fixture(self, organizer_event_fixture):
        invitation_event_fixture = copy.deepcopy(organizer_event_fixture)
        invitation_event_fixture["isOrganizer"] = False
        return invitation_event_fixture

    @pytest.fixture()
    def organizer_event_fixture_parsed(self):
        return {
            "odata_context": "https://graph.microsoft.com/v1.0/$metadata#users('cd209b0b-3f83-4c35-82d2-d88a61820480')/events/$entity",
            "odata_etag": 'W/"ZlnW4RIAV06KYYwlrfNZvQAALfZeRQ=="',
            "id": "AAMkAGI1AAAt9AHjAAA=",
            "created_date_time": "2017-04-15T03:00:50.7579581Z",
            "last_modified_date_time": "2017-04-15T03:00:51.245372Z",
            "change_key": "ZlnW4RIAV06KYYwlrfNZvQAALfZeRQ==",
            "categories": [],
            "original_start_time_zone": "Pacific Standard Time",
            "original_end_time_zone": "Pacific Standard Time",
            "uid": "040000008200E00074C5B7101A82E00800000000DA2B357D94B5D201000000000000000010000000EC4597557F0CB34EA4CC2887EA7B17C3",
            "reminder_minutes_before_start": 15,
            "is_reminder_on": True,
            "has_attachments": False,
            "hide_attendees": False,
            "subject": "Let's go brunch",
            "body_preview": "Does noon work for you?",
            "importance": "normal",
            "sensitivity": "normal",
            "is_all_day": False,
            "is_cancelled": False,
            "is_draft": False,
            "is_organizer": True,
            "response_requested": True,
            "series_master_id": None,
            "transaction_id": "7E163156-7762-4BEB-A1C6-729EA81755A7",
            "show_as": "busy",
            "type": "singleInstance",
            "web_link": "https://outlook.office365.com/owa/?itemid=AAMkAGI1AAAt9AHjAAA%3D&exvsurl=1&path=/calendar/item",
            "online_meeting_url": None,
            "is_online_meeting": True,
            "online_meeting_provider": "unknown",
            "online_meeting": None,
            "allow_new_time_proposals": True,
            "locations": [{"displayName": "Harry's Bar", "locationType": "default", "uniqueIdType": "unknown"}],
            "recurrence": None,
            "attendees": [
                {
                    "type": "required",
                    "status": {"response": "none", "time": "0001-01-01T00:00:00Z"},
                    "emailAddress": {"name": "Samantha Booth", "address": "samanthab@contoso.onmicrosoft.com"},
                }
            ],
            "response_status.response": "organizer",
            "response_status.time": "0001-01-01T00:00:00Z",
            "body.content_type": "html",
            "body.content": "<html><head></head><body>Does late morning work for you?</body></html>",
            "start.date_time": "2017-04-15T11:00:00.0000000",
            "start.time_zone": "Pacific Standard Time",
            "end.date_time": "2017-04-15T12:00:00.0000000",
            "end.time_zone": "Pacific Standard Time",
            "location.display_name": "Harry's Bar",
            "location.location_type": "default",
            "location.unique_id": "Harry's Bar",
            "location.unique_id_type": "private",
            "organizer.email_address.name": "Dana Swope",
            "organizer.email_address.address": "danas@contoso.onmicrosoft.com",
        }

    @pytest.fixture()
    def invitation_event_fixture_parsed(self, organizer_event_fixture_parsed):
        invitation_event_fixture_parsed = copy.deepcopy(organizer_event_fixture_parsed)
        invitation_event_fixture_parsed["is_organizer"] = False
        return invitation_event_fixture_parsed

    @pytest.fixture()
    def organizer_master_event_fixture_parsed(self):
        return {
            "id": "unique_id2-ocurrence_pattern_id-unique_recurrence_id2",
            "uid": "unique_fake_id",
            "type": "seriesMaster",
            "start.date_time": "2022-12-12T07:00:00.0000000",
            "end.date_time": "2022-12-12T07:30:00.0000000",
            "created": "2022-12-08T10:37:29.8938372Z",
            "show_as": "busy",
            "subject": "test recc",
            "is_draft": False,
            "web_link": "fake_web_link2",
            "locations": [],
            "categories": [],
            "change_key": "fake_change_key2",
            "importance": "normal",
            "is_all_day": False,
            "odata_etag": "fake_etag2",
            "sensitivity": "normal",
            "body.content": "",
            "body_preview": "",
            "is_cancelled": False,
            "is_organizer": True,
            "participants": [],
            "end.time_zone": "UTC",
            "last_modified": "2022-12-08T10:37:30.0188091Z",
            "occurrence_id": None,
            "odata_context": "fake_odata_context2",
            "hide_attendees": False,
            "is_reminder_on": True,
            "online_meeting": None,
            "transaction_id": "70957719-1fb2-5642-7bb6-c1363e1091e0",
            "has_attachments": False,
            "start.time_zone": "UTC",
            "series_master_id": None,
            "body.content_type": "html",
            "is_online_meeting": False,
            "online_meeting_url": None,
            "response_requested": True,
            "response_status.time": "0001-01-01T00:00:00Z",
            "location.address.type": "unknown",
            "location.display_name": "",
            "recurrence.range.type": "endDate",
            "location.location_type": "default",
            "original_end_time_zone": "W. Europe Standard Time",
            "location.unique_id_type": "unknown",
            "online_meeting_provider": "unknown",
            "recurrence.pattern.type": "daily",
            "allow_new_time_proposals": True,
            "original_start_time_zone": "W. Europe Standard Time",
            "recurrence.pattern.index": "first",
            "recurrence.pattern.month": 0,
            "response_status.response": "organizer",
            "recurrence.range.end_date": "2022-12-14",
            "recurrence.pattern.interval": 1,
            "recurrence.range.start_date": "2022-12-12",
            "organizer.email_address.name": "Fake organizer name",
            "calendar@odata.navigationLink": "fake_navigation_link",
            "reminder_minutes_before_start": 15,
            "calendar@odata.associationLink": "fake_association_link",
            "organizer.email_address.address": "test@test.com",
            "recurrence.pattern.day_of_month": 0,
            "recurrence.pattern.first_day_of_week": "sunday",
            "recurrence.range.recurrence_time_zone": "W. Europe Standard Time",
            "recurrence.range.number_of_occurrences": 0,
        }

    @pytest.fixture()
    def teams_event_fixture(self):
        return {
            "odata_etag": 'W/"AAAAAAAAAAAAAAAAA=="',
            "id": "eventid1",
            "created_date_time": "2023-12-14T10:23:43.4384008Z",
            "last_modified_date_time": "2023-12-14T10:25:13.7822553Z",
            "change_key": "AAAAAAAAAAAAAAAAA==",
            "categories": [],
            "transaction_id": None,
            "original_start_time_zone": "UTC",
            "original_end_time_zone": "UTC",
            "uid": "eventuid1",
            "reminder_minutes_before_start": 15,
            "is_reminder_on": True,
            "has_attachments": False,
            "subject": "Canceled: Weekly Office meeting",
            "body_preview": "________________________________________________________________________________\r\nRéunion Microsoft Teams\r\nParticipez à partir de votre ordinateur, de votre application mobile ou de l’appareil de la salle\r\nCliquez ici pour rejoindre la réunion\r\nID de la",
            "importance": "normal",
            "sensitivity": "normal",
            "is_all_day": False,
            "is_cancelled": False,
            "is_organizer": False,
            "response_requested": True,
            "series_master_id": None,
            "show_as": "free",
            "type": "singleInstance",
            "web_link": "https://test.ch",
            "online_meeting_url": None,
            "is_online_meeting": True,
            "online_meeting_provider": "teamsForBusiness",
            "allow_new_time_proposals": True,
            "occurrence_id": None,
            "is_draft": False,
            "hide_attendees": False,
            "locations": [
                {
                    "displayName": "Microsoft Teams Meeting",
                    "locationType": "default",
                    "uniqueId": "Microsoft Teams Meeting",
                    "uniqueIdType": "private",
                }
            ],
            "recurrence": None,
            "attendees": [
                {
                    "type": "required",
                    "status": {"response": "none", "time": "0001-01-01T00:00:00Z"},
                    "emailAddress": {"name": "organizer1", "address": "organizer1@test.ch"},
                },
                *[
                    {
                        "type": "optional",
                        "status": {"response": "none", "time": "0001-01-01T00:00:00Z"},
                        "emailAddress": {"name": f"attendee{i}", "address": f"attendee{i}@atonra.ch"},
                    }
                    for i in range(1, 15)
                ],
            ],
            "response_status.response": "notResponded",
            "response_status.time": "0001-01-01T00:00:00Z",
            "body.content_type": "html",
            "start.date_time": "2023-12-18T08:30:00.0000000",
            "start.time_zone": "UTC",
            "end.date_time": "2023-12-18T10:00:00.0000000",
            "end.time_zone": "UTC",
            "location.display_name": "Microsoft Teams Meeting",
            "location.location_type": "default",
            "location.unique_id": "Microsoft Teams Meeting",
            "location.unique_id_type": "private",
            "organizer.email_address.name": "organizer1",
            "organizer.email_address.address": "organizer1@atonra.ch",
        }

    @pytest.fixture()
    def canceled_teams_event_fixture(self, teams_event_fixture):
        canceled_event = copy.deepcopy(teams_event_fixture)
        canceled_event["is_cancelled"] = True
        return canceled_event


# recurrence_event = {
#     "id": "unique_id2-ocurrence_pattern_id-unique_recurrence_id2",
#     "uid": event.get("uid"),
#     "type": "seriesMaster",
#     "start": "2022-12-12T07:00:00.0000000",
#     "end": "2022-12-12T07:30:00.0000000",
#     "created": "2022-12-08T10:37:29.8938372Z",
#     "show_as": "busy",
#     "subject": "test recc",
#     "is_draft": False,
#     "web_link": "fake_web_link2",
#     "locations": [],
#     "categories": [],
#     "change_key": "fake_change_key2",
#     "importance": "normal",
#     "is_all_day": False,
#     "odata_etag": "fake_etag2",
#     "sensitivity": "normal",
#     "body.content": "",
#     "body_preview": "",
#     "is_cancelled": False,
#     "is_organizer": True,
#     "participants": [],
#     "end.time_zone": "UTC",
#     "last_modified": "2022-12-08T10:37:30.0188091Z",
#     "occurrence_id": None,
#     "odata_context": "fake_odata_context2",
#     "hide_attendees": False,
#     "is_reminder_on": True,
#     "online_meeting": None,
#     "transaction_id": "70957719-1fb2-5642-7bb6-c1363e1091e0",
#     "has_attachments": False,
#     "start.time_zone": "UTC",
#     "series_master_id": None,
#     "body.content_type": "html",
#     "is_online_meeting": False,
#     "online_meeting_url": None,
#     "response_requested": True,
#     "response_status.time": "0001-01-01T00:00:00Z",
#     "location.address.type": "unknown",
#     "location.display_name": "",
#     "recurrence.range.type": "endDate",
#     "location.location_type": "default",
#     "original_end_time_zone": "W. Europe Standard Time",
#     "location.unique_id_type": "unknown",
#     "online_meeting_provider": "unknown",
#     "recurrence.pattern.type": "daily",
#     "allow_new_time_proposals": True,
#     "original_start_time_zone": "W. Europe Standard Time",
#     "recurrence.pattern.index": "first",
#     "recurrence.pattern.month": 0,
#     "response_status.response": "organizer",
#     "recurrence.range.end_date": "2022-12-14",
#     "recurrence.pattern.interval": 1,
#     "recurrence.range.start_date": "2022-12-12",
#     "organizer.email_address.name": "Fake organizer name",
#     "calendar@odata.navigationLink": "fake_navigation_link",
#     "reminder_minutes_before_start": 15,
#     "calendar@odata.associationLink": "fake_association_link",
#     "organizer.email_address.address": "test@test.com",
#     "recurrence.pattern.day_of_month": 0,
#     "recurrence.pattern.first_day_of_week": "sunday",
#     "recurrence.range.recurrence_time_zone": "W. Europe Standard Time",
#     "recurrence.range.number_of_occurrences": 0,
# }

# occurrences_event = [
#     {
#         "id": "unique_id001-ocurrence_pattern_id-unique_recurrence_id2",
#         "end": "2022-12-12T07:30:00.0000000",
#         "uid": event.get("uid"),
#         "type": "occurrence",
#         "start": "2022-12-12T07:00:00.0000000",
#         "created": "2022-12-08T10:37:29.8938372Z",
#         "show_as": "busy",
#         "subject": "test recc",
#         "is_draft": False,
#         "web_link": "weblink",
#         "locations": [],
#         "categories": [],
#         "change_key": "changekey1",
#         "importance": "normal",
#         "is_all_day": False,
#         "odata_etag": "etag1",
#         "recurrence": None,
#         "sensitivity": "normal",
#         "body.content": "",
#         "body_preview": "",
#         "is_cancelled": False,
#         "is_organizer": True,
#         "participants": [],
#         "end.time_zone": "UTC",
#         "last_modified": "2022-12-08T10:37:30.0188091Z",
#         "occurrence_id": "OID.unique_id2-ocurrence_pattern_id-unique_recurrence_id2.2022-12-12",
#         "hide_attendees": False,
#         "is_reminder_on": True,
#         "online_meeting": None,
#         "transaction_id": "fake_transaction_id",
#         "has_attachments": False,
#         "start.time_zone": "UTC",
#         "series_master_id": "unique_id2-ocurrence_pattern_id-unique_recurrence_id2",
#         "body.content_type": "html",
#         "is_online_meeting": False,
#         "online_meeting_url": None,
#         "response_requested": True,
#         "response_status.time": "0001-01-01T00:00:00Z",
#         "location.address.type": "unknown",
#         "location.display_name": "",
#         "location.location_type": "default",
#         "original_end_time_zone": "W. Europe Standard Time",
#         "location.unique_id_type": "unknown",
#         "online_meeting_provider": "unknown",
#         "allow_new_time_proposals": True,
#         "original_start_time_zone": "W. Europe Standard Time",
#         "response_status.response": "organizer",
#         "organizer.email_address.name": "Fake organizer name",
#         "reminder_minutes_before_start": 15,
#         "organizer.email_address.address": "test@test.com",
#     },
#     {
#         "id": "unique_id002-ocurrence_pattern_id-unique_recurrence_id2",
#         "end": "2022-12-13T07:30:00.0000000",
#         "uid": event.get("uid"),
#         "type": "occurrence",
#         "start": "2022-12-13T07:00:00.0000000",
#         "created": "2022-12-08T10:37:29.8938372Z",
#         "show_as": "busy",
#         "subject": "test recc",
#         "is_draft": False,
#         "web_link": "weblink",
#         "locations": [],
#         "categories": [],
#         "change_key": "changekey1",
#         "importance": "normal",
#         "is_all_day": False,
#         "odata_etag": "etag1",
#         "recurrence": None,
#         "sensitivity": "normal",
#         "body.content": "",
#         "body_preview": "",
#         "is_cancelled": False,
#         "is_organizer": True,
#         "participants": [],
#         "end.time_zone": "UTC",
#         "last_modified": "2022-12-08T10:37:30.0188091Z",
#         "occurrence_id": "OID.unique_id2-ocurrence_pattern_id-unique_recurrence_id2.2022-12-13",
#         "hide_attendees": False,
#         "is_reminder_on": True,
#         "online_meeting": None,
#         "transaction_id": "transaction1",
#         "has_attachments": False,
#         "start.time_zone": "UTC",
#         "series_master_id": "unique_id2-ocurrence_pattern_id-unique_recurrence_id2",
#         "body.content_type": "html",
#         "is_online_meeting": False,
#         "online_meeting_url": None,
#         "response_requested": True,
#         "response_status.time": "0001-01-01T00:00:00Z",
#         "location.address.type": "unknown",
#         "location.display_name": "",
#         "location.location_type": "default",
#         "original_end_time_zone": "W. Europe Standard Time",
#         "location.unique_id_type": "unknown",
#         "online_meeting_provider": "unknown",
#         "allow_new_time_proposals": True,
#         "original_start_time_zone": "W. Europe Standard Time",
#         "response_status.response": "organizer",
#         "organizer.email_address.name": "Fake organizer name",
#         "reminder_minutes_before_start": 15,
#         "organizer.email_address.address": "test@test.com",
#     },
#     {
#         "id": "unique_id003-ocurrence_pattern_id-unique_recurrence_id2",
#         "end": "2022-12-14T07:30:00.0000000",
#         "uid": event.get("uid"),
#         "type": "occurrence",
#         "start": "2022-12-14T07:00:00.0000000",
#         "created": "2022-12-08T10:37:29.8938372Z",
#         "show_as": "busy",
#         "subject": "test recc",
#         "is_draft": False,
#         "web_link": "weblink4",
#         "locations": [],
#         "categories": [],
#         "change_key": "change_key5",
#         "importance": "normal",
#         "is_all_day": False,
#         "odata_etag": "etag3",
#         "recurrence": None,
#         "sensitivity": "normal",
#         "body.content": "",
#         "body_preview": "",
#         "is_cancelled": False,
#         "is_organizer": True,
#         "participants": [],
#         "end.time_zone": "UTC",
#         "last_modified": "2022-12-08T10:37:30.0188091Z",
#         "occurrence_id": "OID.unique_id2-ocurrence_pattern_id-unique_recurrence_id2..2022-12-14",
#         "hide_attendees": False,
#         "is_reminder_on": True,
#         "online_meeting": None,
#         "transaction_id": "transaction3",
#         "has_attachments": False,
#         "start.time_zone": "UTC",
#         "series_master_id": "unique_id2-ocurrence_pattern_id-unique_recurrence_id2",
#         "body.content_type": "html",
#         "is_online_meeting": False,
#         "online_meeting_url": None,
#         "response_requested": True,
#         "response_status.time": "0001-01-01T00:00:00Z",
#         "location.address.type": "unknown",
#         "location.display_name": "",
#         "location.location_type": "default",
#         "original_end_time_zone": "W. Europe Standard Time",
#         "location.unique_id_type": "unknown",
#         "online_meeting_provider": "unknown",
#         "allow_new_time_proposals": True,
#         "original_start_time_zone": "W. Europe Standard Time",
#         "response_status.response": "organizer",
#         "organizer.email_address.name": "Fake organizer name",
#         "reminder_minutes_before_start": 15,
#         "organizer.email_address.address": "test@test.com",
#     },
# ]
