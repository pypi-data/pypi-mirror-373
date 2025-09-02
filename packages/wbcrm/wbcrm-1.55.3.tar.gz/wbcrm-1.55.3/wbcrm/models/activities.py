import zoneinfo
from contextlib import suppress
from datetime import date, datetime, timedelta
from typing import Any

import arrow
import numpy as np
from celery import shared_task
from dateutil.rrule import rrulestr
from django.conf import settings
from django.db import models, transaction
from django.db.models import Exists, OuterRef, Q
from django.db.models.query import QuerySet
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext, pgettext_lazy
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from dynamic_preferences.registries import global_preferences_registry
from ics.alarm import DisplayAlarm
from psycopg.types.range import TimestamptzRange
from slugify import slugify
from wbcore.contrib import workflow
from wbcore.contrib.agenda.models import CalendarItem
from wbcore.contrib.agenda.signals import draggable_calendar_item_ids
from wbcore.contrib.ai.llm.decorators import llm
from wbcore.contrib.color.enums import WBColor
from wbcore.contrib.directory.models import (
    Company,
    EmployerEmployeeRelationship,
    Entry,
    Person,
)
from wbcore.contrib.directory.preferences import get_main_company
from wbcore.contrib.icons import WBIcon
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.enums import RequestType
from wbcore.metadata.configs.buttons import ActionButton
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)
from wbcore.models import WBModel
from wbcore.utils.models import (
    CalendarItemTypeMixin,
    ComplexToStringMixin,
    DefaultMixin,
)

from wbcrm.models.llm.activity_summaries import analyze_activity
from wbcrm.models.recurrence import Recurrence
from wbcrm.synchronization.activity.shortcuts import get_backend
from wbcrm.typings import Activity as ActivityDTO
from wbcrm.typings import ParticipantStatus as ParticipantStatusDTO


class DisplayAlarm2(DisplayAlarm):
    def __hash__(self):
        return hash(repr(self))


class ActivityType(DefaultMixin, CalendarItemTypeMixin, WBModel):
    class Score(models.TextChoices):
        HIGH = "4.0"
        MEDIUM = "3.0"
        LOW = "2.0"
        NONE = "0.0"
        MAX = "9.0"

    title = models.CharField(
        max_length=128,
        verbose_name=_("Title"),
        unique=True,
        blank=False,
        null=False,
    )

    slugify_title = models.CharField(
        max_length=128,
        unique=True,
        verbose_name="Slugified Title",
        blank=True,
        null=True,
    )

    score = models.CharField(
        max_length=8,
        verbose_name=_("Activity Heat Multiplier"),
        choices=Score.choices[:4],
        default=Score.LOW.value,
        unique=False,
        blank=False,
        null=False,
        help_text=_(
            "Used for the activity heat calculation. Multipliers range from low (i.e. e-mail) to medium (i.e. call) and high (i.e. meeting)."
        ),
    )

    @classmethod
    def get_endpoint_basename(cls):
        return "wbcrm:activitytype"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbcrm:activitytyperepresentation-list"

    @classmethod
    def get_representation_label_key(cls):
        return "{{title}}"

    def __str__(self) -> str:
        return f"{self.title}"

    @classmethod
    def get_default_activity_type(cls):
        with suppress(cls.DoesNotExist):
            return cls.objects.get(default=True)

    class Meta:
        verbose_name = _("Activity Type")
        verbose_name_plural = _("Activity Types")

    def save(self, *args, **kwargs):
        self.slugify_title = slugify(self.title, separator=" ")
        super().save(*args, **kwargs)


@receiver(post_save, sender=ActivityType)
def trigger_activity_save(sender, instance: ActivityType, created: bool, raw: bool, **kwargs):
    """
    We need to trigger all activities' save methods to update their color and icon
    """

    if not raw:
        for activity in instance.activity.all():
            activity.save()


def has_permissions(instance, user):  # type: ignore
    if user.has_perm("wbcrm.change_activity"):
        if instance.visibility == CalendarItem.Visibility.PRIVATE:
            return instance.is_private_for_user(user)
        elif instance.visibility == CalendarItem.Visibility.CONFIDENTIAL:
            return instance.is_confidential_for_user(user)
        else:
            return True
    else:
        return False


