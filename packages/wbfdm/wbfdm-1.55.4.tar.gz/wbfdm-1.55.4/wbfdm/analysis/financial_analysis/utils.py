from collections import defaultdict
from contextlib import suppress
from datetime import date

import pandas as pd
from wbcore.pandas.utils import (
    override_number_to_percent,
    override_number_to_x,
    override_number_with_currency,
)

from wbfdm.enums import CalendarType, Financial, MarketData, PeriodType
from wbfdm.models import Instrument
from wbfdm.utils import rename_period_index_level_to_repr


class Loader:
    """
    Utility Class to load financial data into a Pandas dataframe with year and interim as index.
    """

    def __init__(
        self,
        instrument: Instrument,
        values: list[Financial],
        calendar_type: CalendarType = CalendarType.FISCAL,
        market_data_values: list[MarketData] | None = None,
        statement_values: list[Financial] | None = None,
        period_type: PeriodType = PeriodType.ALL,
    ):
        self.instrument = instrument
        self.calendar_type = calendar_type
        self.values = values
        self.market_data_values = (
            market_data_values  # specify if any extra market data needs to be merged into the dataframe
        )
        self.statement_values = (
            statement_values  # specify if any extra statement needs to be merged into the dataframe
        )
        self.period_type = period_type
        self.errors: dict[str, list[str]] = defaultdict(list)

    def load(self) -> pd.DataFrame:
        """
        entry function of the class, loads the data into the dataframe and normalize it
        """
        return self._normalize_df(*self._get_base_df())

    def _get_base_df(self) -> tuple[pd.DataFrame, pd.Series]:
        """
        Private method to load data into a dataframe and returns the resulting data with index [year, interim] and "financials" as columns. The source pandas series is returned as second argument

        Returns:
            a tuple of dataframe and series
        """
        # Get the base dataframe from a dataloader
        df = pd.DataFrame(
            Instrument.objects.filter(id=self.instrument.id).dl.financials(
                values=self.values,
                from_year=date.today().year - 5,
                calendar_type=self.calendar_type,
                period_type=self.period_type,
            )
        )
        if df.empty:
            self.errors["missing_data"].append("Missing financial data")
            df = pd.DataFrame(
                columns=[
                    "year",
                    "interim",
                    "period_type",
                    "estimate",
                    "period_end_date",
                    "source",
                    "financial",
                    "value",
                ]
            )

        df["period_end_date"] = pd.to_datetime(df["period_end_date"])
        source_df = (
            df[["year", "interim", "period_type", "source"]].groupby(["year", "interim", "period_type"]).first().source
        )
        # Pivot the data around
        df = df.pivot_table(
            index=["year", "interim", "period_type", "estimate", "period_end_date"],
            columns="financial",
            values="value",
        )
        allowed_columns: list[str] = [v.value for v in self.values]
        if self.statement_values and not df.empty:
            df = self._annotate_statement_data(df, self.statement_values)
            allowed_columns.extend([v.value for v in self.statement_values])
        # If market data should be included here, we need to annotate it and afterwards rename the column axis
        if self.market_data_values and not df.empty:
            df = self._annotate_market_data(df, self.market_data_values)
            allowed_columns.extend([v.value for v in self.market_data_values])
        df = df[[value for value in allowed_columns if value in df.columns]]
        return df, source_df

    # UTILS METHODS

    def _annotate_market_data(self, df: pd.DataFrame, market_data_values: list[MarketData]) -> pd.DataFrame:
        """
        Annotate the given market data into the given dataframe

        Args:
            df: a Pandas dataframe to annotate extra data into
            market_data_values:  a list of MarketData objects

        Returns:
            The extended dataframe with market data
        """
        # We need to reset the indexes as we merge based on columns
        market_data_df = pd.DataFrame(
            Instrument.objects.filter(id=self.instrument.id).dl.market_data(
                from_date=df.index.get_level_values("period_end_date").min() if not df.empty else None,
                target_currency=self.instrument.currency.key,
            )
        )
        values = [mdv.value for mdv in market_data_values]
        # We convert the period_end_date column to a native datetime object to allow for merges based on backwards data
        if not market_data_df.empty:
            market_data_df["period_end_date"] = pd.to_datetime(market_data_df["valuation_date"])
            market_data_df = market_data_df[["period_end_date", *values]].sort_values("period_end_date")
            df = pd.merge_asof(
                left=df.reset_index().sort_values(by="period_end_date"),
                right=market_data_df,
                on="period_end_date",
                direction="backward",
            ).set_index(["year", "interim", "period_type", "estimate", "period_end_date"])
            if df[values].dropna().empty:
                self.errors["missing_data"].append(
                    "We could not find any market data covering the financial statement period"
                )
            ## TODO We might want to still exclude them from the final df but keep them for the estimate that used these
            ## we actually want to keep the market data in the forecast column, because they are used for other statistic computation
            # df.loc[df.index.get_level_values("estimate"), market_data_df.columns.difference(["period_end_date"])] = (
            #     None
            # )

        return df.rename_axis("financial", axis="columns")

    def _annotate_statement_data(self, df: pd.DataFrame, statement_values: list[Financial]) -> pd.DataFrame:
        """
        Annotate the given statement into the given dataframe

        Args:
            df: a Pandas dataframe to annotate extra data into
            statement_values:  a list of Financial objects

        Returns:
            The extended dataframe with statement
        """
        statement_df = pd.DataFrame(
            Instrument.objects.filter(id=self.instrument.id).dl.statements(
                financials=statement_values, from_year=date.today().year - 5
            ),
        )

        if not statement_df.empty:
            statement_df["period_end_date"] = pd.to_datetime(statement_df["period_end_date"])
            statement_df = statement_df.pivot_table(
                index=["year", "interim", "period_end_date"], columns="financial", values="value"
            )
            statement_df = statement_df.ffill()
            df = pd.merge(
                how="left",
                left=df.reset_index().sort_values(by="period_end_date"),
                right=statement_df,
                on=["year", "interim"],
            ).set_index(["year", "interim", "period_type", "estimate", "period_end_date"])
        else:
            self.errors["missing_data"].append("No statement data")

        return df.rename_axis("financial", axis="columns")

    def _normalize_df(self, df: pd.DataFrame, source_df: pd.Series) -> pd.DataFrame:
        """
        This private method takes a dataframe and it's related source (a source per index), reset the index to be only (year, interim) and detect any possible duplicated row.

        If a duplicate is detected, we appends the attribute `errors` with the duplicated index and take the first one

        Finally, we rename the index into a more human readable format and make sure the the yearly row is present for every year of data

        Args:
            df: the DataFrame to normalize
            source_df: The Series holding the source info for all the DataFrame index

        Returns:
            A normalized DataFrame
        """

        def _ensure_yearly_row_exists(row):
            row["interim"] = row["interim"].astype(int)
            if row[row["interim"] == 0].empty:
                row = pd.concat(
                    [
                        pd.DataFrame(
                            [
                                {
                                    "year": row.name,
                                    "interim": 0,
                                    "period_type": "Y",
                                    "estimate": True,
                                    "period_end_date": row["period_end_date"].max(),
                                }
                            ]
                        ),
                        row,
                    ],
                    axis=0,
                )
            return row

        new_index = (
            df.index.to_frame(index=False)
            .groupby(["year"], group_keys=False, as_index=False)
            .apply(lambda row: _ensure_yearly_row_exists(row), include_groups=True)
            .reset_index(drop=True)
        )
        df = df.reindex(new_index)

        df = df.sort_index().reset_index(
            level=[3, 4], names=["year", "interim", "period_type", "estimate", "period_end_date"]
        )
        # detect duplicates, gracefully handle it by taking the first but log the error for further usage
        index_duplicated = df.index.duplicated()
        if index_duplicated.any():
            for year, interim, period_type in df.index[index_duplicated]:
                interim_info = f"{year} Interim {period_type}{interim}"
                with suppress(KeyError):
                    if source := source_df.loc[(year, interim, period_type), "source"]:
                        interim_info += f" [{source.upper()}]"
                self.errors["duplicated_interims"].append(interim_info)

            # remove duplicated index
            df = df[~index_duplicated]

        df = rename_period_index_level_to_repr(df)

        return df


