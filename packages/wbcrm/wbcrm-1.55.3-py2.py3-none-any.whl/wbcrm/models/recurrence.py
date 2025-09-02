from datetime import datetime, timedelta

import pytz
from dateutil import rrule
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from psycopg.types.range import TimestamptzRange
from wbcore.contrib.agenda.models import CalendarItem
from wbcore.utils.rrules import convert_rrulestr_to_dict

from wbcrm.preferences import (
    get_maximum_allowed_recurrent_date,
    get_recurrence_maximum_count,
)


class Recurrence(CalendarItem):
    class ReoccuranceChoice(models.TextChoices):
        NEVER = "NEVER", _("Never")
        BUSINESS_DAILY = "RRULE:FREQ=DAILY;INTERVAL=1;WKST=MO;BYDAY=MO,TU,WE,TH,FR", _("Business Daily")
        DAILY = "RRULE:FREQ=DAILY", _("Daily")
        WEEKLY = "RRULE:FREQ=WEEKLY", _("Weekly")
        BIWEEKLY = "RRULE:FREQ=WEEKLY;INTERVAL=2", _("Bi-Weekly")
        MONTHLY = "RRULE:FREQ=MONTHLY", _("Monthly")
        QUARTERLY = "RRULE:FREQ=MONTHLY;INTERVAL=3", _("Quarterly")
        YEARLY = "RRULE:FREQ=YEARLY", _("Annually")

    parent_occurrence = models.ForeignKey(
        to="self",
        related_name="child_activities",
        null=True,
        blank=True,
        verbose_name=_("Parent Activity"),
        on_delete=models.deletion.DO_NOTHING,
    )
    propagate_for_all_children = models.BooleanField(
        default=False,
        verbose_name=_("Propagate for all following activities?"),
        help_text=_("If this is checked, changes will be propagated to the following activities."),
    )
    exclude_from_propagation = models.BooleanField(
        default=False,
        verbose_name=_("Exclude occurrence from propagation?"),
        help_text=_("If this is checked, changes will not be propagated on this activity."),
    )
    recurrence_end = models.DateField(
        verbose_name=_("Date"),
        null=True,
        blank=True,
        help_text=_(
            "Specifies until when an event is to be repeated. Is mutually exclusive with the Recurrence Count."
        ),
    )
    recurrence_count = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        null=True,
        blank=True,
        verbose_name=_("Count"),
        help_text=_(
            "Specifies how often an activity should be repeated excluding the original activity. Is mutually exclusive with the end date. Limited to a maximum of 365 recurrences."
        ),
    )
    repeat_choice = models.CharField(
        max_length=56,
        default=ReoccuranceChoice.NEVER,
        choices=ReoccuranceChoice.choices,
        verbose_name=_("Recurrence Frequency"),
        help_text=_("Repeat activity at the specified frequency"),
    )

    class Meta:
        abstract = True

    @property
    def is_recurrent(self):
        return self.repeat_choice != Recurrence.ReoccuranceChoice.NEVER

    @property
    def is_root(self):
        return self.is_recurrent and not self.parent_occurrence

    @property
    def is_leaf(self):
        return self.is_recurrent and not self.next_occurrence

    @property
    def next_occurrence(self):
        if self.is_recurrent:
            parent_occurrence = self if self.is_root else self.parent_occurrence
            if qs := parent_occurrence.child_activities.filter(
                is_active=True, period__startswith__gt=self.period.lower
            ):
                return qs.earliest("period__startswith")

    @property
    def previous_occurrence(self):
        if self.is_recurrent and not self.is_root:
            if qs := self.parent_occurrence.child_activities.filter(
                is_active=True, period__startswith__lt=self.period.lower
            ):
                return qs.latest("period__startswith")
            else:
                return self.parent_occurrence
        # Else, it is a pivot and therefore, no previous occurrence should exist

    def save(self, *args, **kwargs):
        if not self.recurrence_end:
            self.recurrence_end = get_maximum_allowed_recurrent_date()
        if self.does_recurrence_need_cancellation():
            self.cancel_recurrence()
        super().save(*args, **kwargs)

    def delete(self, **kwargs):
        if self.propagate_for_all_children:
            self.forward_deletion()
        elif self.is_root and (next_occurrence := self.next_occurrence):
            next_occurrence.claim_parent_hood()
        super().delete(**kwargs)

    def _get_occurrence_start_datetimes(self, include_self: bool = False) -> list:
        """
        Returns a list with datetime values based on the recurrence options of an activity.

        :return:    list with datetime values
        """
        if self.is_recurrent:
            max_allowed_date = get_maximum_allowed_recurrent_date()
            max_allowed_count = get_recurrence_maximum_count()
            occurrence_count = min(
                self.recurrence_count + 1 if self.recurrence_count else max_allowed_count, max_allowed_count
            )
            end_date = min(
                self.recurrence_end + timedelta(days=1) if self.recurrence_end else max_allowed_date, max_allowed_date
            )
            end_date_time = datetime(end_date.year, end_date.month, end_date.day).astimezone(pytz.utc)
            rule_dict = convert_rrulestr_to_dict(
                self.repeat_choice, dtstart=self.period.lower, count=occurrence_count, until=end_date_time
            )

            start_datetimes = list(rrule.rrule(**rule_dict))
            if not include_self:
                start_date = self.period.lower.replace(microsecond=0)
                if self.period.lower in start_datetimes:
                    start_datetimes.remove(self.period.lower)
                elif start_date in start_datetimes:
                    start_datetimes.remove(start_date)
            return start_datetimes

    def _create_recurrence_child(self, *args):
        """
        Return a new child object based on self (parent/root)
        """
        raise NotImplementedError()

    def get_recurrent_valid_children(self):
        """
        Return a valid queryset representing the recurrent children
        """
        return self.child_activities.filter(exclude_from_propagation=False).order_by("period__startswith")

    def get_recurrent_invalid_children(self):
        valid = self.get_recurrent_valid_children().values_list("id", flat=True)
        return self.child_activities.all().exclude(id__in=valid).order_by("period__startswith")

    def _handle_recurrence_m2m_forwarding(self, child):
        """
        Call this when m2m data needs to be forward from the parent (self) to the passed child

        Args:
            child: Child to get the m2m data from
        """
        pass

    def does_recurrence_need_cancellation(self) -> bool:
        return False

    def cancel_recurrence(self):
        """
        keep the link to the root but exclude the occurrence from the list of valid children's to maintain, propagations will no longer be applied to this activity

        its a transition method, save needs to be called
        """
        self.exclude_from_propagation = True

    def claim_parent_hood(self):
        if self.is_recurrent and not self.is_root:
            new_batch = self._meta.model.objects.filter(
                Q(parent_occurrence=self.parent_occurrence) & Q(period__startswith__gt=self.period.lower)
            ).exclude(id=self.id)
            if new_batch.exists():
                new_batch.update(parent_occurrence=self)
            self._meta.model.objects.filter(id=self.id).update(parent_occurrence=None)

    def generate_occurrences(self, allow_reclaiming_root: bool = True):
        """
        Creation of the occurrences
        Existing occurrences whose start date is part of the list of occurrences dates obtained from the recurrence pattern are excluded
        Those not in the list are deleted
        """
        if self.is_recurrent:
            if not self.is_root and allow_reclaiming_root:
                self.claim_parent_hood()
                self.refresh_from_db()
            if self.is_root:
                if old_occurrences_dict := {occ.period.lower: occ.id for occ in self.child_activities.all()}:
                    occurrence_dates = set(self._get_occurrence_start_datetimes())
                    old_occurrences_dates = set(old_occurrences_dict.keys())
                    new_occurrence_dates = occurrence_dates.difference(old_occurrences_dates)
                    if diff_inv := old_occurrences_dates.difference(occurrence_dates):
                        self.forward_deletion(child_ids=[old_occurrences_dict[x] for x in diff_inv])
                else:
                    new_occurrence_dates = self._get_occurrence_start_datetimes()
                for start_datetime in new_occurrence_dates:
                    child = self._create_recurrence_child(start_datetime)
                    self._handle_recurrence_m2m_forwarding(child)
        return self.get_recurrent_valid_children()

    def forward_change(
        self,
        allow_reclaiming_root: bool = True,
        fields_to_forward: list = [
            "online_meeting",
            "visibility",
            "conference_room",
            "title",
            "description",
            "type",
            "importance",
            "reminder_choice",
            "location",
            "location_longitude",
            "location_latitude",
            "assigned_to",
        ],
        period_time_changed: bool = False,
    ):
        """
        Forward the changes to the following occurrences
        param: fields_to_forward: allows you to specify the fields to update
               allow_reclaiming_root: if True we split the occurrences and this occurrence becomes the parent of the following occurrences
               period_time_changed: boolean field to know if we need to update the period time or not
        """
        if self.is_recurrent and self.propagate_for_all_children:
            if not self.is_root and allow_reclaiming_root:
                self.claim_parent_hood()
                self.refresh_from_db()
            if self.is_root:
                for child in self.get_recurrent_valid_children().order_by("period__startswith"):
                    for field in fields_to_forward:
                        setattr(child, field, getattr(self, field))
                    if period_time_changed:
                        tz = child.period.lower.tzinfo
                        start_datetime = datetime.combine(
                            child.period.lower.date(), self.period.lower.time()
                        ).astimezone(tz)
                        child.period = TimestamptzRange(start_datetime, (start_datetime + self.duration))
                    child.propagate_for_all_children = False
                    child.save()
                    self._handle_recurrence_m2m_forwarding(child)
            self._meta.model.objects.filter(id=self.id).update(propagate_for_all_children=False)

    def forward_deletion(self, child_ids: list["str"] = []):
        if self.is_recurrent:
            if self.is_root:
                occurrences = self.get_recurrent_valid_children()
            else:
                occurrences = self.parent_occurrence.get_recurrent_valid_children().filter(
                    period__startswith__gt=self.period.lower
                )
            if child_ids:
                occurrences = occurrences.filter(id__in=child_ids)
            if self.propagate_for_all_children:
                # We don't call delete but update to is_active=False in order to silently delete the child activities without trggering the signals
                occurrences.update(is_active=False)
                self._meta.model.objects.filter(id=self.id).update(propagate_for_all_children=False)
            else:
                for occurrence in occurrences:
                    occurrence.delete()
