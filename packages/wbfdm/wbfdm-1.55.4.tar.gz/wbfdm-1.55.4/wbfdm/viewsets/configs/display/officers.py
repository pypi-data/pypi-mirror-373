from django.utils.translation import gettext as _
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import DisplayViewConfig


class OfficerDisplayViewConfig(DisplayViewConfig):
    def get_list_display(self) -> dp.ListDisplay:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="position", label=_("Position")),
                dp.Field(key="name", label=_("Name")),
                dp.Field(key="age", label=_("Age"), width=70),
                dp.Field(key="sex", label=_("Sex"), width=70),
                dp.Field(key="start", label=_("Start"), width=100),
            ],
        )
