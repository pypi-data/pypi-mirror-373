from typing import Optional

from django.utils.translation import gettext as _
from django.utils.translation import pgettext
from wbcore.contrib.color.enums import WBColor
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display import (
    Display,
    Inline,
    Layout,
    Page,
    Section,
    Style,
    create_simple_display,
)
from wbcore.metadata.configs.display.instance_display.operators import default
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbcrm.models import Activity


def get_activity_legend() -> list[dp.Legend]:
    """Dynamically creates the activity legend based on the activity status enum"""

    legend_items = []
    for status, color in Activity.Status.get_color_map():
        legend_items.append(dp.LegendItem(icon=color, label=status.label, value=status.value))
    return [dp.Legend(key="status", items=legend_items)]


def get_activity_list_formatting() -> list[dp.Formatting]:
    """Dynamically creates the activity list formatting based on the activity status enum"""

    formatting_rules = []
    for status, color in Activity.Status.get_color_map():
        formatting_rules.append(dp.FormattingRule(condition=("==", status.name), style={"backgroundColor": color}))

    return [dp.Formatting(column="status", formatting_rules=formatting_rules)]


class ActivityTypeDisplay(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="title", label=_("Title")),
                dp.Field(key="icon", label=_("Icon")),
                dp.Field(key="color", label=_("Color")),
                dp.Field(key="score", label=_("Multiplier")),
                dp.Field(key="default", label=_("Is Default")),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display([["default", "."], ["title", "score"], ["color", "icon"]])


