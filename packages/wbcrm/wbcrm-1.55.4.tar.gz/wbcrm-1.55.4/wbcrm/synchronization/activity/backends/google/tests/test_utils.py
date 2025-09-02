# import datetime
# from zoneinfo import ZoneInfo

# import pytest
# from django.conf import settings
# from dynamic_preferences.registries import global_preferences_registry
# from wbcrm.models import (
#     Activity,
#     ActivityParticipant,
#     CalendarItem,
#     EmailContact,
#     Person,
# )

# from ..utils import GoogleSyncUtils
# from .test_data import event, event_list


# @pytest.mark.django_db
# class TestUtils:
#     def test_add_instance_metadata(self, activity_factory):
#         new_metadata = {"google_backend": {"instance": {"uID": "UID"}, "event": {"id": "event id"}}}
#         parent_occurrence: Activity = activity_factory(
#             metadata={"google_backend": {"instance": {"originalStartTime": {"dateTime": "Fake Date Time"}}}}
#         )
#         child_activity_a: Activity = activity_factory(
#             parent_occurrence=parent_occurrence,
#             metadata={"google_backend": {"instance": {"originalStartTime": {"dateTime": "Fake Date Time A"}}}},
#         )
#         child_activity_b: Activity = activity_factory(
#             parent_occurrence=parent_occurrence,
#             metadata={"google_backend": {"instance": {"originalStartTime": {"dateTime": "Fake Date Time B"}}}},
#         )
#         child_activity_c: Activity = activity_factory(
#             parent_occurrence=parent_occurrence,
#             metadata={"google_backend": {"instance": {"originalStartTime": {"dateTime": "Fake Date Time C"}}}},
#         )
#         GoogleSyncUtils.add_instance_metadata(parent_occurrence, event_list, new_metadata)
#         parent_occurrence = Activity.objects.get(id=parent_occurrence.id)
#         child_activity_a = Activity.objects.get(id=child_activity_a.id)
#         child_activity_b = Activity.objects.get(id=child_activity_b.id)
#         child_activity_c = Activity.objects.get(id=child_activity_c.id)
#         assert parent_occurrence.metadata["google_backend"]["instance"]["metaTest"] == "Parent"
#         assert child_activity_a.external_id == "2"
#         assert child_activity_a.metadata["google_backend"]["instance"]["metaTest"] == "Child A"
#         assert child_activity_b.external_id == "3"
#         assert child_activity_b.metadata["google_backend"]["instance"]["metaTest"] == "Child B"
#         assert child_activity_c.external_id == "4"
#         assert child_activity_c.metadata["google_backend"]["instance"]["metaTest"] == "Child C"

#     def test_convert_activity_visibility_to_event_visibility(self):
#         assert (
#             GoogleSyncUtils.convert_activity_visibility_to_event_visibility(CalendarItem.Visibility.PUBLIC) == "public"
#         )
#         assert (
#             GoogleSyncUtils.convert_activity_visibility_to_event_visibility(CalendarItem.Visibility.PRIVATE)
#             == "private"
#         )
#         assert (
#             GoogleSyncUtils.convert_activity_visibility_to_event_visibility(CalendarItem.Visibility.CONFIDENTIAL)
#             == "private"
#         )

#     def test_convert_event_visibility_to_activity_visibility(self):
#         assert (
#             GoogleSyncUtils.convert_event_visibility_to_activity_visibility("private")
#             == CalendarItem.Visibility.PRIVATE
#         ) or (
#             GoogleSyncUtils.convert_event_visibility_to_activity_visibility("private")
#             == CalendarItem.Visibility.CONFIDENTIAL
#         )
#         assert (
#             GoogleSyncUtils.convert_event_visibility_to_activity_visibility("public") == CalendarItem.Visibility.PUBLIC
#         )

#     def test_convert_attendee_status_to_participant_status(self):
#         assert (
#             GoogleSyncUtils.convert_attendee_status_to_participant_status("accepted")
#             == ActivityParticipant.ParticipationStatus.ATTENDS
#         )
#         assert (
#             GoogleSyncUtils.convert_attendee_status_to_participant_status("declined")
#             == ActivityParticipant.ParticipationStatus.CANCELLED
#         )
#         assert (
#             GoogleSyncUtils.convert_attendee_status_to_participant_status("tentative")
#             == ActivityParticipant.ParticipationStatus.MAYBE
#         )
#         assert (
#             GoogleSyncUtils.convert_attendee_status_to_participant_status("Something different")
#             == ActivityParticipant.ParticipationStatus.NOTRESPONDED
#         )

