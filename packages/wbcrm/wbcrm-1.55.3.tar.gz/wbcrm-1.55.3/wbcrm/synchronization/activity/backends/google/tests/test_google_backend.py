# import datetime
# import json
# from unittest.mock import patch

# import pytest
# from django.utils import timezone
# from dynamic_preferences.registries import global_preferences_registry
# from rest_framework.test import APIRequestFactory
# from wbcore.test.utils import get_or_create_superuser
# from wbcrm.models import ActivityParticipant

# from ..google_calendar_backend import GoogleCalendarBackend
# from .test_data import credentials, event_data, execute_service, service_data


# class TestInitialisationGoogleCalendarBackend:
#     @pytest.fixture()
#     def activity_with_user(self, activity_factory):
#         user = get_or_create_superuser()
#         user.metadata = {"google_backend": {"watch": {"id": "fake_id"}}}
#         user.save()
#         return activity_factory(creator=user.profile)

#     @pytest.fixture()
#     def activity_with_user2(self, activity_factory):
#         user = get_or_create_superuser()
#         user.metadata = {"google_backend": {"watch": {"id": "fake_id2"}}}
#         user.save()
#         return activity_factory(creator=user.profile)

#     @pytest.mark.parametrize("credentials", ["", credentials])
#     def test_get_service_account_file(self, credentials):
#         from ..google_calendar_backend import GoogleCalendarBackend

#         global_preferences_registry.manager()["wbactivity_sync__google_sync_credentials"] = credentials

#         backend = GoogleCalendarBackend()

#         if not credentials:
#             with pytest.raises(ValueError) as excinfo:
#                 file = backend._get_service_account_file()
#                 assert (
#                     "The Google credentials are not set. You cannot use the Google Calendar Backend without the Google credentials."
#                     in str(excinfo.value)
#                 )
#         else:
#             file = backend._get_service_account_file()
#             assert file == json.loads(credentials)

#     @pytest.mark.parametrize("credentials", [credentials])
#     def test_get_service_account_url(self, credentials):
#         from ..google_calendar_backend import GoogleCalendarBackend

#         global_preferences_registry.manager()["wbactivity_sync__google_sync_credentials"] = credentials
#         assert GoogleCalendarBackend()._get_service_account_url()

#     def test_get_service_user_email(self, activity_with_user, activity_with_user2, activity_factory):
#         global_preferences_registry.manager()["wbcrm__main_company"] = employee.employers.first().id

#         activity = activity_factory()
#         activity1 = activity_factory()
#         activity2 = activity_with_user2
#         activity3 = activity_with_user
#         activity4 = activity_factory(participants=(employee,))
#         tomorrow = (timezone.now() + datetime.timedelta(days=1)).replace(tzinfo=None)
#         activity3.creator.user_account.metadata["google_backend"]["watch"]["expiration"] = (
#             datetime.datetime.timestamp(tomorrow) * 1000
#         )
#         activity3.creator.user_account.save()
#         employee.user_account.metadata = activity3.creator.user_account.metadata
#         employee.user_account.save()
#         backend = GoogleCalendarBackend()
#         assert backend._get_service_user_email(activity) == ""
#         assert backend._get_service_user_email(activity1) == ""
#         assert backend._get_service_user_email(activity2) == ""
#         assert backend._get_service_user_email(activity3) == activity3.creator.user_account.email
#         assert backend._get_service_user_email(activity4)

#     @patch("wbcrm.synchronization.activity.backends.google.google_calendar_backend.Credentials")
#     @patch("wbcrm.synchronization.activity.backends.google.google_calendar_backend.build")
#     @pytest.mark.parametrize("credentials", ["", credentials])
#     def test_build_service(self, mock_build, mock_credentials, credentials):
#         global_preferences_registry.manager()["wbactivity_sync__google_sync_credentials"] = credentials
#         user = get_or_create_superuser()
#         backend = GoogleCalendarBackend()
#         if not credentials:
#             with pytest.raises(ValueError) as excinfo:
#                 resource = backend._build_service(user.email)
#                 assert backend.error_messages["service_build_error"] in str(excinfo.value)
#         else:
#             resource = backend._build_service(user.email)
#             assert resource


# @patch("wbcrm.synchronization.activity.backends.google.google_calendar_backend.GoogleCalendarBackend._build_service")
# @patch(
#     "wbcrm.synchronization.activity.backends.google.google_calendar_backend.GoogleCalendarBackend._get_service_user_email"
# )
# @pytest.mark.parametrize(
#     "sync_past_activity, event", [(False, ""), (True, ""), (False, event_data), (True, event_data)]
# )
# @pytest.mark.django_db
# class TestGoogleCalendarBackend:
#     @pytest.fixture()
#     def activity_fixture(self, activity_factory, event):
#         user = get_or_create_superuser()
#         user.metadata = {"google_backend": {"watch": {"id": "fake_id"}}}
#         user.save()
#         if event:
#             metadata = {"google_backend": {"event": event}}
#             return activity_factory(creator=user.profile, metadata=metadata, external_id=event["id"])
#         else:
#             metadata = {}
#             return activity_factory(creator=user.profile, metadata=metadata, external_id=None)

