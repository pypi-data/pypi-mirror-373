from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers

from wbfdm.models.instruments.instrument_lists import (
    InstrumentList,
    InstrumentListThroughModel,
)
from wbfdm.serializers.instruments import SecurityRepresentationSerializer


class InstrumentListRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbfdm:instrumentlist-detail")

    class Meta:
        model = InstrumentList
        fields = (
            "id",
            "name",
            "_detail",
        )


class InstrumentListModelSerializer(wb_serializers.ModelSerializer):
    @wb_serializers.register_only_instance_resource()
    def instruments(self, instance, request, user, **kwargs):
        if instance:
            base_url = reverse("wbfdm:instrumentlist-instrumentlistthrough-list", args=[instance.id], request=request)
            return {"instruments": base_url}
        return {}

    class Meta:
        model = InstrumentList
        read_only_fields = ("id", "identifier")
        fields = (
            "id",
            "name",
            "identifier",
            "instrument_list_type",
            "_additional_resources",
        )


class InstrumentListThroughModelSerializer(wb_serializers.ModelSerializer):
    _instrument = SecurityRepresentationSerializer(source="instrument")
    _instrument_list = InstrumentListRepresentationSerializer(source="instrument_list")

    class Meta:
        model = InstrumentListThroughModel
        read_only_fields = ("instrument_str",)
        fields = (
            "id",
            "instrument_str",
            "instrument",
            "_instrument",
            "instrument_list",
            "_instrument_list",
            "from_date",
            "to_date",
            "comment",
            "validated",
            "_additional_resources",
        )
