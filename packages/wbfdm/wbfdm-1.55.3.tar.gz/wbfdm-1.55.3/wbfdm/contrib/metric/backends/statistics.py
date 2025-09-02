from contextlib import suppress
from datetime import date
from typing import Generator

import pandas as pd
from django.db.models import Sum
from wbcore.serializers.fields.number import DisplayMode

from wbfdm.enums import Financial, PeriodType, SeriesType
from wbfdm.models import Instrument, InstrumentPrice

from ..decorators import register
from ..dto import Metric, MetricField, MetricKey
from ..exceptions import MetricInvalidParameterException
from .base import BaseDataloader, InstrumentMetricBaseBackend

STATISTICS_METRIC = MetricKey(
    key="statistic",
    label="Statistic",
    subfields=[
        MetricField(
            key="revenue_y_1",
            label="Revenue Y-1",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "{{currency_symbol}}"}],
            serializer_kwargs={"display_mode": DisplayMode.SHORTENED},
        ),
        MetricField(
            key="revenue_y0",
            label="Revenue Y0",
            decorators=[{"position": "left", "value": "{{currency_symbol}}"}],
            serializer_kwargs={"display_mode": DisplayMode.SHORTENED},
        ),
        MetricField(
            key="revenue_y1",
            label="Revenue Y1",
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "{{currency_symbol}}"}],
            serializer_kwargs={"display_mode": DisplayMode.SHORTENED},
        ),
        MetricField(
            key="market_capitalization",
            label="Market Capitalization",
            decorators=[{"position": "left", "value": "{{currency_symbol}}"}],
            serializer_kwargs={"display_mode": DisplayMode.SHORTENED},
        ),
        MetricField(
            key="price",
            label="Price",
            decorators=[{"position": "left", "value": "{{currency_symbol}}"}],
        ),
        MetricField(
            key="volume_50d",
            label="Volume 50D",
            serializer_kwargs={"display_mode": DisplayMode.SHORTENED},
        ),
    ],
)

STATISTICS_METRIC_USD = MetricKey(
    key="statistic_usd",
    label="Statistic (USD)",
    subfields=[
        MetricField(
            key="revenue_y_1",
            label="Revenue Y-1",
            aggregate=Sum,
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
            serializer_kwargs={"display_mode": DisplayMode.SHORTENED},
        ),
        MetricField(
            key="revenue_y0",
            label="Revenue Y0",
            aggregate=Sum,
            decorators=[{"position": "left", "value": "$"}],
            serializer_kwargs={"display_mode": DisplayMode.SHORTENED},
        ),
        MetricField(
            key="revenue_y1",
            label="Revenue Y1",
            aggregate=Sum,
            list_display_kwargs={"show": "open"},
            decorators=[{"position": "left", "value": "$"}],
            serializer_kwargs={"display_mode": DisplayMode.SHORTENED},
        ),
        MetricField(
            key="market_capitalization",
            label="Market Capitalization",
            aggregate=Sum,
            decorators=[{"position": "left", "value": "$"}],
            serializer_kwargs={"display_mode": DisplayMode.SHORTENED},
        ),
        MetricField(
            key="price",
            label="Price",
            decorators=[{"position": "left", "value": "{{currency_symbol}}"}],
        ),
        MetricField(
            key="volume_50d",
            label="Volume 50D",
            serializer_kwargs={"display_mode": DisplayMode.SHORTENED},
        ),
    ],
)


class Dataloader(BaseDataloader):
    METRIC_KEY = "statistic"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aggregate_callback = {
            "revenue_y_1": "sum",
            "revenue_y0": "sum",
            "revenue_y1": "sum",
            "market_capitalization": "sum",
            "price": "mean",
            "volume_50d": "mean",
        }

    def _compute(self) -> dict[str, float]:
        """
        Compute/fetch the statistics metrics. If the basket is constituted of multiple instrument, take the average of each performance

        Returns:
            The metrics as dictionary
        """
        if self.val_date:
            pivot_year = self.val_date.year
            instruments = self.basket_objects
            df_revenue = pd.DataFrame(
                instruments.dl.financials(
                    values=[Financial.REVENUE],
                    series_type=SeriesType.COMPLETE,
                    period_type=PeriodType.ANNUAL,
                    from_year=pivot_year - 1,
                    to_year=pivot_year + 1,
                )
            )
            if not df_revenue.empty:
                df_revenue = (
                    df_revenue.pivot_table(index="instrument_id", columns="year", values="value")
                    .rename(
                        columns={pivot_year - 1: "revenue_y_1", pivot_year: "revenue_y0", pivot_year + 1: "revenue_y1"}
                    )
                    .astype(float)
                )
            df_price = (
                pd.DataFrame(
                    InstrumentPrice.objects.filter(instrument__in=instruments, calculated=False, date=self.val_date)
                    .annotate(fx_rate=self.fx_rate_expression)
                    .annotate_market_data()
                    .values_list(
                        "instrument",
                        "internal_market_capitalization",
                        "net_value",
                        "volume_50d",
                        "fx_rate",
                    ),
                    columns=[
                        "instrument",
                        "market_capitalization",
                        "price",
                        "volume_50d",
                        "fx_rate",
                    ],
                )
                .set_index("instrument")
                .astype(float)
            )
            fx_rate = df_price["fx_rate"]
            df = pd.concat([df_revenue, df_price.drop("fx_rate", axis=1)], axis=1)
            for key in ["revenue_y_1", "revenue_y0", "revenue_y1", "market_capitalization"]:
                if key in df.columns:
                    df[key] = df[key] / fx_rate

            if not df.empty:
                return (
                    df.reset_index()
                    .agg({k: v for k, v in self.aggregate_callback.items() if k in df.columns})
                    .dropna()
                    .to_dict()
                )
        return dict()


@register(move_first=True)
class InstrumentFinancialStatisticsMetricBackend(InstrumentMetricBaseBackend):
    statistic = STATISTICS_METRIC
    keys = [STATISTICS_METRIC]

    def compute_metrics(self, basket: Instrument) -> Generator[Metric, None, None]:
        val_date = self._get_valid_date(basket)
        metrics = Dataloader(basket, val_date, target_currency_key=self.TARGET_CURRENCY_KEY).compute()
        yield Metric(
            metrics=metrics,
            basket_id=basket.id,
            basket_content_type_id=self.content_type.id,
            key=self.statistic.key,
            date=None,
        )

    def _get_valid_date(self, instrument: Instrument) -> date:
        if self.val_date is None and instrument.last_valuation_date:
            return instrument.last_valuation_date
        elif self.val_date:
            with suppress(InstrumentPrice.DoesNotExist):
                return instrument.valuations.filter(date__lte=self.val_date).latest("date").date
        raise MetricInvalidParameterException()


@register(move_first=True)
class InstrumentFinancialStatisticsUSDMetricBackend(InstrumentFinancialStatisticsMetricBackend):
    statistic = STATISTICS_METRIC_USD
    keys = [STATISTICS_METRIC_USD]
    TARGET_CURRENCY_KEY = "USD"
