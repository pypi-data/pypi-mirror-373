from datetime import timedelta

import factory
from faker import Faker
from pandas.tseries.offsets import BDay

from wbfdm.models import Option, OptionAggregate

fake = Faker()


class OptionAggregateFactory(factory.django.DjangoModelFactory):
    type = factory.Iterator(Option.Type)
    date = factory.LazyAttribute(lambda o: (fake.date_object() + BDay(1)).date())
    instrument = factory.SubFactory("wbfdm.factories.InstrumentFactory")

    volume = factory.Faker("pyfloat")
    volume_5d = factory.Faker("pyfloat")
    volume_20d = factory.Faker("pyfloat")
    volume_50d = factory.Faker("pyfloat")

    open_interest = factory.Faker("pyfloat")
    volatility_30d = factory.Faker("pyfloat")
    volatility_60d = factory.Faker("pyfloat")
    volatility_90d = factory.Faker("pyfloat")

    class Meta:
        django_get_or_create = ("type", "instrument", "date")
        model = OptionAggregate


class OptionFactory(factory.django.DjangoModelFactory):
    type = factory.Iterator(Option.Type)
    contract_identifier = factory.Faker("word")
    date = factory.LazyAttribute(lambda o: (fake.date_object() + BDay(1)).date())
    expiration_date = factory.LazyAttribute(lambda o: o.date + timedelta(days=7))
    instrument = factory.SubFactory("wbfdm.factories.InstrumentFactory")
    strike = factory.Faker("pyfloat")
    open = factory.Faker("pyfloat")
    high = factory.Faker("pyfloat")
    low = factory.Faker("pyfloat")
    close = factory.Faker("pyfloat")
    bid = factory.Faker("pyfloat")
    ask = factory.Faker("pyfloat")
    volume = factory.Faker("pyfloat")
    open_interest = factory.Faker("pyfloat")
    vwap = factory.Faker("pyfloat")
    volatility_30d = factory.Faker("pyfloat")
    volatility_60d = factory.Faker("pyfloat")
    volatility_90d = factory.Faker("pyfloat")
    risk_delta = factory.Faker("pyfloat")
    risk_theta = factory.Faker("pyfloat")
    risk_gamma = factory.Faker("pyfloat")
    risk_vega = factory.Faker("pyfloat")
    risk_rho = factory.Faker("pyfloat")
    risk_lambda = factory.Faker("pyfloat")
    risk_epsilon = factory.Faker("pyfloat")
    risk_vomma = factory.Faker("pyfloat")
    risk_vera = factory.Faker("pyfloat")
    risk_speed = factory.Faker("pyfloat")
    risk_zomma = factory.Faker("pyfloat")
    risk_color = factory.Faker("pyfloat")
    risk_ultima = factory.Faker("pyfloat")

    class Meta:
        django_get_or_create = ("contract_identifier", "type", "instrument", "date")
        model = Option
