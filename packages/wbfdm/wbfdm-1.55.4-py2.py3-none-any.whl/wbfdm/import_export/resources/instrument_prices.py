from import_export import fields
from import_export.widgets import ForeignKeyWidget
from wbcore.contrib.io.resources import FilterModelResource

from wbfdm.models import Instrument, InstrumentPrice


class InstrumentPriceExportResource(FilterModelResource):
    """
    Instrument Price Resource class to use to export instrument price from the viewset
    """

    instrument = fields.Field(
        column_name="instrument",
        attribute="instrument",
        widget=ForeignKeyWidget(Instrument, field="isin"),
    )

    class Meta:
        fields = (
            "date",
            "net_value",
            "gross_value",
            "market_capitalization",
            "sharpe_ratio",
            "correlation",
            "beta",
            "outstanding_shares_consolidated",
            "volume",
            "volume_50d",
            "instrument",
        )
        export_order = fields
        model = InstrumentPrice
