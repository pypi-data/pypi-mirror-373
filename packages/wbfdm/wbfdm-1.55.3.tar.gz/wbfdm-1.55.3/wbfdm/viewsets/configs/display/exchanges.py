from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class ExchangeDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label="Name"),
                dp.Field(key="mic_code", label="MIC"),
                dp.Field(key="operating_mic_code", label="MIC (operating)"),
                dp.Field(key="bbg_exchange_codes", label="BBG Exchange"),
                dp.Field(key="bbg_composite_primary", label="BBG composite 1"),
                dp.Field(key="bbg_composite", label="BBG composite 2"),
                dp.Field(key="refinitiv_identifier_code", label="RIC"),
                dp.Field(key="refinitiv_mnemonic", label="Mnemonic"),
                dp.Field(key="country", label="Country"),
                dp.Field(key="city", label="City"),
                dp.Field(key="website", label="Website"),
                dp.Field(key="comments", label="Comments"),
                dp.Field(key="opening_time", label="Opening Time"),
                dp.Field(key="closing_time", label="Closing Time"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["name", "mic_code", "operating_mic_code", "refinitiv_identifier_code"],
                [".", "bbg_exchange_codes", "bbg_composite_primary", "bbg_composite"],
                ["country", "city", "website", "apply_round_lot_size"],
                [repeat_field(2, "opening_time"), repeat_field(2, "closing_time")],
                [repeat_field(4, "comments")],
            ]
        )
