from rest_framework import serializers
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.directory.models import Person
from wbcore.contrib.directory.serializers import PersonRepresentationSerializer
from wbcore.contrib.tags.serializers import TagSerializerMixin

from wbfdm.models import (
    Classification,
    Instrument,
    InstrumentClassificationRelatedInstrument,
    InstrumentClassificationThroughModel,
    InstrumentFavoriteGroup,
    RelatedInstrumentThroughModel,
)

from .classifications import ClassificationZeroHeightRepresentationSerializer
from .instruments import (
    ClassifiableInstrumentRepresentationSerializer,
    InvestableInstrumentRepresentationSerializer,
    PrimaryInvestableInstrumentRepresentationSerializer,
)


class InstrumentFavoriteGroupRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbfdm:favoritegroup-detail")

    class Meta:
        model = InstrumentFavoriteGroup
        fields = ("id", "name", "owner", "public", "_detail")


class InstrumentFavoriteGroupModelSerializer(wb_serializers.ModelSerializer):
    _instruments = PrimaryInvestableInstrumentRepresentationSerializer(source="instruments", many=True)
    owner = wb_serializers.PrimaryKeyRelatedField(
        queryset=lambda: Person.objects.filter_only_internal(),
        default=wb_serializers.CurrentUserDefault("profile"),
    )
    _owner = PersonRepresentationSerializer(source="owner")

    def validate(self, data):
        if not data.get("owner", None):
            data["owner"] = self.context["request"].user.profile if self.context.get("request") else None
        return data

    class Meta:
        model = InstrumentFavoriteGroup
        fields = (
            "id",
            "name",
            "owner",
            "_owner",
            "public",
            "primary",
            "instruments",
            "_instruments",
            "_additional_resources",
        )


class ReadOnlyInstrumentFavoriteGroupModelSerializer(InstrumentFavoriteGroupModelSerializer):
    class Meta(InstrumentFavoriteGroupModelSerializer.Meta):
        read_only_fields = InstrumentFavoriteGroupModelSerializer.Meta.fields


class RelatedInstrumentThroughInstrumentModelSerializer(wb_serializers.ModelSerializer):
    _related_instrument = InvestableInstrumentRepresentationSerializer(source="related_instrument")
    _instrument = InvestableInstrumentRepresentationSerializer(source="instrument")

    class Meta:
        model = RelatedInstrumentThroughModel
        fields = (
            "id",
            "_related_instrument",
            "related_instrument",
            "_instrument",
            "instrument",
            "related_type",
            "is_primary",
        )


class InstrumentClassificationThroughModelSerializer(TagSerializerMixin, wb_serializers.ModelSerializer):
    instrument = wb_serializers.PrimaryKeyRelatedField(
        queryset=Instrument.objects.all(), default=wb_serializers.DefaultFromKwargs("instrument_id")
    )
    _instrument = ClassifiableInstrumentRepresentationSerializer(source="instrument")
    classification = wb_serializers.PrimaryKeyRelatedField(
        queryset=Classification.objects.all(), default=wb_serializers.DefaultFromKwargs("classification_id")
    )
    _classification = ClassificationZeroHeightRepresentationSerializer(source="classification")
    reason = wb_serializers.TextAreaField(label="Reason", allow_null=True, allow_blank=True, required=False)
    _related_instruments = ClassifiableInstrumentRepresentationSerializer(source="related_instruments", many=True)

    @wb_serializers.register_resource()
    def related_instrument_list(self, instance, request, user):
        return {"related_instruments": reverse("wbfdm:related_instrument-list", args=[instance.id], request=request)}

    def validate(self, data):
        instrument = data.get("instrument", self.instance.instrument if self.instance else None)
        classification = data.get("classification", self.instance.classification if self.instance else None)
        if not instrument:
            raise serializers.ValidationError({"instrument": "Instrument cannot be null"})
        if not classification:
            raise serializers.ValidationError({"classification": "Classification cannot be null"})

        if (
            not self.instance
            and InstrumentClassificationThroughModel.objects.filter(
                classification=classification, instrument=instrument
            ).exists()
        ):
            if hasattr(data, "instrument"):
                raise serializers.ValidationError(
                    {
                        "instrument": f"A relationship already exists between {instrument} and {classification}",
                    }
                )
            else:
                raise serializers.ValidationError(
                    {
                        "classification": f"A relationship already exists between {instrument} and {classification}",
                    }
                )

        return data

    class Meta:
        model = InstrumentClassificationThroughModel
        fields = (
            "id",
            "instrument",
            "classification",
            "_instrument",
            "_classification",
            "related_instruments",
            "_related_instruments",
            "is_favorite",
            "reason",
            "pure_player",
            "top_player",
            "percent_of_revenue",
            "tags",
            "_tags",
            "_additional_resources",
        )
        percent_fields = ["percent_of_revenue"]


class InstrumentClassificationRelatedInstrumentRepresentationSerializer(wb_serializers.ModelSerializer):
    class Meta:
        model = InstrumentClassificationRelatedInstrument
        fields = ("id", "related_instrument")


class InstrumentClassificationRelatedInstrumentModelSerializer(wb_serializers.ModelSerializer):
    _related_instrument = ClassifiableInstrumentRepresentationSerializer(source="related_instrument")

    class Meta:
        model = InstrumentClassificationRelatedInstrument
        fields = (
            "id",
            "classified_instrument",
            # "_classified_instrument",
            "related_instrument",
            "_related_instrument",
            "related_instrument_type",
        )
