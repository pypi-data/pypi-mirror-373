from wbcore.metadata.configs.titles import TitleViewConfig

from wbfdm.models import Instrument


class InstrumentPriceTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Instrument Prices"

    def get_instance_title(self):
        return "Price: {{_instrument.name}} {{date}}"

    def get_create_title(self):
        return "New Price"


class InstrumentPriceInstrumentTitleConfig(InstrumentPriceTitleConfig):
    def get_list_title(self):
        return f"{str(self.view.instrument)} - Prices"


class InstrumentPriceStatisticsInstrumentTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return f"{str(self.view.instrument)} - Statistics Chart"


class MonthlyPerformancesInstrumentTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return f"{str(self.view.instrument)} - Monthly Returns Table"


class InstrumentTitleConfigMixin(TitleViewConfig):
    def get_list_title(self):
        assert self.message, "No message has been set"
        instrument = Instrument.objects.get(id=self.view.kwargs["instrument_id"])
        return f"{self.message} {str(instrument)}"


class FinancialStatisticsInstrumentTitleConfig(InstrumentTitleConfigMixin):
    def get_list_title(self):
        return f"{str(self.view.instrument)} - Financial Statistics Chart"


class InstrumentPriceInstrumentDistributionReturnsChartTitleConfig(InstrumentTitleConfigMixin):
    def get_list_title(self):
        return f"{str(self.view.instrument)} - Distribution Returns Chart"


class BestAndWorstReturnsInstrumentTitleConfig(InstrumentTitleConfigMixin):
    def get_list_title(self):
        return f"{str(self.view.instrument)} - Best and Worst returns Table "
