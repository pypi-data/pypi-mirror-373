from typing import Optional

from wbcore.contrib.color.enums import WBColor
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbfdm.models import Instrument, InstrumentType

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


class InstrumentPriceDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        base_fields = [
            dp.Field(key="date", label="Date"),
            dp.Field(key="net_value", label="Net Value"),
            dp.Field(key="net_value_usd", label="Net Value ($)"),
            dp.Field(key="daily_diff_net_value", label="Daily Diff.", formatting_rules=perf_formatting_rules),
            dp.Field(key="gross_value", label="Gross Value"),
            dp.Field(key="daily_diff_gross_value", label="Daily Diff.", formatting_rules=perf_formatting_rules),
            dp.Field(key="market_capitalization", label="Market Cap./AUM"),
            dp.Field(key="volume", label="Volume"),
            dp.Field(key="volume_50d", label="Avg Volume (50 days)"),
        ]
        if instrument_id := self.view.kwargs.get("instrument_id", None):
            instrument = Instrument.objects.get(id=instrument_id)
            if instrument.instrument_type == InstrumentType.PRODUCT:
                base_fields.extend(
                    [
                        dp.Field(key="sharpe_ratio", label="Sharpe Ratio"),
                        dp.Field(key="correlation", label="Correlation"),
                        dp.Field(key="beta", label="Beta"),
                        dp.Field(key="outstanding_shares_consolidated", label="Outstanding Shares"),
                    ]
                )
        return dp.ListDisplay(
            fields=base_fields,
            legends=[
                dp.Legend(
                    key="calculated",
                    items=[
                        dp.LegendItem(icon=WBColor.YELLOW.value, label="Calculated", value=True),
                        dp.LegendItem(icon=WBColor.GREEN_LIGHT.value, label="Real", value=False),
                    ],
                ),
            ],
            formatting=[
                dp.Formatting(
                    column="calculated",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.YELLOW.value},
                            condition=("==", True),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=("==", False),
                        ),
                    ],
                ),
            ],
        )


class FinancialStatisticsInstrumentPandasDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(
                    key="financial",
                    label="Financial Statistics",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={
                                "fontWeight": "bold",
                            },
                        ),
                    ],
                ),
                dp.Field(key="instrument_statistics", label="Instrument"),
                dp.Field(key="benchmark_statistics", label="Benchmark"),
                dp.Field(
                    key="instrument_one_year",
                    label="Instrument - One Year",
                ),
                dp.Field(
                    key="benchmark_one_year",
                    label="Benchmark - One Year",
                ),
            ]
        )


class BestAndWorstReturnsInstrumentPandasDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="date_best_returns", label="Date Best Returns"),
                dp.Field(key="best_returns", label="Best Returns"),
                dp.Field(key="date_worst_returns", label="Date Worst Returns"),
                dp.Field(key="worst_returns", label="Worst Returns"),
            ]
        )
