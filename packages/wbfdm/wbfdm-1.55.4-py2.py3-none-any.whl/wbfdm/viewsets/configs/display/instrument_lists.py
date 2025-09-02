from typing import Optional

from django.utils.translation import gettext as _
from wbcore.contrib.color.enums import WBColor
from wbcore.enums import Operator, Unit
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display import (
    Display,
    Inline,
    Layout,
    Page,
    Section,
)
from wbcore.metadata.configs.display.instance_display.operators import default
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)

from wbfdm.models import InstrumentList


class InstrumentListDisplayConfig(dp.DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label="Name"),
                dp.Field(key="instrument_list_type", label="Type"),
            ],
            legends=[
                dp.Legend(
                    items=[
                        dp.LegendItem(
                            icon=WBColor.RED_LIGHT.value,
                            label=_("Exclusion List"),
                        ),
                    ],
                )
            ],
            formatting=[
                dp.Formatting(
                    column="instrument_list_type",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.RED_LIGHT.value},
                            condition=dp.Condition(
                                operator=Operator.EQUAL, value=InstrumentList.InstrumentListType.EXCLUSION
                            ),
                        ),
                    ],
                ),
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            grid_template_areas=[["name", "instrument_list_type"], ["instruments_section", "instruments_section"]],
            sections=[
                Section(
                    key="instruments_section",
                    title="Instruments",
                    collapsible=True,
                    collapsed=False,
                    display=Display(
                        pages=[
                            Page(
                                title="Instruments",
                                layouts={
                                    default(): Layout(
                                        grid_template_areas=[["instruments"]],
                                        inlines=[Inline(key="instruments", endpoint="instruments")],
                                    )
                                },
                            ),
                        ]
                    ),
                ),
            ],
        )


class InstrumentListThroughModelDisplayConfig(dp.DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = []
        if self.view.kwargs.get("instrument_id", None):
            fields = [dp.Field(key="instrument_list", label="Instrument List", width=Unit.PIXEL(250))]
        elif self.view.kwargs.get("instrument_list_id", None):
            fields = [
                dp.Field(key="instrument", label="Instrument", width=Unit.PIXEL(300)),
                dp.Field(key="instrument_str", label="Instrument Scraped", width=Unit.PIXEL(300)),
            ]
        fields.extend(
            [
                dp.Field(key="from_date", label="From Date", width=Unit.PIXEL(125)),
                dp.Field(key="to_date", label="To Date", width=Unit.PIXEL(125)),
                dp.Field(key="comment", label="Comment", width=Unit.PIXEL(350)),
            ]
        )
        return dp.ListDisplay(
            fields=fields,
            legends=[
                dp.Legend(
                    items=[
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value,
                            label=_("Validated"),
                        ),
                        dp.LegendItem(
                            icon=WBColor.YELLOW_DARK.value,
                            label=_("Not Validated"),
                        ),
                    ],
                )
            ],
            formatting=[
                dp.Formatting(
                    column="validated",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=dp.Condition(operator=Operator.EQUAL, value=True),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.YELLOW_DARK.value},
                            condition=dp.Condition(operator=Operator.EQUAL, value=False),
                        ),
                    ],
                ),
            ],
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            grid_template_areas=[
                ["instrument", "instrument_str"],
                ["instrument_list", "validated"],
                ["from_date", "to_date"],
                ["comment", "comment"],
            ]
        )
