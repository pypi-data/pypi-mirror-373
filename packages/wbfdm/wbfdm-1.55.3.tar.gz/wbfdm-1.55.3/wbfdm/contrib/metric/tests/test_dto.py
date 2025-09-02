import pytest
from faker import Faker

from ..backends.performances import InstrumentMetricBaseBackend
from ..dto import MetricField, MetricKey

fake = Faker()


@pytest.mark.django_db
class TestMetricKey:
    @pytest.fixture
    def metric_key(self):
        label = fake.word()

        return MetricKey(
            key=label.lower(),
            label=label,
            additional_prefixes=[fake.word()],
            subfields=[
                MetricField(
                    key=label.lower(),
                    label=label,
                    decorators=[{"position": "left", "value": "&", "type": "text"}],
                    serializer_kwargs={"percent": fake.boolean(), "precision": fake.pyint(min_value=1, max_value=4)},
                )
                for label in map(lambda x: fake.word(), range(3))
            ],
        )

    def test_get_fields(self, metric_key):
        fields = list(metric_key.get_fields())
        assert fields[0] == (
            f"{metric_key.key}_{metric_key.subfields[0].key}",
            f"{metric_key.label} {metric_key.subfields[0].label}",
        )
        assert fields[1] == (
            f"{metric_key.key}_{metric_key.subfields[1].key}",
            f"{metric_key.label} {metric_key.subfields[1].label}",
        )
        assert fields[2] == (
            f"{metric_key.key}_{metric_key.subfields[2].key}",
            f"{metric_key.label} {metric_key.subfields[2].label}",
        )

    def test_get_fields_with_prefixed_key(self, metric_key):
        fields = list(metric_key.get_fields(with_prefixed_key=True))
        prefix = metric_key.additional_prefixes[0]
        assert fields[1] == (
            f"{metric_key.key}_{prefix}_{metric_key.subfields[0].key}",
            f"{metric_key.label} {metric_key.subfields[0].label} ({prefix.title()})",
        )
        assert fields[3] == (
            f"{metric_key.key}_{prefix}_{metric_key.subfields[1].key}",
            f"{metric_key.label} {metric_key.subfields[1].label} ({prefix.title()})",
        )
        assert fields[5] == (
            f"{metric_key.key}_{prefix}_{metric_key.subfields[2].key}",
            f"{metric_key.label} {metric_key.subfields[2].label} ({prefix.title()})",
        )

    def test_fields_map(self, metric_key):
        keys = set(map(lambda x: x[0], metric_key.get_fields(with_prefixed_key=True)))
        assert keys == set(metric_key.subfields_filter_map.keys())

    def test_get_serializer_field_attr(self, weekday, metric_key):
        metric_field = metric_key.subfields[0]
        backend = InstrumentMetricBaseBackend(weekday)
        assert backend.get_serializer_field_attr(metric_field)["percent"] == metric_field.serializer_kwargs["percent"]
        assert (
            backend.get_serializer_field_attr(metric_field)["precision"] == metric_field.serializer_kwargs["precision"]
        )
        assert backend.get_serializer_field_attr(metric_field)["decorators"] == metric_field.decorators
