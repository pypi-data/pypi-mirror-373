import math
import re
from datetime import date, datetime
from typing import Generator, List, Optional

import DatastreamPy as dsweb
import numpy as np
import pandas as pd
import pytz
from django.core.cache import cache
from django.utils import timezone
from wbcore.contrib.currency.models import Currency, CurrencyFXRates


class CachedTokenDataClient(dsweb.DataClient):
    def _get_token(self, isProxy=False):
        if (token := cache.get("dsws_token")) and (token_expiry := cache.get("dsws_token_expiry")):
            self.token = token
            self.tokenExpiry = timezone.make_aware(datetime.fromtimestamp(token_expiry), timezone=pytz.UTC)
        else:
            super()._get_token()
            expiry_elapse = (self.tokenExpiry - timezone.now()).seconds
            cache.set("dsws_token", self.token, timeout=expiry_elapse)
            cache.set("dsws_token_expiry", datetime.timestamp(self.tokenExpiry), timeout=expiry_elapse)


class Client:
    MAXIMUM_ITEMS_PER_BUNDLE: int = 500
    MAXIMUM_REQUESTS_PER_BUNDLE: int = 20
    MAXIMUM_INSTRUMENTS_PER_REQUEST: int = 50
    MAXIMUM_DATATYPES_PER_REQUEST: int = 50
    MAXIMUM_ITEMS_PER_REQUEST: int = 100
    PRICE_ERROR_MARGIN: float = 0.10
    IBUNIT_DEFAULT_UNIT: float = 1e6

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self.connection = CachedTokenDataClient(None, username, password)
        super().__init__()

    @classmethod
    def get_chunked_list(cls, identifiers: list[str], fields_number: int) -> list[list[str]]:
        instruments_number = len(identifiers)
        max_chunks_number = instruments_number * fields_number / cls.MAXIMUM_ITEMS_PER_BUNDLE
        chunk_size = int(instruments_number / max_chunks_number) - 1
        res = []
        for x in range(0, len(identifiers), chunk_size):
            res.append(identifiers[x : x + chunk_size])
        return res

    @classmethod
    def _breakdown_requests(
        cls, tickers: List[str], symbols: List[str]
    ) -> Generator[tuple[list[str], list[str]], None, None]:
        """
        Helper function to generate tuple of ticker and symbols that respect the API data usage
        Args:
            tickers: List of tickers to fetch
            symbols: Corresponding list of symbol to fetch

        Returns:
            Yield tuple of list of string
        """
        if len(tickers) * len(symbols) > cls.MAXIMUM_ITEMS_PER_BUNDLE:
            raise ValueError(f"The maximum number of items for a bundle is {cls.MAXIMUM_ITEMS_PER_BUNDLE}")

        if (
            len(tickers) * len(symbols) <= cls.MAXIMUM_ITEMS_PER_REQUEST
            and len(tickers) <= cls.MAXIMUM_INSTRUMENTS_PER_REQUEST
        ):
            yield tickers, symbols
        else:
            nb_tickers = min(
                math.floor(cls.MAXIMUM_ITEMS_PER_REQUEST / len(symbols)),
                len(tickers),
                cls.MAXIMUM_INSTRUMENTS_PER_REQUEST,
            )
            yield tickers[0:nb_tickers], symbols
            yield from cls._breakdown_requests(tickers[nb_tickers:], symbols)

    def get_last_fx_rate(self, base_currency_key: str, target_currency_key: str):
        last_currency_rate = CurrencyFXRates.objects.latest("date").date
        try:
            base_currency = Currency.objects.get(key=base_currency_key)
            target_currency = Currency.objects.get(key=target_currency_key)
            return float(base_currency.convert(last_currency_rate, target_currency, exact_lookup=True))
        except Currency.DoesNotExist:
            return 1.0

    def _process_raw_requests(self, tickers: list[str], fields: list[str], **extra_client_kwargs) -> pd.DataFrame:
        """
        Utility function to fetch data in bulk, aggregate and clean the result
        Args:
            tickers: Instruments tickers
            fields: Symbols
            **extra_client_kwargs: Extra keyword arguments to be passed down to the client (e.g. frequency)

        Returns:
            An aggregated and cleaned dataframe with [Dates, Instrument] as index for timeserie and [Instrument] As index for static data
        """
        requests_data = list(self._breakdown_requests(tickers, fields))
        reqs = []
        if len(requests_data) > self.MAXIMUM_REQUESTS_PER_BUNDLE:
            raise ValueError(f"number of request exceed {self.MAXIMUM_REQUESTS_PER_BUNDLE}")
        # Construct the requests bundle
        for request_tickers, request_symbols in requests_data:
            # Convert a list of string into a valid string
            converted_ticker = ",".join(request_tickers)
            if "start" in extra_client_kwargs or "end" in extra_client_kwargs:
                reqs.append(
                    self.connection.post_user_request(tickers=converted_ticker, fields=fields, **extra_client_kwargs)
                )
            else:
                reqs.append(self.connection.post_user_request(tickers=converted_ticker, fields=fields, kind=0))
        # concat the bundle results
        res = self.connection.get_bundle_data(bundleRequest=reqs)

        df = pd.DataFrame()
        if res:
            if "start" in extra_client_kwargs or "end" in extra_client_kwargs:
                res = list(filter(lambda subdf: subdf.index.name == "Dates", res))
            if res:
                df = pd.concat(res)
                if df.index.name == "Dates":
                    df = (
                        pd.melt(df, ignore_index=False)
                        .reset_index()
                        .rename(columns={"value": "Value", "Field": "Datatype"})
                    )
                df.Value = df.Value.apply(lambda x: None if str(x).startswith("$$ER") else x)
                if not df.empty:
                    df = df[df.Value.notnull()]
                    df = df.replace({"NA": None})
                    if "Dates" in df.columns:
                        df.Dates = pd.to_datetime(df.Dates, utc=True)
                        indexes = ["Instrument", "Dates"]
                    else:
                        indexes = ["Instrument"]
                    df = pd.pivot_table(
                        df, values="Value", index=indexes, columns="Datatype", aggfunc="first", dropna=False
                    )
        return df

    def _normalize_df_units(
        self,
        df: pd.DataFrame,
        ibes_non_per_share_fields: list[str] | None = None,
        ibes_currency_based_fields: list[str] | None = None,
        ibes_fields: list[str] | None = None,
        **extra_client_kwargs,
    ) -> pd.DataFrame:
        """
        Datastream use arbitrary units for some symbols where the denominator needs to be fetch in two steps:
        * Using FIELD#U to get the datastream unit
        * if ibes_non_per_share_fields is provided, fetch for the static symbol IBUNIT and normalized the given columns with the result times a constant (100000)
        * if ibes_currency_based_fields is provided, fetch for the static symbol IBCUR and normalized the given columns latest found currency rate.
        This function uses the index named "Instrument" as ticker fields and the columns as symbols. Start, End or Frequency needs to be passed down using the extra_client_kwargs argument

        Args:
            df: The dataframe to be normalized
            ibes_non_per_share_fields: Columns that need ibunit normalization. Defaults to None
            ibes_currency_based_fields: Columns that need IBES Currency conversion from static field IBCUR
            **extra_client_kwargs: Extra keywords arguments to be passed down to the client (e.g. frequency)

        Returns:
            A normalized dataframe (e.g. volume are in shares and not a million of shares)
        """
        if not ibes_fields:
            ibes_fields = []
        df = df.copy()
        fields = df.columns.unique().tolist()
        tickers = df.index.get_level_values("Instrument").unique().tolist()
        dfu = self._process_raw_requests(tickers, list(map(lambda x: x + "#U", fields)), **extra_client_kwargs).fillna(
            1
        )
        dfu = dfu[dfu.index.isin(df.index)]
        if not dfu.empty:
            dfu = dfu.rename(columns=lambda x: x.replace("#U", "")).fillna(1)
            dfu = dfu[dfu.columns.intersection(df.columns)]
            dff = df[dfu.columns].multiply(dfu, fill_value=1)

            # We do this to ensure that not provided data (nan) are not set with the multiplication with the U matrix
            dff[df.isnull()] = df[df.isnull()]
            dff[df.columns.difference(dff.columns)] = df[
                df.columns.difference(dff.columns)
            ]  # We ensure that the inital colums from df are appended to the new dataframe if missing from dfu. (happens when the colum has non number values)
            df = dff

            # If the symbol is computed directly from refinitiv, we need to normalize it as well given the formula (define as the field name)
            for mav_field in list(filter(lambda x: "MAV#" in x, fields)):
                re_matches = re.findall(r"X\(([^\)]+)\)", mav_field)
                if len(re_matches) > 0 and re_matches[0] in dfu.columns:
                    df.loc[:, mav_field] = df.loc[:, mav_field] * dfu.loc[:, re_matches[0]]

        if ibes_non_per_share_fields:
            df_ibunit = self.get_static_df(tickers, ["IBUNIT"]).fillna(1)
            if not df_ibunit.empty:
                df_ibunit = df_ibunit.set_index("Instrument")["IBUNIT"]
                df[df.columns.intersection(ibes_non_per_share_fields)] = (
                    df[df.columns.intersection(ibes_non_per_share_fields)].multiply(
                        df_ibunit, axis=0, level="Instrument"
                    )
                    * self.IBUNIT_DEFAULT_UNIT
                )
                ibes_fields = list(set(ibes_fields + ibes_non_per_share_fields))
        if ibes_currency_based_fields:
            df_ibcur = self.get_static_df(tickers, ["IBCUR", "ISOCUR"]).replace(
                "BPN", "GBX"
            )  # BPN == GBX but our db only support the latter
            if not df_ibcur.empty:
                df_ibcur["rate"] = 1
                different_curr_idx = df_ibcur["IBCUR"] != df_ibcur["ISOCUR"]
                df_ibcur.loc[different_curr_idx, "rate"] = df_ibcur.loc[different_curr_idx].apply(
                    lambda x: self.get_last_fx_rate(x["IBCUR"], x["ISOCUR"]), axis=1
                )
                df[df.columns.intersection(ibes_currency_based_fields)] = df[
                    df.columns.intersection(ibes_currency_based_fields)
                ].multiply(df_ibcur.set_index("Instrument")["rate"], axis=0, level="Instrument")
                ibes_fields = list(set(ibes_fields + ibes_currency_based_fields))
        if ibes_fields:
            df[df.columns.intersection(ibes_fields)] = (
                df[df.columns.intersection(ibes_fields)] * self.IBUNIT_DEFAULT_UNIT
            )
        return df

    def get_static_df(self, tickers: List[str], fields: List[str], **kwargs) -> pd.DataFrame:
        """
        Public function to returns a dataframe for static symbols

        Args:
            tickers: Ticker to fetch
            fields: Static symbols to fetch

        Returns:
            A valid dataframe result
        """
        # Breakdown tickers and fields into a valid datastream parameters subsets
        return self._process_raw_requests(tickers, fields).reset_index()

    def get_timeserie_df(
        self,
        tickers: List[str],
        fields: List[str],
        ibes_non_per_share_fields: Optional[list[str]] = None,
        ibes_currency_based_fields: Optional[list[str]] = None,
        ibes_fields: list[str] | None = None,
        **extra_client_kwargs,
    ) -> pd.DataFrame:
        """
        Public function to get timeserie type data
        Args:
            tickers: Instrument tickers
            fields: Symbols to fetch
            ibes_non_per_share_fields: Columns that need ibunit normalization. Defaults to None
            ibes_currency_based_fields: Columns that need IBES Currency conversion from static field IBCUR
            **extra_client_kwargs: Extra keywords arguments to be passed down to the client (e.g. frequency)

        Returns:
            The result as a dataframe
        """
        if (start := extra_client_kwargs.get("start", None)) and isinstance(start, date):
            extra_client_kwargs["start"] = start.strftime("%Y-%m-%d")
        if (end := extra_client_kwargs.get("end", None)) and isinstance(end, date):
            extra_client_kwargs["end"] = end.strftime("%Y-%m-%d")

        final_df_list = []
        # Sometime, we get too many fields and therefore, we need to split them based on the maximum number of symbols allowed per request
        for splited_fields in np.array_split(fields, math.ceil((len(fields) / self.MAXIMUM_DATATYPES_PER_REQUEST))):
            # Breakdown tickers and fields into a valid datastream parameters subsets
            df = self._process_raw_requests(tickers, list(splited_fields), **extra_client_kwargs)
            if not df.empty:
                df = self._normalize_df_units(
                    df,
                    ibes_non_per_share_fields=ibes_non_per_share_fields,
                    ibes_currency_based_fields=ibes_currency_based_fields,
                    ibes_fields=ibes_fields,
                    **extra_client_kwargs,
                )
                df = (
                    df.reset_index()
                    .rename_axis(None)
                    .replace([np.inf, -np.inf, np.nan], None)
                    .dropna(how="all", subset=df.columns.intersection(splited_fields))
                )
                if not df.empty:
                    if "Dates" in df.columns:
                        df = df.set_index(["Instrument", "Dates"])
                    else:  # otherwise it's not a timeseries and we set index only on instrument
                        df = df.set_index(["Instrument"])
                    final_df_list.append(df)
        if final_df_list:
            return pd.concat(final_df_list, axis=1).reset_index()
        return pd.DataFrame()

    def raw_fetch(
        self, tickers: List[str], fields: List[str], start: Optional[date] = None, end: Optional[date] = None
    ):
        """
        Utility function to expose the client directly without any modification
        """
        return self.connection.get_data(tickers=tickers, fields=fields, start=start, end=end)
