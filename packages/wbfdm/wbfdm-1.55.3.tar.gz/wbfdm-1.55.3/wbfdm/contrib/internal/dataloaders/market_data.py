from datetime import date
from decimal import Decimal
from typing import Iterator

from django.db.models import Case, Value, When
from django.db.models.functions import Coalesce
from wbcore.contrib.currency.models import Currency, CurrencyFXRates
from wbcore.contrib.dataloader.dataloaders import Dataloader

from wbfdm.dataloaders.protocols import MarketDataProtocol
from wbfdm.dataloaders.types import MarketDataDict
from wbfdm.enums import Frequency, MarketData
from wbfdm.models.instruments.instrument_prices import InstrumentPrice

MarketDataMap = {
    "SHARES_OUTSTANDING": "internal_outstanding_shares",
    "OPEN": "net_value",
    "CLOSE": "net_value",
    "HIGH": "net_value",
    "LOW": "net_value",
    "BID": "net_value",
    "ASK": "net_value",
    "VOLUME": "internal_volume",
    "MARKET_CAPITALIZATION": "market_capitalization",
}

DEFAULT_VALUES = [MarketData[name] for name in MarketDataMap.keys()]


def _cast_decimal_to_float(value: float | Decimal) -> float:
    if isinstance(value, Decimal):
        value = float(value)
    return value


class MarketDataDataloader(MarketDataProtocol, Dataloader):
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
        if not values:
            values = DEFAULT_VALUES
        values_map = {value.name: MarketDataMap[value.name] for value in values if value.name in MarketDataMap}
        calculated = kwargs.get("calculated", None)
        try:
            target_currency = Currency.objects.get(key=target_currency)
        except Currency.DoesNotExist:
            target_currency = None
        fx_rate = (
            Coalesce(
                CurrencyFXRates.get_fx_rates_subquery_for_two_currencies(
                    "date", "instrument__currency", target_currency
                ),
                Value(Decimal("1")),
            )
            if target_currency
            else Value(Decimal("1"))
        )

        prices = InstrumentPrice.objects.filter(instrument__in=self.entities)
        if calculated is not None:
            prices = prices.filter(calculated=calculated)
        else:
            prices = prices.filter_only_valid_prices()

        if exact_date:
            prices = prices.filter(date=exact_date)
        else:
            if from_date:
                prices = prices.filter(date__gte=from_date)
            if to_date:
                prices = prices.filter(date__lte=to_date)
        prices = prices.annotate_market_data().annotate(
            fx_rate=Case(When(calculated=False, then=fx_rate), default=None)
        )

        for row in prices.order_by("date").values(
            "date",
            "instrument",
            "calculated",
            "fx_rate",
            *set(values_map.values()),
        ):
            external_id = row.pop("instrument")
            val_date = row.pop("date")
            if row:
                fx_rate = row["fx_rate"]
                if apply_fx_rate and fx_rate is not None:
                    if row.get("net_value"):
                        row["net_value"] = row["net_value"] * fx_rate
                    if row.get("market_capitalization"):
                        row["market_capitalization"] = row["market_capitalization"] * float(fx_rate)
                    fx_rate = _cast_decimal_to_float(fx_rate)

                yield MarketDataDict(
                    id=f"{external_id}_{val_date}",
                    valuation_date=val_date,
                    instrument_id=external_id,
                    external_id=external_id,
                    source="wbfdm",
                    calculated=row["calculated"],
                    fx_rate=fx_rate,
                    **{MarketData[k].value: _cast_decimal_to_float(row[v]) for k, v in values_map.items()},
                )
