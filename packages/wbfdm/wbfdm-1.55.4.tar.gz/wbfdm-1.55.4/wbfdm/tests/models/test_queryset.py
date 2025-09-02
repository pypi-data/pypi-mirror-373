from datetime import date
from decimal import Decimal

import pandas as pd
import pytest

from wbfdm.models import Instrument


@pytest.mark.django_db
class TestInstrumentQueryset:
    def test_get_returns(self, instrument_factory, instrument_price_factory):
        v1 = date(2024, 12, 31)
        v2 = date(2025, 1, 1)
        v3 = date(2025, 1, 2)
        v4 = date(2025, 1, 3)

        i1 = instrument_factory.create()
        i2 = instrument_factory.create()

        i11 = instrument_price_factory.create(date=v1, instrument=i1)
        i12 = instrument_price_factory.create(date=v2, instrument=i1)
        i14 = instrument_price_factory.create(date=v4, instrument=i1)
        i21 = instrument_price_factory.create(date=v1, instrument=i2)
        i11.refresh_from_db()
        i12.refresh_from_db()
        i14.refresh_from_db()
        prices, returns = Instrument.objects.filter(id__in=[i1.id, i2.id]).get_returns_df(from_date=v1, to_date=v4)

        expected_returns = pd.DataFrame(
            [[i12.net_value / i11.net_value - 1, 0.0], [0.0, 0.0], [i14.net_value / i12.net_value - 1, 0.0]],
            index=[v2, v3, v4],
            columns=[i1.id, i2.id],
            dtype="float64",
        )
        expected_returns.index = pd.to_datetime(expected_returns.index)
        pd.testing.assert_frame_equal(returns, expected_returns, check_names=False, check_freq=False, atol=1e-6)
        assert prices[v1][i1.id] == float(i11.net_value)
        assert prices[v2][i1.id] == float(i12.net_value)
        assert prices[v3][i1.id] == float(i12.net_value)
        assert prices[v4][i1.id] == float(i14.net_value)
        # test that the returned price are ffill
        assert prices[v1][i2.id] == float(i21.net_value)
        assert prices[v2][i2.id] == float(i21.net_value)
        assert prices[v3][i2.id] == float(i21.net_value)
        assert prices[v4][i2.id] == float(i21.net_value)

    def test_get_returns_fix_forex_on_holiday(
        self, instrument, instrument_price_factory, currency_fx_rates_factory, currency_factory
    ):
        v1 = date(2024, 12, 31)
        v2 = date(2025, 1, 1)
        v3 = date(2025, 1, 2)

        target_currency = currency_factory.create()
        fx_target1 = currency_fx_rates_factory.create(currency=target_currency, date=v1)
        fx_target2 = currency_fx_rates_factory.create(currency=target_currency, date=v2)  # noqa
        fx_target3 = currency_fx_rates_factory.create(currency=target_currency, date=v3)

        fx1 = currency_fx_rates_factory.create(currency=instrument.currency, date=v1)
        fx2 = currency_fx_rates_factory.create(currency=instrument.currency, date=v2)  # noqa
        fx3 = currency_fx_rates_factory.create(currency=instrument.currency, date=v3)

        i1 = instrument_price_factory.create(net_value=Decimal("100"), date=v1, instrument=instrument)
        i2 = instrument_price_factory.create(net_value=Decimal("100"), date=v2, instrument=instrument, calculated=True)
        i3 = instrument_price_factory.create(net_value=Decimal("200"), date=v3, instrument=instrument)

        prices, returns = Instrument.objects.filter(id__in=[instrument.id]).get_returns_df(
            from_date=v1, to_date=v3, to_currency=target_currency
        )
        returns.index = pd.to_datetime(returns.index)
        assert prices[v1][instrument.id] == float(i1.net_value)
        assert prices[v2][instrument.id] == float(i2.net_value)
        assert prices[v3][instrument.id] == float(i3.net_value)

        assert returns.loc[pd.Timestamp(v2), instrument.id] == pytest.approx(
            float(
                (i2.net_value * fx_target1.value / fx1.value) / (i1.net_value * fx_target1.value / fx1.value)
                - Decimal("1")
            ),
            abs=10e-8,
        )  # as v2 as a calculated price, the forex won't apply to it
        assert returns.loc[pd.Timestamp(v3), instrument.id] == pytest.approx(
            float(
                (i3.net_value * fx_target3.value / fx3.value) / (i2.net_value * fx_target1.value / fx1.value)
                - Decimal("1")
            ),
            abs=10e-8,
        )
