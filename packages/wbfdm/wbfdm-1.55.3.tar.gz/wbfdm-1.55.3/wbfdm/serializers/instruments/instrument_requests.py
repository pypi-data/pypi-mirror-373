from wbcore import serializers as wb_serializers
from wbcore.contrib.directory.serializers import PersonRepresentationSerializer

from wbfdm.models.instruments import InstrumentRequest

from .instruments import InstrumentModelSerializer, InstrumentRepresentationSerializer


class InstrumentRequestRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbfdm:instrumentrequest-detail")

    class Meta:
        model = InstrumentRequest
        fields = ("id", "status", "_detail")


class InstrumentRequestModelSerializer(wb_serializers.ModelSerializer):
    _requester = PersonRepresentationSerializer(source="requester")
    _handler = PersonRepresentationSerializer(source="handler")
    _created_instrument = InstrumentRepresentationSerializer(source="created_instrument")
    notes = wb_serializers.CharField(required=False)

    def validate(self, data):
        if (not self.instance or not self.instance.requester) and (request := self.context.get("request")):
            data["requester"] = request.user.profile
        return super().validate(data)

    class Meta:
        model = InstrumentRequest
        fields = (
            "id",
            "status",
            "requester",
            "_requester",
            "_handler",
            "handler",
            "_created_instrument",
            "created_instrument",
            "notes",
            "created",
            "_additional_resources",
        )
        flatten_fields = {
            "instrument_data": wb_serializers.JSONTableField(
                serializer_class=InstrumentModelSerializer,
                required=False,
                flatten_field_names=[
                    "name",
                    "name_repr",
                    "instrument_type",
                    "refinitiv_identifier_code",
                    "refinitiv_mnemonic_code",
                    "isin",
                    "ticker",
                    "is_cash",
                    "currency",
                    "country",
                    "tags",
                    "classifications",
                ],
            )
        }
