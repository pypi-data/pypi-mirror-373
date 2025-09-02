import pytest
from faker import Faker

from wbfdm.factories.instruments import InstrumentFactory
from wbfdm.models import (
    Instrument,
    InstrumentClassificationThroughModel,
    RelatedInstrumentThroughModel,
)

fake = Faker()


@pytest.mark.django_db
class TestMergeInstrument:
    @pytest.fixture()
    def merged_instrument(self):
        return InstrumentFactory.create()

    @pytest.fixture()
    def main_instrument(self):
        return InstrumentFactory.create()

    def test_default(
        self,
        main_instrument,
        merged_instrument,
        exchange_factory,
        instrument_favorite_group_factory,
        related_instrument_through_model_factory,
        instrument_classification_through_model_factory,
    ):
        # Prepare data: add exchange
        main_exchange = main_instrument.exchange

        # Prepare data: Create Favorite group with the merged instrument within
        favorite_group = instrument_favorite_group_factory.create(instruments=[merged_instrument])

        # prepare data: related instruments
        main_related_instrument_rel = related_instrument_through_model_factory.create(instrument=main_instrument)
        merged_related_instrument_rel = related_instrument_through_model_factory.create(instrument=merged_instrument)
        reversed_related_instrument_rel = related_instrument_through_model_factory.create(
            related_instrument=merged_instrument
        )

        # prepare data: classification
        main_classification_rel = instrument_classification_through_model_factory.create(instrument=main_instrument)
        merged_classification_rel = instrument_classification_through_model_factory.create(
            instrument=merged_instrument
        )
        reversed_classification_rel = instrument_classification_through_model_factory.create(
            related_instruments=[merged_instrument]
        )

        main_instrument.merge(merged_instrument)

        # Test if the merged instrument is indeed deleted
        with pytest.raises(Instrument.DoesNotExist):
            merged_instrument.refresh_from_db()

        # Check Exchanges
        assert {main_instrument.exchange} == {
            main_exchange
        }  # check that the merged instrument exchange is forward to the main instrument

        # Check favorite Group
        assert list(favorite_group.instruments.all()) == [
            main_instrument
        ]  # Check that the favorite group with the merged instrument removed it and included the main instrument

        # Check related instruments
        assert (
            RelatedInstrumentThroughModel.objects.filter(
                instrument=main_instrument,
                related_instrument=merged_related_instrument_rel.related_instrument,
                is_primary=merged_related_instrument_rel.is_primary,
                related_type=merged_related_instrument_rel.related_type,
            ).exists()
        )  # Check that the related instrument with the merged instrument removed it and included the main instrument
        assert main_instrument.related_instruments.filter(
            id=main_related_instrument_rel.related_instrument.id
        ).exists()  # Check that the main instrument related instrument is still there
        assert RelatedInstrumentThroughModel.objects.filter(
            related_instrument=main_instrument, instrument=reversed_related_instrument_rel.instrument
        ).exists()  # Check that the reverse related instrument relationship has been forward to the main instrument

        # Check classification
        assert InstrumentClassificationThroughModel.objects.filter(
            instrument=main_instrument,
            classification=merged_classification_rel.classification,
            is_favorite=merged_classification_rel.is_favorite,
            reason=merged_classification_rel.reason,
            pure_player=merged_classification_rel.pure_player,
            top_player=merged_classification_rel.top_player,
            percent_of_revenue=merged_classification_rel.percent_of_revenue,
        ).exists()
        assert main_instrument.classifications.filter(
            id=main_classification_rel.classification.id
        ).exists()  # Check that the main instrument classification relationship is still there
        assert (
            InstrumentClassificationThroughModel.objects.filter(
                related_instruments=main_instrument, classification=reversed_classification_rel.classification
            ).exists()
        )  # Check that the reverse classificaiton instrument relationship has been forward to the main instrument
