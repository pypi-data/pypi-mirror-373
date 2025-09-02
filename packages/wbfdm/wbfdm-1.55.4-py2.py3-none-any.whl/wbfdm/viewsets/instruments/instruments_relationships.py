from django.db.models import Prefetch, Q
from django.db.models.expressions import F
from django.db.models.query import QuerySet
from django.utils.functional import cached_property
from rest_framework import filters
from wbcore import filters as wb_filters
from wbcore import serializers as wb_serializers
from wbcore import viewsets
from wbcore.contrib.tags.serializers import TagSerializerMixin
from wbcore.permissions.permissions import InternalUserPermissionMixin

from wbfdm.filters.instruments import BaseClassifiedInstrumentFilterSet
from wbfdm.models import (
    Classification,
    ClassificationGroup,
    Instrument,
    InstrumentFavoriteGroup,
    RelatedInstrumentThroughModel,
)
from wbfdm.models.instruments import (
    InstrumentClassificationRelatedInstrument,
    InstrumentClassificationThroughModel,
)
from wbfdm.preferences import get_default_classification_group
from wbfdm.serializers import (
    ClassifiableInstrumentRepresentationSerializer,
    ClassificationRepresentationSerializer,
    InstrumentClassificationRelatedInstrumentModelSerializer,
    InstrumentClassificationRelatedInstrumentRepresentationSerializer,
    InstrumentFavoriteGroupModelSerializer,
    InstrumentFavoriteGroupRepresentationSerializer,
    ReadOnlyInstrumentFavoriteGroupModelSerializer,
    RelatedInstrumentThroughInstrumentModelSerializer,
)
from wbfdm.viewsets.configs.display import ClassifiedInstrumentDisplayConfig
from wbfdm.viewsets.configs.titles import ClassifiedInstrumentTitleConfig

from ..configs import (
    ClassificationInstrumentRelatedInstrumentDisplayConfig,
    ClassificationInstrumentRelatedInstrumentEndpointConfig,
    ClassifiedInstrumentEndpointConfig,
    InstrumentFavoriteGroupDisplayConfig,
    InstrumentFavoriteGroupEndpointConfig,
    InstrumentFavoriteGroupTitleConfig,
    RelatedInstrumentThroughInstrumentDisplayConfig,
    RelatedInstrumentThroughInstrumentEndpointConfig,
)
from ..mixins import InstrumentMixin


class InstrumentClassificationRelatedInstrumentRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = InstrumentClassificationRelatedInstrument.objects.all()
    serializer_class = InstrumentClassificationRelatedInstrumentRepresentationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if pk := self.kwargs.get("classified_instrument_id", None):
            queryset = queryset.filter(classified_instrument_id=pk)
        return queryset


class InstrumentClassificationRelatedInstrumentModelViewSet(viewsets.ModelViewSet):
    queryset = InstrumentClassificationRelatedInstrument.objects.all()
    serializer_class = InstrumentClassificationRelatedInstrumentModelSerializer
    display_config_class = ClassificationInstrumentRelatedInstrumentDisplayConfig
    endpoint_config_class = ClassificationInstrumentRelatedInstrumentEndpointConfig

    def get_queryset(self):
        queryset = super().get_queryset()
        if pk := self.kwargs.get("classified_instrument_id", None):
            queryset = queryset.filter(classified_instrument_id=pk)
        return queryset


class InstrumentFavoriteGroupRepresentationViewSet(InternalUserPermissionMixin, viewsets.RepresentationViewSet):
    IDENTIFIER = "wbfdm:favoritegroup"
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    ordering_fields = ordering = ("name",)
    search_fields = ("name", "instruments__name", "owner__computed_str")
    queryset = InstrumentFavoriteGroup.objects.all()
    serializer_class = InstrumentFavoriteGroupRepresentationSerializer


class InstrumentFavoriteGroupModelViewSet(InternalUserPermissionMixin, viewsets.ModelViewSet):
    queryset = InstrumentFavoriteGroup.objects.all()
    serializer_class = InstrumentFavoriteGroupModelSerializer

    ordering_fields = ("name", "owner__computed_str", "public")
    ordering = ("name",)
    search_fields = ("name", "instruments__name", "owner__computed_str")

    filterset_fields = {"instruments": ["exact"], "owner": ["exact"], "public": ["exact"]}

    display_config_class = InstrumentFavoriteGroupDisplayConfig
    title_config_class = InstrumentFavoriteGroupTitleConfig
    endpoint_config_class = InstrumentFavoriteGroupEndpointConfig

    @cached_property
    def is_owner(self) -> bool:
        try:
            group = InstrumentFavoriteGroup.objects.get(id=self.kwargs["pk"])
            return group.owner == self.request.user.profile
        except (KeyError, InstrumentFavoriteGroup.DoesNotExist):
            return False

    def get_serializer_class(self):
        if self.is_owner:
            return InstrumentFavoriteGroupModelSerializer
        return ReadOnlyInstrumentFavoriteGroupModelSerializer

    def get_queryset(self):
        qs = InstrumentFavoriteGroup.objects.all()
        if not self.request.user.is_superuser:
            qs = qs.filter(Q(owner=self.request.user.profile) | Q(public=True))
        return qs.select_related("owner").prefetch_related(
            Prefetch("instruments", queryset=Instrument.objects.filter(favorite_groups__isnull=False).distinct())
        )


