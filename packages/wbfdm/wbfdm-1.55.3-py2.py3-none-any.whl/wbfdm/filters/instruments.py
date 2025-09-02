from datetime import datetime

from django.db.models import Q
from psycopg.types.range import DateRange
from wbcore import filters as wb_filters
from wbcore.contrib.tags.filters import TagFilterMixin

from wbfdm.filters.utils import _get_default_classification_group_id, get_earliest_date, get_latest_date
from wbfdm.models import InstrumentType
from wbfdm.models.instruments import (
    ClassificationGroup,
    Instrument,
    InstrumentClassificationThroughModel,
    InstrumentFavoriteGroup,
)
from wbfdm.models.instruments.classifications import Classification


def get_default_favorite_group(field, request, view):
    if favorite := InstrumentFavoriteGroup.objects.filter(owner=request.user.profile, primary=True).first():
        return favorite.id
    return None


class InstrumentFavoriteGroupFilterSet(wb_filters.FilterSet):
    favorite_group = wb_filters.ModelChoiceFilter(
        label="Favorite Group",
        queryset=InstrumentFavoriteGroup.objects.all(),
        endpoint=InstrumentFavoriteGroup.get_representation_endpoint(),
        value_key=InstrumentFavoriteGroup.get_representation_value_key(),
        label_key=InstrumentFavoriteGroup.get_representation_label_key(),
        initial=get_default_favorite_group,
        method="filter_favorite_group",
    )

    def filter_favorite_group(self, queryset, name, value):
        if value:
            return queryset.filter(id__in=value.instruments.values_list("id"))
        return queryset

    class Meta:
        model = Instrument
        fields = {}


class InstrumentFilterSet(TagFilterMixin, InstrumentFavoriteGroupFilterSet):
    parent = wb_filters.ModelChoiceFilter(
        label="Parent",
        queryset=Instrument.objects.all(),
        endpoint=Instrument.get_representation_endpoint(),
        value_key=Instrument.get_representation_value_key(),
        label_key=Instrument.get_representation_label_key(),
        hidden=True,
    )
    parent__isnull = wb_filters.BooleanFilter(field_name="parent", lookup_expr="isnull", hidden=True)

    classifications = wb_filters.ModelChoiceFilter(
        label="Classification",
        queryset=Classification.objects.all(),
        endpoint=Classification.get_representation_endpoint(),
        value_key=Classification.get_representation_value_key(),
        label_key=Classification.get_representation_label_key(),
        method="filter_classification",
    )

    classifications_neq = wb_filters.ModelChoiceFilter(
        label="Instrument not classified in..",
        queryset=Classification.objects.all(),
        endpoint=Classification.get_representation_endpoint(),
        value_key=Classification.get_representation_value_key(),
        label_key=Classification.get_representation_label_key(),
        method="filter_classification",
        hidden=True,
    )

    def filter_classification(self, queryset, name, value):
        if value:
            if name == "classifications":
                return queryset.filter(classifications__in=value.get_descendants(include_self=True))
            else:
                return queryset.exclude(classifications__in=value.get_descendants(include_self=True))
        return queryset

    is_active = wb_filters.BooleanFilter(label="Only Active", method="filter_is_active")

    def filter_is_active(self, queryset, name, value):
        today = datetime.today()
        if value is True:
            return queryset.filter(
                (Q(delisted_date__isnull=True) | Q(delisted_date__gte=today))
                & Q(inception_date__isnull=False)
                & Q(inception_date__lte=today)
            )
        return queryset

    is_investable = wb_filters.BooleanFilter(label="Is Investable", method="filter_is_investable", hidden=True)

    def filter_is_investable(self, queryset, name, value):
        if value:
            return queryset.filter(children__isnull=True)
        return queryset

    instrument_type__key = wb_filters.CharFilter(label="Instrument Type Key", hidden=True)
    instrument_type__is_classifiable = wb_filters.BooleanFilter(label="Instrument Type Classifiable", hidden=True)

    instrument_type = wb_filters.ModelMultipleChoiceFilter(
        label="Asset Classes",
        queryset=InstrumentType.objects.all(),
        endpoint=InstrumentType.get_representation_endpoint(),
        value_key=InstrumentType.get_representation_value_key(),
        label_key=InstrumentType.get_representation_label_key(),
    )

    is_classifiable = wb_filters.BooleanFilter(label="Is Classifiable", method="filter_is_classifiable", hidden=True)

    def filter_is_classifiable(self, queryset, name, value):
        if value:
            return queryset.filter(instrument_type__is_classifiable=True, level=0)
        return queryset

    # is_tree_in_investable_universe = wb_filters.BooleanFilter(label="Investable Universe", method="filter_is_tree_in_investable_universe", required=True)
    # def filter_is_tree_in_investable_universe(self, queryset, name, value):
    #     if value is not None:
    #         return queryset.annotate(
    #             is_tree_in_investable_universe=Exists(
    #                 Instrument.objects.filter(
    #                     tree_id=OuterRef("tree_id"),
    #                     lft__gte=OuterRef("lft"),
    #                     rght__lte=OuterRef("rght"),
    #                     is_investable_universe=True
    #                 )
    #             )
    #         ).filter(Q(is_tree_in_investable_universe=value))
    #     return queryset
    def __init__(self, data=None, *args, **kwargs):
        if data:
            data = data.dict()
            if "parent" in data:
                data.pop("classifications", None)  # remove classifications in case we are navigating the tree
                data.pop("level", None)
        super().__init__(data=data, *args, **kwargs)

    class Meta:
        model = Instrument
        fields = {
            "is_investable_universe": ["exact"],
            "instrument_type": ["exact"],
            "isin": ["exact"],
            "ticker": ["exact"],
            "refinitiv_mnemonic_code": ["exact"],
            "refinitiv_identifier_code": ["exact"],
            "currency": ["exact"],
            # "related_instruments": ["exact"], # I don't think this filter is necessary
            "country": ["exact"],
            "exchange": ["exact"],
            "id": ["in"],
            "is_managed": ["exact"],
            "is_security": ["exact"],
            "is_primary": ["exact"],
            "parent": ["exact", "isnull"],
            "level": ["exact"],
        }
        hidden_fields = ["id__in", "is_managed", "is_security", "level"]


class BaseClassifiedInstrumentFilterSet(TagFilterMixin, wb_filters.FilterSet):
    classification_group = wb_filters.ModelChoiceFilter(
        label="Classification Group",
        queryset=ClassificationGroup.objects.all(),
        endpoint=ClassificationGroup.get_representation_endpoint(),
        value_key=ClassificationGroup.get_representation_value_key(),
        label_key=ClassificationGroup.get_representation_label_key(),
        initial=_get_default_classification_group_id,
        method="fake_filter",
        required=True,
    )

    def query_classification(self, queryset, name, value):
        if value:
            return queryset.filter(**{name.replace("_", "__"): value.id})
        return queryset

    class Meta:
        model = InstrumentClassificationThroughModel
        fields = {
            "instrument": ["exact"],
            "is_favorite": ["exact"],
        }


class MonthlyPerformancesInstrumentFilterSet(wb_filters.FilterSet):
    period = wb_filters.FinancialPerformanceDateRangeFilter(
        label="Period",
        required=True,
        clearable=False,
        method="fake_filter",
        initial=lambda r, v, q: DateRange(get_earliest_date(r, v, q), get_latest_date(r, v, q)),
    )

    class Meta:
        model = Instrument
        fields = {}
