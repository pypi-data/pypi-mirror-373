from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from wbcore import filters

from wbfdm.contrib.metric.models import InstrumentMetric

from .registry import backend_registry


def get_metrics_content_type(request, view):
    return {
        "id__in": list(
            InstrumentMetric.objects.values_list("basket_content_type", flat=True).distinct("basket_content_type")
        )
    }


class InstrumentMetricFilterSet(filters.FilterSet):
    parent_metric = filters.ModelChoiceFilter(
        label="Parent",
        queryset=InstrumentMetric.objects.all(),
        endpoint=InstrumentMetric.get_representation_endpoint(),
        value_key=InstrumentMetric.get_representation_value_key(),
        label_key=InstrumentMetric.get_representation_label_key(),
        hidden=True,
    )
    parent_metric__isnull = filters.BooleanFilter(field_name="parent_metric", lookup_expr="isnull", hidden=True)

    key = filters.ChoiceFilter(choices=backend_registry.get_choices(), label="Key")
    basket_content_type = filters.ModelChoiceFilter(
        queryset=ContentType.objects.all(),
        endpoint="wbcore:contenttyperepresentation-list",
        value_key="id",
        label_key="{{app_label}} | {{model}}",
        label=_("Basket Content Type"),
        filter_params=get_metrics_content_type,
    )

    class Meta:
        model = InstrumentMetric
        fields = {
            "basket_content_type": ["exact"],
            "basket_id": ["exact"],
            "instrument": ["exact"],
            "key": ["exact"],
            "date": ["lte", "gte", "exact"],
            "parent_metric": ["exact", "isnull"],
        }