@llm([analyze_activity])
@workflow.register(serializer_class="wbcrm.serializers.ActivityModelSerializer")
class Activity(Recurrence):
    summary = models.TextField(default="", blank=True, verbose_name=_("LLM Summary"))
    heat = models.PositiveIntegerField(null=True, blank=True)
    online_meeting = models.BooleanField(
        default=False,
        verbose_name=_("Online Meeting"),
        help_text=_("Check this if it happens online"),
    )

    class Status(models.TextChoices):
        CANCELLED = "CANCELLED", _("Cancelled")
        PLANNED = "PLANNED", _("Planned")
        FINISHED = "FINISHED", _("Finished")
        REVIEWED = "REVIEWED", _("Reviewed")

        @classmethod
        def get_color_map(cls):
            colors = [
                WBColor.RED_LIGHT.value,
                WBColor.YELLOW_LIGHT.value,
                WBColor.BLUE_LIGHT.value,
                WBColor.GREEN_LIGHT.value,
            ]
            return [choice for choice in zip(cls, colors)]

    class Importance(models.TextChoices):
        LOW = "LOW", _("Low")
        MEDIUM = "MEDIUM", _("Medium")
        HIGH = "HIGH", _("High")

    class ReminderChoice(models.TextChoices):
        NEVER = "NEVER", _("Never")
        EVENT_TIME = "EVENT_TIME", _("At time of event")
        MINUTES_5 = "MINUTES_5", _("5 minutes before")
        MINUTES_15 = "MINUTES_15", _("15 minutes before")
        MINUTES_30 = "MINUTES_30", _("30 minutes before")
        HOURS_1 = "HOURS_1", _("1 hour before")
        HOURS_2 = "HOURS_2", _("2 hour before")
        HOURS_12 = "HOURS_12", _("12 hour before")
        WEEKS_1 = "WEEKS_1", _("1 week before")

        @classmethod
        def get_minutes_correspondance(cls, name):
            _map = {
                "NEVER": -1,
                "EVENT_TIME": 0,
                "MINUTES_5": 5,
                "MINUTES_15": 15,
                "MINUTES_30": 30,
                "HOURS_1": 60,
                "HOURS_2": 120,
                "HOURS_12": 720,
                "WEEKS_1": 10080,
            }

            return _map[name]

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")
        notification_types = [
            create_notification_type(
                "wbcrm.activity.participant",
                gettext("Activity Participant"),
                gettext("User notification when addeded to an activity."),
            ),
            create_notification_type(
                "wbcrm.activity.reminder",
                gettext("Activity Reminder"),
                gettext("Sends a reminder that an activity is starting soon."),
            ),
            create_notification_type(
                "wbcrm.activity.finished",
                gettext("Finished Activity"),
                gettext("Notifies a user of a finished activity that can be reviewed."),
            ),
            create_notification_type(
                "wbcrm.activity.daily_summary",
                gettext("Daily Summary"),
                gettext("Sends out a daily summary of a user's upcoming day."),
                web=False,
                mobile=False,
                email=True,
                is_lock=True,
            ),
            create_notification_type(
                "wbcrm.activity_sync.admin",
                gettext("Activity Sync Irregularities"),
                gettext("Admin notification to inform about irregularities of the activity sync."),
            ),
        ]

    status = FSMField(default=Status.PLANNED, choices=Status.choices, verbose_name=_("Status"))

    @transition(
        field=status,
        source=[Status.PLANNED],
        target=Status.FINISHED,
        permission=has_permissions,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcrm:activity",),
                icon=WBIcon.CONFIRM.icon,
                key="finish",
                label=_("Finish"),
                action_label=_("Finish"),
                description_fields=_("Are you sure you want to finish this activity?"),
            )
        },
    )
    def finish(self, by=None, description=None, **kwargs):
        self.cancel_recurrence()

    def can_finish(self):
        errors = dict()

        if not self.period:
            errors["period"] = [_("In this status this has to be provided.")]

        return errors

    @transition(
        field=status,
        source=[Status.PLANNED, Status.FINISHED],
        target=Status.REVIEWED,
        permission=has_permissions,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcrm:activity",),
                icon=WBIcon.REVIEW.icon,
                key="review",
                label=pgettext_lazy("Transition button label for Reviews", "Review"),
                action_label=pgettext_lazy("Transition action label for Reviews", "Review"),
                description_fields="",
                instance_display=create_simple_display([["result"], ["participants"], ["companies"]]),
            )
        },
    )
    def review(self, by=None, description=None, **kwargs):
        self.cancel_recurrence()

    def can_review(self):
        errors = self.can_finish()
        if not self.result or self.result == "" or self.result == "<p></p>":
            errors["result"] = [_("When reviewing an activity a result has to be provided!")]

        missing = self._check_employer_employees_entered()

        if missing_companies := missing.get("missing_companies_by_participant", None):
            participants_with_missing_companies = [participant.computed_str for participant in missing_companies]
            errors["companies"] = [
                _(
                    "You need to enter an employer for: {persons}",
                ).format(persons=", ".join(participants_with_missing_companies))
            ]

        if missing_participants := missing.get("missing_participants_by_company", None):
            companies_with_missing_participants = [company.name for company in missing_participants]
            errors["participants"] = [
                _(
                    "You need to enter an employee for: {companies}",
                ).format(companies=", ".join(companies_with_missing_participants))
            ]
        return errors

    @transition(
        field=status,
        source=[Status.PLANNED],
        target=Status.CANCELLED,
        permission=has_permissions,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcrm:activity",),
                icon=WBIcon.REJECT.icon,
                key="cancel",
                label=_("Cancel"),
                action_label=_("Cancel"),
                description_fields=_("Are you sure you want to cancel this activity?"),
            )
        },
    )
    def cancel(self, by=None, description=None, **kwargs):
        self.cancel_recurrence()

    description = models.TextField(default="", blank=True, verbose_name=_("Description"))
    result = models.TextField(default="", blank=True, verbose_name=_("Review"))
    type = models.ForeignKey(
        "wbcrm.ActivityType",
        related_name="activity",
        on_delete=models.PROTECT,
        verbose_name=_("Type"),
    )
    importance = models.CharField(
        max_length=16, default=Importance.LOW, choices=Importance.choices, verbose_name=_("Importance")
    )

    start = models.DateTimeField(blank=True, null=True, verbose_name=_("Start"))
    end = models.DateTimeField(blank=True, null=True, verbose_name=_("End"))

    reminder_choice = models.CharField(
        max_length=16,
        default=ReminderChoice.MINUTES_15,
        choices=ReminderChoice.choices,
        verbose_name=_("Reminder"),
        help_text=_(
            "Sends a mail and system notification to all participating internal employees before the start of the activity."
        ),
    )
    location = models.CharField(
        max_length=2048, null=True, blank=True, verbose_name=_("Location")
    )  # we increase the max lenght to 2048 to accomodate meeting URL (ICS and outlook uses the location field to share meeting link)
    location_longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Longitude")
    )
    location_latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Latitude")
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    creator = models.ForeignKey(
        "directory.Person",
        related_name="activities_owned",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Creator"),
        help_text=_("The creator of this activity"),
    )
    latest_reviewer = models.ForeignKey(
        "directory.Person",
        related_name="activities_reviewed",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Latest Reviewer"),
        help_text=_("The latest person to review the activity"),
    )
    reviewed_at = models.DateTimeField(verbose_name=_("Reviewed at"), null=True, blank=True)
    edited = models.DateTimeField(auto_now=True, verbose_name=_("Edited"))
    assigned_to = models.ForeignKey(
        "directory.Person",
        related_name="activities",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Assigned to"),
        help_text=_("The person in charge of handling this activity"),
    )
    companies = models.ManyToManyField(
        "directory.Company",
        related_name="company_participates",
        blank=True,
        verbose_name=_("Participating Companies"),
        help_text=_("The list of companies other than the main company that participate in this activity"),
        through="wbcrm.ActivityCompanyThroughModel",
        through_fields=("activity", "company"),
    )

    participants = models.ManyToManyField(
        "directory.Person",
        related_name="participates",
        blank=True,
        verbose_name=_("Participating Persons"),
        help_text=_("The list of participants"),
        through="wbcrm.ActivityParticipant",
        through_fields=("activity", "participant"),
    )

    groups = models.ManyToManyField(
        "wbcrm.Group",
        related_name="activities_for_group",
        blank=True,
        verbose_name=_("Groups"),
        help_text=_("Each member of the group will be added to the list of participants and companies automatically."),
    )
    preceded_by = models.ForeignKey(
        "self",
        related_name="followed_by",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Preceded by"),
        help_text=_("The preceding activity"),
    )
    disable_participant_check = models.BooleanField(
        default=False,
        verbose_name=_("Without Participating Company"),
    )
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return "%s" % (self.title,)

    def is_private_for_user(self, user) -> bool:
        return (
            self.visibility == CalendarItem.Visibility.PRIVATE
            and user.profile not in self.participants.all()
            and user.profile != self.assigned_to
            and user.profile != self.creator
        )

    def is_confidential_for_user(self, user) -> bool:
        return (
            self.visibility == CalendarItem.Visibility.CONFIDENTIAL
            and not CalendarItem.has_user_administrate_permission(user)
        )

    def get_extra_ics_kwargs(self) -> dict[str, Any]:
        res = {}
        res["created"] = arrow.get(self.created)
        if self.location:
            res["location"] = "".join(self.location)
        if self.description:
            res["description"] = self.description
        if self.period and self.reminder_choice:
            reminder = self.period.lower - timedelta(
                minutes=Activity.ReminderChoice.get_minutes_correspondance(self.reminder_choice)
            )
            a = DisplayAlarm2(trigger=reminder)
            res["alarms"] = set([a])
        return res

    def get_color(self) -> str:
        return self.type.color

    def get_icon(self) -> str:
        return self.type.icon

    def save(self, synchronize: bool = True, *args, **kwargs):
        pre_save_activity_dto = (
            Activity.all_objects.get(id=self.id)._build_dto() if self.id else None
        )  # we need to refetch to pre save activity from the database because self already contains the updated fields

        # Set reviewed
        if (
            self.status not in [Activity.Status.REVIEWED, Activity.Status.CANCELLED]
            and self.result
            and self.result not in ["<p></p>", ""]
        ):
            self.status = Activity.Status.REVIEWED

        if not self.period and self.start and self.end:
            if self.start == self.end:
                self.end = self.end + timedelta(seconds=1)
            self.period = TimestamptzRange(self.start, self.end)  # type: ignore

        if not (self.period or self.start or self.end):
            self.period = TimestamptzRange(timezone.now(), timezone.now() + timedelta(hours=1))

        if self.period:
            self.start, self.end = self.period.lower, self.period.upper  # type: ignore

        # If all day activity, we ensure period spans the full range
        if self.all_day and self.period:
            tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)

            self.period = TimestamptzRange(
                lower=self.period.lower.astimezone(tz).replace(hour=0, minute=0, second=0),
                upper=self.period.upper.astimezone(tz).replace(hour=23, minute=59, second=59),
            )  # type
        self.is_cancelled = self.status == self.Status.CANCELLED

        # Logic to be called after a save happens (e.g synchronization). We get the activity DTO before saving that we passed around in the signal
        super().save(*args, **kwargs)

        if synchronize and self.is_active:
            if not self.is_recurrent or not (
                self.is_recurrent
                and self.parent_occurrence
                and (self.parent_occurrence.propagate_for_all_children or not pre_save_activity_dto)
            ):
                # countdown of at least 20 seconds is necessary to get m2m
                post_save_callback.apply_async(
                    (self.id,), {"pre_save_activity_dto": pre_save_activity_dto}, countdown=20
                )

        if not self.type:
            self.type = ActivityType.get_default_activity_type()

    def delete(self, synchronize: bool = True, **kwargs):
        # Logic to be called after a deletion happens (e.g synchronization). We get the activity DTO before deletion that we passed around in the signal
        if synchronize and Activity.objects.filter(id=self.id).exists():
            pre_delete_activity_dto = Activity.objects.get(id=self.id)._build_dto()
            super().delete(**kwargs)
            post_delete_callback.apply_async(
                (self.id,), {"pre_delete_activity_dto": pre_delete_activity_dto}, countdown=1
            )
        else:
            super().delete(**kwargs)

    def get_participants(self) -> QuerySet[Person]:
        """
        Get all participants for that activity.

        Returns:
            Queryset<Person> The participants
        """
        return Person.objects.filter(Q(participates__id=self.id)).distinct()

    def get_companies(self):
        """
        Get all companies for that activity.

        Returns:
            Queryset<Company> The companies participating in the activity
        """
        return Company.objects.filter(Q(company_participates__id=self.id)).distinct()

    def _check_employer_employees_entered(self) -> dict:
        if not self.disable_participant_check:
            participants = self.participants.all()
            companies = self.companies.all()

            missing_employers_for_participant = set()
            missing_employees_for_company = set()

            for participant in participants.exclude(
                Q(id__in=Person.objects.filter_only_internal()) | Q(employers__isnull=True)
            ):
                if not participant.employers.filter(id__in=companies).exists():
                    missing_employers_for_participant.add(participant)

            for company in companies.exclude(employees__isnull=True):
                if not company.employees.filter(id__in=participants).exists():
                    missing_employees_for_company.add(company)

            return {
                "missing_employers_for_participant": missing_employers_for_participant,
                "missing_employees_for_company": missing_employees_for_company,
            }
        return {}

    def participants_company_check_message(self) -> str:
        """Checks if the companies and participants fields have been filled in correctly.
            A warning is generated if employees or employers are missing in the corresponding field.

        Returns:
            str: The warning string
        """

        missing = self._check_employer_employees_entered()
        message = ""

        if missing.get("missing_employers_for_participant"):
            participants_with_missing_companies = [
                participant.computed_str for participant in missing["missing_employers_for_participant"]
            ]
            message += _("For the following participants you did not supply an employer: {persons}<br />").format(
                persons=", ".join(participants_with_missing_companies)
            )

        if missing.get("missing_employees_for_company"):
            companies_with_missing_participants = [
                company.computed_str for company in missing["missing_employees_for_company"]
            ]
            message += _("For the following companies you did not supply an employee: {companies}<br />").format(
                companies=", ".join(companies_with_missing_participants)
            )

        return message

    def get_occurrance_dates(self) -> list:
        """
        Returns a list with datetime values based on the recurrence options of an activity.

        :return:    list with datetime values
        :rtype:     list
        """

        occurrance_dates = []
        # dd = self.start.date()
        if not self.period:
            raise AttributeError(_("Period needs to be set for recurrence to work!"))
        dd = self.period.lower.date()
        # weekday = calendar.day_abbr[dd.weekday()].upper()[:2]
        # weekday_position = (dd.day + 6) // 7
        # weekdaycounters = collections.Counter(
        #     [calendar.weekday(dd.year, dd.month, d) for d in range(1, calendar.monthrange(dd.year, dd.month)[1] + 1)]
        # )
        # total_number_of_weekday = weekdaycounters[dd.weekday()]
        repeat_rule = self.repeat_choice
        # if self.repeat_choice == Recurrence.ReoccuranceChoice.MONTHLY_WEEKDAY:
        #     repeat_rule = f"RRULE:FREQ=MONTHLY;BYDAY={weekday};BYSETPOS={weekday_position}"
        # elif self.repeat_choice == Recurrence.ReoccuranceChoice.MONTHLY_LASTWEEKDAY:
        #     repeat_rule = (
        #         f"RRULE:FREQ=MONTHLY;BYDAY={weekday};BYSETPOS={weekday_position - total_number_of_weekday - 1}"
        #     )
        end_date = (
            self.recurrence_end + timedelta(days=1)
            if self.recurrence_end
            else global_preferences_registry.manager()["wbcrm__recurrence_activity_end_date"]
        )
        dstart = datetime.combine(dd, self.start.astimezone().time())
        if self.recurrence_count:
            occurrance_dates = list(rrulestr(repeat_rule + f";COUNT={self.recurrence_count+1}", dtstart=dstart))[1:]
        else:
            occurrance_dates = list(
                rrulestr(
                    repeat_rule + f";UNTIL={end_date.strftime('%Y%m%d')}",
                    dtstart=dstart.replace(tzinfo=None),
                )
            )[1:]

        return occurrance_dates

    def update_last_event(self):
        """
        Updates the entries last activity
        """

        activities = (
            Activity.objects.filter(visibility=CalendarItem.Visibility.PUBLIC)
            .filter(Q(companies__id=self.id) | Q(participants__id=self.id))
            .filter(
                (
                    Q(period__endswith__lt=timezone.now())
                    & Q(status__in=[Activity.Status.FINISHED, Activity.Status.REVIEWED])
                )
                | Q(status=Activity.Status.REVIEWED)
            )
        )
        if activities.exists() and (last_event := activities.latest("period__endswith")):
            self.last_event_id = last_event.id
            self.save()

    def get_participants_for_employer(self, employer: Entry) -> QuerySet[Person]:
        rels = (
            ActivityParticipant.objects.filter(activity=self)
            .annotate(
                is_employee=Exists(
                    EmployerEmployeeRelationship.objects.filter(
                        employee=OuterRef("participant"), employer=employer, primary=True
                    )
                )
            )
            .filter(is_employee=True)
        )
        return Person.objects.filter(id__in=rels.values("participant"))

    @staticmethod
    def get_inrange_activities(
        queryset: QuerySet["Activity"], start_date: date, end_date: date
    ) -> QuerySet["Activity"]:
        """
        Returns all activities taking place during the given interval. Accounts for the recurring activities as well.

        Args:
            queryset (Queryset[Activity]): The base queryset
            start_date (date): The starting point of the interval
            end_date (date): The end point of the interval

        Returns:
            queryset (Queryset[Activity]): A queryset of all activities with occurrences in the specified period
        """
        interval = TimestamptzRange(start_date, end_date)  # type: ignore
        return queryset.filter(period__overlap=interval)

    @staticmethod
    def get_companies_activities(queryset, value):
        """
        Return the activities whose companies are value.

        Arguments:
            queryset {Queryset<Activity>} -- The base queryset
            value {list<Entry>} -- A list of entries considered as companies
        Returns:
            queryset {Queryset<Activity>} -- A queryset whose companies includes value
        """
        return queryset.filter(companies__in=value).distinct()

    @classmethod
    def get_activities_for_user(cls, user, base_qs=None):
        if base_qs is None:
            base_qs = Activity.objects
        if user.is_superuser or user.profile.is_internal:
            queryset = base_qs.all()
        else:
            queryset = base_qs.filter(
                Q(creator=user.profile)
                | Q(assigned_to=user.profile)
                | Q(activity_participants__participant_id=user.profile.id)
                | Q(activity_participants__participant__in=user.profile.clients.all())
                | Q(companies__in=user.profile.clients.all())
            )

        return queryset.distinct()

    # Overriden Function from the recurrence framework
    def _handle_recurrence_m2m_forwarding(self, child):
        child.groups.set(self.groups.union(child.groups.all()))
        child.participants.set(self.participants.union(child.participants.all()))
        child.companies.set(self.companies.union(child.companies.all()))

    def does_recurrence_need_cancellation(self):
        return self.status in [
            Activity.Status.FINISHED,
            Activity.Status.REVIEWED,
            Activity.Status.CANCELLED,
        ]

    def get_recurrent_valid_children(self):
        return super().get_recurrent_valid_children().filter(status=Activity.Status.PLANNED)

    def _create_recurrence_child(self, start_datetime: datetime):
        child = Activity(
            assigned_to=self.assigned_to,
            all_day=self.all_day,
            conference_room=self.conference_room,
            creator=self.creator,
            description=self.description,
            disable_participant_check=self.disable_participant_check,
            importance=self.importance,
            visibility=self.visibility,
            location=self.location,
            location_longitude=self.location_longitude,
            location_latitude=self.location_latitude,
            parent_occurrence=self,
            period=TimestamptzRange(start_datetime, (start_datetime + self.duration)),
            recurrence_end=self.recurrence_end,
            recurrence_count=self.recurrence_count,
            reminder_choice=self.reminder_choice,
            repeat_choice=self.repeat_choice,
            title=self.title,
            type=self.type,
        )
        child.save(synchronize=False)
        return child

    def _build_dto(self):
        return ActivityDTO(
            metadata=self.metadata,
            title=self.title,
            period=self.period,
            description=self.description,
            participants=[
                ParticipantStatusDTO(
                    status=rel.participation_status,
                    status_changed=rel.status_changed,
                    person=rel.participant._build_dto(),
                )
                for rel in self.activity_participants.all()
            ],
            creator=self.creator._build_dto() if self.creator else None,
            visibility=self.visibility,
            reminder_choice=self.reminder_choice,
            is_cancelled=self.is_cancelled,
            all_day=self.all_day,
            online_meeting=self.online_meeting,
            location=self.location,
            conference_room=self.conference_room._build_dto() if self.conference_room else None,
            id=self.id,
            # parent_occurrence=self.parent_occurrence,
            # recurring_activities=self.get_recurrent_valid_children(),
            # invalid_recurring_activities=self.get_recurrent_invalid_children(),
            is_root=self.is_root,
            is_leaf=self.is_leaf,
            propagate_for_all_children=self.propagate_for_all_children,
            recurrence_end=self.recurrence_end,
            recurrence_count=self.recurrence_count,
            repeat_choice=self.repeat_choice,
        )

    @classmethod
    def get_endpoint_basename(cls):
        return "wbcrm:activity"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbcrm:activityrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{title}}"


