from typing import Optional

from django.utils.translation import gettext as _
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display import DisplayViewConfig


class InstrumentPriceDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="valuation_date", label=_("Date")),
                dp.Field(key="open", label=_("Open")),
                dp.Field(key="high", label=_("High")),
                dp.Field(key="low", label=_("Low")),
                dp.Field(key="close", label=_("Close")),
                dp.Field(key="volume", label=_("Volume")),
                dp.Field(key="outstanding_shares", label=_("Oustanding Shares")),
                dp.Field(key="market_capitalization", label=_("Market Cap.")),
            ],
        )
