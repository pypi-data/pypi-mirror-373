from wbcore import filters as wb_filters

from wbfdm.filters.utils import _get_default_classification_group_id
from wbfdm.models import (
    Classification,
    ClassificationGroup,
    Instrument,
    InstrumentClassificationThroughModel,
)


class ClassificationFilter(wb_filters.FilterSet):
    instruments = wb_filters.ModelChoiceFilter(
        label="Instrument",
        queryset=Instrument.objects.all(),
        endpoint=Instrument.get_representation_endpoint(),
        filter_params={"is_classifiable": True},
        value_key=Instrument.get_representation_value_key(),
        label_key=Instrument.get_representation_label_key(),
    )

    instruments_neq = wb_filters.ModelChoiceFilter(
        label="Instrument not classified in",
        queryset=Instrument.objects.all(),
        endpoint=Instrument.get_representation_endpoint(),
        value_key=Instrument.get_representation_value_key(),
        label_key=Instrument.get_representation_label_key(),
        filter_params={"is_classifiable": True},
        field_name="instruments",
        lookup_expr="exact",
        exclude=True,
    )

    instrument_type_key = wb_filters.CharFilter(
        label="Instrument Type Key", hidden=True, method="filter_instrument_type_key"
    )

    def filter_instrument_type_key(self, queryset, name, value):
        if value:
            return queryset.filter(instruments__instrument_type__key=value).distinct()
        return queryset

    class Meta:
        model = Classification
        fields = {
            "id": ["in"],
            "parent": ["exact"],
            "height": ["gte", "exact", "lte"],
            "level": ["gte", "exact", "lte"],
            "group": ["exact"],
            "level_representation": ["icontains"],
            "name": ["icontains"],
            "code_aggregated": ["icontains", "exact"],
        }
        hidden_fields = ["id__in"]


class ClassificationTreeChartFilter(wb_filters.FilterSet):
    top_classification = wb_filters.ModelChoiceFilter(
        label="Top Classification",
        queryset=Classification.objects.all(),
        endpoint=Classification.get_representation_endpoint(),
        value_key=Classification.get_representation_value_key(),
        label_key=Classification.get_representation_label_key(),
        method="filter_top_classification",
    )

    aggregation_type = wb_filters.ChoiceFilter(
        choices=[("classification_count", "Classification Count"), ("instrument_count", "Instrument Count")],
        initial="classification_count",
        label="Aggregation Type",
        method="fake_filter",
    )

    def filter_top_classification(self, queryset, name, value):
        if value:
            return queryset.filter(id__in=value.get_descendants().values("id"))
        return queryset

    class Meta:
        model = Classification
        fields = {}


class InstrumentClassificationThroughModelViewFilterSet(wb_filters.FilterSet):
    classification__group = wb_filters.ModelChoiceFilter(
        label="Group",
        queryset=ClassificationGroup.objects.all(),
        endpoint=ClassificationGroup.get_representation_endpoint(),
        value_key=ClassificationGroup.get_representation_value_key(),
        label_key=ClassificationGroup.get_representation_label_key(),
        initial=_get_default_classification_group_id,
    )

    class Meta:
        model = InstrumentClassificationThroughModel
        fields = {
            "instrument": ["exact"],
            "classification": ["exact"],
            "is_favorite": ["exact"],
            "pure_player": ["exact"],
            "top_player": ["exact"],
        }
