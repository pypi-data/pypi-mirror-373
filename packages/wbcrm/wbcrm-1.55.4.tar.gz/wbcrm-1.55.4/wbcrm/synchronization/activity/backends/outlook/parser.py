import calendar as calendar_reference
from datetime import datetime
from typing import Any

import pandas as pd
import pytz
from dateutil import parser, rrule
from django.utils.timezone import get_default_timezone, get_default_timezone_name
from psycopg.types.range import TimestamptzRange
from wbcore.utils.rrules import (
    convert_rrulestr_to_dict,
    convert_weekday_rrule_to_day_name,
)

from wbcrm.typings import Activity as ActivityDTO
from wbcrm.typings import ConferenceRoom as ConferenceRoomDTO
from wbcrm.typings import ParticipantStatus as ParticipantStatusDTO
from wbcrm.typings import Person as PersonDTO


class OutlookParser:
    default_visibility = "normal"
    visibility_map = {
        ActivityDTO.Visibility.PUBLIC.name: default_visibility,
        ActivityDTO.Visibility.PRIVATE.name: "private",
        ActivityDTO.Visibility.CONFIDENTIAL.name: "confidential",
    }
    default_response_status = "notResponded"
    response_status_map = {
        ParticipantStatusDTO.ParticipationStatus.NOTRESPONDED.name: default_response_status,
        ParticipantStatusDTO.ParticipationStatus.ATTENDS.name: "accepted",
        ParticipantStatusDTO.ParticipationStatus.CANCELLED.name: "declined",
        ParticipantStatusDTO.ParticipationStatus.MAYBE.name: "tentativelyAccepted",
    }
    default_reminder_minutes = 15
    reminder_map = {
        ActivityDTO.ReminderChoice.NEVER.name: -1,
        ActivityDTO.ReminderChoice.EVENT_TIME.name: 0,
        ActivityDTO.ReminderChoice.MINUTES_5.name: 5,
        ActivityDTO.ReminderChoice.MINUTES_15.name: default_reminder_minutes,
        ActivityDTO.ReminderChoice.MINUTES_30.name: 30,
        ActivityDTO.ReminderChoice.HOURS_1.name: 60,
        ActivityDTO.ReminderChoice.HOURS_2.name: 120,
        ActivityDTO.ReminderChoice.HOURS_12.name: 720,
        ActivityDTO.ReminderChoice.WEEKS_1.name: 10080,
    }

    @classmethod
    def convert_visibility_to_sensitivity(cls, visibility: str) -> str:
        return cls.visibility_map.get(visibility, cls.default_visibility)

    @classmethod
    def convert_sensitivity_to_visibility(cls, sensitivity: str) -> str:
        visibility_map_inv = {v: k for k, v in cls.visibility_map.items()}
        return visibility_map_inv.get(sensitivity, visibility_map_inv[cls.default_visibility])

    @classmethod
    def convert_participant_status_to_attendee_status(cls, participant_status: str) -> str:
        if participant_status == ParticipantStatusDTO.ParticipationStatus.ATTENDS_DIGITALLY.name:
            return "accepted"
        if participant_status == ParticipantStatusDTO.ParticipationStatus.PENDING_INVITATION.name:
            return cls.default_response_status
        return cls.response_status_map.get(participant_status, cls.default_response_status)

    @classmethod
    def convert_attendee_status_to_participant_status(cls, attendee_status: str) -> str:
        if attendee_status == "organizer":
            return ParticipantStatusDTO.ParticipationStatus.ATTENDS.name
        response_status_map_inv = {v: k for k, v in cls.response_status_map.items()}
        return response_status_map_inv.get(attendee_status, response_status_map_inv[cls.default_response_status])

    @classmethod
    def convert_reminder_choice_to_minutes(cls, choice: str) -> int:
        return cls.reminder_map[choice]

    @classmethod
    def convert_reminder_minutes_to_choice(cls, minutes: int) -> str:
        reminder_map_inv = {v: k for k, v in cls.reminder_map.items()}
        return reminder_map_inv.get(minutes, reminder_map_inv[cls.default_reminder_minutes])

    @classmethod
    def convert_string_to_datetime(cls, date_time_str: str, time_zone: str) -> datetime:
        date_time = parser.parse(date_time_str)
        try:
            return pytz.timezone(time_zone).localize(date_time)
        except pytz.exceptions.UnknownTimeZoneError:
            return pytz.timezone(get_default_timezone_name()).localize(date_time)

    @classmethod
    def convert_to_all_day_period(cls, period: TimestamptzRange) -> TimestamptzRange:
        return TimestamptzRange(
            lower=datetime(
                year=period.lower.year, month=period.lower.month, day=period.lower.day, tzinfo=get_default_timezone()
            ),
            upper=datetime(
                year=period.upper.year, month=period.upper.month, day=period.upper.day, tzinfo=get_default_timezone()
            ),
        )

    @classmethod
    def deserialize_person(cls, email: str, mame: str) -> PersonDTO:
        if (items := mame.split(" ")) and len(items) > 1:
            first_name = items[0]
            last_name = " ".join(items[1:])
        else:
            last_name = first_name = items[0]
        return PersonDTO(first_name=first_name, last_name=last_name, email=email)

    @classmethod
    def deserialize_conference_room(cls, email: str, name: str) -> ConferenceRoomDTO:
        return ConferenceRoomDTO(name=name, email=email)

    @classmethod
    def deserialize_participants(cls, event: dict) -> tuple[list[ParticipantStatusDTO], list[ConferenceRoomDTO]]:
        participants = {
            event["organizer.email_address.address"]: ParticipantStatusDTO(
                person=OutlookParser.deserialize_person(
                    event["organizer.email_address.address"], event["organizer.email_address.name"]
                ),
                status=ParticipantStatusDTO.ParticipationStatus.ATTENDS.name,
            )
        }
        conference_rooms = {}
        for attendee in event.get("attendees", []):
            if mail_info := attendee.get("emailAddress"):
                email = mail_info["address"]
                name = mail_info.get("name", email)
                if attendee.get("type") == "resource":
                    if not conference_rooms.get(email):
                        conference_rooms[email] = cls.deserialize_conference_room(email, name)
                else:
                    if (status_participant := attendee["status"].get("response")) and (
                        event["is_organizer"] or (not event["is_organizer"] and status_participant != "none")
                    ):
                        status = cls.convert_attendee_status_to_participant_status(status_participant)
                    else:
                        status = None
                    defaults = {"status": status} if status else {}
                    if not participants.get(email):
                        participants[email] = ParticipantStatusDTO(
                            person=cls.deserialize_person(email, name), **defaults
                        )
        # handle conference room when user adds conference room from participant list
        for location in event.get("locations", []):
            if location.get("locationType") == "conferenceRoom":
                email = location["locationUri"]
                name = location.get("displayName", email)
                conference_rooms[email] = cls.deserialize_conference_room(email, name)
        return list(participants.values()), list(conference_rooms.values())

    @classmethod
    def serialize_person(cls, person: PersonDTO) -> dict:
        return {
            "emailAddress": {
                "address": person.email,
                "name": f"{person.first_name} {person.last_name}",
            }
        }

    @classmethod
    def serialize_conference_room(cls, conference_room_dto=ConferenceRoomDTO) -> dict:
        return {
            "emailAddress": {"address": conference_room_dto.email, "name": conference_room_dto.name},
            "type": "resource",
        }

    @classmethod
    def serialize_participants(cls, participants_dto: list[ParticipantStatusDTO]) -> list[dict[str, Any]]:
        attendees = []
        for participant_dto in participants_dto:
            status = cls.convert_participant_status_to_attendee_status(participant_dto.status)
            _data = {
                **cls.serialize_person(participant_dto.person),
                "type": "optional",
            }
            if status != "notResponded":
                _data["status"] = {"response": status}
            attendees += [_data]
        return attendees

    @classmethod
    def _convert_weekday_to_day_name(cls, weekday: rrule.weekday) -> str:
        default_day_name = calendar_reference.day_name[0]  # Monday
        if weekday and (_day_name := convert_weekday_rrule_to_day_name(weekday)):
            return _day_name
        return default_day_name

    @classmethod
    def deserialize_recurring_activities(cls, event: dict) -> dict:
        recurrence = {
            "recurrence_end": None,
            "recurrence_count": 0,
            "repeat_choice": ActivityDTO.ReoccuranceChoice.NEVER.value,
        }
        if event.get("type") == "seriesMaster":
            freq = event["recurrence.pattern.type"]
            interval = event["recurrence.pattern.interval"]
            if freq == "yearly":
                recurrence["repeat_choice"] = ActivityDTO.ReoccuranceChoice.YEARLY.value
            elif freq == "monthly":
                if interval == 3:
                    recurrence["repeat_choice"] = ActivityDTO.ReoccuranceChoice.QUARTERLY.value
                else:
                    recurrence["repeat_choice"] = ActivityDTO.ReoccuranceChoice.MONTHLY.value
            elif freq == "weekly":
                days_of_week = {_day.lower() for _day in event.get("recurrence.pattern.days_of_week", [])}
                if interval == 2:
                    recurrence["repeat_choice"] = ActivityDTO.ReoccuranceChoice.BIWEEKLY.value
                elif interval == 1 and days_of_week == {"monday", "tuesday", "wednesday", "thursday", "friday"}:
                    recurrence["repeat_choice"] = ActivityDTO.ReoccuranceChoice.BUSINESS_DAILY.value
                else:
                    recurrence["repeat_choice"] = ActivityDTO.ReoccuranceChoice.WEEKLY.value
            else:
                recurrence["repeat_choice"] = ActivityDTO.ReoccuranceChoice.DAILY.value
            if event["recurrence.range.type"] == "endDate":
                recurrence["recurrence_end"] = datetime.strptime(event["recurrence.range.end_date"], "%Y-%m-%d")
            else:
                recurrence["recurrence_count"] = event["recurrence.range.number_of_occurrences"] - 1
        return recurrence

    @classmethod
    def serialize_recurring_activities(cls, activity_dto: ActivityDTO) -> dict:
        recurrence = {}
        if activity_dto.is_recurrent and (rule_dict := convert_rrulestr_to_dict(activity_dto.repeat_choice)):
            freq_names = {idx: freq for idx, freq in enumerate(rrule.FREQNAMES)}
            if freq_name := freq_names.get(rule_dict.get("freq")):
                pattern = {
                    "interval": rule_dict.get("interval", 1),
                    "firstDayOfWeek": cls._convert_weekday_to_day_name(rule_dict.get("wkst")),
                }
                if freq_name == "MONTHLY":
                    pattern.update({"type": "absoluteMonthly", "dayOfMonth": activity_dto.period.lower.day})
                elif freq_name == "YEARLY":
                    pattern.update(
                        {
                            "type": "absoluteYearly",
                            "month": activity_dto.period.lower.month,
                            "dayOfMonth": activity_dto.period.lower.day,
                        }
                    )
                else:  # daily or weekly
                    pattern["type"] = freq_name.lower()
                    if weekdays := rule_dict.get("byweekday", []):
                        pattern.update(
                            {
                                "type": "weekly",
                                "daysOfWeek": [cls._convert_weekday_to_day_name(weekday) for weekday in weekdays],
                            }
                        )
                    elif freq_name == "WEEKLY":
                        pattern["daysOfWeek"] = [calendar_reference.day_name[activity_dto.period.lower.weekday()]]

                range = {"startDate": activity_dto.period.lower.strftime("%Y-%m-%d")}
                if activity_dto.recurrence_count:
                    range.update(
                        {
                            "type": "numbered",
                            "numberOfOccurrences": activity_dto.recurrence_count + 1,
                            "recurrenceTimeZone": activity_dto.period.lower.tzname(),
                        }
                    )
                else:
                    range.update(
                        {
                            "type": "endDate",
                            "endDate": activity_dto.recurrence_end.strftime("%Y-%m-%d"),
                        }
                    )

                recurrence = {"recurrence": {"pattern": pattern, "range": range}}
        return recurrence

    @classmethod
    def serialize_recurrence_range_with_end_date(cls, recurrence: dict, end_date: datetime) -> dict:
        if (
            (recc := recurrence.get("recurrence"))
            and (_range := recc.get("range"))
            and (start_date := _range.get("startDate"))
        ):
            if start_date <= end_date.strftime("%Y-%m-%d"):
                recurrence["recurrence"]["range"] = {
                    "type": "endDate",
                    "startDate": start_date,
                    "endDate": end_date.strftime("%Y-%m-%d"),
                }
                if tz := _range.get("recurrenceTimeZone"):
                    recurrence["recurrence"]["range"]["recurrenceTimeZone"] = tz
                return recurrence

    @classmethod
    def serialize_event_keys(cls, event: dict) -> dict:
        inv_map = {value: key for key, value in _map.items()}
        return dict(map(lambda item: (inv_map.get(item[0], item[0]), item[1]), event.items()))


