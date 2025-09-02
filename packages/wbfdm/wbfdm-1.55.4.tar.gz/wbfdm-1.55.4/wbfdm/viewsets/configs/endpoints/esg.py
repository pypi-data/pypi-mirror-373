from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class InstrumentESGPAIEndpointViewConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:pai-list",
            args=[self.view.kwargs["instrument_id"]],
            request=self.request,
        )


class InstrumentESGControversiesEndpointViewConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:controversies-list",
            args=[self.view.kwargs["instrument_id"]],
            request=self.request,
        )
