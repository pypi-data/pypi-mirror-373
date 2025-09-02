from django.utils.translation import gettext as _
from rest_framework.reverse import reverse
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig

from wbcrm.models.activities import Activity, ActivityParticipant
from wbcrm.synchronization.activity.shortcuts import get_backend

DESCRIPTION: str = _(
    "<p> Are you sure you want to delete all the future instances of this activity? <br> \
    Only 'Planned' and 'Canceled' activities will be deleted. <br>\
    Depending on the number of activities to be deleted <br> \
    it may take some time until the deleted activities are no longer displayed in the activity list. </p>",
)


class ActivityButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self) -> set:
        if self.view.kwargs.get("pk"):
            return {
                bt.WidgetButton(
                    label=_("Parent Activity"), icon=WBIcon.CALENDAR.icon, key="get_parent_occurrence", weight=110
                ),
                bt.ActionButton(
                    method=RequestType.DELETE,
                    identifiers=("wbcrm:activity",),
                    key="delete_next_occurrences",
                    label=_("Delete Next Occurrences"),
                    icon=WBIcon.DELETE.icon,
                    description_fields=DESCRIPTION,
                    title=_("Delete"),
                    action_label=_("Delete"),
                    weight=140,
                ),
                bt.WidgetButton(label=_("Next Activity"), icon=WBIcon.NEXT.icon, key="next_occurrence", weight=130),
                bt.WidgetButton(
                    label=_("Previous Activity"),
                    icon=WBIcon.PREVIOUS.icon,
                    key="previous_occurrence",
                    weight=120,
                ),
            }

        return set()


class ActivityParticipantButtonConfig(ButtonViewConfig):
    def get_custom_buttons(self) -> set:
        buttons = set()
        if not self.view.kwargs.get("pk"):
            base_url = reverse("wbcrm:activity-list", args=[], request=self.request)
            activity: Activity = Activity.all_objects.get(id=self.view.kwargs.get("activity_id"))
            if activity.period:
                participants_id_set: set[int] = set(activity.participants.values_list("id", flat=True))
                id_str = ",".join(str(id) for id in participants_id_set)

                start = activity.period.lower.date()
                end = activity.period.upper.date()

                endpoint = f"{base_url}?participants={id_str}&period={start:%Y-%m-%d},{end:%Y-%m-%d}"

                buttons.add(
                    bt.WidgetButton(
                        endpoint=endpoint,
                        label=_("Show Participants' Activities"),
                        icon=WBIcon.CALENDAR.icon,
                    )
                )

            # Activity sync button to send invitation to external participants
            if get_backend():
                if activity.activity_participants.filter(
                    participation_status=ActivityParticipant.ParticipationStatus.PENDING_INVITATION
                ).exists():
                    buttons.add(
                        bt.ActionButton(
                            method=RequestType.PATCH,
                            endpoint=reverse(
                                "wbcrm:activity-participant-send-external-invitation",
                                args=[activity.id],
                                request=self.request,
                            ),
                            label="Send invitation to External",
                            icon=WBIcon.SEND_LATER.icon,
                        )
                    )
        return buttons
