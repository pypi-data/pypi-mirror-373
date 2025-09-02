import factory

from wbfdm.enums import (
    ESGControveryFlag,
    ESGControverySeverity,
    ESGControveryStatus,
    ESGControveryType,
)
from wbfdm.models.esg.controversies import Controversy


class ControversyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Controversy

    instrument = factory.SubFactory("wbfdm.factories.instruments.InstrumentFactory")
    external_id = factory.LazyAttribute(lambda o: f"{o.instrument.id}-{hash(o.headline)}")
    headline = factory.Faker("sentence")
    description = factory.Faker("sentence")
    source = factory.Faker("company")
    status = ESGControveryStatus.ONGOING
    type = ESGControveryType.STRUCTURAL
    severity = ESGControverySeverity.MINOR
    flag = ESGControveryFlag.GREEN
    direct_involvement = True
    company_response = factory.Faker("sentence")
    review = factory.Faker("date_object")
    initiated = factory.Faker("date_object")
