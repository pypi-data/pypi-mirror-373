from __future__ import absolute_import, unicode_literals

import logging
from datetime import date, datetime, time, timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import (
    F,
    FloatField,
    Func,
    Max,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Sum,
    Value,
)
from django.db.models.functions import Cast, Coalesce, Least
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.translation import gettext as _
from dynamic_preferences.registries import global_preferences_registry
from psycopg.types.range import TimestamptzRange
from rest_framework.reverse import reverse
from wbcore.contrib.directory.models import Company, Person
from wbcore.contrib.notifications.dispatch import send_notification

from wbcrm.models import Activity, ActivityType

logger = logging.getLogger()
User = get_user_model()


@shared_task
def notify(time_offset: int = 60, now: datetime | None = None):
    """
    Cron task that runs every 60s and checks which activities will happen during the notify interval

    Arguments:
        time_offset (int):  The notification period. Defaults to 60.
        now (datetime | None, optional):  The time at which activity needs to be checked for a notification. Defaults to None.
    """

    if not now:
        now = timezone.now()
    base_queryset: QuerySet[Activity] = Activity.objects.filter(Q(status=Activity.Status.PLANNED))
    reminder_choices = Activity.ReminderChoice.values

    # we don't notify activity if Reminder is Never
    reminder_choices.remove(Activity.ReminderChoice.NEVER)
    for reminder in reminder_choices:
        # get the reminder correspondance in minutes
        reminder_minutes = Activity.ReminderChoice.get_minutes_correspondance(reminder)
        reminder_range = TimestamptzRange(
            now + timedelta(minutes=reminder_minutes),
            now + timedelta(minutes=reminder_minutes) + timedelta(seconds=time_offset),
        )  # type: ignore #ErrMsg: Expected no arguments to "TimestamptzRange" constructor
        # get all incoming activity with same reminder that happen during the notify interval
        upcoming_occurence = base_queryset.filter(
            reminder_choice=reminder, period__startswith__contained_by=reminder_range
        )
        for activity in upcoming_occurence:
            participants = activity.get_participants()

            # For each Employee in the activity participants
            for employee in Person.objects.filter_only_internal().filter(id__in=participants.values("id")).all():
                # formant and create Notification
                activity_type_label = activity.type.title
                desc = (
                    activity.description
                    if activity.description and activity.description not in ["", "<p></p>"]
                    else None
                )
                message = render_to_string(
                    "email/activity.html",
                    {
                        "participants": participants,
                        "type": activity_type_label,
                        "title": activity.title,
                        "start": activity.period.lower,
                        "end": activity.period.upper,
                        "description": desc,
                    },
                )
                send_notification(
                    code="wbcrm.activity.reminder",
                    title=_("{type} in {reminder} Minutes").format(
                        type=activity_type_label, reminder=reminder_minutes
                    ),
                    body=message,
                    user=employee.user_account,
                    reverse_name="wbcrm:activity-detail",
                    reverse_args=[activity.pk],
                )


@shared_task
def yesterdays_activity_summary(yesterday: date | None = None, report_receiver_user_ids: list[int] | None = None):
    """A daily task that sends a summary of all employees' yesterday's activities to the users assigned to this task

    Args:
        yesterday (date | None, optional): Date of the previous day. Defaults to None.
    """

    if not yesterday:
        yesterday = date.today() - timedelta(days=1)
    yesterday = datetime.combine(yesterday, time(0, 0, 0))  # we convert the date to datetime
    time_range = TimestamptzRange(make_aware(yesterday), make_aware(yesterday + timedelta(days=1)))  # type: ignore #ErrMsg: Expected no arguments to "TimestamptzRange" constructor

    # Create the list of all employees' activities for yesterday
    employees_list: list[Person] = list(Person.objects.filter_only_internal())
    internal_activities: QuerySet[Activity] = (
        Activity.objects.exclude(status=Activity.Status.CANCELLED)
        .filter(period__overlap=time_range, participants__in=employees_list)
        .order_by("period__startswith")
    )

    if not (internal_activities.exists() or report_receiver_user_ids):
        return

    activity_lists: list[list[dict]] = []  # contains an activity list for each employee
    employee_names = []
    for employee in employees_list:
        if internal_activities.filter(participants=employee).exists():
            employees_activities = internal_activities.filter(participants=employee)
            # Create activity list with formatted activity dictionaries for employee
            activity_lists.append(
                [
                    {
                        "type": activity.type.title,
                        "title": activity.title,
                        "start": activity.period.lower,  # type: ignore #ErrMsg: Cannot access member "lower" for type "TimestamptzRange"
                        "end": activity.period.upper,  # type: ignore #ErrMsg: Cannot access member "upper" for type "TimestamptzRange"
                        "endpoint": reverse("wbcrm:activity-detail", args=[activity.pk]),
                    }
                    for activity in employees_activities
                ]
            )
            employee_names.append(employee.full_name)

    # Create the notification for each person with the right permission
    for user in User.objects.filter(id__in=report_receiver_user_ids).distinct():
        context = {
            "map_activities": zip(employee_names, activity_lists),
            "activities_count": internal_activities.count(),
            "report_date": yesterday.strftime("%d.%m.%Y"),
        }
        message = render_to_string("email/global_daily_summary.html", context)
        send_notification(
            code="wbcrm.activity.daily_summary",
            title=_("Activity Summary {}").format(yesterday.strftime("%d.%m.%Y")),
            body=message,
            user=user,
        )