#     def test_create_external_activity(
#         self, mock_user_email, mock_service, sync_past_activity, event, activity_factory
#     ):
#         global_preferences_registry.manager()["wbactivity_sync__sync_past_activity"] = sync_past_activity
#         now = timezone.now()
#         yesterday = now - datetime.timedelta(days=1)
#         tomorrow = now + datetime.timedelta(days=1)

#         activity_passed = activity_factory(start=yesterday, end=yesterday + datetime.timedelta(hours=1))
#         activity = activity_factory(start=tomorrow, end=tomorrow + datetime.timedelta(hours=1))
#         activity_with_parent = activity_factory(
#             start=tomorrow, end=tomorrow + datetime.timedelta(hours=1), parent_occurrence=activity_passed
#         )

#         mock_service.return_value = service_data()
#         with patch.object(execute_service, "execute", return_value=event):

#             backend = GoogleCalendarBackend()
#             if event:
#                 backend.create_external_activity(activity_passed)
#                 backend.create_external_activity(activity)
#                 backend.create_external_activity(activity_with_parent)
#                 assert (
#                     mock_service.call_count == 2
#                 )  # 2 instead of 3 because an activity with a parent cannot be synchronized

#             else:
#                 with pytest.raises(ValueError) as excinfo:
#                     backend.create_external_activity(activity_passed)
#                     backend.create_external_activity(activity)
#                     backend.create_external_activity(activity_with_parent)
#                     assert "Could not create the external google event. Exception" in str(excinfo.value)

#                     if sync_past_activity:
#                         assert mock_service.call_count == 1
#                     else:
#                         assert mock_service.call_count == 1
#             activity_passed.refresh_from_db()
#             activity.refresh_from_db()
#             activity_with_parent.refresh_from_db()

#             assert activity_with_parent.metadata == {}
#             assert activity_with_parent.external_id is None

#             if event:
#                 assert activity.metadata
#                 assert activity.external_id == event["id"]
#             else:
#                 assert activity.metadata == {}
#                 assert activity.external_id is None

#             if sync_past_activity and event:
#                 assert activity_passed.metadata
#                 assert activity_passed.external_id == event["id"]
#             else:
#                 assert activity_passed.metadata == {}
#                 assert activity_passed.external_id is None

#     def test_delete_external_activity(
#         self, mock_user_email, mock_service, sync_past_activity, event, activity_factory
#     ):
#         global_preferences_registry.manager()["wbactivity_sync__sync_past_activity"] = sync_past_activity
#         now = timezone.now()
#         yesterday = now - datetime.timedelta(days=1)
#         tomorrow = now + datetime.timedelta(days=1)

#         activity_passed = activity_factory(start=yesterday, end=yesterday + datetime.timedelta(hours=1))
#         activity = activity_factory(start=tomorrow, end=tomorrow + datetime.timedelta(hours=1))
#         activity_with_parent = activity_factory(
#             start=tomorrow, end=tomorrow + datetime.timedelta(hours=1), parent_occurrence=activity_passed
#         )

#         mock_service.return_value = service_data()
#         with patch.object(execute_service, "execute", return_value=None):

#             backend = GoogleCalendarBackend()
#             backend.delete_external_activity(activity_passed)
#             backend.delete_external_activity(activity)
#             backend.delete_external_activity(activity_with_parent)
#             assert mock_service.call_count == 3

#     def test_update_external_activity(
#         self, mock_user_email, mock_service, sync_past_activity, event, activity_factory
#     ):
#         global_preferences_registry.manager()["wbactivity_sync__sync_past_activity"] = sync_past_activity
#         now = timezone.now()
#         yesterday = now - datetime.timedelta(days=1)
#         tomorrow = now + datetime.timedelta(days=1)

#         metadata = {"google_backend": {"instance": event if event else {}}}
#         external_id = event["id"] if event else None
#         activity_no_metadata = activity_factory(start=tomorrow, end=tomorrow + datetime.timedelta(hours=1))
#         activity_passed = activity_factory(
#             start=yesterday, end=yesterday + datetime.timedelta(hours=1), external_id=external_id, metadata=metadata
#         )
#         activity = activity_factory(
#             start=tomorrow, end=tomorrow + datetime.timedelta(hours=1), external_id=external_id, metadata=metadata
#         )
#         activity_with_parent = activity_factory(
#             start=tomorrow,
#             end=tomorrow + datetime.timedelta(hours=1),
#             parent_occurrence=activity_passed,
#             external_id=external_id,
#             metadata=metadata,
#         )

