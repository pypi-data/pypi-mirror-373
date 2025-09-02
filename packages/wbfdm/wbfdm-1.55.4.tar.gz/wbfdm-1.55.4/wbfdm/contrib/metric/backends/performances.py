from contextlib import suppress
from datetime import date, timedelta
from typing import Any, Generator, Iterable

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from django.db.models import Avg, BooleanField, DateField, F, QuerySet

from wbfdm.models import Instrument, InstrumentPrice, RelatedInstrumentThroughModel

from ..decorators import register
from ..dto import Metric, MetricField, MetricKey
from .base import BaseDataloader, InstrumentMetricBaseBackend
from .utils import get_today

PERFORMANCE_METRIC = MetricKey(
    key="performance",
    label="Performance",
    subfields=[
        MetricField(key="daily", label="Daily", serializer_kwargs={"percent": True, "precision": 4}, aggregate=Avg),
        MetricField(key="weekly", label="Weekly", serializer_kwargs={"percent": True, "precision": 4}, aggregate=Avg),
        MetricField(
            key="monthly", label="Monthly", serializer_kwargs={"percent": True, "precision": 4}, aggregate=Avg
        ),
        MetricField(
            key="quarterly", label="Quarterly", serializer_kwargs={"percent": True, "precision": 4}, aggregate=Avg
        ),
        MetricField(key="yearly", label="Yearly", serializer_kwargs={"percent": True, "precision": 4}, aggregate=Avg),
        MetricField(
            key="week_to_date", label="WTD", serializer_kwargs={"percent": True, "precision": 4}, aggregate=Avg
        ),
        MetricField(
            key="month_to_date", label="MTD", serializer_kwargs={"percent": True, "precision": 4}, aggregate=Avg
        ),
        MetricField(
            key="quarter_to_date", label="QTD", serializer_kwargs={"percent": True, "precision": 4}, aggregate=Avg
        ),
        MetricField(
            key="year_to_date", label="YTD", serializer_kwargs={"percent": True, "precision": 4}, aggregate=Avg
        ),
        MetricField(
            key="previous_week_to_date",
            label="Previous Week",
            serializer_kwargs={"percent": True, "precision": 4},
            aggregate=Avg,
        ),
        MetricField(
            key="previous_month_to_date",
            label="Previous Month",
            serializer_kwargs={"percent": True, "precision": 4},
            aggregate=Avg,
        ),
        MetricField(
            key="previous_quarter_to_date",
            label="Previous Quarter",
            serializer_kwargs={"percent": True, "precision": 4},
            aggregate=Avg,
        ),
        MetricField(
            key="previous_year_to_date",
            label="Previous Year",
            serializer_kwargs={"percent": True, "precision": 4},
            aggregate=Avg,
        ),
        MetricField(
            key="inception", label="Inception", serializer_kwargs={"percent": True, "precision": 4}, aggregate=Avg
        ),
    ],
    extra_subfields=[
        MetricField(
            key="is_estimated",
            label="Estimated",
            help_text="True if the performance used a estimated price",
            field_type=BooleanField,
            aggregate=None,
        ),
        MetricField(
            key="date",
            label="Performance Date",
            help_text="The date at which the performances were computed",
            field_type=DateField,
            aggregate=None,
        ),
    ],
    additional_prefixes=["benchmark", "peer"],
)

PERFORMANCE_METRIC_USD = MetricKey(
    key="performance_usd",
    label=PERFORMANCE_METRIC.label,
    subfields=PERFORMANCE_METRIC.subfields,
    additional_prefixes=PERFORMANCE_METRIC.additional_prefixes,
)


