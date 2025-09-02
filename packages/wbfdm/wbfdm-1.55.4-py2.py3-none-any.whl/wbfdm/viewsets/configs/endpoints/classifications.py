from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class ClassificationEndpointConfig(EndpointViewConfig):
    pass


class ClassificationClassificationGroupEndpointConfig(ClassificationEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:classificationgroup-classification-list",
            args=[self.view.kwargs["group_id"]],
            request=self.request,
        )


class ClassificationParentClassificationEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:classificationparent-classification-list",
            args=[self.view.kwargs["parent_id"]],
            request=self.request,
        )


class ClassificationTreeChartEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class ClassificationIcicleChartEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None


class InstrumentClassificationThroughEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:instrumentclassificationrelationship-list",
            args=[],
            request=self.request,
        )

    def get_update_endpoint(self, **kwargs):
        if "pk" in self.view.kwargs:
            return super().get_update_endpoint()
        return None


class InstrumentClassificationThroughInstrumentModelEndpointConfig(InstrumentClassificationThroughEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:instrument-classification-list",
            args=[self.view.instrument.get_root().id],
            request=self.request,
        )


class ClassificationInstrumentThroughInstrumentModelEndpointConfig(InstrumentClassificationThroughEndpointConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:classification-instrument-list",
            args=[self.view.kwargs["classification_id"]],
            request=self.request,
        )


class ClassificationInstrumentRelatedInstrumentEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse(
            "wbfdm:related_instrument-list",
            args=[self.view.kwargs["classified_instrument_id"]],
            request=self.request,
        )
