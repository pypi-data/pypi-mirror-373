from datetime import date

import pandas as pd
import pytest
from faker import Faker
from wbcore.models import DynamicDecimalField, DynamicFloatField

from wbfdm.models import Instrument, InstrumentPrice, RelatedInstrumentThroughModel

fake = Faker()


@pytest.mark.django_db
class TestInstrumentPriceModel:
    def test_init(self, instrument_price):
        assert instrument_price.id is not None

    def test_str(self, instrument_price):
        assert (
            str(instrument_price)
            == f"{instrument_price.instrument.name}: {instrument_price.net_value} {instrument_price.date:%d.%m.%Y}"
        )

    def test_previous_price(self, instrument, instrument_price_factory):
        previous_price = instrument_price_factory.create(instrument=instrument, date=date(2009, 12, 31))
        price = instrument_price_factory.create(instrument=instrument, date=date(2010, 1, 1))
        assert price.previous_price == previous_price

    def test_previous_price_does_not_exist(self, instrument_price):
        assert instrument_price.previous_price is None

    def test_next_price_price(self, instrument, instrument_price_factory):
        next_price = instrument_price_factory.create(instrument=instrument, date=date(2010, 1, 4))
        price = instrument_price_factory.create(instrument=instrument, date=date(2010, 1, 1))
        assert price.next_price == next_price

    def test_next_price_does_not_exist(self, instrument_price):
        assert instrument_price.next_price is None

    def test_subquery_closest_value(self, instrument, instrument_price_factory):
        instrument_price_factory.create_batch(5, instrument=instrument)
        latest_valid_price = InstrumentPrice.objects.latest("date")
        queryset = Instrument.objects.all().annotate(
            net_value=InstrumentPrice.subquery_closest_value(
                "net_value", val_date=latest_valid_price.date, instrument_pk_name="pk"
            )
        )

        assert queryset.get(id=instrument.id).net_value == latest_valid_price.net_value

    def test_compute_and_update_statistics(self, weekday, instrument_factory, instrument_price_factory):
        product = instrument_factory.create()
        benchmark = instrument_factory.create()
        RelatedInstrumentThroughModel.objects.create(
            instrument=product,
            related_instrument=benchmark,
            related_type=RelatedInstrumentThroughModel.RelatedTypeChoices.BENCHMARK,
        )
        risk_free_rate = instrument_factory.create()
        RelatedInstrumentThroughModel.objects.create(
            instrument=product,
            related_instrument=risk_free_rate,
            related_type=RelatedInstrumentThroughModel.RelatedTypeChoices.RISK_INSTRUMENT,
        )

        for _d in pd.date_range(end=weekday, periods=5, freq="B"):
            instrument_price_factory.create(
                calculated=False, instrument=benchmark, date=_d.date(), sharpe_ratio=None, correlation=None, beta=None
            )
            instrument_price_factory.create(
                calculated=False,
                instrument=risk_free_rate,
                date=_d.date(),
                sharpe_ratio=None,
                correlation=None,
                beta=None,
            )
            instrument_price_factory.create(
                calculated=False, instrument=product, date=_d.date(), sharpe_ratio=None, correlation=None, beta=None
            )

        p = product.valuations.get(date=weekday)
        p.compute_and_update_statistics(min_period=5)
        assert p.sharpe_ratio
        assert p.correlation
        assert p.beta

    # Compute functions tests
    #
    # @pytest.mark.parametrize("instrument_price__custom_beta_180d", [None])
    # def test_compute_custom_beta_180d(self, instrument_price):
    #     assert hasattr(instrument_price, "_compute_custom_beta_180d")
    #     assert isinstance(instrument_price._meta.get_field("custom_beta_180d"), DynamicFloatField)
    #
    # @pytest.mark.parametrize("instrument_price__custom_beta_1y", [None])
    # def test_compute_custom_beta_1y(self, instrument_price):
    #     assert hasattr(instrument_price, "_compute_custom_beta_1y")
    #     assert isinstance(instrument_price._meta.get_field("custom_beta_1y"), DynamicFloatField)
    #
    # @pytest.mark.parametrize("instrument_price__custom_beta_2y", [None])
    # def test_compute_custom_beta_2y(self, instrument_price):
    #     assert hasattr(instrument_price, "_compute_custom_beta_2y")
    #     assert isinstance(instrument_price._meta.get_field("custom_beta_2y"), DynamicFloatField)
    #
    # @pytest.mark.parametrize("instrument_price__custom_beta_3y", [None])
    # def test_compute_custom_beta_3y(self, instrument_price):
    #     assert hasattr(instrument_price, "_compute_custom_beta_3y")
    #     assert isinstance(instrument_price._meta.get_field("custom_beta_3y"), DynamicFloatField)
    #
    # @pytest.mark.parametrize("instrument_price__custom_beta_5y", [None])
    # def test_compute_custom_beta_5y(self, instrument_price):
    #     assert hasattr(instrument_price, "_compute_custom_beta_5y")
    #     assert isinstance(instrument_price._meta.get_field("custom_beta_5y"), DynamicFloatField)
    #
    # @pytest.mark.parametrize(
    #     "instrument_price__free_float_ratio, instrument_price__outstanding_shares", [(None, decimal.Decimal(10))]
    # )
    # def test_compute_free_float_ratio(self, instrument_price):
    #     assert hasattr(instrument_price, "_compute_free_float_ratio")
    #     assert isinstance(instrument_price._meta.get_field("free_float_ratio"), DynamicFloatField)
    #     assert instrument_price.free_float_ratio == instrument_price.free_float / float(
    #         instrument_price.outstanding_shares
    #     )
    #
    # @pytest.mark.parametrize(
    #     "instrument_price__short_interest_ratio, instrument_price__outstanding_shares", [(None, decimal.Decimal(10))]
    # )
    # def test_compute_short_interest_ratio(self, instrument_price):
    #     assert hasattr(instrument_price, "_compute_short_interest_ratio")
    #     assert isinstance(instrument_price._meta.get_field("short_interest_ratio"), DynamicFloatField)
    #     assert instrument_price.short_interest_ratio == instrument_price.short_interest / float(
    #         instrument_price.outstanding_shares
    #     )
    #
    # @pytest.mark.parametrize("instrument_price__net_value_usd", [None])
    # def test_compute_net_value_usd(self, instrument_price):
    #     assert hasattr(instrument_price, "_compute_net_value_usd")
    #     assert isinstance(instrument_price._meta.get_field("net_value_usd"), DynamicFloatField)
    #     assert instrument_price.net_value_usd == instrument_price.currency_fx_usd * float(instrument_price.net_value)
    #
    # @pytest.mark.parametrize("instrument_price__volume_usd", [None])
    # def test_compute_volume_usd(self, instrument_price):
    #     assert hasattr(instrument_price, "_compute_volume_usd")
    #     assert isinstance(instrument_price._meta.get_field("volume_usd"), DynamicFloatField)
    #     assert instrument_price.volume_usd == instrument_price.currency_fx_usd * instrument_price.volume * float(
    #         instrument_price.net_value
    #     )
    #
    # @pytest.mark.parametrize("instrument_price__volume_50d_usd", [None])
    # def test_compute_volume_50d_usd(self, instrument_price):
    #     assert hasattr(instrument_price, "_compute_volume_50d_usd")
    #     assert isinstance(instrument_price._meta.get_field("volume_50d_usd"), DynamicFloatField)
    #     assert instrument_price.volume_50d_usd == instrument_price.net_value_usd * instrument_price.volume_50d
    #
    # @pytest.mark.parametrize("instrument_price__currency_fx_usd", [None])
    # def test_compute_currency_fx_usd(self, instrument_price):
    #     fx_rate = instrument_price.instrument.currency.fx_rates.get(date=instrument_price.date)
    #     instrument_price.save(update_all_dynamic_fields=True)
    #     assert hasattr(instrument_price, "_compute_currency_fx_usd")
    #     assert isinstance(instrument_price._meta.get_field("currency_fx_usd"), DynamicFloatField)
    #     assert instrument_price.currency_fx_usd == 1 / float(fx_rate.value)

    @pytest.mark.parametrize("instrument_price__gross_value", [None])
    def test_compute_gross_value(self, instrument_price):
        assert hasattr(instrument_price, "_compute_gross_value")
        assert isinstance(instrument_price._meta.get_field("gross_value"), DynamicDecimalField)
        assert instrument_price.gross_value == instrument_price.net_value

    @pytest.mark.parametrize("instrument_price__volume_50d", [None])
    def test_compute_volume_50d(self, instrument_price, instrument_price_factory):
        assert hasattr(instrument_price, "_compute_volume_50d")
        assert isinstance(instrument_price._meta.get_field("volume_50d"), DynamicFloatField)

        sum_volume_50d = instrument_price.volume
        for _d in pd.date_range(end=instrument_price.date, periods=50, freq="B", inclusive="left"):
            p = instrument_price_factory.create(date=_d, instrument=instrument_price.instrument)
            sum_volume_50d += p.volume
        instrument_price.save(update_all_dynamic_fields=True)
        assert instrument_price.volume_50d == sum_volume_50d / 50

    # @pytest.mark.parametrize("instrument_price__volume_200d", [None])
    # def test_compute_volume_200d(self, instrument_price, instrument_price_factory):
    #     assert hasattr(instrument_price, "_compute_volume_200d")
    #     assert isinstance(instrument_price._meta.get_field("volume_200d"), DynamicFloatField)
    #
    #     sum_volume_200d = instrument_price.volume
    #     for _d in pd.date_range(end=instrument_price.date, periods=200, freq="B", inclusive="left"):
    #         p = instrument_price_factory.create(date=_d, instrument=instrument_price.instrument)
    #         sum_volume_200d += p.volume
    #     instrument_price.save(update_all_dynamic_fields=True)
    #     assert instrument_price.volume_200d == sum_volume_200d / 200

    # @pytest.mark.parametrize("instrument_price__market_capitalization_usd", [None])
    # def test_compute_market_capitalization_usd(self, instrument_price):
    #     assert hasattr(instrument_price, "market_capitalization_usd")
    #     assert isinstance(instrument_price._meta.get_field("market_capitalization_usd"), DynamicFloatField)
    #     assert (
    #         instrument_price.market_capitalization_usd
    #         == instrument_price.market_capitalization * instrument_price.currency_fx_usd
    #     )

    # def test_compute_performance_1d(self, instrument_price_factory):
    #     previous_price = instrument_price_factory.create()
    #     instrument_price = instrument_price_factory.create(
    #         instrument=previous_price.instrument,
    #         calculated=previous_price.calculated,
    #         date=previous_price.date + BDay(1),
    #         performance_1d=None,
    #     )
    #     assert hasattr(instrument_price, "performance_1d")
    #     assert isinstance(instrument_price._meta.get_field("performance_1d"), DynamicDecimalField)
    #     assert instrument_price.performance_1d == instrument_price.net_value / previous_price.net_value - 1
    #
    # def test_compute_performance_7d(self, instrument_price_factory):
    #     previous_price = instrument_price_factory.create()
    #     instrument_price = instrument_price_factory.create(
    #         instrument=previous_price.instrument,
    #         calculated=previous_price.calculated,
    #         date=previous_price.date + BDay(7),
    #         performance_7d=None,
    #     )
    #     assert hasattr(instrument_price, "performance_7d")
    #     assert isinstance(instrument_price._meta.get_field("performance_7d"), DynamicDecimalField)
    #     assert instrument_price.performance_7d == instrument_price.net_value / previous_price.net_value - 1
    #
    # def test_compute_performance_30d(self, instrument_price_factory):
    #     previous_price = instrument_price_factory.create()
    #     instrument_price = instrument_price_factory.create(
    #         instrument=previous_price.instrument,
    #         calculated=previous_price.calculated,
    #         date=previous_price.date + BDay(30),
    #         performance_30d=None,
    #     )
    #     assert hasattr(instrument_price, "performance_30d")
    #     assert isinstance(instrument_price._meta.get_field("performance_30d"), DynamicDecimalField)
    #     assert instrument_price.performance_30d == instrument_price.net_value / previous_price.net_value - 1
    #
    # def test_compute_performance_90d(self, instrument_price_factory):
    #     previous_price = instrument_price_factory.create()
    #     instrument_price = instrument_price_factory.create(
    #         instrument=previous_price.instrument,
    #         calculated=previous_price.calculated,
    #         date=previous_price.date + BDay(90),
    #         performance_90d=None,
    #     )
    #     assert hasattr(instrument_price, "performance_90d")
    #     assert isinstance(instrument_price._meta.get_field("performance_90d"), DynamicDecimalField)
    #     assert instrument_price.performance_90d == instrument_price.net_value / previous_price.net_value - 1
    #
    # def test_compute_performance_365d(self, instrument_price_factory):
    #     previous_price = instrument_price_factory.create()
    #     instrument_price = instrument_price_factory.create(
    #         instrument=previous_price.instrument,
    #         calculated=previous_price.calculated,
    #         date=previous_price.date + BDay(365),
    #         performance_365d=None,
    #     )
    #     assert hasattr(instrument_price, "performance_365d")
    #     assert isinstance(instrument_price._meta.get_field("performance_365d"), DynamicDecimalField)
    #     assert instrument_price.performance_365d == instrument_price.net_value / previous_price.net_value - 1
    #
    # @pytest.mark.parametrize("instrument_price__performance_ytd", [None])
    # def test_compute_performance_ytd(self, instrument_price, instrument_price_factory):
    #     previous_price = instrument_price_factory.create(
    #         instrument=instrument_price.instrument,
    #         calculated=instrument_price.calculated,
    #         date=(date(instrument_price.date.year, 1, 1) - BDay(0)).date(),
    #         performance_ytd=None,
    #     )
    #     instrument_price.save(update_all_dynamic_fields=True)
    #     assert hasattr(instrument_price, "performance_ytd")
    #     assert isinstance(instrument_price._meta.get_field("performance_ytd"), DynamicDecimalField)
    #     assert instrument_price.performance_ytd == instrument_price.net_value / previous_price.net_value - 1
    #
    # def test_compute_performance_inception(self, instrument_price_factory):
    #     inception_price = instrument_price_factory.create()
    #     inception_price.instrument.inception_date = inception_price.date
    #     inception_price.instrument.save()
    #     instrument_price_factory.create(
    #         instrument=inception_price.instrument,
    #         calculated=inception_price.calculated,
    #         date=inception_price.date + BDay(1),
    #         performance_inception=None,
    #     )
    #     instrument_price = instrument_price_factory.create(
    #         instrument=inception_price.instrument,
    #         calculated=inception_price.calculated,
    #         date=inception_price.date + BDay(2),
    #         performance_inception=None,
    #     )
    #     assert hasattr(instrument_price, "performance_inception")
    #     assert isinstance(instrument_price._meta.get_field("performance_inception"), DynamicDecimalField)
    #     assert instrument_price.performance_inception == instrument_price.net_value / inception_price.net_value - 1
