from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from slugify import slugify
from wbcore import serializers
from wbcore import serializers as wb_serializers
from wbcore.contrib.directory.serializers import CompanyRepresentationSerializer

from wbcrm.models import Product, ProductCompanyRelationship


class ProductRepresentationSerializer(wb_serializers.RepresentationSerializer):
    endpoint = "wbcrm:productrepresentation-list"
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcrm:product-detail")

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "computed_str",
            "_detail",
            "is_competitor",
        )


class ProductCompanyRelationshipModelSerializer(serializers.ModelSerializer):
    _product = ProductRepresentationSerializer(source="product")
    competitor_product = wb_serializers.BooleanField(read_only=True)

    class Meta:
        model = ProductCompanyRelationship
        fields = ("id", "product", "_product", "company", "competitor_product")


class ProductModelSerializer(serializers.ModelSerializer):
    _prospects = CompanyRepresentationSerializer(source="prospects", many=True)

    def validate(self, data):
        title = data.get("title")
        competitor = data.get("is_competitor")
        if title:
            product = Product.objects.filter(is_competitor=competitor, slugify_title=slugify(title, separator=" "))
            if obj := self.instance:
                product = product.exclude(id=obj.id)
            if product.exists():
                product_type = _("competitor ") if competitor else ""
                raise ValidationError({"title": _("Cannot add a duplicate {}product.").format(product_type)})
        return data

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "prospects",
            "_prospects",
            "is_competitor",
        )
