from wbcore.tests.conftest import *  # isort:skip
from datetime import date

from django.apps import apps
from django.db.models.signals import pre_migrate
from faker import Faker
from pandas.tseries.offsets import BDay
from pytest_factoryboy import register
from wbcore.contrib.authentication.factories import (
    InternalUserFactory,
    SuperUserFactory,
    UserFactory,
)
from wbcore.contrib.currency.factories import CurrencyFactory, CurrencyFXRatesFactory
from wbcore.contrib.directory.factories.entries import (
    CompanyFactory,
    CompanyTypeFactory,
    CustomerStatusFactory,
    EntryFactory,
    PersonFactory,
)
from wbcore.contrib.geography.factories import (
    CityFactory,
    ContinentFactory,
    CountryFactory,
    StateFactory,
)
from wbcore.contrib.geography.tests.signals import app_pre_migration
from wbcore.contrib.io.factories import (
    CrontabScheduleFactory,
    DataBackendFactory,
    ImportSourceFactory,
    ParserHandlerFactory,
    ProviderFactory,
    SourceFactory,
)
from wbfdm.factories import (
    ClassificationFactory,
    ClassificationGroupFactory,
    ExchangeFactory,
    InstrumentClassificationThroughModelFactory,
    InstrumentFactory,
    InstrumentFavoriteGroupFactory,
    InstrumentListFactory,
    InstrumentPriceFactory,
    InstrumentTypeFactory,
    OptionAggregateFactory,
    OptionFactory,
    ParentClassificationFactory,
    RelatedInstrumentThroughModelFactory,
)

fake = Faker()
register(ImportSourceFactory)
register(DataBackendFactory)
register(ProviderFactory)
register(SourceFactory)
register(ParserHandlerFactory)
register(CrontabScheduleFactory)

register(ClassificationFactory)
register(InstrumentClassificationThroughModelFactory)
register(ParentClassificationFactory)
register(ClassificationGroupFactory)
register(ExchangeFactory)
register(InstrumentFactory)
register(InstrumentTypeFactory)
register(InstrumentPriceFactory)
register(InstrumentFavoriteGroupFactory)
register(RelatedInstrumentThroughModelFactory)
register(CurrencyFXRatesFactory)
register(InstrumentListFactory)
register(OptionFactory)
register(OptionAggregateFactory)

register(CurrencyFactory)
register(CityFactory)
register(StateFactory)
register(CountryFactory)
register(ContinentFactory)

register(CompanyFactory)
register(PersonFactory)
register(InternalUserFactory)
register(EntryFactory)
register(CustomerStatusFactory)
register(CompanyTypeFactory)

register(UserFactory)
register(SuperUserFactory, "superuser")

pre_migrate.connect(app_pre_migration, sender=apps.get_app_config("wbfdm"))