#         mock_service.return_value = service_data()
#         with patch.object(execute_service, "execute", return_value=event if event else {"id": None}):
#             backend = GoogleCalendarBackend()
#             backend.update_external_activity(activity_no_metadata)
#             backend.update_external_activity(activity_passed)
#             backend.update_external_activity(activity)
#             backend.update_external_activity(activity_with_parent)

#             assert (
#                 mock_service.call_count == 5
#             )  # rather than 4 because we call create_external_activity if no metadata
#             assert activity_no_metadata.external_id == external_id
#             assert activity_no_metadata.metadata == {"google_backend": {"event": event if event else {"id": None}}}

#     @pytest.mark.parametrize("response_status", [*list(ActivityParticipant.ParticipationStatus)])
#     def test_send_participant_response_external_activity(
#         self,
#         mock_user_email,
#         mock_service,
#         response_status,
#         sync_past_activity,
#         event,
#         person_factory,
#         activity_fixture,
#     ):
#         global_preferences_registry.manager()["wbactivity_sync__sync_past_activity"] = sync_past_activity
#         activity = activity_fixture
#         person = person_factory()
#         activity.participants.add(person, activity.creator)
#         activity.save()
#         creator_participant = ActivityParticipant.objects.filter(
#             activity=activity, participant=activity.creator
#         ).first()
#         mock_service.return_value = service_data()
#         with patch.object(execute_service, "execute", return_value=event if event else {"id": None}) as mock_execute:
#             backend = GoogleCalendarBackend()
#             activityparticipant = activity.activity_participants.filter(participant=person).first()
#             backend.send_participant_response_external_activity(activityparticipant, response_status)
#             backend.send_participant_response_external_activity(creator_participant, response_status)
#             if event:
#                 assert mock_execute.call_count
#             else:
#                 assert mock_execute.call_count == 0

#     @patch(
#         "wbcrm.synchronization.activity.backends.google.google_calendar_backend.GoogleCalendarBackend.sync_with_external_calendar"
#     )
#     def test_sync_with_external_calendar(
#         self, mock_handle_changes, mock_user_email, mock_service, sync_past_activity, event
#     ):
#         user = get_or_create_superuser()
#         request = APIRequestFactory().get("", **{"HTTP_X-Goog-Channel-Id": user.id})
#         backend = GoogleCalendarBackend()
#         backend.sync_with_external_calendar(request)
#         assert mock_handle_changes.call_count == 1

#     def test_get_sync_token(self, mock_user_email, mock_service, sync_past_activity, event):
#         user = get_or_create_superuser()
#         user.metadata = {"google_backend": {"sync_token": "fake_token"}}
#         user.save()
#         backend = GoogleCalendarBackend()
#         assert backend.get_sync_token(user) == "fake_token"

#     def test_get_external_activity(self, mock_user_email, mock_service, sync_past_activity, event):
#         pass

#     def test_forward_external_activity(self, mock_user_email, mock_service, sync_past_activity, event):
#         pass

#     @patch(
#         "wbcrm.synchronization.activity.backends.google.google_calendar_backend.GoogleCalendarBackend._get_service_account_url"
#     )
#     def test_set_web_hook(self, mock_url, mock_user_email, mock_service, sync_past_activity, event):
#         user = get_or_create_superuser()
#         watch = {"id": "fake_id"}
#         mock_service.return_value = service_data()
#         with patch.object(execute_service, "execute", return_value=watch):
#             GoogleCalendarBackend().set_web_hook(user)
#         assert user.metadata["google_backend"]["watch"] == watch

#     def test_stop_web_hook(self, mock_user_email, mock_service, sync_past_activity, event):
#         user = get_or_create_superuser()
#         user.metadata = {"google_backend": {"watch": {"id": "fake_id", "resourceId": "fake_resource_id"}}}
#         user.save()
#         watch = {"id": "fake_id"}
#         mock_service.return_value = service_data()
#         with patch.object(execute_service, "execute", return_value=watch):
#             GoogleCalendarBackend().stop_web_hook(user)
#         assert user.metadata["google_backend"] == {}

#     def test_check_web_hook(self, mock_user_email, mock_service, sync_past_activity, event):
#         tomorrow = (timezone.now() + datetime.timedelta(days=1)).replace(tzinfo=None)
#         user = get_or_create_superuser()
#         user.metadata = {"google_backend": {"watch": {"expiration": datetime.datetime.timestamp(tomorrow) * 1000}}}
#         user.save()
#         with pytest.warns() as record:
#             GoogleCalendarBackend().check_web_hook(user)
#         assert len(record) == 1
