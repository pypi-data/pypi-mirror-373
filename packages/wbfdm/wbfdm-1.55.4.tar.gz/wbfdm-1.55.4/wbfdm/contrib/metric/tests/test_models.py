import pytest
from django.contrib.contenttypes.models import ContentType

from wbfdm.models import Instrument

from ..dto import Metric
from ..models import InstrumentMetric
from ..registry import backend_registry


@pytest.mark.django_db
class TestInstrumentMetric:
    def test_save(self, instrument_metric):
        assert instrument_metric.basket_repr == str(instrument_metric.basket)

    def test_update_or_create_from_metric(self, weekday, instrument_factory):
        i1 = instrument_factory.create()
        i2 = instrument_factory.create()
        i3 = instrument_factory.create()
        key = "key"
        basket_content_type_id = ContentType.objects.get_for_model(i1).id
        level1_dto_metric = Metric(
            basket_id=i1.id,
            basket_content_type_id=basket_content_type_id,
            key=key,
            metrics={"a": "a"},
            date=weekday,
        )
        level1_dto_metric = Metric(
            basket_id=i2.id,
            basket_content_type_id=basket_content_type_id,
            key=key,
            metrics={"b": "b"},
            date=weekday,
            dependency_metrics=[level1_dto_metric],
        )
        base_dto_metric = Metric(
            basket_id=i3.id,
            basket_content_type_id=basket_content_type_id,
            key=key,
            metrics={"c": "c"},
            date=weekday,
            dependency_metrics=[level1_dto_metric],
        )
        InstrumentMetric.update_or_create_from_metric(base_dto_metric)

        level2_metric = InstrumentMetric.objects.get(
            basket_id=i1.id, basket_content_type_id=basket_content_type_id, date=weekday, key=key
        )
        level1_metric = InstrumentMetric.objects.get(
            basket_id=i2.id, basket_content_type_id=basket_content_type_id, date=weekday, key=key
        )
        base_metric = InstrumentMetric.objects.get(
            basket_id=i3.id, basket_content_type_id=basket_content_type_id, date=weekday, key=key
        )

        assert level2_metric.metrics == {"a": "a"}
        assert level2_metric.parent_metric == level1_metric

        assert level1_metric.metrics == {"b": "b"}
        assert level1_metric.parent_metric == base_metric

        assert base_metric.metrics == {"c": "c"}

    def test_annotate_with_metrics(self, instrument_metric):
        qs = Instrument.objects.filter(id=instrument_metric.basket_id)
        qs = InstrumentMetric.annotate_with_metrics(
            qs, backend_registry._metric_key_map[instrument_metric.key], Instrument, val_date=instrument_metric.date
        )
        for field in instrument_metric.metrics.keys():
            qs_field = instrument_metric.key + "_" + field
            res = list(qs.values_list(qs_field, flat=True))[0]
            assert res == instrument_metric.metrics[field]
