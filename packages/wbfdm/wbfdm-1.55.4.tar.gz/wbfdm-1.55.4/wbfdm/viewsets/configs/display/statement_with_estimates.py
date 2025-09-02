import typing

from rest_framework.reverse import reverse
from wbcore.contrib.color.enums import WBColor
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import DisplayViewConfig

if typing.TYPE_CHECKING:
    from wbfdm.viewsets import StatementWithEstimatesPandasViewSet


class StatementWithEstimatesDisplayViewConfig(DisplayViewConfig):
    view: "StatementWithEstimatesPandasViewSet"

    ESTIMATE_COLOR = "#D2E5F6"
    DEFAULT_COL_WIDTH = 100

    def get_list_display(self) -> dp.ListDisplay:
        def generate_formatting_rules(col_key: str) -> typing.Iterator[dp.FormattingRule]:
            yield dp.FormattingRule(
                style={"color": WBColor.RED_DARK.value, "fontWeight": "bold"},
                condition=[("<", 0), ("!=", "Net Debt", "financial"), ("!=", "Net Debt/Shares", "financial")],
            )
            yield dp.FormattingRule(
                condition=[("<", 0), ("==", "Net Debt", "financial")],
                style={"color": WBColor.GREEN_DARK.value, "fontWeight": "bold"},
            )
            yield dp.FormattingRule(
                condition=[("<", 0), ("==", "Net Debt/Shares", "financial")],
                style={"color": WBColor.GREEN_DARK.value, "fontWeight": "bold"},
            )
            yield dp.FormattingRule(
                condition=[(">", 0), ("==", "Net Debt", "financial")],
                style={"color": WBColor.RED_DARK.value, "fontWeight": "bold"},
            )
            yield dp.FormattingRule(
                condition=[(">", 0), ("==", "Net Debt/Shares", "financial")],
                style={"color": WBColor.RED_DARK.value, "fontWeight": "bold"},
            )
            if self.view.estimate_mapping[col_key] is True:
                yield dp.FormattingRule(style={"background-color": self.ESTIMATE_COLOR})

        def generate_year_field(year_col) -> dp.Field:
            year = year_col[:-2]
            year_column = dp.Field(
                key=year,
                label=year,
                open_by_default=year_col in self.view.year_columns and bool(self.view.df[year_col].isna().all()),
                children=[
                    *map(
                        lambda interim_col: dp.Field(
                            key=interim_col,
                            label=interim_col[5:],
                            show="open",
                            formatting_rules=generate_formatting_rules(interim_col),
                            width=self.DEFAULT_COL_WIDTH,
                        ),
                        filter(lambda col: year in col, self.view.interim_columns),
                    ),
                    dp.Field(
                        key=year_col,
                        label="Y",
                        formatting_rules=generate_formatting_rules((year_col)),
                        width=self.DEFAULT_COL_WIDTH,
                    ),
                ],
            )

            return year_column

        return dp.ListDisplay(
            fields=[
                dp.Field(key="financial", label="Financial", pinned="left"),
                dp.Field(key="progress", label="Yearly Trend", pinned="left"),
                *map(generate_year_field, self.view.year_columns),
            ],
            legends=[dp.Legend(items=[dp.LegendItem(label="Estimated", icon=self.ESTIMATE_COLOR)])],
            # formatting=[
            #     dp.Formatting(
            #         column="financial",
            #         formatting_rules=[
            #             dp.FormattingRule(
            #                 condition=("==", "Net Debt/Shares"),
            #                 style={"color": "red"},
            #             )
            #         ]
            #     )
            # ],
            tree=True,
            tree_group_field="financial",
            tree_group_level_options=[
                dp.TreeGroupLevelOption(
                    list_endpoint=reverse(
                        "wbfdm:financial_metric_analysis-list",
                        args=[self.view.kwargs.get("instrument_id")],
                        request=self.request,
                    ),
                )
            ],
        )
