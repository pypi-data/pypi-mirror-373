from contextlib import suppress
from datetime import date
from decimal import Decimal
from typing import Any, Generator, Generic, Type, TypeVar

import pandas as pd
from django.contrib.contenttypes.models import ContentType
from django.db.models import F, Model, QuerySet, Value
from rest_framework.serializers import Field
from wbcore import serializers as wb_serializers
from wbcore.contrib.currency.models import CurrencyFXRates

from wbfdm.models import Instrument, InstrumentPrice

from ..dto import Metric, MetricField, MetricKey
from ..exceptions import MetricInvalidParameterException
from .utils import get_today

T = TypeVar("T", bound=Model)


class AbstractBackend(Generic[T]):
    BASKET_MODEL_CLASS: Type[Model]
    keys: list[MetricKey]

    def __init__(self, val_date: date | None):
        self.val_date = val_date
        if not self.BASKET_MODEL_CLASS:
            raise ValueError("A class implementing AbstractBackend needs to define a BASKET_MODEL_CLASS")
        self.content_type = ContentType.objects.get_for_model(self.BASKET_MODEL_CLASS)

    def compute_metrics(self, basket: Any) -> Generator[Metric, None, None]:
        raise NotImplementedError()

    def get_queryset(self) -> QuerySet:
        return self.BASKET_MODEL_CLASS.objects.all()

    def get_serializer_field_attr(self, metric_field: MetricField) -> dict[str, Any]:
        """
        Returns all the serializer attributes for that metric

        We expect the implementing backends to override this method to define custom logics
        """
        return {
            "decorators": metric_field.decorators,
            "help_text": metric_field.help_text,
            **metric_field.serializer_kwargs,
        }

    def get_serializer_fields(
        self, with_prefixed_key: bool = False, metric_key: MetricKey | None = None
    ) -> dict[str, Field]:
        if metric_key is None:
            metric_keys = self.keys
        else:
            metric_keys = [metric_key]
        fields = {}
        for metric_key in metric_keys:
            fields.update(
                {
                    field_key: wb_serializers.FloatField(
                        label=field_title,
                        read_only=True,
                        **self.get_serializer_field_attr(metric_key.subfields_map[field_key]),
                    )
                    for field_key, field_title in metric_key.get_fields(with_prefixed_key=with_prefixed_key)
                }
            )
            for extra_subfield in metric_key.extra_subfields:
                fields[f"{metric_key.key}_{extra_subfield.key}"] = (
                    wb_serializers.ModelSerializer.serializer_field_mapping[
                        extra_subfield.field_type
                    ](read_only=True, label=extra_subfield.label, **self.get_serializer_field_attr(extra_subfield))
                )
        return fields


class InstrumentMetricBaseBackend(AbstractBackend[Instrument]):
    BASKET_MODEL_CLASS = Instrument
    TARGET_CURRENCY_KEY: str | None = None

    def get_queryset(self) -> QuerySet[Instrument]:
        return super().get_queryset().filter(is_investable_universe=True)

    def _get_valid_date(self, instrument: Instrument) -> date:
        val_date = None
        if self.val_date is None and instrument.last_price_date:
            val_date = instrument.last_price_date
        elif self.val_date:
            with suppress(InstrumentPrice.DoesNotExist):
                val_date = instrument.prices.filter(date__lte=self.val_date).latest("date").date
        if val_date:
            return min(
                [val_date, (get_today() - pd.tseries.offsets.BDay(1)).date()]
            )  # ensure that value date is at least lower than today (otherwise, we might compute performance for intraday, which we do not want yet
        else:
            raise MetricInvalidParameterException()


class BaseDataloader:
    METRIC_KEY: str

    def __init__(
        self,
        basket,
        val_date: date | None = None,
        min_date: date | None = None,
        target_currency_key: str | None = None,
        use_cached_metrics_key: str | None = None,
        basket_objects: QuerySet | None = None,
    ):
        self.val_date = val_date
        self.min_date = min_date
        self.basket = basket
        self.use_cached_metrics_key = use_cached_metrics_key
        self.target_currency_key = target_currency_key
        self.basket_objects = basket_objects
        if self.basket_objects is None:
            self.basket_objects = self._get_basket_basket_objects()
        self.basket_object_ids = list(map(lambda x: x.id, self.basket_objects))
        self.aggregate_callback = "mean"
        if self.target_currency_key == "USD":
            self.fx_rate_expression = F("currency_fx_rate_to_usd__value")
        elif self.target_currency_key:
            self.fx_rate_expression = CurrencyFXRates.get_fx_rates_subquery_for_two_currencies(
                "date", start_currency="instrument__currency", target_currency=self.target_currency_key
            )
        else:
            self.fx_rate_expression = Value(Decimal(1.0))

    def _get_basket_basket_objects(self) -> QuerySet:
        """
        Return an iterable of instrument contains within the basket. Expected to be override for custom logic

        Returns:
            An iterable of instrument. Default to the basket itself
        """
        return Instrument.objects.filter(id=self.basket.id)

    def _compute(self):
        raise NotImplementedError()

    def compute(self):
        if self.basket_object_ids:
            if self.use_cached_metrics_key:
                from wbfdm.contrib.metric.models import InstrumentMetric

                df = pd.json_normalize(
                    InstrumentMetric.objects.filter(
                        basket_content_type=ContentType.objects.get_for_model(self.basket_objects.model),
                        basket_id__in=self.basket_object_ids,
                        key=self.use_cached_metrics_key,
                        date__isnull=True,
                    ).values_list("metrics", flat=True)
                )
                if not df.empty:
                    if (
                        "date" in df.columns
                    ):  # it can happen that the cached metric don't contain a date key value, so we ffill it in case
                        df["date"] = df["date"].ffill()
                    if isinstance(self.aggregate_callback, dict):
                        df = df.agg({k: v for k, v in self.aggregate_callback.items() if k in df.columns})
                    else:
                        df = df.agg(self.aggregate_callback)
                    return df.dropna().to_dict()
        return self._compute()
