from typing import Optional

from django.utils.translation import gettext_lazy as _
from wbcore.contrib.color.enums import WBColor
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbfdm.models import InstrumentRequest


class InstrumentRequestDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="instrument_data__name", label="Instrument Name"),
                dp.Field(key="instrument_data__isin", label="Instrument ISIN"),
                dp.Field(key="requester", label="Requester"),
                dp.Field(key="created", label="Created"),
                dp.Field(key="notes", label="Notes"),
                dp.Field(key="handler", label="Handler"),
                dp.Field(key="created_instrument", label="Created Instrument"),
            ],
            legends=[
                dp.Legend(
                    key="status",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.YELLOW_LIGHT.value,
                            label=InstrumentRequest.Status.DRAFT.label,
                            value=InstrumentRequest.Status.DRAFT.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.BLUE_LIGHT.value,
                            label=InstrumentRequest.Status.PENDING.label,
                            value=InstrumentRequest.Status.PENDING.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value,
                            label=InstrumentRequest.Status.APPROVED.label,
                            value=InstrumentRequest.Status.APPROVED.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.RED_LIGHT.value,
                            label=InstrumentRequest.Status.DENIED.label,
                            value=InstrumentRequest.Status.DENIED.value,
                        ),
                    ],
                ),
            ],
            formatting=[
                dp.Formatting(
                    column="status",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.YELLOW_LIGHT.value},
                            condition=("==", InstrumentRequest.Status.DRAFT.value),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.BLUE_LIGHT.value},
                            condition=("==", InstrumentRequest.Status.PENDING.value),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=("==", InstrumentRequest.Status.APPROVED.value),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.RED_LIGHT.value},
                            condition=("==", InstrumentRequest.Status.DENIED.value),
                        ),
                    ],
                )
            ],
        )

    def get_instance_display(self) -> Display:
        fields = [
            [repeat_field(3, "status")],
            [repeat_field(3, "notes")],
        ]
        if "pk" in self.view.kwargs:
            fields.append(["requester", "created", "created_instrument"])
        fields.append([repeat_field(3, "data_section")])

        return create_simple_display(
            fields,
            [
                create_simple_section(
                    "data_section",
                    _("Instrument Data"),
                    [
                        [
                            repeat_field(2, "instrument_data__instrument_type"),
                            "instrument_data__name",
                            "instrument_data__name_repr",
                        ],
                        [
                            "instrument_data__isin",
                            "instrument_data__ticker",
                            "instrument_data__refinitiv_identifier_code",
                            "instrument_data__refinitiv_mnemonic_code",
                        ],
                        [repeat_field(2, "instrument_data__currency"), repeat_field(2, "instrument_data__country")],
                        [
                            repeat_field(4, "instrument_data__is_cash"),
                        ],
                        [repeat_field(4, "instrument_data__tags")],
                        [repeat_field(4, "instrument_data__classifications")],
                    ],
                )
            ],
        )