@receiver(m2m_changed, sender=Activity.participants.through)
def m2m_changed_participants(sender, instance: Activity, action: str, pk_set: set[int], **kwargs):
    """
    Handle the post custom logic when adding a participant. In that case, we call the relationship save method because we define a through model
    """
    if action in ["post_add", "pre_remove", "pre_clear"]:
        for participant_id in pk_set:
            rel = ActivityParticipant.objects.get(activity=instance, participant=participant_id)
            if action == "post_add":
                rel.save()
                if not instance.parent_occurrence:
                    send_employee_notification.delay(instance.id, participant_id)
            else:
                rel.delete()


@receiver(m2m_changed, sender=Activity.companies.through)
def m2m_changed_companies(sender, instance: Activity, action: str, pk_set: set[int], **kwargs):
    """
    Send a notification whenever a user who did not create the activity is added as a participant.
    """
    if pk_set:
        if "add" in action:
            if (main_company := get_main_company()) and main_company.id in pk_set:
                pk_set.remove(main_company.id)
        if "post" in action:
            for company_id in pk_set:
                entry = Entry.all_objects.get(id=company_id)
                if action == "post_add":
                    instance.entities.add(entry)
                elif not instance.get_participants_for_employer(entry).exists():
                    instance.entities.remove(entry)
        if action == "post_add":
            for company_id in pk_set:
                with suppress(
                    ActivityCompanyThroughModel.DoesNotExist
                ):  # we save to trigger the computed str computation. I don't know of any other choice as django only allow bulk create on m2m insertion
                    ActivityCompanyThroughModel.objects.get(
                        company_id=company_id,
                        activity=instance,
                    ).save()


