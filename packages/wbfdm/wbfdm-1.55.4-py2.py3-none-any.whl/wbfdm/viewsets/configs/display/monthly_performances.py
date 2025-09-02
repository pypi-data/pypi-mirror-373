from typing import Optional

from wbcore.contrib.color.enums import WBColor
from wbcore.enums import Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import DisplayViewConfig

perf_formatting_rules = [
    dp.FormattingRule(
        style={
            "color": WBColor.RED_DARK.value,
        },
        condition=("<", 0),
    ),
    dp.FormattingRule(
        style={
            "color": WBColor.GREEN_DARK.value,
        },
        condition=(">", 0),
    ),
]
perf_formatting_rules_bold = [
    dp.FormattingRule(
        style={
            "color": WBColor.RED_DARK.value,
            "fontWeight": "bold",
        },
        condition=("<", 0),
    ),
    dp.FormattingRule(
        style={
            "color": WBColor.GREEN_DARK.value,
            "fontWeight": "bold",
        },
        condition=(">", 0),
    ),
]


class MonthlyPerformancesInstrumentDisplayViewConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(
                    key="year",
                    label="Year",
                    width=Unit.PIXEL(75),
                    formatting_rules=[
                        dp.FormattingRule(
                            style={
                                "fontWeight": "bold",
                            },
                        ),
                    ],
                ),
                dp.Field(key="1", label="Jan", width=Unit.PIXEL(75), formatting_rules=perf_formatting_rules),
                dp.Field(key="2", label="Feb", width=Unit.PIXEL(75), formatting_rules=perf_formatting_rules),
                dp.Field(key="3", label="Mar", width=Unit.PIXEL(75), formatting_rules=perf_formatting_rules),
                dp.Field(key="4", label="Apr", width=Unit.PIXEL(75), formatting_rules=perf_formatting_rules),
                dp.Field(key="5", label="May", width=Unit.PIXEL(75), formatting_rules=perf_formatting_rules),
                dp.Field(key="6", label="Jun", width=Unit.PIXEL(75), formatting_rules=perf_formatting_rules),
                dp.Field(key="7", label="Jul", width=Unit.PIXEL(75), formatting_rules=perf_formatting_rules),
                dp.Field(key="8", label="Aug", width=Unit.PIXEL(75), formatting_rules=perf_formatting_rules),
                dp.Field(key="9", label="Sep", width=Unit.PIXEL(75), formatting_rules=perf_formatting_rules),
                dp.Field(key="10", label="Oct", width=Unit.PIXEL(75), formatting_rules=perf_formatting_rules),
                dp.Field(key="11", label="Nov", width=Unit.PIXEL(75), formatting_rules=perf_formatting_rules),
                dp.Field(key="12", label="Dec", width=Unit.PIXEL(75), formatting_rules=perf_formatting_rules),
                dp.Field(
                    key="annual", label="Yearly", width=Unit.PIXEL(75), formatting_rules=perf_formatting_rules_bold
                ),
            ]
        )
