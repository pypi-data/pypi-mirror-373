import pytest
from django.forms.models import model_to_dict
from faker import Faker

from wbfdm.import_export.handlers.option import (
    OptionAggregateImportHandler,
    OptionImportHandler,
)
from wbfdm.models import Option, OptionAggregate

fake = Faker()


@pytest.mark.django_db
class TestOptionAggregateModel:
    def test_option_creation(self, option_aggregate):
        assert option_aggregate.id is not None

    def test_import_option(self, import_source, instrument, option_aggregate_factory):
        def serialize(option_aggregate):
            data = model_to_dict(option_aggregate)
            data["date"] = option_aggregate.date.strftime("%Y-%m-%d")
            data["instrument"] = {"id": instrument.id}
            del data["id"]
            del data["import_source"]
            return data

        option_aggregate = option_aggregate_factory.build()
        data = {"data": [serialize(option_aggregate)]}
        handler = OptionAggregateImportHandler(import_source)

        # Import non existing data
        handler.process(data)
        assert OptionAggregate.objects.count() == 1

        # Import already existing data
        # import_source.data['data'][0]['shares'] *= 2

        handler.process(data)
        assert OptionAggregate.objects.count() == 1


@pytest.mark.django_db
class TestOptionModel:
    def test_option_creation(self, option):
        assert option.id is not None

    def test_import_option(self, import_source, instrument, option_factory):
        def serialize(option):
            data = model_to_dict(option)
            data["date"] = option.date.strftime("%Y-%m-%d")
            data["expiration_date"] = option.expiration_date.strftime("%Y-%m-%d")
            data["instrument"] = {"id": instrument.id}
            del data["id"]
            del data["import_source"]
            return data

        option = option_factory.build()
        data = {"data": [serialize(option)]}
        handler = OptionImportHandler(import_source)

        # Import non existing data
        handler.process(data)
        assert Option.objects.count() == 1

        # Import already existing data
        # import_source.data['data'][0]['shares'] *= 2

        handler.process(data)
        assert Option.objects.count() == 1
