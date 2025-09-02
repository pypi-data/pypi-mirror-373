from rest_framework.reverse import reverse
from wbcore.contrib.icons import WBIcon
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig


class InstrumentPriceButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return {
            bt.HyperlinkButton(
                key="import_source",
                label="Import Source",
                icon=WBIcon.SAVE.icon,
            )
        }


class InstrumentPriceInstrumentButtonConfig(InstrumentPriceButtonConfig):
    pass


class FinancialStatisticsInstrumentButtonConfig(ButtonViewConfig):
    def get_custom_buttons(self):
        if instrument_id := self.view.kwargs.get("instrument_id", None):
            return {
                bt.DropDownButton(
                    label="Charts",
                    icon=WBIcon.UNFOLD.icon,
                    buttons=(
                        bt.WidgetButton(
                            endpoint=f'{reverse("wbfdm:market_data-list", args=[instrument_id], request=self.request)}?chart_type=ret',
                            label="Returns Chart",
                            icon=WBIcon.CHART_BARS_HORIZONTAL.icon,
                        ),
                        bt.WidgetButton(
                            endpoint=f'{reverse("wbfdm:market_data-list", args=[instrument_id], request=self.request)}?chart_type=drawdown',
                            label="Drawdowns Chart",
                            icon=WBIcon.CHART_BARS_HORIZONTAL.icon,
                        ),
                    ),
                ),
                bt.WidgetButton(
                    key="bestandworstreturns",
                    label="Best and Worst returns table",
                    icon=WBIcon.CHART_BARS_HORIZONTAL.icon,
                ),
            }

        return set()
