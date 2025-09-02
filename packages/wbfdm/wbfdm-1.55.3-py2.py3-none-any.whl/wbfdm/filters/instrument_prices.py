from datetime import date

from django.db import models
from psycopg.types.range import DateRange
from wbcore import filters as wb_filters

from wbfdm.filters.utils import get_earliest_date, get_latest_date
from wbfdm.models import Instrument, InstrumentPrice

from .financials_analysis import byearend_2_year_ago


class FakeDateRange(wb_filters.FilterSet):
    date = wb_filters.FinancialPerformanceDateRangeFilter(
        method=lambda queryset, label, value: queryset,
        label="Date Range",
        required=True,
        clearable=False,
        initial=lambda r, v, q: DateRange(byearend_2_year_ago(r, v, q), date.today()),
    )

    class Meta:
        model = Instrument
        fields = {}


class InstrumentPriceFilterSet(wb_filters.FilterSet):
    date = wb_filters.FinancialPerformanceDateRangeFilter(
        method=wb_filters.DateRangeFilter.base_date_range_filter_method,
        label="Date Range",
        required=True,
        clearable=False,
        initial=lambda r, v, q: DateRange(get_earliest_date(r, v, q), get_latest_date(r, v, q)),
    )

    class Meta:
        model = InstrumentPrice
        fields = {
            "volume": ["gte", "exact", "lte"],
            "volume_50d": ["gte", "exact", "lte"],
            # 'volume_200d': ['exact'],
            "market_capitalization": ["gte", "exact", "lte"],
            "instrument__instrument_type": ["exact"],
        }


class InstrumentPriceSingleBenchmarkFilterSet(InstrumentPriceFilterSet):
    benchmark = wb_filters.ModelChoiceFilter(
        label="Compare to..",
        queryset=Instrument.objects.all(),
        endpoint=Instrument.get_representation_endpoint(),
        value_key=Instrument.get_representation_value_key(),
        label_key=Instrument.get_representation_label_key(),
        filter_params={"is_security": True},
        method="fake_filter",
    )

    class Meta:
        model = InstrumentPrice
        fields = {}


class InstrumentPriceMultipleBenchmarkChartFilterSet(InstrumentPriceFilterSet):
    benchmarks = wb_filters.ModelMultipleChoiceFilter(
        label="Benchmarks",
        queryset=Instrument.objects.all(),
        endpoint=Instrument.get_representation_endpoint(),
        value_key=Instrument.get_representation_value_key(),
        label_key=Instrument.get_representation_label_key(),
        filter_params={"is_security": True},
        method="fake_filter",
    )
    normalized = wb_filters.BooleanFilter(label="Normalize", initial=True, required=True, method="fake_filter")

    class Meta:
        model = InstrumentPrice
        fields = {}


class InstrumentPriceFrequencyFilter(InstrumentPriceFilterSet):
    class FrequencyChoice(models.TextChoices):
        DAILY = "B", "Daily"
        WEEKLY = "W-MON", "Weekly (Monday)"
        MONTHLY = "BME", "Monthly"

    frequency = wb_filters.ChoiceFilter(
        label="Frequency",
        choices=FrequencyChoice.choices,
        initial=FrequencyChoice.DAILY,
        required=True,
        method="fake_filter",
    )

    class Meta:
        model = InstrumentPrice
        fields = {}


class InstrumentPriceFinancialStatisticsChartFilterSet(
    InstrumentPriceSingleBenchmarkFilterSet, InstrumentPriceFrequencyFilter
):
    class Meta:
        model = InstrumentPrice
        fields = {}


class InstrumentPriceInstrumentFilterSet(wb_filters.FilterSet):
    class Meta:
        model = InstrumentPrice
        fields = {
            "date": ["gte", "exact", "lte"],
            "net_value": ["gte", "exact", "lte"],
            "sharpe_ratio": ["gte", "exact", "lte"],
            "correlation": ["gte", "exact", "lte"],
            "beta": ["gte", "exact", "lte"],
            "calculated": ["exact"],
        }
