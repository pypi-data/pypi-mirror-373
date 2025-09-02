from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig

from wbfdm.models import InstrumentRequest


class InstrumentRequestEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbfdm:instrumentrequest-list", args=[], request=self.request)

    def get_instance_endpoint(self, **kwargs):
        try:
            obj = self.view.get_object()
            if not self.view.has_validation_permission and obj.status != InstrumentRequest.Status.DRAFT:
                return None
        except AssertionError:
            pass
        return self.get_endpoint(**kwargs)

    def get_delete_endpoint(self, **kwargs):
        return None
