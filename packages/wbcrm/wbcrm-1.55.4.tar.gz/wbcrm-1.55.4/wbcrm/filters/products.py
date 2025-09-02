from django.utils.translation import gettext_lazy as _
from wbcore import filters as wb_filters
from wbcore.contrib.directory.models import Company

from wbcrm.models import Product, ProductCompanyRelationship


class ProductFilterSet(wb_filters.FilterSet):
    prospects = wb_filters.ModelMultipleChoiceFilter(
        label=_("Prospects"),
        queryset=Company.objects.all(),
        endpoint=Company.get_representation_endpoint(),
        value_key=Company.get_representation_value_key(),
        label_key=Company.get_representation_label_key(),
    )

    class Meta:
        model = Product
        fields = {
            "title": ["exact", "icontains"],
            "is_competitor": ["exact"],
        }


class ProductCompanyFilterSet(wb_filters.FilterSet):
    competitor_product = wb_filters.BooleanFilter(label=_("Is Competitor"), method="filter_competitor_product")

    def filter_competitor_product(self, queryset, label, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(product__is_competitor=value)

    class Meta:
        model = ProductCompanyRelationship
        fields = {
            "product": ["exact"],
        }
