from rest_framework import serializers as rf_serializers
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.serializers import DefaultAttributeFromRemoteField, DefaultFromView

from wbfdm.models.instruments import Classification, ClassificationGroup
from wbfdm.preferences import get_default_classification_group


class ClassificationRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbfdm:classification-detail")

    class Meta:
        model = Classification
        fields = (
            "id",
            "name",
            "computed_str",
            "level",
            "height",
            "code_aggregated",
            "_detail",
        )


class ClassificationZeroHeightRepresentationSerializer(ClassificationRepresentationSerializer):
    def get_filter_params(self, request):
        filter_params = {"height": 0}
        if (view := request.parser_context.get("view", None)) and (
            instrument_id := view.kwargs.get("instrument_id", None)
        ):
            filter_params["instruments_neq"] = instrument_id
        return filter_params


class ClassificationIsFavoriteZeroHeightRepresentationSerializer(ClassificationRepresentationSerializer):
    def get_filter_params(self, request):
        filter_params = {
            "height": 0,
            "instruments_through__is_favorite": True,
        }
        if group := get_default_classification_group():
            filter_params["group"] = group.id
        return filter_params


class ClassificationGroupRepresentationSerializer(wb_serializers.RepresentationSerializer):
    max_depth = wb_serializers.IntegerField(read_only=True)
    _detail = wb_serializers.HyperlinkField(reverse_name="wbfdm:classificationgroup-detail")

    class Meta:
        model = ClassificationGroup
        fields = ("id", "name", "is_primary", "max_depth", "_detail")


class ClassificationModelSerializer(wb_serializers.ModelSerializer):
    parent = wb_serializers.PrimaryKeyRelatedField(
        queryset=Classification.objects.all(), default=DefaultAttributeFromRemoteField("parent_id", Classification)
    )
    _parent = ClassificationRepresentationSerializer(source="parent")
    group = wb_serializers.PrimaryKeyRelatedField(
        queryset=ClassificationGroup.objects.all(),
        default=DefaultAttributeFromRemoteField("parent_id", Classification, source="group"),
    )
    _group = ClassificationGroupRepresentationSerializer(source="group")
    code_aggregated = wb_serializers.CharField(required=False, default=DefaultFromView("next_valid_code_aggregated"))
    level_representation = wb_serializers.CharField(required=False, default="")
    description = wb_serializers.TextAreaField(label="Description", allow_null=True, allow_blank=True, required=False)

    @wb_serializers.register_only_instance_resource()
    def additional_resources(self, instance, request, user, **kwargs):
        resources = {
            "childs": reverse("wbfdm:classificationparent-classification-list", args=[instance.id], request=request),
        }
        if instance.children.exists():
            resources["iciclechart"] = (
                f'{reverse("wbfdm:classificationgroup-iciclechart-list", args=[instance.group.id], request=request)}?top_classification={instance.id}'
            )
            resources["treechart"] = (
                f'{reverse("wbfdm:classificationgroup-treechart-list", args=[instance.group.id], request=request)}?top_classification={instance.id}'
            )

        resources["instruments"] = reverse("wbfdm:classification-instrument-list", args=[instance.id], request=request)

        return resources

    def validate(self, data):
        errors = {}
        if parent := data.get("parent", None):
            data["level"] = parent.level + 1
            data["group"] = parent.group
        if (
            (investable := data.get("investable", None))
            and self.instance
            and investable is True
            and self.instance.get_ancestors().filter(investable=False).exists()
        ):
            errors["investable"] = "This classification cannot be investable as long as its parent is non investable."
        if len(errors.keys()) > 0:
            raise rf_serializers.ValidationError(errors)
        return data

    class Meta:
        model = Classification
        fields = (
            "id",
            "parent",
            "_parent",
            "height",
            "group",
            "_group",
            "level",
            "level_representation",
            "name",
            "code_aggregated",
            "investable",
            "description",
            "_additional_resources",
        )


class ClassificationGroupModelSerializer(wb_serializers.ModelSerializer):
    @wb_serializers.register_resource()
    def additional_resources(self, instance, request, user):
        if instance.classifications.exists():
            return {
                "classifications": reverse(
                    "wbfdm:classificationgroup-classification-list", args=[instance.id], request=request
                ),
                "treechart": reverse("wbfdm:classificationgroup-treechart-list", args=[instance.id], request=request),
                "iciclechart": reverse(
                    "wbfdm:classificationgroup-iciclechart-list", args=[instance.id], request=request
                ),
            }

        return {}

    class Meta:
        model = ClassificationGroup
        fields = ("id", "name", "is_primary", "max_depth", "code_level_digits", "_additional_resources")
