import factory
import rstr

from wbfdm.models import (
    Classification,
    ClassificationGroup,
    InstrumentClassificationThroughModel,
)


class ClassificationGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClassificationGroup
        django_get_or_create = ("is_primary",)

    name = factory.Sequence(lambda n: f"Classification Group {n}")
    is_primary = True
    max_depth = 1
    code_level_digits = 2


class ClassificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Classification

    code_aggregated = factory.LazyAttribute(lambda o: rstr.xeger("([0-9]{8})"))
    name = factory.Sequence(lambda n: f"Classification {n}")
    # parent = factory.SubFactory("wbfdm.factories.ParentClassificationFactory", parent=None)
    group = factory.SubFactory(ClassificationGroupFactory)
    level = 0
    # level_representation = factory.LazyAttribute(lambda x: f"Level {x.level}")


class ParentClassificationFactory(ClassificationFactory):
    parent = None


class InstrumentClassificationThroughModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InstrumentClassificationThroughModel
        django_get_or_create = ("instrument", "classification")

    instrument = factory.SubFactory("wbfdm.factories.InstrumentFactory")
    classification = factory.SubFactory("wbfdm.factories.ClassificationFactory")
    is_favorite = factory.Faker("pybool")
    reason = factory.Faker("paragraph")
    pure_player = factory.Faker("pybool")
    top_player = factory.Faker("pybool")

    @factory.post_generation
    def related_instruments(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for instrument in extracted:
                self.related_instruments.add(instrument)