@receiver(m2m_changed, sender=Activity.groups.through)  # type: ignore
def m2m_changed_groups(sender, instance: Activity, action, pk_set, **kwargs):
    from wbcrm.models.groups import Group

    if action == "post_add" or action == "post_remove" and pk_set:
        instance_participants = instance.participants.all()
        instance_companies = instance.companies.all()
        edited_groups = Group.objects.filter(id__in=pk_set)
        edited_groups_members = edited_groups.values_list("members__id", flat=True)
        edited_persons = Person.objects.filter(id__in=edited_groups_members)
        edited_companies = Company.objects.filter(id__in=edited_groups_members)

        if action == "post_add":
            instance.participants.set(instance_participants.union(edited_persons))
            instance.companies.set(instance_companies.union(edited_companies))
        else:
            # Get group members who are members in groups that are to be removed and are also members in groups that remain in the instance.
            # These group members are not to be removed from the instance.
            remaining_groups_members = instance.groups.exclude(id__in=pk_set).values_list("members__id", flat=True)
            members_in_different_groups = np.intersect1d(edited_groups_members, remaining_groups_members)  # type: ignore

            instance.participants.set(
                instance_participants.difference(edited_persons.exclude(id__in=members_in_different_groups))
            )
            instance.companies.set(
                instance_companies.difference(edited_companies.exclude(id__in=members_in_different_groups))
            )


