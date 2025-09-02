from django.utils.translation import gettext_lazy as _
from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig


class AbstractClassificationButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return {
            bt.WidgetButton(key="treechart", label=_("Tree Chart"), icon=WBIcon.CHART_PIE.icon),
            bt.WidgetButton(key="iciclechart", label=_("Icicle Chart"), icon=WBIcon.CHART_PYRAMID.icon),
        }

    def get_custom_instance_buttons(self):
        return self.get_custom_list_instance_buttons()


class ClassificationGroupButtonConfig(AbstractClassificationButtonConfig):
    pass


class ClassificationButtonConfig(AbstractClassificationButtonConfig):
    pass
