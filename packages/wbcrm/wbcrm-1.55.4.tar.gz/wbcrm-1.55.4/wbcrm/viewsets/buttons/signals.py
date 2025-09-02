from django.dispatch import receiver
from django.utils.translation import gettext as _
from wbcore.contrib.directory.viewsets import (
    CompanyModelViewSet,
    EntryModelViewSet,
    PersonModelViewSet,
)
from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.signals.instance_buttons import add_instance_button


@receiver(add_instance_button, sender=PersonModelViewSet)
@receiver(add_instance_button, sender=EntryModelViewSet)
@receiver(add_instance_button, sender=CompanyModelViewSet)
def add_activity_instance_button_in_directory_viewsets(sender, many, *args, **kwargs):
    return bt.WidgetButton(key="activity", label=_("Activities"), icon=WBIcon.CALENDAR.icon, weight=1)