class FinancialAnalysisResult:
    """
    Wrapper class to help present a multi index pivoted dataframe with (year, interim) as index and financials as columns into a transposed DataFrame for Tree view

    This transposed dataframe is available under the attribute `formatted_df`
    """

    FINANCIAL_MAP = {**MarketData.name_mapping(), **Financial.name_mapping()}

    def __init__(
        self,
        df,
        ordering: list[str] | None = None,
        ignore_group_keys: list[Financial] | None = None,
        override_number_with_currency: str | None = None,
        override_number_with_currency_financials: list[str] | None = None,
        override_number_to_x_financials: list[str] | None = None,
        override_number_to_percent_financials: list[str] | None = None,
        errors: dict[str, list[str]] | None = None,
    ):
        self.df = df
        self.columns = list(self.df.drop(columns=["estimate", "period_end_date"]).columns)

        if ordering:
            ordering.extend(["estimate", "period_end_date"])
            allowed_columns = list(self.FINANCIAL_MAP.keys())
            self.df = self.df[[col for col in ordering if col in self.df.columns]]
            allowed_columns.extend(ordering)
            self.df = self.df.drop(columns=self.df.columns.difference(allowed_columns))

        if not ignore_group_keys:
            ignore_group_keys = []
        self.ignore_group_keys = ignore_group_keys
        self.override_number_with_currency = override_number_with_currency
        self.override_number_with_currency_financials = override_number_with_currency_financials
        self.override_number_to_x_financials = override_number_to_x_financials
        self.override_number_to_percent_financials = override_number_to_percent_financials
        self.errors = errors

        self.formatted_df, self.estimated_mapping = self._get_formatted_df()

    def _get_formatted_df(self) -> tuple[pd.DataFrame, dict[str, bool]]:
        # Transpose and reset the index twice to create an artificial index-column
        df = self.df.copy()

        # Flatten and Rename index into year-interim format
        df.index = df.index.map(lambda index: f"{index[0]}-{index[1]}")

        # store the estimate per index
        estimated_mapping = df["estimate"].to_dict()

        df = df.drop(columns=["estimate", "period_end_date"])

        # get the group keys minus the one ignored
        group_keys = [col if col not in self.ignore_group_keys and col in Financial else None for col in df.columns]

        # Transpose table
        df = df.T.reset_index().reset_index()

        df["_group_key"] = group_keys

        if "financial" in df.columns:
            # set the _overriding columns to define extra decorator for the frontend
            if self.override_number_with_currency and self.override_number_with_currency_financials:
                override_number_with_currency(
                    df,
                    self.override_number_with_currency,
                    *list(map(lambda x: df["financial"] == x, self.override_number_with_currency_financials)),
                )
            if self.override_number_to_x_financials:
                override_number_to_x(
                    df, *list(map(lambda x: df["financial"] == x, self.override_number_to_x_financials))
                )
            if self.override_number_to_percent_financials:
                override_number_to_percent(
                    df, *list(map(lambda x: df["financial"] == x, self.override_number_to_percent_financials))
                )
            # Rename Financials into their verbose representation
            df.financial = df.financial.map(self.FINANCIAL_MAP)

        return df.rename(columns={"index": "id"}), estimated_mapping
