import factory
import rstr

from wbfdm.models import Exchange


class ExchangeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Exchange
        django_get_or_create = ("mic_code",)

    city = None
    name = factory.LazyAttribute(lambda o: f"Exchange: {o.city}")
    mic_code = factory.LazyAttribute(lambda o: rstr.xeger("([A-Z]{4})"))
    operating_mic_code = factory.LazyAttribute(lambda o: rstr.xeger("([A-Z]{4})"))
    bbg_exchange_codes = factory.LazyAttribute(lambda o: [rstr.xeger("([A-Z]{4})")])
    bbg_composite_primary = factory.Faker("boolean")
    bbg_composite = factory.LazyAttribute(lambda o: rstr.xeger("([A-Z]{4})"))
    refinitiv_identifier_code = factory.LazyAttribute(lambda o: rstr.xeger("([A-Z]{4})"))

    website = factory.Faker("url")
    comments = factory.Faker("paragraph")
