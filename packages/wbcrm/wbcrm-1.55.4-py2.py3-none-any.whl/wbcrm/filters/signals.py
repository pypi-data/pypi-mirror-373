from datetime import timedelta

from django.db.models.query import QuerySet
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from psycopg.types.range import TimestamptzRange
from wbcore import filters as wb_filters
from wbcore.contrib.directory.filters.entries import (
    CompanyFilter,
    EntryFilter,
    PersonFilter,
    UserIsManagerFilter,
)
from wbcore.contrib.directory.models import Entry
from wbcore.signals.filters import add_filters

from wbcrm.models import Account, AccountRole, Product


def choice_noactivity(queryset: QuerySet[Entry], name, value: str | None) -> QuerySet[Entry]:
    """Returns only those entries who didn't participate in any activities during the selected timeframe"""

    if value is None:
        return queryset
    else:
        value = int(value)
        if value:
            end = timezone.now()
            start = end - timedelta(days=value)
            no_activity_timeframe = TimestamptzRange(start, end)
            return queryset.exclude(
                calendar_entities__period__overlap=no_activity_timeframe,
                calendar_entities__item_type="wbcrm.Activity",
            )
        # A value of 0 corresponds to "All Time" in the filter so we need exclude any activities the entries participated in
        return queryset.exclude(calendar_entities__item_type="wbcrm.Activity")


@receiver(add_filters, sender=EntryFilter)
@receiver(add_filters, sender=PersonFilter)
@receiver(add_filters, sender=CompanyFilter)
@receiver(add_filters, sender=UserIsManagerFilter)
def add_account_filter(sender, request=None, *args, **kwargs):
    def _filter_with_account(queryset: QuerySet[Entry], name, value: str | None) -> QuerySet[Entry]:
        accounts = Account.objects.filter_for_user(request.user)
        if value:
            return queryset.filter(accounts__in=accounts).distinct()
        return queryset

    def _filter_with_account_role(queryset: QuerySet[Entry], name, value: str | None) -> QuerySet[Entry]:
        roles = AccountRole.objects.filter_for_user(request.user)
        if value:
            return queryset.filter(account_roles__in=roles).distinct()
        return queryset

    def filter_interested_products(queryset, name, value):
        if value:
            return queryset.filter(interested_products__in=value)
        return queryset

    interested_products = wb_filters.ModelMultipleChoiceFilter(
        label="Interested Products",
        help_text="Filter by products (ours and comptetitors) that the customer is interested in",
        queryset=Product.objects.all(),
        endpoint=Product.get_representation_endpoint(),
        value_key=Product.get_representation_value_key(),
        label_key=Product.get_representation_label_key(),
        method=filter_interested_products,
    )

    return {
        "without_activity": wb_filters.ChoiceFilter(
            label=_("No Activity"),
            help_text="Filter for entries without any activities",
            field_name="without_activity",
            choices=[
                (31, _("Last Month")),
                (92, _("Last 3 Months")),
                (182, _("Last 6 Months")),
                (365, _("Last 12 Months")),
                (0, _("All Time")),
            ],
            method=choice_noactivity,
        ),
        "with_account": wb_filters.BooleanFilter(
            label="With Account", help_text="Filter for entries without an account", method=_filter_with_account
        ),
        "with_account_role": wb_filters.BooleanFilter(
            label="With Account Role",
            help_text="Filter for entries without an account role",
            method=_filter_with_account_role,
        ),
        "interested_products": interested_products,
    }