_map = {
    "lastModifiedDateTime": "last_modified_date_time",
    "startDateTime": "start_date_time",
    "endDateTime": "end_date_time",
    "organizer": "organizer",
    "displayName": "display_name",
    "businessPhones": "business_phones",
    "mobilePhone": "mobile_phone",
    "surname": "surname",
    "givenName": "given_name",
    "mailNickname": "mail_nickname",
    "userPrincipalName": "user_principal_name",
    "notificationUrl": "notification_url",
    "changeType": "change_type",
    "expirationDateTime": "expiration_date_time",
    "resourceData": "resource_data",
    "subscriptionExpirationDateTime": "subscription_expiration_date_time",
    "clientState": "client_state",
    "tenantId": "tenant_id",
    "subscriptionId": "subscription_id",
    "organizer.user": "organizer.user",
    "organizer.user.id": "organizer.user.id",
    "organizer.user.displayName": "organizer.user.display_name",
    "organizer.phone": "organizer.phone",
    "organizer.phone.id": "organizer.phone.id",
    "organizer.phone.displayName": "organizer.phone.display_name",
    "organizer.guest": "organizer.guest",
    "organizer.guest.id": "organizer.guest.id",
    "organizer.guest.displayName": "organizer.guest.display_name",
    "organizer.spoolUser": "organizer.splool_user",
    "organizer.acsUser": "organizer.acs_user",
    "organizer.encrypted": "organizer.encrypted",
    "organizer.onPremises": "organizer.on_premises",
    "organizer.acsApplicationInstance": "organizer.acs_application_instance",
    "organizer.spoolApplicationInstance": "organizer.spool_application_instance",
    "organizer.applicationInstance": "organizer.application_instance",
    "organizer.application": "organizer.application",
    "organizer.device": "organizer.device",
    "joinWebUrl": "join_web_url",
    "preferredLanguage": "preferred_language",
    "officeLocation": "office_location",
    "jobTitle": "job_title",
    "createdDateTime": "created_date_time",
    "isReminderOn": "is_reminder_on",
    "reminderMinutesBeforeStart": "reminder_minutes_before_start",
    "hasAttachments": "has_attachments",
    "webLink": "web_link",
    "start.dateTime": "start.date_time",
    "start.timeZone": "start.time_zone",
    "end.dateTime": "end.date_time",
    "end.timeZone": "end.time_zone",
    "location.displayName": "location.display_name",
    "location.locationUri": "location.location_uri",
    "location.locationType": "location.location_type",
    "location.uniqueId": "location.unique_id",
    "location.uniqueIdType": "location.unique_id_type",
    "location.address.type": "location.address.type",
    "location.address.street": "location.address.street",
    "location.address.city": "location.address.city",
    "location.address.postalCode": "location.address.postal_code",
    "location.address.countryOrRegion": "location.address.country_or_region",
    "recurrence.pattern.daysOfWeek": "recurrence.pattern.days_of_week",
    "recurrence.pattern.dayOfMonth": "recurrence.pattern.day_of_month",
    "recurrence.pattern.firstDayOfWeek": "recurrence.pattern.first_day_of_week",
    "recurrence.range.recurrenceTimeZone": "recurrence.range.recurrence_time_zone",
    "recurrence.range.numberOfOccurrences": "recurrence.range.number_of_occurrences",
    "recurrence.range.startDate": "recurrence.range.start_date",
    "recurrence.range.endDate": "recurrence.range.end_date",
    "organizer.emailAddress.name": "organizer.email_address.name",
    "organizer.emailAddress.address": "organizer.email_address.address",
    "responseStatus.response": "response_status.response",
    "responseStatus.time": "response_status.time",
    "attendees": "attendees",
    "@odata.context": "odata_context",
    "@odata.etag": "odata_etag",
    "applicationId": "application_id",
    "includeResourceData": "include_resource_data",
    "latestSupportedTlsVersion": "latest_supported_tls_version",
    "encryptionCertificate": "encryption_certificate",
    "encryptionCertificateId": "encryption_certificate_id",
    "notificationQueryOptions": "notification_query_options",
    "notificationContentType": "notification_content_type",
    "lifecycleNotificationUrl": "lifecycle_notification_url",
    "creatorId": "creator_id",
    "isDefaultCalendar": "is_default_calendar",
    "hexColor": "hex_color",
    "changeKey": "change_key",
    "canShare": "can_share",
    "canViewPrivateItems": "can_view_private_items",
    "isShared": "is_shared",
    "isSharedWithMe": "is_shared_with_me",
    "canEdit": "can_edit",
    "allowedOnlineMeetingProviders": "allowed_online_meeting_providers",
    "defaultOnlineMeetingProvider": "default_online_meeting_provider",
    "isTallyingResponses": "is_tallying_responses",
    "isRemovable": "is_removable",
    "teamsForBusiness": "teams_for_business",
    "transactionId": "transaction_id",
    "originalStartTimeZone": "original_start_time_zone",
    "originalEndTimeZone": "original_end_time_zone",
    "bodyPreview": "body_preview",
    "isAllDay": "is_all_day",
    "isCancelled": "is_cancelled",
    "isOrganizer": "is_organizer",
    "responseRequested": "response_requested",
    "seriesMasterId": "series_master_id",
    "showAs": "show_as",
    "onlineMeeting": "online_meeting",
    "onlineMeetingUrl": "online_meeting_url",
    "isOnlineMeeting": "is_online_meeting",
    "onlineMeetingProvider": "online_meeting_provider",
    "allowNewTimeProposals": "allow_new_time_proposals",
    "occurrenceId": "occurrence_id",
    "isDraft": "is_draft",
    "hideAttendees": "hide_attendees",
    "responseStatus": "response_status",
    "appId": "app_id",
    "passwordCredentials": "password_credentials",
    "iCalUId": "uid",
    "id": "id",
    "body.contentType": "body.content_type",
}


def parse(_dict: dict, scalar_value: bool = False):
    data = None
    try:
        if scalar_value:
            df = pd.DataFrame(_dict, index=[0])
        else:
            df = pd.DataFrame(_dict)
    except ValueError:
        _dict = pd.json_normalize(_dict)
        df = pd.DataFrame(_dict)
    df = df.rename(columns=_map)
    data = df.to_dict("records")
    return data
