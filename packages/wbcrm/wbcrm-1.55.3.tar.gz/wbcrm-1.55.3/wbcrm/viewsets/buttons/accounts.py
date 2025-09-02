from django.dispatch import receiver
from wbcore.contrib.directory.viewsets import (
    CompanyModelViewSet,
    EntryModelViewSet,
    PersonModelViewSet,
)
from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.signals.instance_buttons import add_instance_button


class AccountButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self):
        return {bt.WidgetButton(key="claims", label="Show Claims", icon=WBIcon.TRADE.icon)}

    def get_custom_list_instance_buttons(self):
        return self.get_custom_instance_buttons()


@receiver(add_instance_button, sender=PersonModelViewSet)
@receiver(add_instance_button, sender=EntryModelViewSet)
@receiver(add_instance_button, sender=CompanyModelViewSet)
def crm_adding_instance_buttons(sender, many, *args, **kwargs):
    if many:
        return
    return bt.WidgetButton(key="account", label="Accounts", icon=WBIcon.FOLDERS_MONEY.icon)
