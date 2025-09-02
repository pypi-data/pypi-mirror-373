import factory
import rstr
from slugify import slugify

from wbfdm.models import Cash, Instrument, InstrumentType


class InstrumentTypeFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")
    key = factory.LazyAttribute(lambda o: slugify(o.name))

    class Meta:
        django_get_or_create = ("key",)
        model = InstrumentType


class InstrumentFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("company")
    name_repr = factory.LazyAttribute(lambda x: x.name)
    description = factory.Faker("paragraph")
    instrument_type = factory.SubFactory(InstrumentTypeFactory)
    inception_date = factory.Faker("past_date")
    delisted_date = None
    currency = factory.SubFactory("wbcore.contrib.currency.factories.CurrencyUSDFactory")
    country = factory.SubFactory("wbcore.contrib.geography.factories.CountryFactory")
    exchange = factory.SubFactory("wbfdm.factories.exchanges.ExchangeFactory")

    identifier = factory.LazyAttribute(lambda o: rstr.xeger("([A-Z]{2}[A-Z0-9]{9}[0-9]{1})"))
    isin = factory.LazyAttribute(lambda o: rstr.xeger("([A-Z]{2}[A-Z0-9]{9}[0-9]{1})"))
    ticker = factory.LazyAttribute(lambda o: rstr.xeger("([A-Z]{4})"))
    dl_parameters = {"market_data": {"path": "wbfdm.contrib.internal.dataloaders.market_data.MarketDataDataloader"}}

    @factory.post_generation
    def classifications(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for classification in extracted:
                self.classifications.add(classification)

    @factory.post_generation
    def related_instruments(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for instrument in extracted:
                self.related_instruments.add(instrument)

    class Meta:
        model = Instrument


class CashFactory(factory.django.DjangoModelFactory):
    is_cash = True
    currency = factory.SubFactory("wbcore.contrib.currency.factories.CurrencyUSDFactory")
    name = factory.LazyAttribute(lambda o: o.currency.title)
    instrument_type = factory.LazyAttribute(
        lambda o: InstrumentType.objects.get_or_create(key="cash", defaults={"name": "Cash", "short_name": "Cash"})[0]
    )

    class Meta:
        model = Cash
        django_get_or_create = ("currency",)


class EquityFactory(InstrumentFactory):
    instrument_type = factory.LazyAttribute(lambda o: InstrumentTypeFactory.create(name="Equity", key="equity"))

    class Meta:
        model = Instrument
