from django.utils.translation import gettext as _
from wbcore.contrib.color.enums import WBColor
from wbcore.enums import Operator
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import DisplayViewConfig

from wbfdm.enums import ESGControveryFlag


class InstrumentESGControversyDisplayViewConfig(DisplayViewConfig):
    def get_list_display(self) -> dp.ListDisplay:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="initiated", label=_("Initiated"), width=100),
                dp.Field(key="review", label=_("Review"), width=100),
                dp.Field(key="headline", label=_("Headline")),
                dp.Field(key="narrative", label=_("Narrative")),
                dp.Field(key="source", label=_("Source")),
                dp.Field(key="status", label=_("Status")),
                dp.Field(key="type", label=_("Type")),
                dp.Field(key="assessment", label=_("Assessment")),
                dp.Field(key="response", label=_("Response")),
            ],
            formatting=[
                dp.Formatting(
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"background-color": WBColor.GREEN_LIGHT.value},
                            condition=dp.Condition(operator=Operator.EQUAL, value=ESGControveryFlag.GREEN.value),
                        ),
                        dp.FormattingRule(
                            style={"background-color": WBColor.RED_LIGHT.value},
                            condition=dp.Condition(operator=Operator.EQUAL, value=ESGControveryFlag.RED.value),
                        ),
                        dp.FormattingRule(
                            style={"background-color": WBColor.YELLOW_LIGHT.value},
                            condition=dp.Condition(operator=Operator.EQUAL, value=ESGControveryFlag.YELLOW.value),
                        ),
                        dp.FormattingRule(
                            style={"background-color": WBColor.YELLOW_DARK.value},
                            condition=dp.Condition(operator=Operator.EQUAL, value=ESGControveryFlag.ORANGE.value),
                        ),
                        dp.FormattingRule(
                            style={"background-color": WBColor.GREEN_LIGHT.value},
                            condition=dp.Condition(operator=Operator.EQUAL, value=ESGControveryFlag.UNKNOWN.value),
                        ),
                    ],
                    column="flag",
                )
            ],
            legends=[
                dp.Legend(
                    label="Flag",
                    items=[
                        dp.LegendItem(icon="#99c140", label="Green"),
                        dp.LegendItem(icon="#fdfd96", label="Yellow"),
                        dp.LegendItem(icon="#db7b2b", label="Orange"),
                        dp.LegendItem(icon="#cc3232", label="Red"),
                        dp.LegendItem(icon="#d3d3d3", label="Unknown"),
                    ],
                )
            ],
        )


class InstrumentESGPAIDisplayViewConfig(DisplayViewConfig):
    def get_list_display(self) -> dp.ListDisplay:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="section", label=_("Section"), width=90),
                dp.Field(key="asi", label=_("Adverse sustainability indicator")),
                dp.Field(key="metric", label=_("Metric")),
                dp.Field(key="factor", label=_("Factor"), width=450),
                dp.Field(key="value", label=_("Value"), width=120),
            ],
        )
