from contextlib import suppress

from rest_framework.reverse import reverse
from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons import ButtonViewConfig

from wbfdm.models import Instrument


class ChildrenInstrumentModelViewConfig(ButtonViewConfig):
    SHOW_INLINE = True

    def get_custom_buttons(self) -> set:
        with suppress(Instrument.DoesNotExist):
            instrument = Instrument.objects.get(id=self.view.kwargs.get("instrument_id"))
            if instrument.parent:
                return {
                    bt.WidgetButton(
                        label="Parent",
                        endpoint=reverse("wbfdm:instrument-detail", args=[instrument.parent.id], request=self.request),
                    ),
                }
        return set()


class InstrumentButtonViewConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self) -> set:
        return {*super().get_custom_list_instance_buttons(), *self.get_custom_instance_buttons()}

    def get_custom_instance_buttons(self):
        return {
            bt.DropDownButton(
                label="Performance Analysis",
                weight=1,
                icon=WBIcon.UNFOLD.icon,
                buttons=(
                    bt.WidgetButton(
                        weight=0,
                        label="Prices",
                        icon=WBIcon.DOLLAR.icon,
                        key="prices",
                    ),
                    bt.WidgetButton(
                        weight=1,
                        key="bestandworstreturns",
                        label="Best and Worst Returns Table",
                        icon=WBIcon.INVERSE.icon,
                    ),
                    bt.WidgetButton(
                        weight=2,
                        label="Monthly Performances",
                        icon=WBIcon.TABLE.icon,
                        key="monthly_performances",
                    ),
                    bt.WidgetButton(
                        label="Financial Statistics",
                        weight=3,
                        icon=WBIcon.CHART_WATERFALL.icon,
                        key="financial-statistics",
                    ),
                    bt.DropDownButton(
                        label="Valuations",
                        weight=4,
                        icon=WBIcon.UNFOLD.icon,
                        buttons=[
                            bt.WidgetButton(
                                key="instrumentprices", label="Price and Performance", icon=WBIcon.DOLLAR.icon
                            ),
                            bt.WidgetButton(
                                key="instrumentpricestatisticchart",
                                label="Price Statistical Chart",
                                icon=WBIcon.CHART_MULTILINE.icon,
                            ),
                        ],
                    ),
                    bt.DropDownButton(
                        label="Charts",
                        weight=1000,
                        icon=WBIcon.UNFOLD.icon,
                        buttons=(
                            bt.WidgetButton(
                                label="Market Data Chart",
                                weight=0,
                                icon=WBIcon.CHART_LINE.icon,
                                key="market_data",
                            ),
                            bt.WidgetButton(
                                label="Drawdown Chart",
                                weight=1,
                                icon=WBIcon.CHART_AREA.icon,
                                key="drawdown",
                            ),
                            bt.WidgetButton(
                                label="Performance Summary",
                                weight=2,
                                icon=WBIcon.CHART_BARS_VERTICAL.icon,
                                key="performance_summary",
                            ),
                            bt.WidgetButton(
                                label="Cumulative Returns Chart",
                                weight=3,
                                icon=WBIcon.CHART_WATERFALL.icon,
                                key="cumulativereturn",
                            ),
                            bt.WidgetButton(
                                key="distributionreturnschart",
                                label="Distribution Returns Chart",
                                weight=4,
                                icon=WBIcon.CHART_BARS_HORIZONTAL.icon,
                            ),
                            bt.WidgetButton(
                                key="price_and_volume", label="Price And Volume", weight=5, icon=WBIcon.CHART_LINE.icon
                            ),
                        ),
                    ),
                ),
            ),
            bt.DropDownButton(
                label="Financial Analysis",
                icon=WBIcon.UNFOLD.icon,
                weight=2,
                buttons=[
                    bt.WidgetButton(
                        label="Income Statement",
                        weight=0,
                        icon=WBIcon.DOCUMENT_WITH_DOLLAR.icon,
                        key="income-statement",
                    ),
                    bt.WidgetButton(
                        label="Balance Sheet",
                        weight=1,
                        icon=WBIcon.ACCOUNT_BALANCE.icon,
                        key="balance-sheet",
                    ),
                    bt.WidgetButton(
                        label="Cash Flow Statement",
                        weight=2,
                        icon=WBIcon.CURRENCY_EXCHANGE.icon,
                        key="cash-flow-statement",
                    ),
                    bt.DropDownButton(
                        label="IBES",
                        weight=3,
                        icon=WBIcon.UNFOLD.icon,
                        buttons=(
                            bt.WidgetButton(
                                label="Summary",
                                weight=0,
                                icon=WBIcon.DATA_EXPLORATION.icon,
                                key="swe-summary",
                            ),
                            bt.WidgetButton(
                                label="Income Statement / Estimates",
                                weight=1,
                                icon=WBIcon.DOCUMENT_WITH_DOLLAR.icon,
                                key="swe-income-statement",
                            ),
                            bt.WidgetButton(
                                label="Balance Sheet / Estimates",
                                weight=2,
                                icon=WBIcon.ACCOUNT_BALANCE.icon,
                                key="swe-balance-sheet",
                            ),
                            bt.WidgetButton(
                                label="Cash Flow / Estimates",
                                weight=3,
                                icon=WBIcon.CURRENCY_EXCHANGE.icon,
                                key="swe-cashflow-statement",
                            ),
                            bt.WidgetButton(
                                label="Ratios / Estimates",
                                weight=4,
                                icon=WBIcon.DATA_EXPLORATION.icon,
                                key="swe-ratios",
                            ),
                            bt.WidgetButton(
                                label="Margins",
                                weight=5,
                                icon=WBIcon.DATA_EXPLORATION.icon,
                                key="swe-margins",
                            ),
                            bt.WidgetButton(
                                label="Cashflow Ratios",
                                weight=6,
                                icon=WBIcon.DATA_EXPLORATION.icon,
                                key="swe-cashflow-ratios",
                            ),
                            bt.WidgetButton(
                                label="Asset Turnover Ratios",
                                weight=7,
                                icon=WBIcon.DATA_EXPLORATION.icon,
                                key="swe-asset-turnover-ratios",
                            ),
                            bt.WidgetButton(
                                label="Credit Ratios",
                                weight=8,
                                icon=WBIcon.DATA_EXPLORATION.icon,
                                key="swe-credit",
                            ),
                            bt.WidgetButton(
                                label="Long-Term Solvency Ratios",
                                weight=9,
                                icon=WBIcon.DATA_EXPLORATION.icon,
                                key="swe-long-term-solvency",
                            ),
                            bt.WidgetButton(
                                label="Short-Term Liquidity Ratios",
                                weight=10,
                                icon=WBIcon.DATA_EXPLORATION.icon,
                                key="swe-short-term-liquidity",
                            ),
                        ),
                    ),
                ],
            ),
            bt.WidgetButton(
                label="Officers",
                icon=WBIcon.PEOPLE.icon,
                key="officers",
            ),
            bt.DropDownButton(
                label="ESG",
                icon=WBIcon.UNFOLD.icon,
                weight=3,
                buttons=[
                    bt.WidgetButton(
                        label="Controversies",
                        icon=WBIcon.EVENT.icon,
                        key="controversies",
                    ),
                    bt.WidgetButton(
                        label="PAI",
                        icon=WBIcon.CHART_SWITCHES.icon,
                        key="pai",
                    ),
                ],
            ),
            # bt.DropDownButton(
            #     label="Financial Analysis (Old)",
            #     weight=3,
            #     icon=WBIcon.UNFOLD.icon,
            #     buttons=(
            #         bt.WidgetButton(
            #             key="summary_table",
            #             label="Summary Table",
            #             icon=WBIcon.TABLE.icon,
            #         ),
            #         bt.WidgetButton(
            #             key="financials_graph",
            #             label="Financials Graph",
            #             icon=WBIcon.CHART_BARS_HORIZONTAL.icon,
            #         ),
            #         bt.WidgetButton(
            #             key="profitability_ratios",
            #             label="Profitability Ratios",
            #             icon=WBIcon.CHART_LINE.icon,
            #         ),
            #         bt.WidgetButton(
            #             key="cash_flow_analysis_table",
            #             label="Cash Flow Analysis Table",
            #             icon=WBIcon.TABLE.icon,
            #         ),
            #         bt.WidgetButton(
            #             key="cash_flow_analysis_chart",
            #             label="Cash Flow Analysis Chart",
            #             icon=WBIcon.CHART_BARS_HORIZONTAL.icon,
            #         ),
            #         bt.WidgetButton(
            #             key="net_debt_and_ebitda_chart",
            #             label="Net Debt And EBITDA Analysis Chart",
            #             icon=WBIcon.CHART_BARS_HORIZONTAL.icon,
            #         ),
            #         bt.WidgetButton(
            #             key="valuation_ratios-old",
            #             label="Valuation Ratios",
            #             icon=WBIcon.CHART_MULTILINE.icon,
            #         ),
            #         bt.WidgetButton(
            #             key="earnings_chart",
            #             label="Earnings Analysis",
            #             icon=WBIcon.CHART_LINE.icon,
            #         ),
            #     ),
            # ),
        }
