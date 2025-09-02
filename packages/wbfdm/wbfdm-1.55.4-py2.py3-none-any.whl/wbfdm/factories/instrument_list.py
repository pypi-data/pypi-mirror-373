import factory
from slugify import slugify

from wbfdm.models import InstrumentList, InstrumentListThroughModel


class InstrumentListFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")
    identifier = factory.LazyAttribute(lambda o: slugify(o.name))
    instrument_list_type = None

    class Meta:
        django_get_or_create = ("identifier",)
        model = InstrumentList


class InstrumentListThroughModelFactory(factory.django.DjangoModelFactory):
    instrument_list = factory.SubFactory(InstrumentListFactory)
    instrument = factory.SubFactory("wbfdm.factories.instruments.InstrumentFactory")

    class Meta:
        django_get_or_create = ("instrument_list",)
        model = InstrumentListThroughModel
