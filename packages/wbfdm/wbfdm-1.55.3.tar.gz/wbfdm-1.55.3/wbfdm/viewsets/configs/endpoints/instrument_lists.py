from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class InstrumentListThroughModelEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:instrumentlistthrough-list",
            args=[],
            request=self.request,
        )


class InstrumentListThroughModelInstrumentListEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:instrumentlist-instrumentlistthrough-list",
            args=[self.view.kwargs["instrument_list_id"]],
            request=self.request,
        )


class InstrumentListThroughModelInstrumentEndpointConfig(EndpointViewConfig):
    PK_FIELD = "instrument_list"  # we expect that users want to go directly to the Instrument List model

    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:instrument-instrumentlistthrough-list",
            args=[self.view.kwargs["instrument_id"]],
            request=self.request,
        )

    def get_instance_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:instrumentlist-list",
            args=[],
            request=self.request,
        )