#     def test_convert_participant_status_to_attendee_status(self):
#         assert (
#             GoogleSyncUtils.convert_participant_status_to_attendee_status(
#                 ActivityParticipant.ParticipationStatus.ATTENDS
#             )
#             == "accepted"
#         )
#         assert (
#             GoogleSyncUtils.convert_participant_status_to_attendee_status(
#                 ActivityParticipant.ParticipationStatus.ATTENDS_DIGITALLY
#             )
#             == "accepted"
#         )
#         assert (
#             GoogleSyncUtils.convert_participant_status_to_attendee_status(
#                 ActivityParticipant.ParticipationStatus.CANCELLED
#             )
#             == "declined"
#         )
#         assert (
#             GoogleSyncUtils.convert_participant_status_to_attendee_status(
#                 ActivityParticipant.ParticipationStatus.MAYBE
#             )
#             == "tentative"
#         )
#         assert GoogleSyncUtils.convert_participant_status_to_attendee_status("Something different") == "notResponded"

#     @pytest.mark.parametrize("google_event", [{}, event])
#     def test_get_participants(self, google_event, person_factory, email_contact_factory):
#         person_a = person_factory()
#         person_b = person_factory()
#         person_c = person_factory()
#         email_contact_factory(primary=True, entry=person_a, address="Foo@Foo.com")
#         email_contact_factory(primary=True, entry=person_b, address="Bar@Bar.com")
#         part_list = GoogleSyncUtils.get_or_create_participants(google_event, person_c)
#         if not google_event:
#             assert part_list == [{"person_id": person_c.id, "status": ActivityParticipant.ParticipationStatus.ATTENDS}]
#         else:
#             person_d = Person.objects.get(last_name="Foo Bar")
#             person_e = Person.objects.get(last_name="Bar@Foo.com")
#             assert len(part_list) == 5
#             assert {"person_id": person_a.id, "status": ActivityParticipant.ParticipationStatus.ATTENDS} in part_list
#             assert {"person_id": person_b.id, "status": ActivityParticipant.ParticipationStatus.CANCELLED} in part_list
#             assert {"person_id": person_c.id, "status": ActivityParticipant.ParticipationStatus.ATTENDS} in part_list
#             assert {"person_id": person_d.id, "status": ActivityParticipant.ParticipationStatus.MAYBE} in part_list
#             assert {"person_id": person_e.id, "status": ActivityParticipant.ParticipationStatus.MAYBE} in part_list

#     @pytest.mark.parametrize("can_sync", [False, True])
#     @pytest.mark.parametrize("google_event", [{}, event])
#     def test_convert_activity_participants_to_attendees_list(
#         self, can_sync, google_event, activity_factory, person_factory, internal_user_factory, email_contact_factory
#     ):
#         global_preferences_registry.manager()["wbactivity_sync__sync_external_participants"] = can_sync
#         person_a: Person = internal_user_factory()
#         person_b: Person = person_factory()
#         person_c: Person = person_factory()
#         email_contact_factory(primary=True, entry=person_a, address="A@A.com")
#         email_contact_factory(primary=True, entry=person_b, address="B@B.com")
#         email_contact_factory(primary=True, entry=person_c, address="Foo@Bar.com")
#         activity: Activity = activity_factory(creator=person_a, participants=[person_a.id, person_b.id, person_c])
#         # attendees: list[dict] = convert_activity_participants_to_attendees_list(activity, google_event)
#         attendees: list[dict] = GoogleSyncUtils.convert_activity_participants_to_attendees(activity, google_event)

#         person_a_dict: dict = {
#             "displayName": person_a.computed_str,
#             "email": str(person_a.primary_email_contact()),
#             "responseStatus": "accepted",
#         }
#         person_b_dict: dict = {
#             "displayName": person_b.computed_str,
#             "email": str(person_b.primary_email_contact()),
#             "responseStatus": "needsAction",
#         }
#         person_c_dict: dict = {
#             "displayName": person_c.computed_str,
#             "email": str(person_c.primary_email_contact()),
#             "responseStatus": "needsAction",
#         }
#         if not google_event and not can_sync:
#             assert len(attendees) == 1
#             assert person_a_dict in attendees
#         elif not google_event and can_sync:
#             assert len(attendees) == 3
#             assert person_a_dict in attendees
#             assert person_b_dict in attendees
#         elif google_event and not can_sync:
#             assert len(attendees) == 2
#             assert person_a_dict in attendees
#             assert person_c_dict in attendees
#             assert person_b_dict not in attendees
#         else:
#             assert len(attendees) == 3
#             assert person_a_dict in attendees
#             assert person_b_dict in attendees
#             assert person_c_dict in attendees