@shared_task
def todays_activity_summary(today: date | None = None):
    """Creates a summary of the daily upcoming activities for all employees

    Args:
        today (date | None, optional): Date of today. Defaults to None.
    """

    if not today:
        today = date.today()
    tz_info = timezone.get_current_timezone()
    today_range = TimestamptzRange(
        lower=datetime.combine(today, time(0, 0, 0)).replace(tzinfo=tz_info),
        upper=datetime.combine(today + timedelta(days=1), time(0, 0, 0).replace(tzinfo=tz_info)),
    )

    for employee in Person.objects.filter_only_internal():
        # Get all the employee's activities from that day
        activity_qs: QuerySet[Activity] = (
            Activity.objects.exclude(status=Activity.Status.CANCELLED)
            .filter(period__overlap=today_range, participants=employee)
            .order_by("period__startswith")
        )

        # Create the formatted activity dictionaries
        activity_list = []
        for activity in activity_qs:
            activity_list.append(
                {
                    "type": activity.type.title,
                    "title": activity.title,
                    "start": activity.period.lower,
                    "end": activity.period.upper,
                    "endpoint": reverse("wbcrm:activity-detail", args=[activity.pk]),
                }
            )

        # Create the proper notification for each employee
        if activity_list and employee.primary_email_contact():
            context = {"activities": activity_list}
            message = render_to_string("email/daily_summary.html", context)
            send_notification(
                code="wbcrm.activity.daily_summary",
                title=_("Your Schedule for Today"),
                body=message,
                user=employee.user_account,
            )


@shared_task
def finish(now: datetime | None = None):
    """Cron task running every X Seconds. Checks all activities that have finished and sends a reminder to review the activity to the assigned person.

    Args:
        now (datetime | None, optional): Current datetime. Defaults to None.
    """

    if not now:
        now = timezone.now()
    # Get all finished activities during the cron task interval
    finished_activities: QuerySet[Activity] = Activity.objects.filter(
        Q(status=Activity.Status.PLANNED.name)
        & Q(repeat_choice=Activity.ReoccuranceChoice.NEVER)
        & Q(period__endswith__lte=now)
    )

    # For each of these activities, Send the Notification to the person in charge of that activity
    for activity in finished_activities:
        activity.finish()
        activity.save()
        if (assignee := activity.assigned_to) and assignee.is_internal and assignee.user_account:
            send_notification(
                code="wbcrm.activity.finished",
                title=_("Activity Finished"),
                body=_('The activity "{title}" just finished and you are in charge of it. Please review.').format(
                    title=activity.title
                ),
                user=assignee.user_account,
                reverse_name="wbcrm:activity-detail",
                reverse_args=[activity.pk],
            )


@shared_task
def default_activity_heat_calculation(check_datetime: datetime | None = None):
    """A script that calculates the activity heat of companies and
    persons on a scale from 0.0 to 1.0. The type and time interval of
    completed activities serve as the basis for the heat calculation for companies. A person's rating is based
    on the score of the person's employer.

    Args:
        check_datetime (datetime | None, optional): The datetime of the activity heat check. Defaults to None.
    """

    if not check_datetime:
        check_datetime = timezone.now()

    class JulianDay(Func):
        """
        The Julian day is the continuous count of days since the beginning of the Julian period.
        """

        function = ""
        output_field = FloatField()  # type: ignore #ErrMsg: Expression of type "FloatField[float]" cannot be assigned to declared type "property"

        def as_postgresql(self, compiler, connection):
            self.template = "CAST (to_char(%(expressions)s, 'J') AS INTEGER)"
            return self.as_sql(compiler, connection)

    global_preferences_manager = global_preferences_registry.manager()
    main_company: int = global_preferences_manager["directory__main_company"]

    external_employees: QuerySet[Person] = Person.objects.exclude(id__in=Person.objects.filter_only_internal())
    external_companies: QuerySet[Company] = Company.objects.exclude(id=main_company)
    # Calculate the activity heat of a person in the last 180 days.
    activity_score = (
        Activity.objects.filter(
            companies__id=OuterRef("id"),
            status__in=["REVIEWED", "FINISHED"],
            period__endswith__gte=check_datetime - timedelta(days=180),
            period__endswith__lte=check_datetime,
        )
        .annotate(
            ratio=JulianDay(Value(check_datetime)) - JulianDay(F("period__endswith")),
            date_score=(Value(365) - F("ratio")) / Value(365.0),
            score=Cast(F("type__score"), FloatField()) * F("date_score"),
        )
        .values("companies__id")
        .annotate(sum_score=Sum(F("score")))
        .values("sum_score")
    )

    company_score = (
        Company.objects.filter(
            id=OuterRef("id"),
        )
        .annotate(
            norm_score=Coalesce(
                Subquery(activity_score) / float(ActivityType.Score.MAX),
                Value(0.0),
            ),
            abs_norm_score=Least(F("norm_score"), 1.0),
        )
        .values("abs_norm_score")
    )
    employer_max_score = (
        external_companies.filter(employees__id=OuterRef("id"))
        .values("employees__id")
        .annotate(max_score=Max("activity_heat"))
        .values("max_score")
    )

    external_companies.update(activity_heat=Subquery(company_score))
    external_employees.filter(employers__id__in=external_companies).update(activity_heat=Subquery(employer_max_score))