@shared_task()
def post_save_callback(activity_id: int, pre_save_activity_dto: ActivityDTO = None):
    with suppress(Activity.DoesNotExist):
        activity = Activity.all_objects.get(id=activity_id)
        # Set calendar item entities once all activity m2m relations are settled
        activity_dto = activity._build_dto()

        if activity.is_recurrent:
            if activity.is_root and not pre_save_activity_dto:  # create the recurring activities.
                activity.generate_occurrences()
            elif activity.propagate_for_all_children:  # update occurrences from activity
                period_time_changed = False
                if (
                    activity_dto.period.lower.time() != pre_save_activity_dto.period.lower.time()
                    or activity_dto.period.upper.time() != pre_save_activity_dto.period.upper.time()
                ):
                    period_time_changed = True
                activity.forward_change(period_time_changed=period_time_changed)

            activity_dto.recurring_activities = [
                instance._build_dto() for instance in activity.get_recurrent_valid_children()
            ]
            activity_dto.invalid_recurring_activities = [
                instance._build_dto() for instance in activity.get_recurrent_invalid_children()
            ]

        if controller := get_backend():
            controller.handle_outbound(activity_dto, old_activity_dto=pre_save_activity_dto)


@shared_task()
def post_delete_callback(activity_id: int, pre_delete_activity_dto: ActivityDTO):
    if controller := get_backend():
        with suppress(Activity.DoesNotExist):
            activity_dto = Activity.all_objects.get(id=activity_id)._build_dto()
            controller.handle_outbound(activity_dto, old_activity_dto=pre_delete_activity_dto, is_deleted=True)


