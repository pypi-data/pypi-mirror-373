from wbcore import filters as wb_filters
from wbcore.contrib.directory.models import Entry

from wbcrm.models.accounts import Account, AccountRole


class AccountFilter(wb_filters.FilterSet):
    parent = wb_filters.ModelChoiceFilter(
        label="Parent",
        queryset=Account.objects.all(),
        endpoint=Account.get_representation_endpoint(),
        value_key=Account.get_representation_value_key(),
        label_key=Account.get_representation_label_key(),
        hidden=True,
    )
    parent__isnull = wb_filters.BooleanFilter(field_name="parent", lookup_expr="isnull", hidden=True)
    customer = wb_filters.ModelChoiceFilter(
        label="Customer",
        queryset=Entry.objects.all(),
        endpoint=Entry.get_representation_endpoint(),
        value_key=Entry.get_representation_value_key(),
        label_key=Entry.get_representation_label_key(),
        method="filter_customer",
    )

    owner = wb_filters.ModelMultipleChoiceFilter(
        label="Owner",
        queryset=Entry.objects.all(),
        endpoint=Entry.get_representation_endpoint(),
        value_key=Entry.get_representation_value_key(),
        label_key=Entry.get_representation_label_key(),
    )

    not_owner = wb_filters.ModelMultipleChoiceFilter(
        column_field_name="owner",
        lookup_icon="!=",
        lookup_label="Not Equals",
        queryset=Entry.objects.all(),
        endpoint=Entry.get_representation_endpoint(),
        value_key=Entry.get_representation_value_key(),
        label_key=Entry.get_representation_label_key(),
        method="filter_not_owner",
    )

    status = wb_filters.MultipleChoiceFilter(
        choices=Account.Status.choices, label="Status", initial=[Account.Status.OPEN.value]
    )

    def filter_not_owner(self, queryset, name, value):
        if value:
            return queryset.exclude(owner__in=value)
        return queryset

    def filter_customer(self, queryset, name, value):
        if value:
            return queryset.filter(id__in=Account.get_accounts_for_customer(value))
        return queryset

    class Meta:
        model = Account
        fields = {
            "reference_id": ["icontains"],
            "is_active": ["exact"],
            "parent": ["exact", "isnull"],
            "is_terminal_account": ["exact"],
            "is_public": ["exact"],
        }


class AccountRoleFilterSet(wb_filters.FilterSet):
    is_currently_valid = wb_filters.BooleanFilter(label="Valid", initial=True, field_name="is_currently_valid")

    class Meta:
        model = AccountRole
        fields = {
            "role_type": ["exact"],
            "entry": ["exact"],
            "is_hidden": ["exact"],
            "authorized_hidden_users": ["exact"],
        }
