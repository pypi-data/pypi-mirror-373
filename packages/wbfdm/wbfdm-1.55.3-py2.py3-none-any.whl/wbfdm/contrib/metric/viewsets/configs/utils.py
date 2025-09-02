from django.utils.translation import gettext_lazy as _
from wbcore.contrib.color.enums import WBColor
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.formatting import Condition, Operator

PERFORMANCE_FORMATTING = [
    dp.FormattingRule(
        style={"color": WBColor.GREY.value, "fontWeight": "bold"},
        condition=Condition(Operator("=="), 0),
    ),
    dp.FormattingRule(
        style={"color": WBColor.RED_DARK.value, "fontWeight": "bold"},
        condition=Condition(Operator("<"), 0),
    ),
    dp.FormattingRule(
        style={"color": WBColor.GREEN_DARK.value, "fontWeight": "bold"},
        condition=Condition(Operator(">"), 0),
    ),
]

BORDER_LEFT = dp.FormattingRule(
    style={
        "borderLeft": "1px solid #bdc3c7",
    }
)


def get_performance_fields(with_comparison_performances: bool = False) -> list[dp.Field]:
    def _get_performance_field(key: str, label: str, show=None):
        if not with_comparison_performances:
            return dp.Field(
                key=f"performance_{key}",
                label=label,
                width=100,
                formatting_rules=PERFORMANCE_FORMATTING,
            )
        return dp.Field(
            key=None,
            label=label,
            width=100,
            show=show,
            children=[
                dp.Field(
                    key=f"performance_{key}",
                    label="Absolute",
                    width=100,
                    formatting_rules=PERFORMANCE_FORMATTING + [BORDER_LEFT],
                ),
                dp.Field(
                    key=f"performance_peer_{key}",
                    label="vs Peer",
                    width=100,
                    formatting_rules=PERFORMANCE_FORMATTING,
                    show="open",
                    tooltip=dp.Tooltip(key="peers"),
                ),
                dp.Field(
                    key=f"performance_benchmark_{key}",
                    label="vs Benchmark",
                    width=100,
                    formatting_rules=PERFORMANCE_FORMATTING,
                    show="open",
                    tooltip=dp.Tooltip(key="benchmarks"),
                ),
            ],
        )

    return [
        dp.Field(
            key=None,
            label="Rolling",
            open_by_default=False,
            children=[
                _get_performance_field(key="daily", label="Daily"),
                _get_performance_field(
                    key="weekly",
                    label="Weekly",
                    show="open",
                ),
                _get_performance_field(
                    key="monthly",
                    label="Monthly",
                    show="open",
                ),
                _get_performance_field(
                    key="quarterly",
                    label="Quarterly",
                    show="open",
                ),
                _get_performance_field(
                    key="yearly",
                    label="Yearly",
                    show="open",
                ),
            ],
        ),
        dp.Field(
            key=None,
            label="Performance-To-Date (PTD)",
            open_by_default=False,
            children=[
                _get_performance_field(key="week_to_date", label="Week", show="open"),
                _get_performance_field(key="month_to_date", label="Month"),
                _get_performance_field(key="quarter_to_date", label="Quarter", show="open"),
                _get_performance_field(key="year_to_date", label="Year", show="open"),
            ],
        ),
        dp.Field(
            key=None,
            label="Previous Performance",
            open_by_default=False,
            show="open",
            children=[
                _get_performance_field(key="previous_week_to_date", label="Week", show="open"),
                _get_performance_field(key="previous_month_to_date", label="Month"),
                _get_performance_field(key="previous_quarter_to_date", label="Quarter", show="open"),
                _get_performance_field(key="previous_year_to_date", label="Year", show="open"),
            ],
        ),
        _get_performance_field(key="inception", label="Inception"),
    ]


def get_statistic_field():
    return dp.Field(
        key=None,
        label=_("Fundamentals"),
        open_by_default=False,
        children=[
            dp.Field(key="statistic_price", label="Last Price", width=100),
            dp.Field(key="statistic_market_capitalization", label="Market Capitalization", width=100),
            dp.Field(key="statistic_revenue_y_1", label="Revenue Y-1", width=100, show="closed"),
            dp.Field(key="statistic_revenue_y0", label="Revenue Y", width=100, show="closed"),
            dp.Field(key="statistic_revenue_y1", label="Revenue Y+1", width=100),
            dp.Field(key="statistic_volume_50d", label="Avg Volume (3m)", width=100, show="closed"),
        ],
    )
