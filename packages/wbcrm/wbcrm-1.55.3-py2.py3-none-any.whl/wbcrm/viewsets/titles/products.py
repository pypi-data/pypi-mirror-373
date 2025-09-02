from django.utils.translation import gettext as _
from wbcore.metadata.configs.titles import TitleViewConfig


class ProductTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return _("Products")

    def get_create_title(self):
        return _("Add Product")

    def get_instance_title(self):
        return _("Product")
