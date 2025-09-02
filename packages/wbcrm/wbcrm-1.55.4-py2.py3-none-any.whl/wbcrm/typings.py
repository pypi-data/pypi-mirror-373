import enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from psycopg.types.range import TimestamptzRange
from wbcore.contrib.agenda.typings import ConferenceRoom
from wbcore.contrib.directory.typings import Person


@dataclass
class User:
    metadata: dict[str, Any]
    id: str = None

    def __eq__(self, other):
        if other:
            return self.id == other.id
        return super().__eq__(other)


@dataclass
class ParticipantStatus:
    class ParticipationStatus(enum.Enum):
        CANCELLED = "CANCELLED"
        MAYBE = "MAYBE"
        ATTENDS = "ATTENDS"
        NOTRESPONDED = "NOTRESPONDED"
        ATTENDS_DIGITALLY = "ATTENDS_DIGITALLY"
        PENDING_INVITATION = "PENDING_INVITATION"

    person: Person
    status_changed: datetime = None
    status: str = ParticipationStatus.PENDING_INVITATION.name
    activity: "Activity" = None
    id: str = None

    def __eq__(self, other):
        if other and (
            (self.id and other.id and self.id == other.id)
            or (self.person == other.person and self.activity == other.activity)
        ):
            return True
        return super().__eq__(other)


@dataclass
class Activity:
    class ReoccuranceChoice(enum.Enum):
        NEVER = "NEVER"
        BUSINESS_DAILY = "RRULE:FREQ=DAILY;INTERVAL=1;WKST=MO;BYDAY=MO,TU,WE,TH,FR"
        DAILY = "RRULE:FREQ=DAILY"
        WEEKLY = "RRULE:FREQ=WEEKLY"
        BIWEEKLY = "RRULE:FREQ=WEEKLY;INTERVAL=2"
        MONTHLY = "RRULE:FREQ=MONTHLY"
        QUARTERLY = "RRULE:FREQ=MONTHLY;INTERVAL=3"
        YEARLY = "RRULE:FREQ=YEARLY"

    class Visibility(enum.Enum):
        PUBLIC = "PUBLIC"
        PRIVATE = "PRIVATE"
        CONFIDENTIAL = "CONFIDENTIAL"

    class ReminderChoice(enum.Enum):
        NEVER = "NEVER"
        EVENT_TIME = "EVENT_TIME"
        MINUTES_5 = "MINUTES_5"
        MINUTES_15 = "MINUTES_15"
        MINUTES_30 = "MINUTES_30"
        HOURS_1 = "HOURS_1"
        HOURS_2 = "HOURS_2"
        HOURS_12 = "HOURS_12"
        WEEKS_1 = "WEEKS_1"

    @property
    def is_recurrent(self):
        return self.repeat_choice != self.ReoccuranceChoice.NEVER.name

    metadata: dict[str, Any]
    title: str
    period: TimestamptzRange = None
    description: str = ""
    participants: list["ParticipantStatus"] = field(default_factory=list)
    creator: Person = None
    visibility: str = Visibility.PUBLIC
    reminder_choice: str = ReminderChoice.MINUTES_15.name
    is_cancelled: bool = False
    all_day: bool = False
    online_meeting: bool = False
    location: str = None
    conference_room: ConferenceRoom = None
    id: str = None

    # parent_occurrence: "Activity" = None
    recurring_activities: list["Activity"] = field(default_factory=list)
    invalid_recurring_activities: list["Activity"] = field(default_factory=list)
    is_root: bool = False
    is_leaf: bool = False
    exclude_from_propagation: bool = False
    propagate_for_all_children: bool = False
    recurrence_end: datetime = None
    recurrence_count: int = 0
    repeat_choice: str = ReoccuranceChoice.NEVER.name
    delete_notification: bool = False

    def __eq__(self, other):
        if other and (self.id and other.id and self.id == other.id):
            return True
        return super().__eq__(other)
