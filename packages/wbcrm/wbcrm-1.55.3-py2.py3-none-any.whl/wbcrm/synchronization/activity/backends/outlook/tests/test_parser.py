from datetime import datetime

import pytest
from psycopg.types.range import TimestamptzRange
from wbcore.contrib.agenda.factories import ConferenceRoomFactory

from wbcrm.models.recurrence import Recurrence
from wbcrm.synchronization.activity.backends.outlook.parser import OutlookParser

from .fixtures import TestOutlookSyncFixture


@pytest.mark.django_db
class TestOutlookSyncParser(TestOutlookSyncFixture):
    def test_convert_string_to_datetime(self, organizer_event_fixture_parsed):
        start = OutlookParser.convert_string_to_datetime(
            organizer_event_fixture_parsed["start.date_time"], organizer_event_fixture_parsed["start.time_zone"]
        )
        assert isinstance(start, datetime)

    def test_convert_to_all_day_period(self, organizer_event_fixture_parsed):
        start = OutlookParser.convert_string_to_datetime(
            organizer_event_fixture_parsed["start.date_time"], organizer_event_fixture_parsed["start.time_zone"]
        )
        end = OutlookParser.convert_string_to_datetime(
            organizer_event_fixture_parsed["end.date_time"], organizer_event_fixture_parsed["end.time_zone"]
        )
        period = OutlookParser.convert_to_all_day_period(TimestamptzRange(start, end))
        assert period
        assert isinstance(period, TimestamptzRange)

    def test_deserialize_participants(self, organizer_event_fixture_parsed):
        participants, conference_rooms = OutlookParser.deserialize_participants(organizer_event_fixture_parsed)
        assert len(conference_rooms) == 0
        assert len(participants) == len(organizer_event_fixture_parsed["attendees"]) + 1  # include the organizer

    def test_deserialize_recurring_activities(
        self, organizer_event_fixture_parsed, organizer_master_event_fixture_parsed
    ):
        assert OutlookParser.deserialize_recurring_activities(organizer_event_fixture_parsed) == {
            "recurrence_count": 0,
            "recurrence_end": None,
            "repeat_choice": "NEVER",
        }
        assert OutlookParser.deserialize_recurring_activities(organizer_master_event_fixture_parsed) != {
            "recurrence_count": 0,
            "recurrence_end": None,
            "repeat_choice": "NEVER",
        }

    def test_deserialize_person(self, organizer_event_fixture_parsed):
        person_dto = OutlookParser.deserialize_person("test@test.ch", "test")
        person_dto1 = OutlookParser.deserialize_person("test@test.ch", "first_name_test last_name_test")
        person_dto2 = OutlookParser.deserialize_person(
            organizer_event_fixture_parsed["organizer.email_address.address"],
            organizer_event_fixture_parsed["organizer.email_address.name"],
        )
        assert person_dto.email == person_dto1.email == "test@test.ch"
        assert person_dto2.email == organizer_event_fixture_parsed["organizer.email_address.address"]
        assert person_dto.first_name == person_dto.last_name == "test"
        assert person_dto1.first_name == "first_name_test"
        assert person_dto1.last_name == "last_name_test"

    @pytest.mark.parametrize(
        "visibility, sensitivity",
        [("PUBLIC", "normal"), ("PRIVATE", "private"), ("CONFIDENTIAL", "confidential"), ("PUBLIC", None)],
    )
    def test_convert_sensitivity_to_visibility(self, visibility, sensitivity):
        assert OutlookParser.convert_sensitivity_to_visibility(sensitivity) == visibility

    @pytest.mark.parametrize(
        "visibility, sensitivity",
        [("PUBLIC", "normal"), ("PRIVATE", "private"), ("CONFIDENTIAL", "confidential"), (None, "normal")],
    )
    def test_convert_visibility_to_sensitivity(self, visibility, sensitivity):
        assert OutlookParser.convert_visibility_to_sensitivity(visibility) == sensitivity

    @pytest.mark.parametrize(
        "reminder_choice, reminder_minute",
        [
            ("NEVER", -1),
            ("EVENT_TIME", 0),
            ("MINUTES_5", 5),
            ("MINUTES_15", 15),
            ("MINUTES_30", 30),
            ("HOURS_1", 60),
            ("HOURS_2", 120),
            ("HOURS_12", 720),
            ("WEEKS_1", 10080),
            ("MINUTES_15", None),
        ],
    )
    def test_convert_reminder_minutes_to_choice(self, reminder_choice, reminder_minute):
        assert OutlookParser.convert_reminder_minutes_to_choice(reminder_minute) == reminder_choice

    @pytest.mark.parametrize(
        "reminder_choice, reminder_minute",
        [
            ("NEVER", -1),
            ("EVENT_TIME", 0),
            ("MINUTES_5", 5),
            ("MINUTES_15", 15),
            ("MINUTES_30", 30),
            ("HOURS_1", 60),
            ("HOURS_2", 120),
            ("HOURS_12", 720),
            ("WEEKS_1", 10080),
        ],
    )
    def test_convert_reminder_choice_to_minutes(self, reminder_choice, reminder_minute):
        assert OutlookParser.convert_reminder_choice_to_minutes(reminder_choice) == reminder_minute

    def test_serialize_person(self, person_factory):
        person_dto = person_factory()._build_dto()
        person_dict = OutlookParser.serialize_person(person_dto)
        assert set(person_dict.keys()) == {"emailAddress"}
        assert person_dict["emailAddress"]["address"] == person_dto.email
        assert person_dict["emailAddress"]["name"] == f"{person_dto.first_name} {person_dto.last_name}"

    @pytest.mark.parametrize(
        "participant_status, attendee_status",
        [
            ("NOTRESPONDED", "notResponded"),
            ("ATTENDS", "accepted"),
            ("CANCELLED", "declined"),
            ("MAYBE", "tentativelyAccepted"),
            ("ATTENDS_DIGITALLY", "accepted"),
        ],
    )
    def test_convert_participant_status_to_attendee_status(self, participant_status, attendee_status):
        assert OutlookParser.convert_participant_status_to_attendee_status(participant_status) == attendee_status

    @pytest.mark.parametrize(
        "participant_status, attendee_status",
        [
            ("NOTRESPONDED", "notResponded"),
            ("ATTENDS", "accepted"),
            ("CANCELLED", "declined"),
            ("MAYBE", "tentativelyAccepted"),
            ("NOTRESPONDED", None),
            ("ATTENDS", "organizer"),
        ],
    )
    def test_convert_attendee_status_to_participant_status(self, participant_status, attendee_status):
        assert OutlookParser.convert_attendee_status_to_participant_status(attendee_status) == participant_status

    def test_serialize_participants(self, activity_factory, person_factory):
        activity = activity_factory(preceded_by=None, participants=(person_factory(),))
        activity_dto = activity._build_dto()
        assert activity_dto.participants
        attendees = OutlookParser.serialize_participants(activity_dto.participants)
        assert attendees
        assert attendees[0]

    def test_serialize_conference_room(self):
        cf_dto = ConferenceRoomFactory()._build_dto()
        cf_dict = OutlookParser.serialize_conference_room(cf_dto)
        assert set(cf_dict.keys()) == {"emailAddress", "type"}
        assert cf_dict["type"] == "resource"
        assert cf_dict["emailAddress"]["address"] == cf_dto.email
        assert cf_dict["emailAddress"]["name"] == cf_dto.name

    def test_serialize_recurring_activities(self, activity_factory):
        act_dto0 = activity_factory()._build_dto()
        act_dto = activity_factory(
            repeat_choice=Recurrence.ReoccuranceChoice.DAILY, recurrence_count=3, preceded_by=None
        )._build_dto()
        reccurence_dict = OutlookParser.serialize_recurring_activities(act_dto)
        assert OutlookParser.serialize_recurring_activities(act_dto0) == {}
        assert set(reccurence_dict.keys()) == {"recurrence"}
        assert reccurence_dict["recurrence"]["pattern"]["type"] == "daily"
        assert reccurence_dict["recurrence"]["range"]["type"] == "numbered"
        assert reccurence_dict["recurrence"]["range"]["numberOfOccurrences"] == 4
        assert reccurence_dict["recurrence"]["range"]["startDate"] == act_dto.period.lower.strftime("%Y-%m-%d")
