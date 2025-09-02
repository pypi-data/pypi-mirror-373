from django.utils.functional import cached_property
from wbcore import viewsets

from wbfdm.models.instruments import InstrumentRequest
from wbfdm.serializers.instruments.instrument_requests import (
    InstrumentRequestModelSerializer,
    InstrumentRequestRepresentationSerializer,
)

from ..configs import (
    InstrumentRequestDisplayConfig,
    InstrumentRequestEndpointConfig,
    InstrumentRequestTitleConfig,
)


class InstrumentRequestRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = InstrumentRequest.objects.all()
    serializer_class = InstrumentRequestRepresentationSerializer
    search_fields = ("notes", "requester__computed_str")
    ordering_fields = ["created"]
    ordering = ["-created"]


class InstrumentRequestModelViewSet(viewsets.ModelViewSet):
    queryset = InstrumentRequest.objects.select_related("requester", "handler", "created_instrument")
    serializer_class = InstrumentRequestModelSerializer
    filterset_fields = {
        "status": ["exact"],
        "requester": ["exact"],
        "notes": ["icontains"],
        "created": ["gte", "exact", "lte"],
    }

    ordering_fields = ("status", "requester", "notes", "created")
    ordering = ("-created",)
    search_fields = ("notes", "requester__computed_str", "instrument_data__isin")

    display_config_class = InstrumentRequestDisplayConfig
    title_config_class = InstrumentRequestTitleConfig
    endpoint_config_class = InstrumentRequestEndpointConfig

    @cached_property
    def has_validation_permission(self):
        return self.request.user.has_perm("wbfdm.administrate_instrument")

    # def get_queryset(self):
    #     return (
    #         super(InstrumentRequestModelViewSet, self)
    #         .get_queryset()
    #         .annotate(**{field: F(field) for field in INSTRUMENT_BASE_FIELDS})
    #     )
