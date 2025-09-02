from datetime import date, timedelta

import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Q
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django.utils.translation import gettext_lazy as _
from dynamic_preferences.registries import global_preferences_registry
from psycopg.types.range import DateRange, TimestamptzRange
from wbcore import filters as wb_filters
from wbcore.contrib.agenda.filters import CalendarItemPeriodBaseFilterSet
from wbcore.contrib.agenda.models import CalendarItem
from wbcore.contrib.directory.models import CustomerStatus
from wbcore.contrib.directory.models.entries import Company, Person
from wbcore.filters.lookups import ALL_TEXT_LOOKUPS

from wbcrm.models import Activity, ActivityParticipant, ActivityType, Group
from wbcrm.models.activities import ActivityCompanyThroughModel


def get_employee_filter_params(request, view):
    if employer_id := global_preferences_registry.manager()["directory__main_company"]:
        return {"employers": employer_id}
    return {}


class ActivityBaseFilterSet(CalendarItemPeriodBaseFilterSet):
    type = wb_filters.ModelMultipleChoiceFilter(
        label=gettext_lazy("Types"),
        queryset=ActivityType.objects.all(),
        endpoint=ActivityType.get_representation_endpoint(),
        value_key=ActivityType.get_representation_value_key(),
        label_key=ActivityType.get_representation_label_key(),
    )

    visibility = wb_filters.MultipleChoiceFilter(
        choices=CalendarItem.Visibility.choices,
        label=gettext_lazy("Visibility"),
    )

    participants = wb_filters.ModelMultipleChoiceFilter(
        label=gettext_lazy("Participants"),
        queryset=Person.objects.all(),
        endpoint=Person.get_representation_endpoint(),
        value_key=Person.get_representation_value_key(),
        label_key=Person.get_representation_label_key(),
    )

    companies = wb_filters.ModelMultipleChoiceFilter(
        label=gettext_lazy("Companies"),
        queryset=Company.objects.all(),
        endpoint=Company.get_representation_endpoint(),
        value_key=Company.get_representation_value_key(),
        label_key=Company.get_representation_label_key(),
    )

    groups = wb_filters.ModelMultipleChoiceFilter(
        label=gettext_lazy("Groups"),
        queryset=Group.objects.all(),
        endpoint=Group.get_representation_endpoint(),
        value_key=Group.get_representation_value_key(),
        label_key=Group.get_representation_label_key(),
    )


class ActivityFilter(ActivityBaseFilterSet):
    clients_of = wb_filters.ModelChoiceFilter(
        label=gettext_lazy("Clients of"),
        queryset=Person.objects.all(),
        endpoint=Person.get_representation_endpoint(),
        value_key=Person.get_representation_value_key(),
        label_key=Person.get_representation_label_key(),
        method="filter_clients_of",
        filter_params=get_employee_filter_params,
    )

    latest_reviewer = wb_filters.ModelMultipleChoiceFilter(
        label=gettext_lazy("Latest Reviewers"),
        queryset=Person.objects.all(),
        endpoint=Person.get_representation_endpoint(),
        value_key=Person.get_representation_value_key(),
        label_key=Person.get_representation_label_key(),
    )

    importance = wb_filters.MultipleChoiceFilter(
        label=gettext_lazy("Importance"), choices=Activity.Importance.choices, widget=django_filters.widgets.CSVWidget
    )

    created = wb_filters.DateTimeRangeFilter(
        method=wb_filters.DateRangeFilter.base_date_range_filter_method, label=gettext_lazy("Created")
    )
    edited = wb_filters.DateTimeRangeFilter(
        method=wb_filters.DateRangeFilter.base_date_range_filter_method, label=gettext_lazy("Edited")
    )

    only_recent = wb_filters.BooleanFilter(label=gettext_lazy("Only Recent"), method="boolean_only_recent")

    customer_status = wb_filters.ModelChoiceFilter(
        label=gettext_lazy("Customer Status"),
        queryset=CustomerStatus.objects.all(),
        endpoint=CustomerStatus.get_representation_endpoint(),
        value_key=CustomerStatus.get_representation_value_key(),
        label_key=CustomerStatus.get_representation_label_key(),
        method="filter_customer_status",
        help_text="Filter activities based on the company customer status at the activity creation time",
    )

    def boolean_only_recent(self, queryset: QuerySet[Activity], name, value: bool | None) -> QuerySet[Activity]:
        if value:
            today = date.today()
            next_week = today + timedelta(days=7)
            last_month = today - timedelta(days=30)
            return queryset.filter(period__overlap=TimestamptzRange(last_month, next_week))
        return queryset

    def filter_clients_of(self, queryset, name, value):
        if value:
            user = self.request.user
            return Activity.objects.filter(
                (Q(participants__relationship_managers=value) | Q(companies__relationship_managers=value))
                & (
                    Q(visibility=CalendarItem.Visibility.PUBLIC)
                    | (
                        Q(visibility=CalendarItem.Visibility.CONFIDENTIAL)  # TODO move that to a queryset method
                        & Exists(
                            get_user_model().objects.filter(
                                Q(id=user.id)
                                & (
                                    Q(groups__permissions__codename="administrate_confidential_items")
                                    | Q(user_permissions__codename="administrate_confidential_items")
                                )
                            )
                        )
                    )
                    | Q(
                        Exists(
                            ActivityParticipant.objects.filter(activity_id=OuterRef("pk"), participant=user.profile)
                        )
                    )
                    | Q(assigned_to=user.profile)
                )
            )
        return queryset

    def filter_customer_status(self, queryset, name, value):
        if value:
            rel = ActivityCompanyThroughModel.objects.filter(customer_status=value)
            return queryset.filter(id__in=rel.values("activity"))
        return queryset

    class Meta:
        model = Activity
        fields = {
            "status": ["exact"],
            "repeat_choice": ["exact"],
            "title": ALL_TEXT_LOOKUPS,
            "result": ALL_TEXT_LOOKUPS,
            "description": ALL_TEXT_LOOKUPS,
        }


def default_activitychart_get_params(*args, **kwargs):
    current_last_week_date_start = timezone.now().date() - timedelta(days=7)
    current_next_week_date_end = timezone.now().date() + timedelta(days=7)
    return DateRange(current_last_week_date_start, current_next_week_date_end)


class ActivityChartFilter(ActivityBaseFilterSet):
    status = wb_filters.MultipleChoiceFilter(
        label=gettext_lazy("Status"), choices=Activity.Status.choices, widget=django_filters.widgets.CSVWidget
    )
    period = wb_filters.DateTimeRangeFilter(label="Period", required=True, initial=default_activitychart_get_params)

    class Meta:
        model = Activity
        fields = {}


class ActivityTypeFilter(wb_filters.FilterSet):
    score = wb_filters.MultipleChoiceFilter(
        label=_("Multipliers"), choices=ActivityType.Score.choices[:3], widget=django_filters.widgets.CSVWidget
    )

    class Meta:
        model = ActivityType
        fields = {
            "title": ["exact", "icontains"],
            "color": ["exact", "icontains"],
            "default": ["exact"],
        }


class ActivityParticipantFilter(wb_filters.FilterSet):
    is_occupied_filter = wb_filters.BooleanFilter(
        label=gettext_lazy("Is occupied by different activity"), method="boolean_is_occupied"
    )

    def boolean_is_occupied(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(is_occupied=value)

    class Meta:
        model = ActivityParticipant
        fields = {}
