from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class InstrumentEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbfdm:instrument-list", args=[], request=self.request)

    def get_delete_endpoint(self, **kwargs):
        return None

    def get_create_endpoint(self, **kwargs):
        return reverse("wbfdm:instrumentrequest-list", args=[], request=self.request)