@shared_task
def send_employee_notification(activity_id: int, participant_id):
    """Sends all employees that were added to the activity as participants a notification via system and mail

    Args:
        activity_id: The activity instance id to which participants were added
        participant_id: id of the participant to send notification to
    """
    with suppress(Activity.DoesNotExist):
        activity = Activity.all_objects.get(id=activity_id)
        with suppress(Person.DoesNotExist):
            employee = Person.objects.filter_only_internal().get(id=participant_id)
            if activity.creator != employee:
                activity_type_label = activity.type.title.lower()
                description = (
                    activity.description if activity.description and activity.description != "<p></p>" else None
                )
                message = render_to_string(
                    "email/activity.html",
                    {
                        "participants": activity.participants.all(),
                        "type": activity_type_label,
                        "title": activity.title,
                        "start": activity.period.lower if activity.period else "",
                        "end": activity.period.upper if activity.period else "",
                        "description": description,
                    },
                )
                if activity.period:
                    start_datetime: datetime = activity.period.lower
                    datetime_string = _(" starting at the {} at {}").format(
                        start_datetime.strftime("%d.%m.%Y"), start_datetime.strftime("%H:%M:%S")
                    )
                else:
                    datetime_string = ""
                creator_string = (
                    _("{} added you").format(str(activity.creator))
                    if activity.creator
                    else _("You were automatically added")
                )

                send_notification(
                    code="wbcrm.activity.participant",
                    title=_("{} as participant in a {}{}").format(
                        creator_string, activity_type_label, datetime_string
                    ),
                    body=message,
                    user=employee.user_account,
                    reverse_name="wbcrm:activity-detail",
                    reverse_args=[activity.id],
                )


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#                                               >>> Activity Participants <<<
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


def is_participant(instance, user):
    return instance.participant == user.profile and instance.activity.period.lower >= timezone.now()


def conference_room_is_videoconference_capable(instance):
    return not instance.activity.conference_room or instance.activity.conference_room.is_videoconference_capable


