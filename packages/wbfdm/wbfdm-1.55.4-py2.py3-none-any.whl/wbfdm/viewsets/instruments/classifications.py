import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.db.models import Count, Value
from django.db.models.expressions import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from reversion.views import RevisionMixin
from wbcore import viewsets
from wbcore.cache.decorators import cache_table
from wbcore.filters import DjangoFilterBackend
from wbcore.permissions.permissions import InternalUserPermissionMixin
from wbcore.utils.date import get_next_day_timedelta

from wbfdm.filters import (
    ClassificationFilter,
    ClassificationTreeChartFilter,
    InstrumentClassificationThroughModelViewFilterSet,
)
from wbfdm.models import (
    Classification,
    ClassificationGroup,
    InstrumentClassificationThroughModel,
)
from wbfdm.serializers import (
    ClassificationGroupModelSerializer,
    ClassificationGroupRepresentationSerializer,
    ClassificationModelSerializer,
    ClassificationRepresentationSerializer,
    InstrumentClassificationThroughModelSerializer,
)
from wbfdm.viewsets.configs import (
    ChildClassificationParentClassificationTitleConfig,
    ClassificationButtonConfig,
    ClassificationClassificationGroupEndpointConfig,
    ClassificationClassificationGroupTitleConfig,
    ClassificationDisplayConfig,
    ClassificationEndpointConfig,
    ClassificationGroupButtonConfig,
    ClassificationGroupDisplayConfig,
    ClassificationGroupTitleConfig,
    ClassificationIcicleChartEndpointConfig,
    ClassificationIcicleChartTitleConfig,
    ClassificationInstrumentThroughInstrumentModelEndpointConfig,
    ClassificationParentClassificationEndpointConfig,
    ClassificationTitleConfig,
    ClassificationTreeChartEndpointConfig,
    ClassificationTreeChartTitleConfig,
    InstrumentClassificationThroughDisplayConfig,
    InstrumentClassificationThroughEndpointConfig,
    InstrumentClassificationThroughInstrumentModelEndpointConfig,
    InstrumentClassificationThroughTitleConfig,
)

from ..mixins import InstrumentMixin


class ClassificationRepresentationViewSet(InternalUserPermissionMixin, viewsets.RepresentationViewSet):
    IDENTIFIER = "wbfdm:classification"
    queryset = Classification.objects.all()
    serializer_class = ClassificationRepresentationSerializer

    filterset_class = ClassificationFilter
    ordering_fields = ["code_aggregated"]
    ordering = ["code_aggregated"]
    search_fields = ["code_aggregated", "name"]


class ClassificationGroupRepresentationViewSet(InternalUserPermissionMixin, viewsets.RepresentationViewSet):
    IDENTIFIER = "wbfdm:classificationgrouprepresentation"
    queryset = ClassificationGroup.objects.all()
    serializer_class = ClassificationGroupRepresentationSerializer

    filterset_fields = {"is_primary": ["exact"], "max_depth": ["gte", "exact", "lte"]}
    ordering_fields = ["name"]
    ordering = ["name"]
    search_fields = ["name"]


class ClassificationModelViewSet(InternalUserPermissionMixin, RevisionMixin, viewsets.ModelViewSet):
    IDENTIFIER = "wbfdm:classification"

    queryset = Classification.objects.select_related("parent", "group")
    serializer_class = ClassificationModelSerializer
    filterset_class = ClassificationFilter

    ordering_fields = (
        "name",
        "code_aggregated",
        "level_representation",
    )
    ordering = ("level_representation", "name")
    search_fields = ("name", "group__name", "parent__name", "code_aggregated")

    endpoint_config_class = ClassificationEndpointConfig
    display_config_class = ClassificationDisplayConfig
    title_config_class = ClassificationTitleConfig
    button_config_class = ClassificationButtonConfig

    @cached_property
    def next_valid_code_aggregated(self) -> str:
        group = None
        parent = None
        if group_id := self.kwargs.get("group_id", None):
            group = ClassificationGroup.objects.get(id=group_id)
        elif parent_id := self.kwargs.get("parent_id", None):
            parent = Classification.objects.get(id=parent_id)
            group = parent.group
        if group:
            return Classification.get_next_valid_code(group, parent=parent)
        return ""


class ClassificationClassificationGroupModelViewSet(ClassificationModelViewSet):
    endpoint_config_class = ClassificationClassificationGroupEndpointConfig
    title_config_class = ClassificationClassificationGroupTitleConfig

    def get_queryset(self):
        return super().get_queryset().filter(group=self.kwargs["group_id"], level=0)


class ChildClassificationParentClassificationModelViewSet(ClassificationModelViewSet):
    endpoint_config_class = ClassificationParentClassificationEndpointConfig
    title_config_class = ChildClassificationParentClassificationTitleConfig

    def get_queryset(self):
        parent = Classification.objects.get(id=self.kwargs["parent_id"])
        return super().get_queryset().filter(parent=self.kwargs["parent_id"], level=parent.level + 1)


class ClassificationGroupModelViewSet(InternalUserPermissionMixin, RevisionMixin, viewsets.ModelViewSet):
    IDENTIFIER = "wbfdm:classificationgroup"

    queryset = ClassificationGroup.objects.all()
    serializer_class = ClassificationGroupModelSerializer
    filterset_fields = {"is_primary": ["exact"], "max_depth": ["gte", "exact", "lte"]}
    ordering_fields = ("name",)
    ordering = ("name",)
    search_fields = ("name",)

    display_config_class = ClassificationGroupDisplayConfig
    title_config_class = ClassificationGroupTitleConfig
    button_config_class = ClassificationGroupButtonConfig


