import logging
from contextlib import suppress
from datetime import date, timedelta
from decimal import Decimal

import numpy as np
import pandas as pd
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.core.validators import DecimalValidator
from django.db.models import (
    AutoField,
    Case,
    Exists,
    ExpressionWrapper,
    F,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from skfolio.preprocessing import prices_to_returns
from wbcore.contrib.currency.models import Currency, CurrencyFXRates

from wbfdm.enums import MarketData

logger = logging.getLogger("pms")


class InstrumentQuerySet(QuerySet):
    def filter_active_at_date(self, val_date: date):
        return self.filter(
            (Q(delisted_date__isnull=True) | Q(delisted_date__gte=val_date))
            & (Q(inception_date__isnull=True) | Q(inception_date__lte=val_date))
        )

    def annotate_classification_for_group(
        self, classification_group, classification_height: int = 0, **kwargs
    ) -> QuerySet:
        return classification_group.annotate_queryset(
            self, classification_height, "", annotation_label="ancestor_classifications", **kwargs
        )

    def annotate_base_data(self):
        base_qs = InstrumentQuerySet(self.model, using=self._db)
        return self.annotate(
            is_investable=~Exists(base_qs.filter(parent=OuterRef("pk"))),
            root=Subquery(base_qs.filter(tree_id=OuterRef("tree_id"), level=0).values("id")[:1]),
            primary_security=ExpressionWrapper(
                Coalesce(
                    Subquery(
                        base_qs.filter(
                            parent=OuterRef("pk"),
                            is_primary=True,
                            is_security=True,
                        ).values("id")[:1]
                    ),
                    F("id"),
                ),
                output_field=AutoField(),
            ),
            primary_quote=ExpressionWrapper(
                Coalesce(
                    Subquery(
                        base_qs.filter(
                            parent=OuterRef("primary_security"),
                            is_primary=True,
                        ).values("id")[:1]
                    ),
                    F("primary_security"),
                ),
                output_field=AutoField(),
            ),
        )

    def annotate_all(self):
        return self.annotate_base_data()

    @property
    def dl(self):
        """Provides access to the dataloader proxy for the entities in the QuerySet.

        This method allows for easy retrieval of the DataloaderProxy instance
        associated with the QuerySet. It enables the utilization of dataloader
        functionalities directly from the QuerySet, facilitating data fetching and
        processing tasks.

        Returns:
            DataloaderProxy: An instance of DataloaderProxy associated with the
                entities in the QuerySet.
        """
        return self.model.dl_proxy(self)

    def get_instrument_prices_from_market_data(self, from_date: date, to_date: date):
        from wbfdm.models import InstrumentPrice

        def _dict_to_object(instrument, row):
            close = row.get("close", None)
            price_date = row.get("date")
            if price_date and close is not None:
                close = round(Decimal(close), 6)
                # we validate that close can be inserting into our table<
                with suppress(ValidationError):
                    validator = DecimalValidator(16, 6)
                    validator(close)
                    try:
                        try:
                            InstrumentPrice.objects.get(instrument=instrument, date=price_date)
                        except MultipleObjectsReturned:
                            InstrumentPrice.objects.get(
                                instrument=instrument, date=price_date, calculated=False
                            ).delete()
                        p = InstrumentPrice.objects.get(instrument=instrument, date=price_date)
                        p.net_value = close
                        p.gross_value = close
                        p.calculated = row["calculated"]
                        p.volume = row.get("volume", p.volume)
                        p.market_capitalization = row.get("market_capitalization", p.market_capitalization)
                        p.market_capitalization_consolidated = p.market_capitalization
                        p.set_dynamic_field(False)
                        p.id = None
                        return p
                    except InstrumentPrice.DoesNotExist:
                        with suppress(CurrencyFXRates.DoesNotExist):
                            p = InstrumentPrice(
                                currency_fx_rate_to_usd=CurrencyFXRates.objects.get(
                                    # we need to get the currency rate because we bulk create the object, and thus save is not called
                                    date=price_date,
                                    currency=instrument.currency,
                                ),
                                instrument=instrument,
                                date=price_date,
                                calculated=row["calculated"],
                                net_value=close,
                                gross_value=close,
                                volume=row.get("volume", None),
                                market_capitalization=row.get("market_capitalization", None),
                            )
                            p.set_dynamic_field(False)
                            return p

        df = pd.DataFrame(
            self.dl.market_data(
                from_date=from_date,
                to_date=to_date,
                values=[MarketData.CLOSE, MarketData.VOLUME, MarketData.MARKET_CAPITALIZATION],
            )
        )
        if not df.empty:
            df["valuation_date"] = pd.to_datetime(df["valuation_date"])
            df = df.rename(columns={"valuation_date": "date"})
            df = df.drop(
                columns=df.columns.difference(
                    ["calculated", "close", "market_capitalization", "volume", "instrument_id", "date"]
                )
            )
            df["calculated"] = False

            for instrument_id, dff in df.groupby("instrument_id", group_keys=False, as_index=False):
                dff = dff.drop(columns=["instrument_id"]).set_index("date").sort_index()
                if dff.index.duplicated().any():
                    dff = dff.groupby(level=0).first()
                    logger.warning(
                        f"We detected a duplicated index for instrument id {instrument_id}. Please correct the dl parameter which likely introduced this issue."
                    )

                dff = dff.reindex(pd.date_range(dff.index.min(), dff.index.max(), freq="B"))

                dff[["close", "market_capitalization"]] = dff[["close", "market_capitalization"]].astype(float).ffill()
                dff.volume = dff.volume.astype(float).fillna(0)
                dff.calculated = dff.calculated.astype(bool).fillna(
                    True
                )  # we do not ffill calculated but set the to True to mark them as "estimated"/"not real"

                dff = dff.reset_index(names="date").dropna(subset=["close"])
                dff = dff.replace([np.inf, -np.inf, np.nan], None)
                instrument = self.get(id=instrument_id)

                yield from filter(
                    lambda x: x, map(lambda row: _dict_to_object(instrument, row), dff.to_dict("records"))
                )

    def get_returns_df(
        self, from_date: date, to_date: date, to_currency: Currency | None = None, use_dl: bool = False
    ) -> tuple[dict[date, dict[int, float]], pd.DataFrame]:
        """
        Utility methods to get instrument returns for a given date range

        Args:
            from_date: date range lower bound
            to_date: date range upper bound
            to_currency: currency to use for returns
            use_dl: whether to get data straight from the dataloader or use the internal table

        Returns:
            Return a tuple of the raw prices and the returns dataframe
        """
        padded_from_date = from_date - timedelta(days=15)
        padded_to_date = to_date + timedelta(days=3)
        logger.info(
            f"Loading returns from {from_date:%Y-%m-%d} (padded to {padded_from_date:%Y-%m-%d}) to {to_date:%Y-%m-%d} (padded to {padded_to_date:%Y-%m-%d}) for {self.count()} instruments"
        )

        if use_dl:
            kwargs = dict(
                from_date=padded_from_date, to_date=padded_to_date, values=[MarketData.CLOSE], apply_fx_rate=False
            )
            if to_currency:
                kwargs["target_currency"] = to_currency.key
            df = pd.DataFrame(self.dl.market_data(**kwargs))
            if df.empty:
                df = pd.DataFrame(columns=["instrument_id", "fx_rate", "close", "valuation_date"])
            else:
                df = df[["instrument_id", "fx_rate", "close", "valuation_date"]]
        else:
            from wbfdm.models import InstrumentPrice

            if to_currency:
                fx_rate = Coalesce(
                    CurrencyFXRates.get_fx_rates_subquery_for_two_currencies(
                        "date", "instrument__currency", to_currency
                    ),
                    Decimal("1"),
                )
            else:
                fx_rate = Value(Decimal("1"))
            # annotate fx rate only if the price is not calculated, in that case we assume the instrument is not tradable and we set a forex of None (to be fast forward filled)
            prices = InstrumentPrice.objects.filter(
                instrument__in=self, date__gte=padded_from_date, date__lte=padded_to_date
            ).annotate(fx_rate=Case(When(calculated=False, then=fx_rate), default=None))
            df = pd.DataFrame(
                prices.filter_only_valid_prices().values_list("instrument", "fx_rate", "net_value", "date"),
                columns=["instrument_id", "fx_rate", "close", "valuation_date"],
            )
        df = (
            df.pivot_table(index="valuation_date", columns="instrument_id", values=["fx_rate", "close"], dropna=False)
            .astype(float)
            .sort_index()
        )
        if not df.empty:
            ts = pd.bdate_range(df.index.min(), df.index.max(), freq="B")
            df = df.reindex(ts)
            df = df.ffill()
            df.index = pd.to_datetime(df.index)
            df = df[
                (df.index <= pd.Timestamp(to_date)) & (df.index >= pd.Timestamp(from_date))
            ]  # ensure the returned df corresponds to requested date range
            prices_df = df["close"]
            if "fx_rate" in df.columns:
                fx_rate_df = df["fx_rate"].fillna(1.0)
            else:
                fx_rate_df = pd.DataFrame(np.ones(prices_df.shape), index=prices_df.index, columns=prices_df.columns)
            returns = prices_to_returns(fx_rate_df * prices_df, drop_inceptions_nan=False, fill_nan=True)
            return {
                ts.date(): row for ts, row in prices_df.replace([np.nan], None).to_dict("index").items()
            }, returns.replace([np.inf, -np.inf, np.nan], 0)
        return {}, pd.DataFrame()