class RelatedInstrumentThroughInstrumentModelViewSet(
    InstrumentMixin, InternalUserPermissionMixin, viewsets.ModelViewSet
):
    serializer_class = RelatedInstrumentThroughInstrumentModelSerializer
    queryset = RelatedInstrumentThroughModel.objects.select_related(
        "related_instrument",
        "instrument",
    )

    search_fields = ("related_instrument__computed_str",)
    ordering_fields = ["is_primary"]
    ordering = ["-is_primary"]

    filterset_fields = {"is_primary": ["exact"], "related_instrument": ["exact"], "related_type": ["exact"]}
    display_config_class = RelatedInstrumentThroughInstrumentDisplayConfig
    endpoint_config_class = RelatedInstrumentThroughInstrumentEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(instrument=self.instrument)


def get_classified_instrument_serializer_class(classification_grouo_id: int) -> type:
    """
    Unwrap defined serializer class and inject the metric fields into a new class
    """

    group = ClassificationGroup.objects.get(id=classification_grouo_id)

    attrs = dict()
    serializer_fields = [
        "id",
        "instrument",
        "_instrument",
        "classification",
        "_classification",
        "is_favorite",
        "tags",
        "_tags",
    ]
    for field_name in group.get_fields_names(sep="_"):
        base_field_name = f"classification_{field_name}"
        # representation_field_name = f"_classification_{field_name}"
        attrs[base_field_name] = wb_serializers.CharField(read_only=True)
        serializer_fields.append(base_field_name)

    class BaseClassifiedInstrumentModelSerializer(TagSerializerMixin, wb_serializers.ModelSerializer):
        _instrument = ClassifiableInstrumentRepresentationSerializer(source="instrument")
        _classification = ClassificationRepresentationSerializer(source="classification", label_key="{{name}}")

        class Meta:
            model = InstrumentClassificationThroughModel
            fields = read_only_fields = serializer_fields

    serializer_class = type("ClassifiedInstrumentModelSerializer", (BaseClassifiedInstrumentModelSerializer,), attrs)

    return serializer_class


class ClassifiedInstrumentModelViewSet(InternalUserPermissionMixin, viewsets.ModelViewSet):
    queryset = InstrumentClassificationThroughModel.objects.all()
    display_config_class = ClassifiedInstrumentDisplayConfig
    title_config_class = ClassifiedInstrumentTitleConfig
    endpoint_config_class = ClassifiedInstrumentEndpointConfig

    search_fields = ("instrument__computed_str",)

    def get_ordering_fields(self) -> list[str]:
        ordering_fields = ["instrument"]
        for field_name in self.classification_group.get_fields_names(sep="_"):
            ordering_fields.append(f"classification_{field_name}")
        return ordering_fields

    def get_resource_serializer_class(self):
        return {
            "serializer_class_path": "wbfdm.viewsets.instruments.instruments_relationships.get_classified_instrument_serializer_class",
            "serializer_class_method_args": [self.classification_group.id],
        }

    def get_serializer_class(self):
        return get_classified_instrument_serializer_class(self.classification_group.id)

    def get_filterset_class(self, request):
        group = self.classification_group

        attrs = {
            "classification": wb_filters.ModelChoiceFilter(
                label="Height 0",
                queryset=Classification.objects.filter(group=group, height=0),
                endpoint=Classification.get_representation_endpoint(),
                filter_params={"height": 0, "group": group.id},
                value_key=Classification.get_representation_value_key(),
                label_key="{{name}}",
            )
        }
        for index, field_name in enumerate(group.get_fields_names(sep="_"), start=1):
            attrs[f"classification_{field_name}"] = wb_filters.ModelChoiceFilter(
                label=f"Height {index}",
                queryset=Classification.objects.filter(group=group, height=index),
                endpoint=Classification.get_representation_endpoint(),
                filter_params={"height": index, "group": group.id},
                value_key=Classification.get_representation_value_key(),
                method="query_classification",
                label_key="{{name}}",
            )
        filter_class = type("ClassifiedInstrumentFilterSet", (BaseClassifiedInstrumentFilterSet,), attrs)

        def _get_filter_class_for_remote_filter(cls):
            """
            Define which filterset class sender to user for remote filter registration
            """
            return BaseClassifiedInstrumentFilterSet

        filter_class.get_filter_class_for_remote_filter = classmethod(_get_filter_class_for_remote_filter)
        return filter_class

    @cached_property
    def classification_group(self):
        try:
            return ClassificationGroup.objects.get(id=self.request.GET.get("classification_group"))
        except ClassificationGroup.DoesNotExist:
            return get_default_classification_group()

    def get_queryset(self) -> QuerySet[InstrumentClassificationThroughModel]:
        return (
            super()
            .get_queryset()
            .filter(classification__group=self.classification_group)
            .annotate(
                **{
                    f"classification_{field_name}".replace("__", "_"): F(f"classification__{field_name}__name")
                    for field_name in self.classification_group.get_fields_names()
                }
            )
            .select_related(
                *[f"classification__{field_name}" for field_name in self.classification_group.get_fields_names()]
            )
            .prefetch_related(
                "tags",
                Prefetch("instrument", queryset=Instrument.objects.filter(classifications_through__isnull=False)),
            )
        )
