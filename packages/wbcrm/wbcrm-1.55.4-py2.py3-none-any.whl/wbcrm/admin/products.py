from django.contrib import admin

from wbcrm.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ("title",)
    list_display = ("title", "id")
