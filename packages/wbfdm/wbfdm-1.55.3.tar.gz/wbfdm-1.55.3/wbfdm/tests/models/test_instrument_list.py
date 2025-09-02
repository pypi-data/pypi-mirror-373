from unittest.mock import patch

import pytest
from django.contrib.auth.models import Permission
from faker import Faker
from wbcore.contrib.io.exceptions import DeserializationError

from wbfdm.import_export.handlers.instrument_list import InstrumentListImportHandler
from wbfdm.models import InstrumentListThroughModel

fake = Faker()


@pytest.mark.django_db
class TestInstrumentListModel:
    def test_instrument_list_creation(self, instrument_list):
        assert instrument_list.id is not None

    @pytest.mark.parametrize(
        "from_date,to_date,comment",
        [
            (fake.past_date(), fake.future_date(), fake.sentence()),
            (fake.past_date(), fake.future_date(), None),
            (fake.past_date(), None, fake.sentence()),
            (None, fake.future_date(), fake.sentence()),
        ],
    )
    def test_handler_deserialization(self, instrument_list, instrument, import_source, from_date, to_date, comment):
        data = dict()
        if from_date:
            data["from_date"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            data["to_date"] = to_date.strftime("%Y-%m-%d")
        if comment:
            data["comment"] = comment

        data["instrument"] = instrument.id
        data["instrument_list"] = instrument_list.id
        handler = InstrumentListImportHandler(import_source)
        handler._deserialize(data)
        assert data["instrument"] == instrument
        assert data["instrument_list"] == instrument_list
        if to_date:
            assert data["to_date"] == to_date
        if from_date:
            assert data["from_date"] == from_date
        if comment:
            assert data["comment"] == comment
        # try with a dictionary
        data = {}
        data["instrument"] = {"instrument_type": instrument.instrument_type, "isin": instrument.isin}
        data["instrument_list"] = {
            "identifier": instrument_list.identifier,
            "name": instrument_list.name,
            "instrument_list_type": instrument_list.instrument_list_type,
        }
        handler._deserialize(data)
        assert data["instrument"] == instrument
        assert data["instrument_list"] == instrument_list

        # assert missing instrument raise error
        data = {}
        data["instrument"] = instrument.id
        with pytest.raises((DeserializationError,)):
            handler._deserialize(data)
            raise DeserializationError

        # automatically match the instrument if the string representation is provided and the match has already been done for that list
        data = {}
        data["instrument_list"] = instrument_list.id
        data["instrument_str"] = instrument.name
        InstrumentListThroughModel.objects.create(
            instrument_list=instrument_list, instrument_str=instrument.name, instrument=instrument
        )
        handler._deserialize(data)
        assert data["instrument"].id == instrument.id

    @patch("wbfdm.import_export.handlers.instrument_list.send_notification")
    def test_post_processing_objects(
        self, mock_fct, import_source, instrument_list_factory, instrument_factory, user_factory
    ):
        initial_call = mock_fct.call_count
        pm = user_factory.create()
        user_factory.create()  # normal user

        pm.user_permissions.add(
            Permission.objects.get(content_type__app_label="wbfdm", codename="administrate_instrumentlist")
        )
        handler = InstrumentListImportHandler(import_source)

        # Test if the leftover elements are removed on every imports. (e.g. instrument that are not in an exclusion list anymore)
        list1 = instrument_list_factory.create()
        list2 = instrument_list_factory.create()

        leftover1 = InstrumentListThroughModel.objects.create(
            instrument_list=list1, instrument=instrument_factory.create()
        )
        remaining_obj1 = InstrumentListThroughModel.objects.create(
            instrument_list=list1, instrument=instrument_factory.create()
        )
        leftover2 = InstrumentListThroughModel.objects.create(
            instrument_list=list2, instrument=instrument_factory.create()
        )
        remaining_obj2 = InstrumentListThroughModel.objects.create(
            instrument_list=list2, instrument=instrument_factory.create()
        )

        handler._post_processing_objects([remaining_obj1, remaining_obj2], [], [])
        with pytest.raises((InstrumentListThroughModel.DoesNotExist)):
            leftover1.refresh_from_db()
        with pytest.raises((InstrumentListThroughModel.DoesNotExist)):
            leftover2.refresh_from_db()
        remaining_obj2.refresh_from_db()
        remaining_obj1.refresh_from_db()
        assert remaining_obj1
        assert remaining_obj2

        assert mock_fct.call_count - initial_call == 2  # 2 because there are two instrument added to the list
