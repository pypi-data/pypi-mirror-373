import factory

from wbfdm.models import InstrumentFavoriteGroup, RelatedInstrumentThroughModel


class RelatedInstrumentThroughModelFactory(factory.django.DjangoModelFactory):
    instrument = factory.SubFactory("wbfdm.factories.InstrumentFactory")
    related_instrument = factory.SubFactory("wbfdm.factories.InstrumentFactory")
    related_type = factory.Iterator(RelatedInstrumentThroughModel.RelatedTypeChoices.values)

    class Meta:
        model = RelatedInstrumentThroughModel
        django_get_or_create = ("instrument", "related_instrument", "related_type")


class InstrumentFavoriteGroupFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("company")
    owner = factory.SubFactory("wbcore.contrib.directory.factories.PersonFactory")
    public = factory.Faker("pybool")
    primary = factory.Faker("pybool")

    class Meta:
        model = InstrumentFavoriteGroup

    @factory.post_generation
    def instruments(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for instrument in extracted:
                self.instruments.add(instrument)
