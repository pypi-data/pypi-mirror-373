from django.utils.translation import gettext_lazy
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)

from wbhuman_resources.serializers import DeactivateEmployeeSerializer


class EmployeeButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self):
        return {
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbhuman_resources:employee",),
                key="deactivate",
                action_label=gettext_lazy("Deactivating Employee"),
                label=gettext_lazy("Deactivate Employee"),
                icon=WBIcon.DISABLED.icon,
                title=gettext_lazy("Deactivate Employee"),
                serializer=DeactivateEmployeeSerializer,
                description_fields=gettext_lazy(
                    """
                    <p>You are about to deactivate the employee <b>{{computed_str}}</b>. This will disable this employee's and user's accounts. If you want to transfer relationships to a substitute, please select it in the list bellow:</p>
                """
                ),
                instance_display=create_simple_display([["substitute"]]),
            ),
            bt.WidgetButton(key="balance_and_usage", label="Balance & Usage", icon=WBIcon.DATA_GRID.icon),
        }

    def get_custom_list_instance_buttons(self):
        return self.get_custom_instance_buttons()


class YearBalanceEmployeeHumanResourceButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return super().get_custom_list_instance_buttons()

    def get_custom_instance_buttons(self):
        return super().get_custom_instance_buttons()
