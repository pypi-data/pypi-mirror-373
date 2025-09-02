from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.content_type.serializers import ContentTypeRepresentationSerializer

from wbfdm.contrib.metric.models import InstrumentMetric
from wbfdm.serializers.instruments import InstrumentRepresentationSerializer


class InstrumentMetricRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = InstrumentMetric
        fields = ("id", "key", "date", "basket_repr")


class InstrumentMetricModelSerializer(wb_serializers.ModelSerializer):
    _basket_content_type = ContentTypeRepresentationSerializer(source="basket_content_type")
    _instrument = InstrumentRepresentationSerializer(source="instrument")
    _parent_metric = InstrumentMetricRepresentationSerializer(source="parent_metric")
    _group_key = wb_serializers.CharField(read_only=True)

    @wb_serializers.register_resource()
    def additional_resources(self, instance, request, user):
        return {
            "children_metrics": f'{reverse("metric:instrumentmetric-list", args=[], request=request)}?parent_metric={instance.id}'
        }

    class Meta:
        model = InstrumentMetric
        fields = (
            "id",
            "basket_content_type",
            "_basket_content_type",
            "basket_repr",
            "basket_id",
            "instrument",
            "_instrument",
            "date",
            "key",
            "metrics",
            "parent_metric",
            "_parent_metric",
            "_group_key",
            "_additional_resources",
        )
        read_only_fields = fields
