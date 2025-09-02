from datetime import date, timedelta

import pandas as pd
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.pandas import fields as pf
from wbcore.serializers.fields.types import DisplayMode
from wbcore.utils.date import get_date_interval_from_request

from wbfdm.filters.instrument_prices import FakeDateRange
from wbfdm.models.instruments import Instrument
from wbfdm.viewsets.configs.display.prices import InstrumentPriceDisplayConfig
from wbfdm.viewsets.configs.titles.prices import InstrumentPriceTitleViewConfig

from .mixins import InstrumentMixin


class InstrumentPriceViewSet(InstrumentMixin, ExportPandasAPIViewSet):
    IDENTIFIER = "wbfdm:instrument-price"
    display_config_class = InstrumentPriceDisplayConfig
    title_config_class = InstrumentPriceTitleViewConfig
    pandas_fields = pf.PandasFields(
        fields=(
            pf.PKField(key="id", label="ID"),
            pf.DateField(
                key="valuation_date",
                label="valuation_date",
            ),
            pf.FloatField(key="open", label="open"),
            pf.FloatField(key="high", label="high"),
            pf.FloatField(key="low", label="low"),
            pf.FloatField(key="close", label="close"),
            pf.FloatField(key="volume", label="volume", display_mode=DisplayMode.SHORTENED),
            pf.FloatField(key="outstanding_shares", label="outstanding_shares", display_mode=DisplayMode.SHORTENED),
            pf.FloatField(
                key="market_capitalization", label="market_capitalization", display_mode=DisplayMode.SHORTENED
            ),
        )
    )
    permission_classes = []
    filterset_class = FakeDateRange
    queryset = Instrument.objects.all()
    ordering_fields = (
        "valuation_date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "outstanding_shares",
        "market_capitalization",
    )
    ordering = ["-valuation_date"]

    def get_queryset(self):
        return Instrument.objects.filter(id=self.instrument.id)

    def get_dataframe(self, request, queryset, **kwargs):
        start, end = get_date_interval_from_request(request, date_range_fieldname="date")
        if not end:
            end = date.today()
        if not start:
            start = end - timedelta(days=365)
        return pd.DataFrame(queryset.dl.market_data(from_date=start, to_date=end))
