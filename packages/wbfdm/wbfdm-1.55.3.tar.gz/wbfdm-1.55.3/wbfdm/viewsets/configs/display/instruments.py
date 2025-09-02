from contextlib import suppress
from typing import Optional

from django.utils.translation import gettext as _
from dynamic_preferences.registries import global_preferences_registry
from rest_framework.reverse import reverse
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import DisplayViewConfig
from wbcore.metadata.configs.display.instance_display.layouts.inlines import Inline
from wbcore.metadata.configs.display.instance_display.layouts.layouts import Layout
from wbcore.metadata.configs.display.instance_display.pages import Page
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_page_with_inline,
    create_simple_section,
    default,
)
from wbcore.metadata.configs.display.instance_display.styles import Style
from wbcore.metadata.configs.display.instance_display.utils import repeat, repeat_field

from wbfdm.contrib.metric.viewsets.configs.utils import (
    get_performance_fields,
    get_statistic_field,
)
from wbfdm.models import Instrument

ALL_GRIDS = [
    "swe-summary",
    "swe-income-statement",
    "swe-balance-sheet",
    "swe-cashflow-statement",
    "swe-ratios",
    "swe-margins",
    "swe-cashflow-ratios",
    "swe-asset-turnover-ratios",
    "swe-credit",
    "swe-long-term-solvency",
    "swe-short-term-liquidity",
]


def _get_hierarchy_section_title(instrument_id):
    with suppress(Instrument.DoesNotExist):
        instrument = Instrument.objects.get(id=instrument_id)
        if instrument.children.exists():
            if instrument.level == 0:
                return "Securities"
            elif instrument.level == 1:
                return "Quotes"
    return "Children"


def get_financial_summary_section_name() -> str:
    try:
        return global_preferences_registry.manager()["wbfdm__financial_summary_section_name"]
    except Exception:
        return "Financial Summary"


def remove_ref_from_list(grid_list: list, ref: str) -> list[str]:
    _l = grid_list.copy()
    _l.remove(ref)
    return _l


class InstrumentDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label=_("Name"), pinned="left"),
                dp.Field(
                    key=None,
                    label=_("Information"),
                    open_by_default=False,
                    children=[
                        dp.Field(key="instrument_type", label=_("Instrument Type"), show="open"),
                        dp.Field(key="exchange", label=_("Exchange")),
                        dp.Field(key="isin", label=_("ISIN")),
                        dp.Field(key="ticker", label=_("Ticker")),
                        dp.Field(key="refinitiv_identifier_code", label=_("RIC")),
                        dp.Field(key="refinitiv_mnemonic_code", label=_("Refinitiv Mnemonic")),
                        dp.Field(key="description", label=_("Description"), show="open"),
                        dp.Field(key="currency", label=_("Currency"), show="open"),
                        dp.Field(key="country", label=_("Country"), show="open"),
                        dp.Field(key="classifications", label="Classifications", show="open"),
                        dp.Field(key="tags", label="Tags", show="open"),
                    ],
                ),
                dp.Field(
                    key=None,
                    label=_("Extra"),
                    open_by_default=False,
                    children=[
                        dp.Field(key="is_primary", label=_("Primary")),
                        dp.Field(key="is_investable_universe", label=_("Investable Universe"), show="open"),
                        dp.Field(key="is_security", label=_("Security"), show="open"),
                        dp.Field(key="is_managed", label=_("Internally Managed"), show="open"),
                    ],
                ),
                dp.Field(key=None, label=_("Performance"), open_by_default=False, children=get_performance_fields()),
                get_statistic_field(),
            ],
            tree=True,
            tree_group_field="name",
            tree_group_level_options=[
                dp.TreeGroupLevelOption(
                    filter_key="parent",
                    filter_depth=1,
                    filter_blacklist=["parent__isnull"],
                    list_endpoint=reverse(
                        "wbfdm:instrument-list",
                        args=[],
                        request=self.request,
                    ),
                )
            ],
        )

    def get_instance_display(self):
        return Display(
            pages=[
                Page(
                    title="Home",
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["name", "ticker", "isin", "exchange", "market_data_chart", "valuation_ratios-new"],
                                [
                                    "name_repr",
                                    "instrument_type",
                                    "currency",
                                    "country",
                                    "market_data_chart",
                                    "valuation_ratios-new",
                                ],
                                [
                                    "inception_date",
                                    "delisted_date",
                                    ".",
                                    ".",
                                    "market_data_chart",
                                    "valuation_ratios-new",
                                ],
                                [
                                    "description",
                                    "description",
                                    "description",
                                    "description",
                                    "market_data_chart",
                                    "valuation_ratios-new",
                                ],
                                [repeat_field(4, "fin-summary"), repeat_field(2, ".")],
                            ],
                            grid_template_rows=["min-content"] * 3 + ["1fr", "446px"],
                            grid_template_columns=[repeat(4, "183px"), "1fr", "1fr"],
                            inlines=[
                                Inline(key="market_data_chart", endpoint="market_data", title="Prices"),
                                Inline(key="valuation_ratios-new", endpoint="valuation_ratios-new", title="Ratios"),
                                Inline(
                                    key="fin-summary",
                                    endpoint="fin-summary",
                                    title="Financial Summary",
                                    hide_controls=True,
                                ),
                            ],
                        ),
                    },
                ),
                Page(
                    title="Fundamentals",
                    display=Display(
                        navigation_type=dp.NavigationType.PANEL,
                        pages=[
                            create_simple_page_with_inline("Summary", "swe-summary"),
                            create_simple_page_with_inline("Income Statement", "swe-income-statement"),
                            create_simple_page_with_inline("Balance Sheet", "swe-balance-sheet"),
                            create_simple_page_with_inline("Cashflow Statement", "swe-cashflow-statement"),
                            create_simple_page_with_inline("Ratios", "swe-ratios"),
                        ],
                    ),
                ),
                Page(
                    title="Performance",
                    display=Display(
                        navigation_type=dp.NavigationType.PANEL,
                        pages=[
                            dp.Page(
                                title="Overview",
                                layouts={
                                    default(): dp.Layout(
                                        grid_template_areas=[
                                            ["market_data", "market_data", "market_data"],
                                            ["bestandworstreturns", "performance_summary", "."],
                                        ],
                                        grid_template_rows=["450px", "300px"],
                                        grid_template_columns=["2fr", "2fr", "1fr"],
                                        inlines=[
                                            dp.Inline(key="market_data", endpoint="market_data"),
                                            dp.Inline(
                                                key="performance_summary",
                                                endpoint="performance_summary",
                                                hide_controls=True,
                                                title="Performance Summary",
                                            ),
                                            dp.Inline(
                                                key="bestandworstreturns",
                                                endpoint="bestandworstreturns",
                                                hide_controls=True,
                                                title="Best / Worst Returns",
                                            ),
                                        ],
                                    )
                                },
                            ),
                            create_simple_page_with_inline("Prices", "prices"),
                            create_simple_page_with_inline("Statistics", "financial-statistics"),
                        ],
                    ),
                ),
                Page(
                    title="Classifications & Lists",
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["classifications_list", "instrument_lists"],
                            ],
                            grid_template_columns=[Style.pct(50), Style.pct(50)],
                            sections=[
                                create_simple_section(
                                    key="classifications_list",
                                    title="Classifications",
                                    grid_template_areas=[["classifications_list"]],
                                    inline_key="classifications_list",
                                    collapsible=False,
                                ),
                                create_simple_section(
                                    key="instrument_lists",
                                    title="Instrument Lists",
                                    grid_template_areas=[["instrument_lists"]],
                                    inline_key="instrument_lists",
                                    collapsible=False,
                                ),
                            ],
                        )
                    },
                ),
                # TODO Renable after adapting the code to use financial dataloader
                # Page(
                #     title="Financial Analysis",
                #     layouts={
                #         default(): Layout(
                #             grid_template_areas=[
                #                 ["sect_head_fin_summary", "sect_head_fin_summary"],
                #                 ["summary_table", "summary_table"],
                #                 ["sect_head_inc_cf_summary", "sect_head_inc_cf_summary"],
                #                 ["financials_graph", "cash_flow_analysis_chart"],
                #                 ["sect_head_profit_debt_summary", "sect_head_profit_debt_summary"],
                #                 ["profitability_ratios", "net_debt_and_ebitda_chart"],
                #                 ["sect_head_earnings", "sect_head_earnings"],
                #                 ["earnings_chart_ttm", "earnings_chart_ntm"],
                #             ],
                #             grid_template_rows=[
                #                 Style.px(40),
                #                 Style.px(800),
                #                 Style.px(40),
                #                 Style.px(500),
                #                 Style.px(40),
                #                 Style.px(500),
                #                 Style.px(40),
                #                 Style.px(500),
                #             ],
                #             inlines=[
                #                 Inline(key="summary_table", endpoint="summary_table"),
                #                 Inline(key="financials_graph", endpoint="financials_graph"),
                #                 Inline(key="profitability_ratios", endpoint="profitability_ratios"),
                #                 Inline(key="cash_flow_analysis_chart", endpoint="cash_flow_analysis_chart"),
                #                 Inline(key="net_debt_and_ebitda_chart", endpoint="net_debt_and_ebitda_chart"),
                #                 Inline(key="earnings_chart_ttm", endpoint="earnings_chart_ttm"),
                #                 Inline(key="earnings_chart_ntm", endpoint="earnings_chart_ntm"),
                #             ],
                #             sections=[
                #                 create_simple_section(key="sect_head_fin_summary", title="Financial Summary"),
                #                 create_simple_section(
                #                     key="sect_head_inc_cf_summary",
                #                     title="Income Statement and Cash Flow Summary Charts",
                #                 ),
                #                 create_simple_section(
                #                     key="sect_head_profit_debt_summary",
                #                     title="Profitability and Net Debt Summary Charts",
                #                 ),
                #                 create_simple_section(key="sect_head_earnings", title="Earnings Analysis"),
                #             ],
                #         )
                #     },
                # ),
                # Page(
                #     title="Valuation Ratios",
                #     layouts={
                #         default(): Layout(
                #             grid_template_areas=[
                #                 ["valuation_ratios_ranges", "valuation_ratios_related"],
                #             ],
                #             grid_template_columns=[Style.pct(50), Style.pct(50)],
                #             grid_template_rows=[Style.px(575), Style.fr(1)],
                #             inlines=[
                #                 Inline(key="valuation_ratios_ranges", endpoint="valuation_ratios_ranges"),
                #                 Inline(key="valuation_ratios_related", endpoint="valuation_ratios_related"),
                #             ],
                #         )
                #     },
                # ),
                Page(
                    title="Management",
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["ticker", "refinitiv_identifier_code", "refinitiv_mnemonic_code", "identifier"],
                                ["base_color", "old_isins", "is_cash", "."],
                                ["tags", "tags", "related", "related"],
                            ],
                            grid_template_columns=[repeat(4, Style.fr(1))],
                            inlines=[
                                Inline(key="exchanges", endpoint="exchanges"),
                                Inline(key="related", endpoint="related_instruments"),
                            ],
                        )
                    },
                ),
                Page(
                    title=_("Hierarchy"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[["children"]],
                            inlines=[Inline(key="children", endpoint="children")],
                            grid_template_columns=[
                                "minmax(min-content, 1fr)",
                            ],
                            grid_template_rows=["1fr"],
                        ),
                    },
                ),
                Page(
                    title=_("News"),
                    layouts={
                        default(): Layout(
                            grid_template_areas=[["news"]],
                            inlines=[Inline(key="news", endpoint="news")],
                            grid_template_columns=[
                                "minmax(min-content, 1fr)",
                            ],
                            grid_template_rows=["1fr"],
                        ),
                    },
                ),
            ]
        )