class AbstractClassificationChartView(viewsets.ChartViewSet):
    filter_backends = (DjangoFilterBackend,)
    queryset = Classification.objects.all()
    filterset_class = ClassificationTreeChartFilter

    @cached_property
    def aggregation_type(self) -> str:
        return self.request.GET.get("aggregation_type", "classification_count")

    @cached_property
    def classification_group(self) -> ClassificationGroup:
        return ClassificationGroup.objects.get(id=self.kwargs["group_id"])

    @cached_property
    def top_level(self) -> int:
        top_level = 0
        if top_classification_id := self.request.GET.get("top_classification", None):
            top_level = Classification.objects.get(id=top_classification_id).level
        return top_level

    def get_df(self, queryset) -> tuple[pd.DataFrame, list[str]]:
        _range = self.classification_group.max_depth + 1 - self.top_level
        df = pd.DataFrame(columns=[self.aggregation_type])
        level_representation = []
        if queryset.exists():
            df = pd.DataFrame(
                queryset.values(*[f"{'parent__' * height}name" for height in range(_range)], self.aggregation_type)
            ).fillna(0)

            level_representation = self.classification_group.get_levels_representation()[:_range]
            df.columns = [*level_representation, self.aggregation_type]
        return df, level_representation

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(height=0, group=self.classification_group)
            .annotate(
                instrument_count=Coalesce(
                    Subquery(
                        InstrumentClassificationThroughModel.objects.filter(classification=OuterRef("pk"))
                        .values("classification")
                        .annotate(c=Count("classification"))
                        .values("c")[:1]
                    ),
                    0,
                ),
                classification_count=Value(1),
            )
        )

    def get_plotly(self, queryset):
        return go.Figure()


@cache_table(
    timeout=get_next_day_timedelta(),
    key_prefix=lambda view: f"{view.classification_group.id}_{view.aggregation_type}_{view.top_level}",
    periodic_caching=True,
    periodic_caching_view_kwargs=lambda: [
        {"group_id": group_id} for group_id in ClassificationGroup.objects.values_list("id", flat=True)
    ],
    periodic_caching_get_parameters=[
        {"aggregation_type": "classification_count"},
        {"aggregation_type": "instrument_count"},
    ],
)
class ClassificationTreeChartView(AbstractClassificationChartView):
    IDENTIFIER = "wbfdm:classificationgroup-tree"
    title_config_class = ClassificationTreeChartTitleConfig
    endpoint_config_class = ClassificationTreeChartEndpointConfig

    def get_plotly(self, queryset):
        df, level_representation = self.get_df(queryset)
        fig = px.treemap(df, path=[*level_representation[::-1]], values=self.aggregation_type, branchvalues="total")
        fig.update_traces(root_color="lightgrey", hovertemplate=f"{self.aggregation_type}: %{{value}}")
        fig.update_layout(margin=dict(t=25, l=25, r=25, b=25))
        return fig


@cache_table(
    timeout=get_next_day_timedelta(),
    key_prefix=lambda view: f"{view.classification_group.id}_{view.aggregation_type}_{view.top_level}",
    periodic_caching=True,
    periodic_caching_view_kwargs=lambda: [
        {"group_id": group_id} for group_id in ClassificationGroup.objects.values_list("id", flat=True)
    ],
    periodic_caching_get_parameters=[
        {"aggregation_type": "classification_count"},
        {"aggregation_type": "instrument_count"},
    ],
)
class ClassificationIcicleChartView(AbstractClassificationChartView):
    IDENTIFIER = "wbfdm:classificationgroup-iciclechart"
    title_config_class = ClassificationIcicleChartTitleConfig
    endpoint_config_class = ClassificationIcicleChartEndpointConfig

    def get_plotly(self, queryset):
        df, level_representation = self.get_df(queryset)
        fig = px.icicle(df, path=[*level_representation[::-1]], values=self.aggregation_type)
        fig.update_traces(
            root_color="lightgrey", tiling=dict(orientation="v"), hovertemplate=f"{self.aggregation_type}: %{{value}}"
        )
        fig.update_layout(margin=dict(t=25, l=25, r=25, b=25))
        return fig


class InstrumentClassificationThroughModelViewSet(InternalUserPermissionMixin, viewsets.ModelViewSet):
    serializer_class = InstrumentClassificationThroughModelSerializer
    queryset = InstrumentClassificationThroughModel.objects.select_related(
        "instrument",
        "classification",
    ).prefetch_related("related_instruments", "tags")
    search_fields = ("classification__name", "classification__code_aggregated")
    ordering_fields = ordering = ["classification__name"]

    filterset_class = InstrumentClassificationThroughModelViewFilterSet
    display_config_class = InstrumentClassificationThroughDisplayConfig
    endpoint_config_class = InstrumentClassificationThroughEndpointConfig
    title_config_class = InstrumentClassificationThroughTitleConfig


class InstrumentClassificationThroughInstrumentModelViewSet(
    InstrumentMixin, InstrumentClassificationThroughModelViewSet
):
    endpoint_config_class = InstrumentClassificationThroughInstrumentModelEndpointConfig
    search_fields = ["classification__computed_str"]
    ordering_fields = ordering = ["classification__computed_str"]

    def get_queryset(self):
        return super().get_queryset().filter(instrument__in=self.instrument.get_family())


class ClassificationInstrumentThroughInstrumentModelViewSet(InstrumentClassificationThroughModelViewSet):
    search_fields = ["instrument__computed_str"]
    ordering_fields = ordering = ["instrument__computed_str"]

    endpoint_config_class = ClassificationInstrumentThroughInstrumentModelEndpointConfig

    def get_queryset(self):
        classification = get_object_or_404(Classification, id=self.kwargs["classification_id"])
        return (
            super()
            .get_queryset()
            .filter(classification__in=classification.get_descendants(include_self=True).values("id"))
        )
