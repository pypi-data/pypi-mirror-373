from django.utils.translation import gettext_lazy as _
from wbcore import filters as wb_filters
from wbcore.contrib.directory.models import Entry

from wbcrm.models import Group


class GroupFilter(wb_filters.FilterSet):
    members = wb_filters.ModelMultipleChoiceFilter(
        label=_("Members"),
        queryset=Entry.objects.all(),
        endpoint=Entry.get_representation_endpoint(),
        value_key=Entry.get_representation_value_key(),
        label_key=Entry.get_representation_label_key(),
    )

    class Meta:
        model = Group
        fields = {
            "title": ["exact", "icontains"],
        }
