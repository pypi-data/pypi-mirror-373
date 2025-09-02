import random
from datetime import date
from decimal import Decimal

import factory
from pandas.tseries.offsets import BDay
from wbcore.contrib.currency.models import CurrencyFXRates

from wbfdm.models import InstrumentPrice


def get_weekday(o):
    if (
        o.instrument.id
        and (prices := InstrumentPrice.objects.filter(instrument=o.instrument, calculated=o.calculated)).exists()
    ):
        latest_price = prices.latest("date").date
    else:
        latest_price = date(2020, 1, 1)
    return (latest_price + BDay(1)).date()


def get_coherent_net_value(o):
    previous_prices = InstrumentPrice.objects.filter(date__lt=o.date)
    if previous_prices.exists() and (last_price := previous_prices.latest("date")):
        return last_price.net_value * Decimal(
            1 + random.randrange(-5, 5)
        )  # Simulating a markov chain process of variance 10%
    return Decimal(100)


class InstrumentPriceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InstrumentPrice
        django_get_or_create = ("instrument", "date", "calculated")

    instrument = factory.SubFactory("wbfdm.factories.InstrumentFactory")
    date = factory.LazyAttribute(lambda o: get_weekday(o))
    currency_fx_rate_to_usd = factory.LazyAttribute(
        lambda o: CurrencyFXRates.objects.get_or_create(
            currency=o.instrument.currency, date=o.date, defaults={"value": Decimal(1.0)}
        )[0]
    )

    net_value = factory.Faker(
        "pydecimal", min_value=90, max_value=110, right_digits=6
    )  # we narrow down the range to simulate more realistic returns
    gross_value = factory.LazyAttribute(lambda o: o.net_value + Decimal(random.random()))

    calculated = False
    sharpe_ratio = factory.LazyAttribute(lambda o: random.random())
    correlation = factory.LazyAttribute(lambda o: random.random())
    beta = factory.LazyAttribute(lambda o: random.random())

    volume = factory.LazyAttribute(lambda o: random.randint(1000, 100000))
    volume_50d = factory.LazyAttribute(lambda o: random.randint(1000, 100000))
    volume_200d = factory.LazyAttribute(lambda o: random.randint(1000, 100000))
    market_capitalization = factory.LazyAttribute(lambda o: random.randint(10000, 100000))

    # custom_beta_180d = factory.Faker("pyfloat", positive=True, max_value=10e3)
    # custom_beta_1y = factory.Faker("pyfloat", positive=True, max_value=10e3)
    # custom_beta_2y = factory.Faker("pyfloat", positive=True, max_value=10e3)
    # custom_beta_3y = factory.Faker("pyfloat", positive=True, max_value=10e3)
    # custom_beta_5y = factory.Faker("pyfloat", positive=True, max_value=10e3)

    outstanding_shares = None
    volume_50d = factory.Faker("pyfloat", positive=True, max_value=10e3)
    volume_200d = factory.Faker("pyfloat", positive=True, max_value=10e3)

    # performance_1d = factory.Faker("pydecimal", min_value=-1, max_value=1)
    # performance_7d = factory.Faker("pydecimal", min_value=-1, max_value=1)
    # performance_30d = factory.Faker("pydecimal", min_value=-1, max_value=1)
    # performance_90d = factory.Faker("pydecimal", min_value=-1, max_value=1)
    # performance_365d = factory.Faker("pydecimal", min_value=-1, max_value=1)
    # performance_ytd = factory.Faker("pydecimal", min_value=-1, max_value=1)
    # performance_inception = factory.Faker("pydecimal", min_value=-1, max_value=1)

    @factory.post_generation
    def post_gen_currency_creation(self, create, extracted, **kwargs):
        CurrencyFXRates.objects.get_or_create(
            currency=self.instrument.currency, date=self.date, defaults={"value": Decimal(1.0)}
        )
