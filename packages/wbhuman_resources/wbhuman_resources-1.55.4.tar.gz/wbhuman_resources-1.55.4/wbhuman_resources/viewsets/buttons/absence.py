from django.utils.translation import gettext as _
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)

from wbhuman_resources.serializers import IncreaseDaySerializer


class AbsenceRequestButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self):
        return {
            bt.ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbhuman_resources:absencerequest",),
                key="increase_days",
                action_label=_("Increasing Days"),
                label=_("Increase Days"),
                icon=WBIcon.ADD.icon,
                title=_("Increase Days"),
                serializer=IncreaseDaySerializer,
                description_fields=_(
                    """
                    <p>You are about to increase the abscence request by {{number_days}} days</p>
                """
                ),
                instance_display=create_simple_display([["number_days"]]),
            )
        }