class ActivityCompanyThroughModel(ComplexToStringMixin, models.Model):
    activity = models.ForeignKey(
        on_delete=models.CASCADE,
        to="wbcrm.Activity",
        verbose_name=_("Activity"),
        related_name="activity_companies",
    )
    company = models.ForeignKey(
        on_delete=models.CASCADE,
        to="directory.Company",
        verbose_name=_("Company"),
        related_name="activity_companies",
    )
    customer_status = models.ForeignKey(
        to="directory.CustomerStatus",
        related_name="activity_companies",
        on_delete=models.SET_NULL,
        verbose_name=_("Initial Customer Status"),
        help_text=_("The Customer Status at activity creation time"),
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        self.customer_status = self.company.customer_status
        super().save(*args, **kwargs)

    def compute_str(self):
        rep = self.company.computed_str
        if self.customer_status:
            rep += f" ({self.customer_status.title})"
        return rep


class ActivityParticipant(models.Model):
    class ParticipationStatus(models.TextChoices):
        CANCELLED = "CANCELLED", _("Cancelled")
        MAYBE = "MAYBE", _("Maybe")
        ATTENDS = "ATTENDS", _("Attends")
        NOTRESPONDED = "NOTRESPONDED", _("Not Responded")
        ATTENDS_DIGITALLY = "ATTENDS_DIGITALLY", _("Attends Digitally")
        PENDING_INVITATION = "PENDING_INVITATION", _("Pending Invitation")

    activity = models.ForeignKey(
        on_delete=models.CASCADE,
        to="wbcrm.Activity",
        verbose_name=_("Activity"),
        related_name="activity_participants",
    )
    participant = models.ForeignKey(
        on_delete=models.CASCADE,
        to="directory.Person",
        verbose_name=_("Participant"),
        related_name="activity_participants",
    )
    participation_status = FSMField(
        default=ParticipationStatus.PENDING_INVITATION,
        choices=ParticipationStatus.choices,
        verbose_name=_("Participation Status"),
    )
    status_changed = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return _("Status of {participant} for activity {title} is: {status}").format(
            participant=self.participant.computed_str,
            title=self.activity.title,
            status=self.ParticipationStatus[self.participation_status].label,
        )

    class Meta:
        constraints = [models.UniqueConstraint(name="unique_participant", fields=["activity", "participant"])]
        verbose_name = _("Activity's Participant")
        verbose_name_plural = _("Activities' Participants")

    def save(self, *args, **kwargs):
        self.activity.entities.add(self.participant)
        with suppress(EmployerEmployeeRelationship.DoesNotExist):
            rel = EmployerEmployeeRelationship.objects.get(employee=self.participant, primary=True)
            self.activity.companies.add(rel.employer)
        # Set the status 'Attends' by default for activity creator
        if self.activity.creator == self.participant:
            self.status = ActivityParticipant.ParticipationStatus.ATTENDS

        pre_save_participant_dto = ActivityParticipant.objects.get(id=self.id)._build_dto() if self.id else None
        # Logic to be called after a save happens (e.g synchronization). We get the activity Participant DTO before saving that we passed around in the signal
        super().save(*args, **kwargs)
        # we activate synchronization only if the rel was already created (we expect synchronization on the activity creation itself)
        post_save_participant_callback.apply_async(
            (self.id,), {"pre_save_participant_dto": pre_save_participant_dto}, countdown=10
        )

    def delete(self, *args, **kwargs):
        self.activity.entities.remove(self.participant.entry_ptr)
        with suppress(EmployerEmployeeRelationship.DoesNotExist):
            rel = EmployerEmployeeRelationship.objects.get(employee=self.participant, primary=True)
            # delete only if no other participants are of the same company
            if not self.activity.get_participants_for_employer(rel.employer).exclude(id=rel.employee.id).exists():
                self.activity.companies.remove(rel.employer)
                self.activity.entities.remove(rel.employer.entry_ptr)
        if self.activity.is_active:
            post_delete_participant_callback.apply_async((self.id,), countdown=10)
        super().delete(*args, **kwargs)

    def _build_dto(self):
        return ParticipantStatusDTO(
            person=self.participant._build_dto(),
            status_changed=self.status_changed,
            status=self.participation_status,
            activity=self.activity._build_dto(),
            id=self.id,
        )

    @transition(
        field=participation_status,
        source=[
            ParticipationStatus.PENDING_INVITATION,
            ParticipationStatus.NOTRESPONDED,
            ParticipationStatus.ATTENDS,
            ParticipationStatus.ATTENDS_DIGITALLY,
            ParticipationStatus.CANCELLED,
        ],
        target=ParticipationStatus.MAYBE,
        permission=is_participant,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcrm:activityparticipant",),
                icon=WBIcon.QUESTION.icon,
                key="maybe",
                label=_("Maybe"),
                action_label=_("Setting Maybe"),
            )
        },
    )
    def maybe(self, by=None, description=None, **kwargs):
        pass

    @transition(
        field=participation_status,
        source=[
            ParticipationStatus.PENDING_INVITATION,
            ParticipationStatus.NOTRESPONDED,
            ParticipationStatus.MAYBE,
            ParticipationStatus.ATTENDS_DIGITALLY,
            ParticipationStatus.CANCELLED,
        ],
        target=ParticipationStatus.ATTENDS,
        permission=is_participant,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcrm:activityparticipant",),
                icon=WBIcon.APPROVE.icon,
                key="attends",
                label=_("Accept"),
                action_label=_("Accepting"),
                description_fields=_("Are you sure you want to participate in this activity?"),
            )
        },
    )
    def attends(self, by=None, description=None, **kwargs):
        pass

    @transition(
        field=participation_status,
        source=[
            ParticipationStatus.PENDING_INVITATION,
            ParticipationStatus.NOTRESPONDED,
            ParticipationStatus.MAYBE,
            ParticipationStatus.ATTENDS,
            ParticipationStatus.CANCELLED,
        ],
        target=ParticipationStatus.ATTENDS_DIGITALLY,
        permission=is_participant,
        conditions=[conference_room_is_videoconference_capable],
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcrm:activityparticipant",),
                icon="laptop",
                key="attendsdigitally",
                label=_("Attend Digitally"),
                action_label=_("Setting Attendance"),
                description_fields=_("Are you sure you want to attend digitally in this activity?"),
            )
        },
    )
    def attendsdigitally(self, by=None, description=None, **kwargs):
        pass

    @transition(
        field=participation_status,
        source=[
            ParticipationStatus.PENDING_INVITATION,
            ParticipationStatus.NOTRESPONDED,
            ParticipationStatus.MAYBE,
            ParticipationStatus.ATTENDS,
            ParticipationStatus.ATTENDS_DIGITALLY,
        ],
        target=ParticipationStatus.CANCELLED,
        permission=is_participant,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcrm:activityparticipant",),
                icon=WBIcon.DENY.icon,
                key="cancelled",
                label=_("Decline"),
                action_label=_("Decline"),
                description_fields=_("Are you sure you want to decline to participate in this activity?"),
            )
        },
    )
    def cancelled(self, by=None, description=None, **kwargs):
        pass

    @transition(
        field=participation_status,
        source=ParticipationStatus.CANCELLED,
        target=ParticipationStatus.NOTRESPONDED,
        permission=lambda instance, user: instance.activity.creator == user.profile != instance.participant,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbcrm:activityparticipant",),
                icon=WBIcon.REDO.icon,
                key="notresponded",
                label=_("Resend Invitation"),
                action_label=_("Resending Invitation"),
                description_fields=_(
                    "Are you sure you want to send this person an invitation to participate in this activity again?"
                ),
            )
        },
    )
    def notresponded(self, by=None, description=None, **kwargs):
        pass

    @classmethod
    def get_representation_value_key(cls):
        return "id"


