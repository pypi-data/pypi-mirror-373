from typing import Optional

from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    Display,
    create_simple_display,
)
from wbcore.metadata.configs.display.instance_display.utils import repeat_field
from wbcore.metadata.configs.display.view_config import DisplayViewConfig


class InstrumentFavoriteGroupDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="name", label="Name"),
                dp.Field(key="owner", label="Owner"),
                dp.Field(key="instruments", label="Instruments"),
                dp.Field(key="public", label="Public"),
            ]
        )

    def get_instance_display(self) -> Display:
        return create_simple_display(
            [
                [repeat_field(2, "name")],
                ["public", "primary"],
                [repeat_field(2, "instruments")],
            ]
        )


class RelatedInstrumentThroughInstrumentDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        fields = [
            dp.Field(key="related_instrument", label="Related Instrument", width=500),
            dp.Field(key="related_type", label="Type"),
            dp.Field(key="is_primary", label="Is Primary"),
        ]

        if self.tooltip:
            fields = fields[:1]

        return dp.ListDisplay(fields=[*fields])

    def get_instance_display(self) -> Display:
        return create_simple_display([["related_instrument", "related_type", "is_primary"]])


class ClassifiedInstrumentDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        if group := self.view.classification_group:
            fields = [dp.Field(key="instrument", label="Instrument")]
            level_representations = group.get_levels_representation()
            for key, label in zip(reversed(group.get_fields_names(sep="_")), reversed(level_representations[1:])):
                fields.append(
                    dp.Field(key=f"classification_{key}", label=label),
                )
            fields.extend(
                [
                    dp.Field(key="classification", label=level_representations[0]),
                    dp.Field(key="tags", label="Tags"),
                ]
            )
            return dp.ListDisplay(fields=fields, editable=True)
