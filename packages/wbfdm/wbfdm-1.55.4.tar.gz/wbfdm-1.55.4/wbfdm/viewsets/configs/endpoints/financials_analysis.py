from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class SummaryTableInstrumentChartEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:instrument-summarytablechart-list",
            args=[self.view.kwargs["instrument_id"]],
            request=self.request,
        )


class FinancialsGraphInstrumentChartEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:instrument-financialsgraphchart-list",
            args=[self.view.kwargs["instrument_id"]],
            request=self.request,
        )


class ProfitabilityRatiosInstrumentChartEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:instrument-profitabilityratioschart-list",
            args=[self.view.kwargs["instrument_id"]],
            request=self.request,
        )


class CashFlowAnalysisInstrumentTableChartEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:instrument-cashflowanalysistablechart-list",
            args=[self.view.kwargs["instrument_id"]],
            request=self.request,
        )


class CashFlowAnalysisInstrumentBarChartEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:instrument-cashflowanalysisbarchart-list",
            args=[self.view.kwargs["instrument_id"]],
            request=self.request,
        )


class NetDebtAndEbitdaInstrumentChartEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:instrument-netdebtandebitdachart-list",
            args=[self.view.kwargs["instrument_id"]],
            request=self.request,
        )


class EarningsInstrumentChartEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:instrument-earningschart-list",
            args=[self.view.kwargs["instrument_id"]],
            request=self.request,
        )
