from wbcore import filters
from wbcore.filters.defaults import five_year_data_range

from wbfdm.enums import CalendarType, DataType, Indicator, MarketDataChartType
from wbfdm.models.instruments import Instrument


class MarketDataChartFilterSet(filters.FilterSet):
    period = filters.FinancialPerformanceDateRangeFilter(
        label="Period", method="fake_filter", initial=five_year_data_range, required=True
    )
    chart_type = filters.ChoiceFilter(
        method="fake_filter",
        label="Chart Type",
        choices=MarketDataChartType.choices,
        required=True,
        initial=MarketDataChartType.CLOSE,
    )
    benchmarks = filters.ModelMultipleChoiceFilter(
        label="Benchmarks",
        queryset=Instrument.objects.all(),
        endpoint=Instrument.get_representation_endpoint(),
        value_key=Instrument.get_representation_value_key(),
        label_key=Instrument.get_representation_label_key(),
        filter_params={"is_security": True},
        method="fake_filter",
    )
    indicators = filters.MultipleChoiceFilter(
        method="fake_filter",
        label="Indicators",
        choices=Indicator.choices,
        required=False,
    )
    volume = filters.BooleanFilter(
        method="fake_filter",
        label="Add Volume",
        initial=False,
    )
    show_estimates = filters.BooleanFilter(
        method="fake_filter",
        label="Show Estimates",
        initial=True,
    )

    class Meta:
        model = Instrument
        fields = {}


class FinancialRatioFilterSet(filters.FilterSet):
    ttm = filters.BooleanFilter(method="fake_filter", label="TTM/FTM", initial=True, required=True)

    period = filters.FinancialPerformanceDateRangeFilter(
        method="fake_filter", label="Period", initial=five_year_data_range, required=True
    )

    class Meta:
        model = Instrument
        fields = {}


class StatementFilter(filters.FilterSet):
    data_type = filters.ChoiceFilter(
        method="fake_filter",
        label="Data Type",
        choices=DataType.choices,
        required=True,
        initial=DataType.STANDARDIZED,
    )

    class Meta:
        model = Instrument
        fields = {}


class StatementWithEstimateFilter(filters.FilterSet):
    calendar_type = filters.ChoiceFilter(
        method="fake_filter",
        label="Calendar Type",
        choices=CalendarType.choices,
        required=True,
        initial=CalendarType.FISCAL,
    )

    class Meta:
        model = Instrument
        fields = {}