#     @pytest.mark.parametrize("created", [False])
#     @pytest.mark.parametrize(
#         "metadata",
#         [{}, {"recurrence": ["Recurrence A"], "google_backend": {"event": {"recurrence": ["Recurrence B"]}}}],
#     )
#     def test_convert_activity_to_event(
#         self, internal_user_factory, activity_factory, email_contact_factory, created, metadata
#     ):
#         timezone = ZoneInfo(settings.TIME_ZONE)
#         person_a: Person = internal_user_factory()
#         person_b: Person = internal_user_factory()
#         email_contact_factory(primary=True, entry=person_a, address="Foo@Foo.com")
#         email_contact_factory(primary=True, entry=person_b, address="Bar@Bar.com")
#         activity: Activity = activity_factory(
#             creator=person_a,
#             participants=[person_b.id],
#             visibility=CalendarItem.Visibility.PUBLIC,
#             metadata=metadata,
#         )
#         event = GoogleSyncUtils.convert_activity_to_event(activity, created)
#         assert event["summary"] == activity.title
#         assert event["creator"] == str(activity.creator.primary_email_contact())
#         assert event["organizer"] == str(activity.assigned_to.primary_email_contact())
#         assert event["location"] == activity.location
#         assert event["visibility"] == "public"
#         assert event["attendees"] == [
#             {
#                 "displayName": person_b.computed_str,
#                 "email": str(person_b.primary_email_contact()),
#                 "responseStatus": "needsAction",
#             }
#         ]
#         assert event["start"] == {
#             "dateTime": activity.period.lower.astimezone(timezone).isoformat(),
#             "timeZone": settings.TIME_ZONE,
#         }
#         assert event["end"] == {
#             "dateTime": activity.period.upper.astimezone(timezone).isoformat(),
#             "timeZone": settings.TIME_ZONE,
#         }
#         if metadata and not created:
#             assert event["recurrence"] == ["Recurrence B"]
#         elif metadata and created:
#             assert event["recurrence"] == ["Recurrence A"]
#         else:
#             assert event["recurrence"] == []

#     def test_get_start_and_end(self):
#         meta = {
#             "start": {"dateTime": "2022-12-20T11:30:00+01:00", "timeZone": "Europe/Berlin"},
#             "end": {"dateTime": "2022-12-20T12:30:00+01:00", "timeZone": "Europe/Berlin"},
#         }
#         meta_date = {
#             "start": {"date": "2022-12-24"},
#             "end": {"date": "2022-12-25"},
#         }
#         start, end = GoogleSyncUtils.get_start_and_end(meta)
#         assert start == datetime.datetime(
#             2022, 12, 20, 11, 30, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))
#         )
#         assert end == datetime.datetime(
#             2022, 12, 20, 12, 30, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))
#         )
#         start, end = GoogleSyncUtils.get_start_and_end(meta_date)
#         assert start == datetime.datetime(2022, 12, 24)
#         assert end == datetime.datetime(2022, 12, 24, 23, 59, 59)

#     @pytest.mark.parametrize(
#         "organizer",
#         ["", "Foo@Foo.com", "Bar@Bar.com"],
#     )
#     def test_get_person(self, person_factory, email_contact_factory, organizer):
#         person_a: Person = person_factory()
#         email_contact_factory(primary=True, entry=person_a, address="foo@foo.com")

#         if organizer == "Foo@Foo.com":
#             assert GoogleSyncUtils.get_or_create_person(organizer) == person_a
#         elif organizer and (mail := organizer) == "Bar@Bar.com":
#             creator = GoogleSyncUtils.get_or_create_person(mail)
#             person_b = Person.objects.get(last_name=mail)
#             assert EmailContact.objects.filter(entry=creator, address=mail.lower(), primary=True).exists()
#             assert creator.id == person_b.id
#             assert creator.last_name == mail
#         else:
#             assert GoogleSyncUtils.get_or_create_person(organizer) is None
