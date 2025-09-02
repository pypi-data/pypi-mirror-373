from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class RelatedInstrumentThroughInstrumentEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:instrument-relatedinstrument-list",
            args=[self.view.kwargs["instrument_id"]],
            request=self.request,
        )


class ClassifiedInstrumentEndpointConfig(EndpointViewConfig):
    PK_FIELD = "instrument"

    def get_endpoint(self, **kwargs):
        return reverse("wbfdm:classifiedinstrument-list", args=[], request=self.request)

    def get_instance_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:instrument-list",
            args=[],
            request=self.request,
        )

    def get_create_endpoint(self, **kwargs):
        return None

    def get_delete_endpoint(self, **kwargs):
        return None


class InstrumentFavoriteGroupEndpointConfig(EndpointViewConfig):
    def get_update_endpoint(self, **kwargs):
        if self.view.is_owner:
            return self.get_instance_endpoint(**kwargs)
        return None

    def get_delete_endpoint(self, **kwargs):
        return self.get_update_endpoint(**kwargs)