class ActivityDisplay(DisplayViewConfig):
    @classmethod
    def _get_activity_instance_display(cls, instance: Activity) -> Display:
        """Returns an activity instance's display

        Args:
            instance: The activity instance that will be displayed

        Returns:
            Display: The display instance
        """

        participants_section = Section(
            key="participants_section",
            collapsible=False,
            title=_("Participants"),
            display=Display(
                pages=[
                    Page(
                        title=_("Participants"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["participants_table"]],
                                inlines=[Inline(key="participants_table", endpoint="activity_participants_table")],
                            )
                        },
                    ),
                ]
            ),
        )

        if instance.status == Activity.Status.PLANNED:
            display = Display(
                pages=[
                    Page(
                        title=_("Main Information"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[
                                    [
                                        "status",
                                        "status",
                                        "participants_section",
                                        "participants_section",
                                    ],
                                    [
                                        "title",
                                        "type",
                                        "participants_section",
                                        "participants_section",
                                    ],
                                    [
                                        "period",
                                        "all_day",
                                        "participants_section",
                                        "participants_section",
                                    ],
                                    [
                                        "participants",
                                        "groups",
                                        "participants_section",
                                        "participants_section",
                                    ],
                                    [
                                        "companies",
                                        "disable_participant_check",
                                        "participants_section",
                                        "participants_section",
                                    ],
                                    [
                                        "description",
                                        "description",
                                        "result",
                                        "result",
                                    ],
                                    ["summary", "summary", "summary", "summary"],
                                ],
                                grid_auto_columns="1fr",
                                grid_auto_rows=Style.MIN_CONTENT,
                                sections=(participants_section,),
                            ),
                        },
                    ),
                    Page(
                        title=_("Recurrence"),
                        layouts={
                            default(): Layout(grid_template_areas=[["propagate_for_all_children", "repeat_choice"]])
                        },
                    ),
                    Page(
                        title=_("Additional Information"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[
                                    [
                                        "assigned_to",
                                        "assigned_to",
                                        "reminder_choice",
                                        "visibility",
                                    ],
                                    ["conference_room", "online_meeting", "location", "importance"],
                                    [
                                        "created",
                                        "edited",
                                        ".",
                                        ".",
                                    ],
                                ],
                                grid_template_columns=[
                                    "minmax(min-content, 1fr)",
                                    "minmax(min-content, 1fr)",
                                    "minmax(min-content, 2fr)",
                                    "minmax(min-content, 2fr)",
                                ],
                                grid_auto_rows=Style.MIN_CONTENT,
                            )
                        },
                    ),
                ]
            )
        else:
            display = Display(
                pages=[
                    Page(
                        title=_("Main Information"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[
                                    [
                                        "status",
                                        ".",
                                    ],
                                    [
                                        "title",
                                        "type",
                                    ],
                                    [
                                        "period",
                                        "all_day",
                                    ],
                                    [
                                        "participants",
                                        "groups",
                                    ],
                                    [
                                        "companies",
                                        "disable_participant_check",
                                    ],
                                    [
                                        "description",
                                        "description" if instance.status == Activity.Status.CANCELLED else "result",
                                    ],
                                    ["summary", "summary"],
                                ],
                                grid_auto_columns="1fr",
                                grid_auto_rows=Style.MIN_CONTENT,
                            ),
                        },
                    ),
                    Page(
                        title=_("Participant Information"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["participants_section"]], sections=(participants_section,)
                            )
                        },
                    ),
                    Page(
                        title=_("Recurrence"),
                        layouts={default(): Layout(grid_template_areas=[["propagate_for_all_children"]])},
                    ),
                    Page(
                        title=_("Additional Information"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[
                                    [
                                        "assigned_to",
                                        "assigned_to",
                                        "reminder_choice",
                                        "visibility",
                                    ],
                                    ["conference_room", "online_meeting", "location", "importance"],
                                    [
                                        "created",
                                        "edited",
                                        ".",
                                        ".",
                                    ],
                                ],
                                grid_template_columns=[
                                    "minmax(min-content, 1fr)",
                                    "minmax(min-content, 1fr)",
                                    "minmax(min-content, 2fr)",
                                    "minmax(min-content, 2fr)",
                                ],
                                grid_auto_rows=Style.MIN_CONTENT,
                            )
                        },
                    ),
                ]
            )

        return display

    @classmethod
    def _get_new_activity_instance_display(cls) -> Display:
        """Returns the display for creating a new activity

        Returns:
            Display: The display instance
        """

        new_recurrence_section = Section(
            key="new_recurrence_section",
            collapsible=False,
            title=_("Repeat Until"),
            display=Display(
                pages=[
                    Page(
                        title=_("Repeat Until"),
                        layouts={
                            default(): Layout(
                                grid_template_areas=[["recurrence_end", "recurrence_count", "."]],
                                grid_template_columns=[
                                    "minmax(min-content, 1fr)",
                                    "minmax(min-content, 1fr)",
                                    "minmax(min-content, 2fr)",
                                ],
                                grid_auto_rows=Style.MIN_CONTENT,
                            )
                        },
                    ),
                ]
            ),
        )

        return Display(
            pages=[
                Page(
                    title=_("Main Information"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                [
                                    "title",
                                    "type",
                                ],
                                [
                                    "period",
                                    "all_day",
                                ],
                                [
                                    "participants",
                                    "groups",
                                ],
                                [
                                    "companies",
                                    "disable_participant_check",
                                ],
                                [
                                    "description",
                                    "result",
                                ],
                            ],
                            grid_auto_columns="1fr",
                            grid_auto_rows=Style.MIN_CONTENT,
                        ),
                    },
                ),
                Page(
                    title=_("Recurrence"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["repeat_choice", "."],
                                ["new_recurrence_section", "new_recurrence_section"],
                            ],
                            grid_template_columns=["minmax(min-content, 1fr)", "minmax(min-content, 3fr)"],
                            grid_auto_rows=Style.MIN_CONTENT,
                            sections=(new_recurrence_section,),
                        )
                    },
                ),
                Page(
                    title=_("Additional Information"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                [
                                    "assigned_to",
                                    "assigned_to",
                                    "reminder_choice",
                                    "visibility",
                                ],
                                ["conference_room", "online_meeting", "location", "importance"],
                            ],
                            grid_template_columns=[
                                "minmax(min-content, 1fr)",
                                "minmax(min-content, 1fr)",
                                "minmax(min-content, 2fr)",
                                "minmax(min-content, 2fr)",
                            ],
                            grid_auto_rows=Style.MIN_CONTENT,
                        )
                    },
                ),
            ]
        )

    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="heat", label=_("Sentiment"), width=75),
                dp.Field(key="type", label=_("Type")),
                dp.Field(key="title", label=_("Title")),
                dp.Field(key="summary", label=_("Summary")),
                dp.Field(key="period", label=_("Period")),
                dp.Field(key="participants", label=_("Participants")),
                dp.Field(key="companies", label=_("Companies")),
                dp.Field(key="groups", label=_("Groups")),
                dp.Field(key="edited", label=_("Edited")),
                dp.Field(key="created", label=pgettext("As a table header", "Created")),
                dp.Field(key="description", label=_("Description")),
                dp.Field(key="result", label=pgettext("As a table header", "Review")),
                dp.Field(key="latest_reviewer", label=_("Latest Reviewer")),
            ],
            legends=get_activity_legend(),
            formatting=get_activity_list_formatting(),
        )

    def get_instance_display(self) -> Display:
        return (
            self._get_activity_instance_display(self.view.get_object())
            if "pk" in self.view.kwargs
            else self._get_new_activity_instance_display()
        )


class ActivityParticipantDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="participant", label=_("Participant")),
                dp.Field(key="participation_status", label=_("Participation Status")),
                dp.Field(key="status_changed", label=_("Status Changed")),
                dp.Field(key="position", label=_("Position")),
                dp.Field(key="primary_email", label=_("Primary Email")),
                dp.Field(key="primary_telephone", label=_("Primary Phone Number")),
            ],
            legends=[
                dp.Legend(
                    key="is_occupied_filter",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value,
                            label=_("Is Available"),
                            value=False,
                        ),
                        dp.LegendItem(
                            icon=WBColor.RED_LIGHT.value,
                            label=_("Is Occupied"),
                            value=True,
                        ),
                    ],
                )
            ],
            formatting=[
                dp.Formatting(
                    column="is_occupied",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=("==", False),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.RED_LIGHT.value},
                            condition=("==", True),
                        ),
                    ],
                )
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [["participation_status", "participation_status"], ["participant", "customer_status"]]
        )
