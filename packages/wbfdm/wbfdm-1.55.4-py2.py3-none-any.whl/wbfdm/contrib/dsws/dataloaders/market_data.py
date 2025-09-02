from contextlib import suppress
from datetime import date
from typing import Iterator

from DatastreamPy import DSUserObjectFault
from django.conf import settings
from pandas.tseries.offsets import BDay
from wbcore.contrib.currency.models import Currency, CurrencyFXRates
from wbcore.contrib.dataloader.dataloaders import Dataloader
from wbfdm.dataloaders.protocols import MarketDataProtocol
from wbfdm.dataloaders.types import MarketDataDict
from wbfdm.enums import Frequency, MarketData

from ..client import Client

FIELD_MAP = {
    "close": "P",
    "open": "PO",
    "high": "PH",
    "low": "PL",
    "bid": "PB",
    "ask": "PA",
    "vwap": "VWAP",
    "volume": "VO",
    "outstanding_shares": "NOSH",
    "market_capitalization": "MV",
}


class DSWSMarketDataDataloader(MarketDataProtocol, Dataloader):
    def market_data(
        self,
        values: list[MarketData] = [MarketData.CLOSE],
        from_date: date | None = None,
        to_date: date | None = None,
        exact_date: date | None = None,
        frequency: Frequency = Frequency.DAILY,
        target_currency: str | None = None,
        apply_fx_rate: bool = True,
        **kwargs,
    ) -> Iterator[MarketDataDict]:
        """Get prices for instruments.

        Args:
            values (list[MarketData]): List of values to include in the results.
            from_date (date | None): The starting date for filtering prices. Defaults to None.
            to_date (date | None): The ending date for filtering prices. Defaults to None.
            frequency (Frequency): The frequency of the requested data

        Returns:
            Iterator[MarketDataDict]: An iterator of dictionaries conforming to the DailyValuationDict.
        """
        default_lookup = {
            k: {"id": p, "symbol": v}
            for k, v, p in self.entities.values_list(
                "dl_parameters__market_data__parameters__identifier",
                "dl_parameters__market_data__parameters__price_symbol",
                "id",
            )
        }
        instruments = {entity.id: entity for entity in self.entities}
        try:
            target_currency = Currency.objects.get(key=target_currency)
        except Currency.DoesNotExist:
            target_currency = None

        if (dsws_username := getattr(settings, "REFINITIV_DATASTREAM_USERNAME", None)) and (
            dsws_password := getattr(settings, "REFINITIV_DATASTREAM_PASSWORD", None)
        ):
            with suppress(DSUserObjectFault):
                client = Client(username=dsws_username, password=dsws_password)
                default_fields = list(set(map(lambda x: x[1]["symbol"], default_lookup.items())))
                values_fields = [FIELD_MAP[v.value] for v in values if v.value in FIELD_MAP]
                fields = list(set(default_fields + values_fields))
                identifiers = list(default_lookup.keys())
                parameters: dict[str, str | list[str] | date] = {}
                if exact_date:
                    parameters["start"] = exact_date
                    parameters["end"] = (exact_date + BDay(1)).date()
                else:
                    if from_date:
                        parameters["start"] = from_date.strftime("%Y-%m-%d")
                    if to_date:
                        parameters["end"] = to_date.strftime("%Y-%m-%d")
                for chunked_identifiers in client.get_chunked_list(identifiers, len(fields)):
                    df = client.get_timeserie_df(chunked_identifiers, fields, **parameters)
                    if exact_date:
                        df = df[df["Dates"] == exact_date]
                    for row in df.to_dict("records"):
                        jsondate = row["Dates"].date()
                        external_id = row["Instrument"]
                        fx_rate = 1.0
                        if target_currency:
                            instrument = instruments[default_lookup[external_id]["id"]]
                            if instrument.currency != target_currency:
                                with suppress(CurrencyFXRates.DoesNotExist):
                                    fx_rate = float(instrument.currency.convert(jsondate, target_currency))
                        data = dict(fx_rate=fx_rate)
                        for market_value in values:
                            data[market_value.value] = row.get(FIELD_MAP[market_value.value], None)
                            if (
                                apply_fx_rate
                                and data[market_value.value]
                                and market_value.value
                                not in [
                                    MarketData.MARKET_CAPITALIZATION.value,
                                    MarketData.VOLUME.value,
                                    MarketData.VWAP.value,
                                ]
                            ):
                                data[market_value.value] *= fx_rate

                        with suppress(KeyError):
                            if default_symbol := default_lookup[external_id].get("symbol", None):
                                data["close"] = row[default_symbol]

                            yield MarketDataDict(
                                id=f"{default_lookup[external_id]['id']}_{jsondate}",
                                valuation_date=jsondate,
                                instrument_id=default_lookup[external_id]["id"],
                                external_id=external_id,
                                source="refinitiv-dsws",
                                **data,
                                # **{value: field for value, field in zip_longest(values, fields[1:])},
                            )

    def get_adjustments(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
        exact_date: date | None = None,
    ):
        lookup = dict(self.entities.values_list("external_id", "id"))
        if (dsws_username := getattr(settings, "REFINITIV_DATASTREAM_USERNAME", None)) and (
            dsws_password := getattr(settings, "REFINITIV_DATASTREAM_PASSWORD", None)
        ):
            with suppress(DSUserObjectFault):
                client = Client(username=dsws_username, password=dsws_password)
                identifiers = list(lookup.keys())
                parameters: dict[str, str | list[str]] = {}
                if from_date:
                    parameters["start"] = from_date.strftime("%Y-%m-%d")
                if to_date:
                    parameters["end"] = to_date.strftime("%Y-%m-%d")
                for chunked_identifiers in client.get_chunked_list(identifiers, 1):
                    df = client.get_timeserie_df(chunked_identifiers, ["AX"], **parameters)
                    for row in df.to_dict("records"):
                        jsondate = row["Dates"].date()
                        del row["Dates"]
                        external_id = row["Instrument"]
                        del row["Instrument"]
                        yield {
                            "id": f"{lookup[external_id]}_{jsondate}",
                            "adjustment_date": jsondate,
                            "instrument_id": lookup[external_id],
                            "external_id": external_id,
                            "source": "refinitiv-dsws",
                            "adjustment_factor": row["AX"],
                        }
