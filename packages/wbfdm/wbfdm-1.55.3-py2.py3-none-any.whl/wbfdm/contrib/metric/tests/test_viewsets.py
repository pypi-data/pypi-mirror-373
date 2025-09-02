from datetime import date

import pytest
from faker import Faker
from rest_framework.test import APIRequestFactory
from wbcore import viewsets
from wbcore.utils.strings import get_aggregate_symbol

from wbfdm.contrib.metric.backends.performances import (
    PERFORMANCE_METRIC,
    InstrumentPerformanceMetricBackend,
)
from wbfdm.contrib.metric.models import InstrumentMetric
from wbfdm.models import Instrument
from wbfdm.serializers import InstrumentModelSerializer

from ..viewsets.mixins import InstrumentMetricMixin

fake = Faker()


@pytest.mark.django_db
class TestInstrumentMetricMixin:
    @pytest.fixture
    def viewset(self, instrument_metric_factory):
        metric = instrument_metric_factory.create(key="performance")

        class InstrumentWithMetricModelViewSet(InstrumentMetricMixin, viewsets.ModelViewSet):
            METRIC_KEYS = (PERFORMANCE_METRIC,)
            METRIC_WITH_PREFIXED_KEYS = fake.boolean()
            serializer_class = InstrumentModelSerializer
            queryset = Instrument.objects.all()

            @property
            def metric_basket(self):
                return metric.basket

            @property
            def metric_date(self) -> date | None:
                return metric.date

        request = APIRequestFactory().get("")
        return InstrumentWithMetricModelViewSet(request=request, format_kwarg={})

    def test_metric_serializer_fields(self, weekday, viewset):
        assert (
            viewset._metric_serializer_fields.keys()
            == InstrumentPerformanceMetricBackend(weekday)
            .get_serializer_fields(with_prefixed_key=viewset.METRIC_WITH_PREFIXED_KEYS)
            .keys()
        )

    def test_get_ordering_fields(self, viewset):
        ordering_fields = viewset.get_ordering_fields()
        for key, _ in PERFORMANCE_METRIC.get_fields(with_prefixed_key=viewset.METRIC_WITH_PREFIXED_KEYS):
            assert key in ordering_fields

    def test_get_queryset(self, viewset):
        queryset = viewset.get_queryset()
        annotations = list(queryset.query.annotations.keys())
        for key, _ in PERFORMANCE_METRIC.get_fields(with_prefixed_key=viewset.METRIC_WITH_PREFIXED_KEYS):
            assert key in annotations

    def test_get_serializer(self, viewset):
        serializer = viewset.get_serializer()
        for key, _ in PERFORMANCE_METRIC.get_fields(with_prefixed_key=viewset.METRIC_WITH_PREFIXED_KEYS):
            assert key in serializer.fields

    def test_get_aggregates(self, viewset):
        queryset = viewset.get_queryset()
        aggregates = viewset.get_aggregates(queryset, queryset)
        metric = InstrumentMetric.objects.first()
        assert metric is not None
        for key, _ in PERFORMANCE_METRIC.get_fields(with_prefixed_key=viewset.METRIC_WITH_PREFIXED_KEYS):
            key_filter = PERFORMANCE_METRIC.subfields_filter_map[key]
            subfield = PERFORMANCE_METRIC.subfields_map[key]
            assert subfield.aggregate is not None

            if key_filter in metric.metrics:
                assert aggregates[key] == {get_aggregate_symbol(subfield.aggregate.name): metric.metrics[key_filter]}
