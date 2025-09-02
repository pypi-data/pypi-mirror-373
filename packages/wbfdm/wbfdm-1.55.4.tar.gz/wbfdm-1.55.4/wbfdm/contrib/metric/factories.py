import factory
from django.contrib.contenttypes.models import ContentType
from faker import Faker

from wbfdm.contrib.metric.models import InstrumentMetric
from wbfdm.factories import InstrumentFactory
from wbfdm.models import Instrument

from .registry import backend_registry

fake = Faker()


def _get_metrics(key: str):
    backend = backend_registry[key, Instrument]
    metrics = {}
    for sub_field in backend.keys[0].subfields:
        metrics[sub_field.key] = fake.pyfloat()
    return metrics


class InstrumentMetricFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InstrumentMetric
        # django_get_or_create = ["basket_content_type", "basket_id", "instrument", "date", "key"]

    basket = factory.SubFactory(InstrumentFactory)
    basket_content_type = factory.LazyAttribute(lambda o: ContentType.objects.get_for_model(Instrument))
    basket_id = factory.LazyAttribute(lambda o: o.basket.id)

    date = factory.Faker("date_object")
    key = factory.Iterator(backend_registry.keys())
    metrics = factory.LazyAttribute(lambda o: _get_metrics(o.key))
    parent_metric = None
