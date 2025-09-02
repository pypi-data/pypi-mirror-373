from django.db.models import F
from wbcore import viewsets

from wbcrm.filters.products import ProductCompanyFilterSet, ProductFilterSet
from wbcrm.models import Product, ProductCompanyRelationship
from wbcrm.serializers import (
    ProductCompanyRelationshipModelSerializer,
    ProductModelSerializer,
    ProductRepresentationSerializer,
)
from wbcrm.viewsets.display import ProductCompanyRelationshipDisplay, ProductDisplay
from wbcrm.viewsets.endpoints import ProductCompanyRelationshipEndpointConfig
from wbcrm.viewsets.titles import ProductTitleConfig


class ProductModelViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbcrm:product"
    LIST_DOCUMENTATION = "wbcrm/markdown/documentation/product.md"
    queryset = Product.objects.all()
    serializer_class = ProductModelSerializer
    display_config_class = ProductDisplay
    title_config_class = ProductTitleConfig
    search_fields = ("title",)

    filterset_class = ProductFilterSet
    ordering_fields = ("title",)
    ordering = ["title", "is_competitor"]


class ProductCompanyRelationshipCompanyModelViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbcrm:company-interestedproduct"
    queryset = ProductCompanyRelationship.objects.all()
    serializer_class = ProductCompanyRelationshipModelSerializer
    display_config_class = ProductCompanyRelationshipDisplay
    title_config_class = ProductTitleConfig
    endpoint_config_class = ProductCompanyRelationshipEndpointConfig
    search_fields = ("product__title",)
    ordering_fields = ("product__title",)
    ordering = ("product__title", "company__name")
    filterset_class = ProductCompanyFilterSet

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .filter(company=self.kwargs["company_id"])
            .annotate(competitor_product=F("product__is_competitor"))
        )
        return qs


class ProductRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbcrm:productrepresentation"
    serializer_class = ProductRepresentationSerializer
    search_fields = ("title",)
    queryset = Product.objects.all()
    ordering = ("title", "is_competitor")