@receiver(post_save, sender=Activity)
def post_save_activity(sender, instance, created, raw, **kwargs):
    # need to the post save because instance might not be created yet in the save method
    if not raw and created:
        if instance.creator:
            instance.entities.add(instance.creator)
        if instance.assigned_to:
            instance.entities.add(instance.assigned_to)


@shared_task()
def post_save_participant_callback(
    activity_participant_id: int, pre_save_participant_dto: ParticipantStatusDTO = None
):
    if controller := get_backend():
        with suppress(ActivityParticipant.DoesNotExist):
            participant_dto = ActivityParticipant.objects.get(id=activity_participant_id)._build_dto()
            controller.handle_outbound_participant(participant_dto, old_participant_dto=pre_save_participant_dto)


@shared_task()
def post_delete_participant_callback(activity_participant_id: int):
    if controller := get_backend():
        with suppress(ActivityParticipant.DoesNotExist):
            participant_dto = ActivityParticipant.objects.get(id=activity_participant_id)._build_dto()
            controller.handle_outbound_participant(participant_dto, is_deleted=True)


@shared_task()
def send_invitation_participant_as_task(activity_id: int):
    if controller := get_backend():
        with suppress(Activity.DoesNotExist):
            activity_dto = Activity.all_objects.get(id=activity_id)._build_dto()
            participants_dto = [
                participant._build_dto()
                for participant in ActivityParticipant.objects.filter(
                    activity_id=activity_id,
                    participation_status=ActivityParticipant.ParticipationStatus.PENDING_INVITATION,
                )
            ]
            controller.handle_outbound_external_participants(activity_dto, participants_dto)


@receiver(draggable_calendar_item_ids, sender="agenda.CalendarItem")
def activity_draggable_calendar_item_ids(sender, request, **kwargs) -> QuerySet[CalendarItem]:
    return Activity.objects.filter(
        (Q(creator=request.user.profile) | Q(assigned_to=request.user.profile)) & Q(status=Activity.Status.PLANNED)
    ).values("id")


@receiver(post_save, sender=EmployerEmployeeRelationship)
def post_save_eer(sender, instance: EmployerEmployeeRelationship, created, raw, **kwargs):
    """
    Post save EER signal: Triggers the post_save signals of the employee which updates his computed_str and adds the
    employer to future planned activities if it became the only employer
    """

    if not raw and created and sender.objects.filter(employee=instance.employee, primary=True).count() == 1:
        transaction.on_commit(lambda: add_employer_to_activities.delay(instance.pk))


@receiver(post_delete, sender=EmployerEmployeeRelationship)
def post_delete_eer(sender, instance: EmployerEmployeeRelationship, **kwargs):
    """
    Post delete EER signal: Triggers the post_delete signals of the employee which updates his computed_str and adds the
    employer to future planned activities if it became the only employer
    """
    if sender.objects.filter(employee=instance.employee, primary=True).count() == 1:
        eer_obj = sender.objects.get(employee=instance.employee, primary=True)
        transaction.on_commit(lambda: add_employer_to_activities.delay(eer_obj.pk))


@shared_task
def add_employer_to_activities(eer_id: int):
    with suppress(EmployerEmployeeRelationship.DoesNotExist):
        eer_obj = EmployerEmployeeRelationship.objects.get(id=eer_id)

        for activity in Activity.objects.filter(
            status=Activity.Status.PLANNED,
            start__gte=timezone.now(),
            participants=eer_obj.employee,
        ):
            if eer_obj.employer not in activity.entities.all():
                activity.entities.add(eer_obj.employer)
            if eer_obj.employer not in activity.companies.all():
                activity.companies.add(eer_obj.employer)
