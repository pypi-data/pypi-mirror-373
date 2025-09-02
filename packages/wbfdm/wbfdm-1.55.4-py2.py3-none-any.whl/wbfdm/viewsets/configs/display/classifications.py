from typing import Optional

from django.utils.translation import gettext_lazy as _
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
    create_simple_section,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class ClassificationDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label="Title"),
                dp.Field(key="code_aggregated", label="Code"),
                dp.Field(key="parent", label="Parent"),
                dp.Field(key="group", label="Group"),
                dp.Field(key="height", label="Height"),
                dp.Field(key="level", label="Level"),
                dp.Field(key="level_representation", label="Level Representation"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["name", "code_aggregated"],
                ["parent", "group"],
                ["height", "level_representation"],
                [repeat_field(2, "description")],
                [repeat_field(2, "childs_section")],
                [repeat_field(2, "instruments_section")],
            ],
            [
                create_simple_section(
                    "childs_section", _("Child Classifications"), [["childs"]], "childs", collapsed=False
                ),
                create_simple_section(
                    "instruments_section", _("Instruments"), [["instruments"]], "instruments", collapsed=True
                ),
            ],
        )


class ClassificationGroupDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label="Title"),
                dp.Field(key="is_primary", label="Primary"),
                dp.Field(key="max_depth", label="Max Depth"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "name")],
                ["is_primary", "max_depth"],
                [repeat_field(2, "classifications_section")],
            ],
            [
                create_simple_section(
                    "classifications_section",
                    _("Classification"),
                    [["classifications"]],
                    "classifications",
                    collapsed=False,
                )
            ],
        )


class InstrumentClassificationThroughDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="instrument", label="Instrument") if "instrument_id" not in self.view.kwargs else None,
                dp.Field(key="classification", label="Classification")
                if "classification_id" not in self.view.kwargs
                else None,
                dp.Field(key="is_favorite", label="Favorite"),
                dp.Field(key="pure_player", label="Pure Player"),
                dp.Field(key="top_player", label="Top Player"),
                dp.Field(key="reason", label="Reason"),
                dp.Field(key="percent_of_revenue", label="% of revenue"),
                dp.Field(key="tags", label="Tags"),
                dp.Field(key="related_instruments", label="RelatedInstruments"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [
                    "instrument" if "instrument_id" not in self.view.kwargs else ".",
                    "classification" if "classification_id" not in self.view.kwargs else ".",
                ],
                ["is_favorite", "top_player"],
                ["pure_player", "percent_of_revenue"],
                [repeat_field(2, "reason")],
                [repeat_field(2, "tags")],
                [repeat_field(2, "related_instruments_section")],
            ],
            [
                create_simple_section(
                    "related_instruments_section",
                    _("Related Instruments"),
                    [["related_instruments"]],
                    "related_instruments",
                    collapsed=False,
                )
            ],
        )


class ClassificationInstrumentRelatedInstrumentDisplayConfig(DisplayViewConfig):
    def get_list_display(self):
        return dp.ListDisplay(
            fields=[
                dp.Field(key="related_instrument", label="Related Instrument"),
                dp.Field(key="related_instrument_type", label="Type"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [
                    "related_instrument",
                    "related_instrument_type",
                ]
            ]
        )
