import typing

from wbcore.contrib.color.enums import WBColor
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import DisplayViewConfig

if typing.TYPE_CHECKING:
    from wbfdm.viewsets import FinancialSummary


class FinancialSummaryDisplayViewConfig(DisplayViewConfig):
    view: "FinancialSummary"

    ESTIMATE_COLOR = "#D2E5F6"

    def get_list_display(self) -> dp.ListDisplay:
        def generate_formatting_rules(col_key: str) -> typing.Iterator[dp.FormattingRule]:
            yield dp.FormattingRule(
                condition=[("==", "eps_growth", "id")],
                style={
                    "borderBottom": "1px solid #000000",
                },
            )
            yield dp.FormattingRule(
                condition=[("==", "roic", "id")],
                style={
                    "borderBottom": "1px solid #000000",
                },
            )
            yield dp.FormattingRule(
                condition=[("==", "interest_coverage_ratio", "id")],
                style={
                    "borderBottom": "1px solid #000000",
                },
            )
            yield dp.FormattingRule(
                condition=[("==", "revenue_growth", "id")],
                style={
                    "color": "#9FA0A1",
                    "fontStyle": "italic",
                },
            )
            yield dp.FormattingRule(
                condition=[("==", "net_profit_growth", "id")],
                style={
                    "color": "#9FA0A1",
                    "fontStyle": "italic",
                },
            )
            yield dp.FormattingRule(
                condition=[("==", "eps_growth", "id")],
                style={
                    "color": "#9FA0A1",
                    "fontStyle": "italic",
                },
            )
            yield dp.FormattingRule(
                condition=[("==", "free_cash_flow_per_share_growth", "id")],
                style={
                    "color": "#9FA0A1",
                    "fontStyle": "italic",
                },
            )
            yield dp.FormattingRule(
                condition=[("==", "year", "id")],
                style={
                    "fontWeight": "bold",
                },
            )
            yield dp.FormattingRule(
                style={"color": WBColor.RED_DARK.value},
                condition=[("<", 0)],
            )
            if self.view.estimate_columns.get(col_key, False) is True:
                yield dp.FormattingRule(style={"background-color": self.ESTIMATE_COLOR})

        def generate_field(col: str) -> dp.Field:
            return dp.Field(
                key=col,
                label=col,
                width=80,
                formatting_rules=generate_formatting_rules(col),
                auto_size=False,
                resizable=False,
                movable=False,
                menu=False,
                size_to_fit=False,
            )

        return dp.ListDisplay(
            fields=[
                dp.Field(
                    key="label",
                    label=" ",
                    width=120,
                    auto_size=False,
                    resizable=False,
                    movable=False,
                    menu=False,
                    size_to_fit=False,
                    formatting_rules=[
                        dp.FormattingRule(
                            condition=[("==", "eps_growth", "id")],
                            style={
                                "borderBottom": "1px solid #000000",
                            },
                        ),
                        dp.FormattingRule(
                            condition=[("==", "roic", "id")],
                            style={
                                "borderBottom": "1px solid #000000",
                            },
                        ),
                        dp.FormattingRule(
                            condition=[("==", "interest_coverage_ratio", "id")],
                            style={
                                "borderBottom": "1px solid #000000",
                            },
                        ),
                        dp.FormattingRule(style={"background-color": "#ECECEC"}),
                        dp.FormattingRule(
                            condition=[("==", "year", "id")],
                            style={
                                "fontWeight": "bold",
                            },
                        ),
                    ],
                ),
                *map(generate_field, self.view.fiscal_columns),
            ],
            condensed=True,
            editable=False,
        )
