from wbcore import serializers as wb_serializers
from wbcore.contrib.geography.serializers import GeographyRepresentationSerializer

from wbfdm.models import Exchange


class ExchangeRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbfdm:exchange-detail")

    class Meta:
        model = Exchange
        fields = ("id", "name", "mic_code", "_detail")


class ExchangeModelSerializer(wb_serializers.ModelSerializer):
    _country = GeographyRepresentationSerializer(source="country")
    _city = GeographyRepresentationSerializer(source="city")

    class Meta:
        model = Exchange
        fields = (
            "id",
            "name",
            "mic_code",
            "operating_mic_code",
            "bbg_exchange_codes",
            "bbg_composite_primary",
            "bbg_composite",
            "refinitiv_identifier_code",
            "refinitiv_mnemonic",
            "country",
            "_country",
            "city",
            "website",
            "opening_time",
            "closing_time",
            "_city",
            "city",
            "comments",
            "apply_round_lot_size",
        )
