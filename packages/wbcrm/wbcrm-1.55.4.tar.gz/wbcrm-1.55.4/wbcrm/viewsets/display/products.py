from typing import Optional

from django.utils.translation import gettext as _
from wbcore.contrib.directory.viewsets.display import CompanyModelDisplay
from wbcore.dispatch import receiver_all_subclasses
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import add_display_pages
from wbcore.metadata.configs.display.instance_display import (
    Display,
    Inline,
    Layout,
    Page,
    Section,
    Style,
)
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
    default,
)
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class ProductDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=(
                dp.Field(key="title", label=_("Title")),
                dp.Field(key="is_competitor", label=_("Is Competitor")),
                dp.Field(key="prospects", label=_("Prospects")),
            )
        )

    def get_instance_display(self) -> Display:
        return Display(
            pages=[
                Page(
                    layouts={
                        default(): Layout(
                            grid_template_areas=[["title", "is_competitor", "prospects"]],
                            grid_template_columns=[
                                "minmax(min-content, 0.5fr)",
                                "minmax(min-content, 1fr)",
                                "minmax(min-content, 1fr)",
                            ],
                            grid_auto_rows=Style.MIN_CONTENT,
                            column_gap=Style.rem(6),
                        ),
                    },
                ),
            ]
        )


class ProductCompanyRelationshipDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=(
                dp.Field(key="product", label=_("Product")),
                dp.Field(key="competitor_product", label=_("Is Competitor")),
            )
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["product"]])


@receiver_all_subclasses(add_display_pages, sender=CompanyModelDisplay)
def add_interested_product_page(sender, *args, **kwargs):
    return [
        Page(
            title=_("Interests"),
            layouts={
                default(): Layout(
                    grid_template_areas=[["interested_products_section"]],
                    grid_auto_columns="minmax(min-content, 1fr)",
                    grid_auto_rows=Style.MIN_CONTENT,
                    sections=[
                        Section(
                            key="interested_products_section",
                            title=_("Interested Products"),
                            collapsible=False,
                            display=Display(
                                pages=[
                                    Page(
                                        title=_("Interested Products"),
                                        layouts={
                                            default(): Layout(
                                                grid_template_areas=[["interested_products_table"]],
                                                inlines=[
                                                    Inline(
                                                        key="interested_products_table",
                                                        endpoint="interested_products",
                                                    )
                                                ],
                                            )
                                        },
                                    ),
                                ]
                            ),
                        )
                    ],
                ),
            },
        )
    ]
