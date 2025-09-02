from wbcore import viewsets
from wbcore.permissions.permissions import InternalUserPermissionMixin

from wbfdm.filters import ExchangeFilterSet
from wbfdm.models import Exchange
from wbfdm.serializers import ExchangeModelSerializer, ExchangeRepresentationSerializer

from .configs import (
    ExchangeButtonConfig,
    ExchangeDisplayConfig,
    ExchangeEndpointConfig,
    ExchangeTitleConfig,
)


class ExchangeRepresentationViewSet(InternalUserPermissionMixin, viewsets.RepresentationViewSet):
    queryset = Exchange.objects.all()
    serializer_class = ExchangeRepresentationSerializer

    search_fields = (
        "name",
        "mic_code",
        "operating_mic_code",
        "bbg_exchange_codes",
        "bbg_composite_primary",
        "bbg_composite",
        "refinitiv_mnemonic",
        "refinitiv_identifier_code",
        "city__name",
        "website",
        "comments",
    )
    ordering_fields = search_fields
    ordering = ["name"]


class ExchangeModelViewSet(InternalUserPermissionMixin, viewsets.ModelViewSet):
    filterset_class = ExchangeFilterSet
    serializer_class = ExchangeModelSerializer
    queryset = Exchange.objects.select_related(
        "country",
        "city",
    )

    search_fields = (
        "name",
        "mic_code",
        "operating_mic_code",
        "bbg_exchange_codes",
        "bbg_composite_primary",
        "refinitiv_mnemonic",
        "bbg_composite",
        "refinitiv_identifier_code",
        "city__name",
        "website",
        "comments",
    )
    ordering_fields = search_fields
    ordering = ["name"]

    display_config_class = ExchangeDisplayConfig
    button_config_class = ExchangeButtonConfig
    title_config_class = ExchangeTitleConfig
    endpoint_config_class = ExchangeEndpointConfig
