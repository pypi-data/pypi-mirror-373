from datetime import date

import pandas as pd
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from pandas.tseries.offsets import QuarterEnd, YearEnd
from tqdm import tqdm
from wbcore.contrib.io.models import ImportedObjectProviderRelationship, Provider

from wbfdm.contrib.dsws.client import Client
from wbfdm.models.instruments.instruments import Instrument

REPORT_TYPE_MAP = {"QTR": "Q", "TRI": "4M", "SAN": "6M", "ANN": "Y"}


class Controller:
    def __init__(self, client_username: str, client_password: str):
        self.provider = Provider.objects.get(key="refinitiv")
        self.client = Client(username=client_username, password=client_password)

    @classmethod
    def _wrap_identifier_in_bracklet(cls, perm_ids: list[str]) -> list[str]:
        return [f"<{perm_id}>" for perm_id in perm_ids]

    def get_start_and_end_date_for_interim(self, perm_id: str, end: date, start: date | None = None) -> date | None:
        if not start:
            start = end - QuarterEnd(1)
        if rel := ImportedObjectProviderRelationship.objects.filter(
            provider=self.provider,
            provider_identifier=perm_id,
            content_type=ContentType.objects.get_for_model(Instrument),
        ).first():
            instrument = rel.content_object
            fundamentals = instrument.fundamentals.order_by("-period__period_year", "-period__period_index")
            # Not an historical import, it's a bulk one, we need to get the next fiscal period to fetch
            if fundamentals.exists() and (fiscal_period := fundamentals.first().period):
                start = fiscal_period.calendar_period.end_time.date()

        return (start + QuarterEnd(0)).date(), (
            end + QuarterEnd(0) + QuarterEnd(1)
        ).date()  # We always refetch since the beginning of the quarter

    @classmethod
    def get_start_date_for_annual(cls, end: date, start: date | None = None) -> date:
        if not start:
            start = end
        return (start - YearEnd(1)).date(), (
            end + YearEnd(0)
        ).date()  # We always refetch since the beginning of the quarter

    def get_frequency(self, instrument: str) -> str:
        try:
            res = self.client.get_static_df([instrument], ["IBEFPD"])
            if not res.empty:
                return REPORT_TYPE_MAP[res.set_index("Instrument").loc[instrument, "IBEFPD"]]
        except Exception:
            return "Q"

    def fetch_perm_id(
        self,
        instrument_ric: str = None,
        instrument_isin: str = None,
        instrument_mnemonic: str = None,
        perm_id_symbols: list[str] = ["QPID", "IPID"],
    ) -> str | None:
        def _process_ticker(ticker):
            if not (df := self.client.get_static_df(tickers=[ticker], fields=perm_id_symbols)).empty:
                for perm_id in perm_id_symbols:
                    if identifier := df[perm_id].iloc[0]:
                        return identifier

        res = None
        if instrument_ric:
            res = _process_ticker(f"<{instrument_ric}>")
        if instrument_mnemonic and not res:
            res = _process_ticker(instrument_mnemonic)
        if instrument_isin and not res:
            res = _process_ticker(instrument_isin)
        return res

    def get_data(
        self,
        identifiers: list[str],
        fields: list[str],
        start: date | None = None,
        end: date | None = None,
        wrap_tickers_into_brackets: bool = True,
        **extra_client_kwargs,
    ) -> pd.DataFrame:
        df_list = []
        chunked_identifiers = self.client.get_chunked_list(identifiers, len(fields))

        if settings.DEBUG:
            chunked_identifiers = tqdm(chunked_identifiers, total=len(chunked_identifiers))

        frequency = extra_client_kwargs.pop("freq", "D")
        for perm_ids in chunked_identifiers:
            if wrap_tickers_into_brackets:
                perm_ids = self._wrap_identifier_in_bracklet(perm_ids)
            if start or end:
                dff = self.client.get_timeserie_df(
                    perm_ids, fields, start=start, end=end, freq=frequency, **extra_client_kwargs
                )
                df_list.append(dff)
            else:
                df_list.append(self.client.get_static_df(perm_ids, fields, **extra_client_kwargs))
        if df_list:
            return pd.concat(df_list, axis=0)
        return pd.DataFrame()

    def get_interim_fundamental_data(
        self,
        identifiers: list[str],
        annual_fields: list[str],
        initial_start: date | None = None,
        initial_end: date | None = None,
        wrap_tickers_into_brackets: bool = True,
        **extra_client_kwargs,
    ) -> pd.DataFrame:
        df_list = []
        interim_fields_map = {field + "A" if field[0:2] == "WC" else field: field for field in annual_fields}
        if settings.DEBUG:
            identifiers = tqdm(identifiers, total=len(identifiers))

        for instrument_perm_id in identifiers:
            start = initial_start  # copy start argument
            end = initial_end  # copy end argument

            start, end = self.get_start_and_end_date_for_interim(instrument_perm_id, end, start=start)
            if start and end:
                perm_ids = [instrument_perm_id]
                if wrap_tickers_into_brackets:
                    perm_ids = self._wrap_identifier_in_bracklet(perm_ids)
                # frequency = self.get_frequency(identifiers[0])
                df = self.client.get_timeserie_df(
                    perm_ids,
                    list(interim_fields_map.keys()),
                    start=start,
                    end=end,
                    **extra_client_kwargs,
                )
                if not df.empty:
                    df_list.append(df)
        if df_list:
            df = pd.concat(df_list, axis=0).dropna(how="all")
            df["period__period_interim"] = True
            return df.rename(columns=interim_fields_map)
        return pd.DataFrame()

    def get_annual_fundamental_data(
        self,
        identifiers: list[str],
        annual_fields: list[str],
        initial_start: date | None = None,
        initial_end: date | None = None,
        wrap_tickers_into_brackets: bool = True,
        **extra_client_kwargs,
    ) -> pd.DataFrame:
        df_list = []
        start, end = self.get_start_date_for_annual(initial_end, start=initial_start)
        chunked_identifiers = self.client.get_chunked_list(identifiers, len(annual_fields))
        if settings.DEBUG:
            chunked_identifiers = tqdm(chunked_identifiers, total=len(chunked_identifiers))
        for perm_ids in chunked_identifiers:
            if wrap_tickers_into_brackets:
                perm_ids = self._wrap_identifier_in_bracklet(perm_ids)
            df = self.client.get_timeserie_df(
                perm_ids,
                annual_fields,
                start=start,
                end=end,
                freq="Y",
                **extra_client_kwargs,
            )
            if not df.empty:
                df_list.append(df)

        if df_list:
            df = pd.concat(df_list, axis=0).dropna(how="all")
            df["WC05200"] = 4
            df["period__period_interim"] = False
            return df
        return pd.DataFrame()
