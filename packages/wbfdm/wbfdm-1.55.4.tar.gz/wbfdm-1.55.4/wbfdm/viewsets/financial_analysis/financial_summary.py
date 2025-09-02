import pandas as pd
from django.contrib.messages import warning
from django.utils.functional import cached_property
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.metadata.configs.endpoints import NoEndpointViewConfig
from wbcore.pandas import fields as pf
from wbcore.pandas.utils import (
    override_number_to_decimal,
    override_number_to_integer_without_decorations,
    override_number_to_percent,
    override_number_to_x,
    pct_change_with_negative_values,
    sanitize_fields,
)

from wbfdm.enums import Financial
from wbfdm.models.instruments import Instrument
from wbfdm.viewsets.configs.display import (
    FinancialSummaryDisplayViewConfig,
)

from ..mixins import InstrumentMixin


class FinancialSummary(InstrumentMixin, ExportPandasAPIViewSet):
    queryset = Instrument.objects.none()
    display_config_class = FinancialSummaryDisplayViewConfig
    ordering_fields = "__all__"
    endpoint_config_class = NoEndpointViewConfig

    def get_queryset(self):
        return Instrument.objects.filter(id=self.instrument.id)

    def get_pandas_fields(self, request):
        return pf.PandasFields(
            fields=[
                pf.PKField(key="id", label="ID"),
                pf.CharField(key="label", label="Financial"),
                pf.JsonField(key="_overwrites", label="Overwrites"),
                *[pf.FloatField(key=k, label=k, precision=1) for k in self.fiscal_columns],
            ]
        )

    def add_messages(self, request, instance=None, **kwargs):
        super().add_messages(request, instance=instance, **kwargs)
        if self.df.empty:
            warning(request, "There is no data available for the Financial Summary table", extra_tags="auto_close=0")

    def get_dataframe(self, request, queryset, **kwargs):
        # Get all necessary data from the dataloader and load a dataframe
        df = pd.DataFrame(
            queryset.dl.financials(
                values=self.FINANCIAL_VALUES,
                from_index=-5,
                to_index=3,
            )
        )
        if not df.empty:
            # Pivot the data
            df = df.pivot_table(
                columns="financial",
                index=["year", "period_end_date", "estimate"],
                values="value",
            ).rename_axis(columns=None)

            sanitize_fields(df, map(lambda enum: enum.value, self.FINANCIAL_VALUES))

            # Compute all necessary fields
            df["revenue_growth"] = df["revenue"].pct_change() * 100
            df["gross_profit_pct"] = df["gross_profit"] / df["revenue"] * 100
            df["ebitda_pct"] = df["ebitda"] / df["revenue"] * 100
            df["ebit_pct"] = df["ebit"] / df["revenue"] * 100
            df["net_income_pct"] = df["net_income"] / df["revenue"] * 100
            df["eps_growth"] = pct_change_with_negative_values(df, "eps") * 100

            df["net_debt_ebitda"] = df["net_debt"] / df["ebitda"]
            df["debt_assets"] = df["total_debt"] / df["total_assets"] * 100
            df["debt_equity"] = df["total_debt"] / df["total_assets"] * 100

            df["interest_coverage_ratio"] = df["ebit"] / df["interest_expense"]
            df["free_cash_flow_per_share"] = df["free_cash_flow"] / df["shares_outstanding"]
            df["free_cash_flow_per_share_growth"] = (
                pct_change_with_negative_values(df, "free_cash_flow_per_share") * 100
            )

            # Normalize data
            df["revenue"] = df["revenue"] / 1_000_000
            df["net_income"] = df["net_income"] / 1_000_000

            # Sort the columns into the desired order
            # Reset the index to get the period end date as a column
            # Pivot back to have the dates on top
            df = df[self.FIELDS]

            # Reset the 2 indices and transpose back
            df = df.reset_index(level=[0, 2]).sort_index()

            # Adjust the columns to be in a different format
            df.index = df.index.map(lambda x: x.strftime("%b/%y"))
            MAX_ROW = 8
            if df.shape[0] > MAX_ROW:
                df = df.iloc[1:]  # remove first row
                df = df.iloc[0 : min([df.shape[0], MAX_ROW])]  # keep only 8 row maximum

            self._estimate_columns = df["estimate"].to_dict()
            df = df.drop(columns=["estimate"], errors="ignore")
        return df

    def manipulate_dataframe(self, df):
        if not df.empty:
            df = df.T
            # Add labels for human readable output
            df["label"] = self.LABELS

            override_number_to_percent(
                df,
                *list(
                    map(
                        lambda x: df.index == x,
                        [
                            "revenue_growth",
                            "gross_profit_pct",
                            "ebitda_pct",
                            "ebit_pct",
                            "net_income_pct",
                            "eps_growth",
                            "roe",
                            "roic",
                            "roc",
                            "roa",
                            "debt_equity",
                            "debt_assets",
                            "free_cash_flow_per_share_growth",
                        ],
                    )
                ),
            )

            override_number_to_x(
                df,
                *list(
                    map(
                        lambda x: df.index == x,
                        [
                            "net_debt_ebitda",
                            "interest_coverage_ratio",
                        ],
                    )
                ),
            )

            override_number_to_decimal(
                df,
                *list(
                    map(
                        lambda x: df.index == x,
                        [
                            "revenue",
                            "net_income",
                        ],
                    )
                ),
            )

            override_number_to_integer_without_decorations(
                df,
                *list(
                    map(
                        lambda x: df.index == x,
                        [
                            "year",
                        ],
                    )
                ),
            )

            df = df.reset_index(names="id")
        return df

    @cached_property
    def fiscal_columns(self) -> list:
        """Returns the fiscal columns from the dataframe"""
        return self.df.columns.difference(["label", "_overwrites", "id"]).to_list()

    @cached_property
    def estimate_columns(self) -> dict:
        """Returns a dictionary with the estimate column for each fiscal column
        The _estimate_columns will be set if the dataframe is constructed.
        """
        return getattr(self, "_estimate_columns", {})

    @cached_property
    def FINANCIAL_VALUES(self) -> list[Financial]:
        return [
            Financial.REVENUE,  # SAL
            Financial.GROSS_PROFIT,  # GRI
            Financial.EBITDA,  # EBT
            Financial.EBIT,  # EBI
            Financial.NET_INCOME,  # NET
            Financial.EPS,  # EPS
            Financial.SHAREHOLDERS_EQUITY,  # SHE
            Financial.TOTAL_ASSETS,  # TAS
            Financial.TAX_RATE,  # TAX
            Financial.RETURN_ON_INVESTED_CAPITAL,  # RIC
            Financial.NET_DEBT,  # NDT
            Financial.TOTAL_DEBT,  # TDT
            Financial.INTEREST_EXPENSE,  # INE
            Financial.FREE_CASH_FLOW,  # FCF
            Financial.SHARES_OUTSTANDING,
            Financial.CURRENT_LIABILITIES,  # CRL
            Financial.CASH_EQUIVALENTS,
            Financial.RETURN_ON_EQUITY,
            Financial.RETURN_ON_ASSETS,
            Financial.RETURN_ON_CAPITAL,
            Financial.RETURN_ON_INVESTED_CAPITAL,
        ]

    @cached_property
    def FIELDS(self) -> list[str]:
        return [
            "revenue",
            "revenue_growth",
            "gross_profit_pct",
            "ebitda_pct",
            "ebit_pct",
            "net_income_pct",
            "net_income",
            "eps",
            "eps_growth",
            "roe",
            "roa",
            "roc",
            "roic",
            "net_debt_ebitda",
            "debt_assets",
            "debt_equity",
            "interest_coverage_ratio",
            "free_cash_flow_per_share",
            "free_cash_flow_per_share_growth",
        ]

    @property
    def LABELS(self) -> list[str]:
        currency_key = self.instrument.currency.key if self.instrument.currency else "N.A."
        return [
            f"in {currency_key} MN",
            "Revenue",
            "Y/Y Change",
            "Gross Margin",
            "EBITDA Margin",
            "EBIT Margin",
            "Net Profit Margin",
            "Net Profit",
            "EPS",
            "Y/Y Change",
            "ROE",
            "ROA",
            "ROC",
            "ROIC",
            "Net Debt/EBITDA",
            "D/A",
            "D/E",
            "Int. Cov. Ratio",
            "FCF per share",
            "Y/Y Change",
        ]
