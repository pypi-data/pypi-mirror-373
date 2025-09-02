from typing import Optional

from rest_framework.reverse import reverse
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display import Display
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class AccountDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label="Title", pinned="left"),
                dp.Field(key="status", label="Status"),
                dp.Field(
                    key="owner",
                    label="Owner",
                ),
                dp.Field(key="reference_id", label="Reference ID"),
                dp.Field(key="is_terminal_account", label="Terminal Account"),
                dp.Field(key="is_public", label="Public"),
                dp.Field(
                    key="llm",
                    label="LLM Analysis",
                    children=[
                        dp.Field(key="relationship_status", label="Relationship Status"),
                        dp.Field(key="relationship_summary", label="Relationship Summary", show="open"),
                        dp.Field(key="action_plan", label="Action Plan", show="open"),
                    ],
                ),
            ],
            tree=True,
            tree_group_field="title",
            tree_group_field_sortable=True,
            tree_group_level_options=[
                dp.TreeGroupLevelOption(
                    filter_key="parent",
                    filter_depth=1,
                    # lookup="id_repr",
                    filter_blacklist=["parent__isnull"],
                    list_endpoint=reverse(
                        "wbcrm:account-list",
                        args=[],
                        request=self.request,
                    ),
                )
            ],
        )

    def get_instance_display(self) -> Display:
        child_account_section = create_simple_section(
            "child_account_section", "Child Accounts", [["childaccounts"]], "childaccounts", collapsed=True
        )
        account_role_section = create_simple_section(
            "account_role_section", "Account Roles", [["accountroles"]], "accountroles", collapsed=True
        )
        inherited_account_role_section = create_simple_section(
            "inherited_account_role_section",
            "Inherited Account Roles",
            [["inheritedaccountroles"]],
            "inheritedaccountroles",
            collapsed=True,
        )
        return create_simple_display(
            [
                [repeat_field(3, "status")],
                ["title", "title", "reference_id"],
                ["is_active", "is_terminal_account", "is_public"],
                ["parent", "owner", "owner"] if "account_id" not in self.view.kwargs else [repeat_field(3, "owner")],
                [repeat_field(3, "child_account_section")],
                [repeat_field(3, "account_role_section")],
                [repeat_field(3, "inherited_account_role_section")],
            ],
            [child_account_section, account_role_section, inherited_account_role_section],
        )


class AccountRoleAccountDisplayConfig(DisplayViewConfig):
    def get_instance_display(self) -> Display:
        return create_simple_display([["role_type", "entry"], ["is_hidden", "authorized_hidden_users"]])

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="role_type", label="Role"),
                dp.Field(key="entry", label="entry"),
                dp.Field(key="is_currently_valid", label="Valid"),
                dp.Field(key="is_hidden", label="Hidden"),
                dp.Field(key="authorized_hidden_users", label="Authorized Hidden Users"),
            ]
        )


class InheritedAccountRoleAccountDisplayConfig(AccountRoleAccountDisplayConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="account", label="Account"),
                dp.Field(key="role_type", label="Role"),
                dp.Field(key="entry", label="Entry"),
                dp.Field(key="is_currently_valid", label="Valid"),
                dp.Field(key="is_hidden", label="Hidden"),
                dp.Field(key="authorized_hidden_users", label="Authorized Hidden Users"),
            ]
        )
