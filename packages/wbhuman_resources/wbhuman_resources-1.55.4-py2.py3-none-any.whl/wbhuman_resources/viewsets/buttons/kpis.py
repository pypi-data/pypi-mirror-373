from django.utils.translation import gettext as _
from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt


class KPIButtonConfig(bt.ButtonViewConfig):
    def get_custom_instance_buttons(self):
        BUTTONS = []
        if self.view.kwargs.get("pk", None):
            BUTTONS += [
                bt.WidgetButton(
                    key="evaluationgraph", label=_("Evaluation Graph"), icon=WBIcon.CHART_BARS_HORIZONTAL.icon
                ),
                bt.WidgetButton(key="kpievaluationpandas", label=_("Latest Evaluations"), icon=WBIcon.DATA_GRID.icon),
            ]
        return {*BUTTONS}
