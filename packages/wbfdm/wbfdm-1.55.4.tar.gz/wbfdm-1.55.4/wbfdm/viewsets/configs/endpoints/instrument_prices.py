from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class InstrumentPriceInstrumentEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class InstrumentPriceStatisticsInstrumentEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:instrument-pricestatisticchart-list",
            [self.view.kwargs["instrument_id"]],
            request=self.request,
        )


class MonthlyPerformancesInstrumentEndpointConfig(InstrumentPriceInstrumentEndpointConfig):
    pass


class FinancialStatisticsInstrumentEndpointConfig(InstrumentPriceInstrumentEndpointConfig):
    pass


class InstrumentPriceInstrumentDistributionReturnsChartEndpointConfig(EndpointViewConfig):
    pass


class BestAndWorstReturnsInstrumentEndpointConfig(EndpointViewConfig):
    pass
