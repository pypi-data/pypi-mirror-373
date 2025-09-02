from django.db import models
from django.utils.translation import gettext_lazy as _
from slugify import slugify
from wbcore.models import WBModel
from wbcore.utils.models import ComplexToStringMixin


class ProductCompanyRelationship(models.Model):
    product = models.ForeignKey(
        on_delete=models.CASCADE,
        to="wbcrm.Product",
        verbose_name=_("Product"),
        related_name="product_company_relationships",
    )
    company = models.ForeignKey(
        on_delete=models.CASCADE,
        to="directory.Company",
        verbose_name=_("Company"),
        related_name="product_company_relationships",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(name="unique_company_product_relationship", fields=["product", "company"])
        ]
        verbose_name = _("Company-Product Relationship")
        verbose_name_plural = _("Company-Product Relationships")


class Product(ComplexToStringMixin, WBModel):
    title = models.CharField(
        max_length=128,
        verbose_name=_("Title"),
    )

    slugify_title = models.CharField(
        max_length=128,
        verbose_name="Slugified Title",
        blank=True,
        null=True,
    )
    is_competitor = models.BooleanField(
        verbose_name=_("Is Competitor"),
        default=False,
        help_text=_("Indicates wether this is a competitor's product"),
    )

    prospects = models.ManyToManyField(
        "directory.Company",
        related_name="interested_products",
        blank=True,
        verbose_name=_("Prospects"),
        help_text=_("The list of prospects"),
        through="wbcrm.ProductCompanyRelationship",
        through_fields=("product", "company"),
    )

    def __str__(self) -> str:
        return self.title

    def compute_str(self) -> str:
        return _("{} (Competitor)").format(self.title) if self.is_competitor else self.title

    @classmethod
    def get_endpoint_basename(cls):
        return "wbcrm:product"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbcrm:productrepresentation-list"

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        unique_together = [["slugify_title", "is_competitor"]]

    def save(self, *args, **kwargs):
        self.slugify_title = slugify(self.title, separator=" ")
        super().save(*args, **kwargs)