class Dataloader(BaseDataloader):
    METRIC_KEY = "performance"

    PERFORMANCE_MAP = {
        "weekly": 7,
        "monthly": 30,
        "quarterly": 120,
        "yearly": 365,
        "daily": "B",
        "week_to_date": "W-FRI",
        "month_to_date": "BME",
        "quarter_to_date": "BQE",
        "year_to_date": "BYE",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aggregate_callback = (
            lambda df: df.min() if df.name == "date" else df.mean()
        )  # we need to not sum the "date" column otherwise pandas crashes

    @classmethod
    def get_performance_date_map(cls, pivot_date) -> dict[str, date]:
        pivot_date = pivot_date + timedelta(days=1) - pd.tseries.offsets.BDay(1)
        return {
            "weekly": (pivot_date - relativedelta(weeks=1) + timedelta(days=1) - pd.tseries.offsets.BDay(1)).date(),
            "monthly": (pivot_date - relativedelta(months=1) + timedelta(days=1) - pd.tseries.offsets.BDay(1)).date(),
            "quarterly": (
                pivot_date - relativedelta(months=3) + timedelta(days=1) - pd.tseries.offsets.BDay(1)
            ).date(),
            "yearly": (pivot_date - relativedelta(years=1) + timedelta(days=1) - pd.tseries.offsets.BDay(1)).date(),
            "daily": (pivot_date - pd.tseries.offsets.BDay(1)).date(),
            "week_to_date": (pivot_date - pd.tseries.offsets.Week(1, weekday=4)).date(),
            "month_to_date": (pivot_date - pd.tseries.offsets.BMonthEnd(1)).date(),
            "quarter_to_date": (pivot_date - pd.tseries.offsets.BQuarterEnd(1)).date(),
            "year_to_date": (pivot_date - pd.tseries.offsets.BYearEnd(1)).date(),
        }

    def get_data(self) -> Iterable[tuple[Instrument, pd.Series, pd.Series]]:
        """
        Helper method to return the instrument prices as a pandas Series

        Args:
            instrument: The instrument to get the prices from

        Returns:
            a tuple of the prices as Series and the calculated mask (as series as well)
        """

        qs = (
            InstrumentPrice.objects.filter(instrument__in=self.basket_objects, date__lte=self.val_date)
            .annotate_base_data()
            .annotate(fx_rate=self.fx_rate_expression, price=F("net_value") / F("fx_rate"))
        )
        fields = ["instrument", "date", "price", "fx_rate", "calculated"]
        instruments_map = {i.id: i for i in self.basket_objects}

        if self.min_date:
            qs = qs.filter(date__gte=self.min_date)
        else:
            qs = qs.filter(date__gte=F("instrument__inception_date"))
        recs = qs.values_list(*fields)
        df = (
            pd.DataFrame.from_records(recs, columns=fields)
            .sort_values(by="calculated")
            .groupby(["instrument", "date"])
            .agg("first")
            .sort_index()
        )
        for instrument_id, dff in df.groupby(level=0):
            dff = dff.droplevel(0)
            dff = dff.reindex(pd.date_range(dff.index.min(), dff.index.max()), method="ffill")
            dff.index = pd.to_datetime(dff.index).date
            yield instruments_map[instrument_id], dff["price"].astype(float), dff["calculated"]

    def _compute(self) -> dict[str, float]:
        """
        Compute the performance metrics for all the PERFORMANCE_MAP keys. If the basket is constituted of multiple instrument, take the average of each performance

        Returns:
            The metrics as dictionary
        """
        res = {}
        if self.val_date:
            agg_metrics = []
            is_estimated = False
            for _, prices_df, calculated_df in self.get_data():
                if not prices_df.empty and not calculated_df.empty:
                    metrics = {}
                    is_estimated = is_estimated or bool(calculated_df.iloc[-1])
                    for performance, start_date in self.get_performance_date_map(self.val_date).items():
                        with suppress(KeyError):
                            if start_price := prices_df.loc[start_date]:
                                metrics[performance] = round(prices_df.loc[self.val_date] / start_price - 1, 6)
                            previous_start_date = self.get_performance_date_map(start_date)[performance]
                            if previous_start_price := prices_df.loc[previous_start_date]:
                                metrics[f"previous_{performance}"] = round(
                                    prices_df.loc[start_date] / previous_start_price - 1, 6
                                )

                    if not prices_df.empty and prices_df.iloc[0]:
                        metrics["inception"] = round(float(prices_df.iloc[-1] / prices_df.iloc[0] - 1), 6)
                    agg_metrics.append(metrics)
            res = (
                pd.DataFrame(agg_metrics).astype(float).mean(axis=0).replace([np.inf, -np.inf, np.nan], None).to_dict()
            )
            res["is_estimated"] = is_estimated
        return res


@register(move_first=True)
class InstrumentPerformanceMetricBackend(InstrumentMetricBaseBackend):
    performance = PERFORMANCE_METRIC
    keys = [PERFORMANCE_METRIC]

    def get_related_instrument_relationships(self, basket) -> QuerySet[RelatedInstrumentThroughModel]:
        if issubclass(basket.__class__, Instrument):
            return RelatedInstrumentThroughModel.objects.filter(instrument=basket)
        return RelatedInstrumentThroughModel.objects.none()

    def compute_metrics(self, basket: Instrument) -> Generator[Metric, None, None]:
        val_date = self._get_valid_date(basket)
        metrics = Dataloader(basket, val_date, target_currency_key=self.TARGET_CURRENCY_KEY).compute()
        instrument_relationships = self.get_related_instrument_relationships(basket)
        if instrument_relationships.exists():
            for related_type in [
                RelatedInstrumentThroughModel.RelatedTypeChoices.BENCHMARK,
                RelatedInstrumentThroughModel.RelatedTypeChoices.PEER,
            ]:
                type_metrics = []
                for rel in instrument_relationships.filter(related_type=related_type):
                    type_metrics.append(
                        Dataloader(
                            rel.related_instrument, val_date, target_currency_key=self.TARGET_CURRENCY_KEY
                        ).compute()
                    )

                type_metrics = pd.DataFrame(type_metrics).mean(axis=0).round(6)
                for subfield in self.performance.subfields:
                    if (base_value := metrics.get(subfield.key)) and (type_value := type_metrics.get(subfield.key)):
                        metrics[f"{related_type.value.lower()}_{subfield.key}"] = round(base_value - type_value, 6)
        metrics["date"] = val_date
        yield Metric(
            metrics=metrics,
            basket_id=basket.id,
            basket_content_type_id=self.content_type.id,
            key=self.performance.key,
            date=None,
        )

    def get_serializer_field_attr(self, metric_field: MetricField) -> dict[str, Any]:
        attrs = super().get_serializer_field_attr(metric_field)
        pivot_date = self.val_date
        if not pivot_date:
            pivot_date = (get_today() - pd.tseries.offsets.BDay(1)).date()
        if "previous" in metric_field.key:
            pivot_date = Dataloader.get_performance_date_map(pivot_date)[metric_field.key.replace("previous_", "")]

        with suppress(KeyError):
            start_date = Dataloader.get_performance_date_map(pivot_date)[metric_field.key.replace("previous_", "")]
            attrs["help_text"] = (
                f"The {metric_field.label} performance is computed from {start_date:%Y-%m-%d} to {pivot_date:%Y-%m-%d}"
            )
        return attrs


@register(move_first=True)
class InstrumentPerformanceUSDMetricBackend(InstrumentPerformanceMetricBackend):
    performance = PERFORMANCE_METRIC_USD
    keys = [PERFORMANCE_METRIC_USD]
    TARGET_CURRENCY_KEY = "USD"
