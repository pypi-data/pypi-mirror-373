import calendar
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from faker import Faker
from pandas.tseries.offsets import BDay

from wbfdm.dataloaders.proxies import InstrumentDataloaderProxy
from wbfdm.factories.instrument_prices import InstrumentPrice
from wbfdm.models import Instrument, RelatedInstrumentThroughModel

fake = Faker()


@pytest.mark.django_db
class TestInstrumentModel:
    def test_init(self, instrument):
        assert instrument.id is not None

    def test_get_prices(self, instrument_factory, instrument_price_factory):
        instrument = instrument_factory.create()
        other_instrument = instrument_factory.create()
        price = instrument_price_factory.create(instrument=instrument, outstanding_shares=100)
        price.refresh_from_db()
        instrument_price_factory.create(instrument=other_instrument)  # Noise
        res = list(instrument.get_prices())
        assert len(res) == 1
        assert res[0]["valuation_date"] == price.date
        assert res[0]["open"] == float(price.net_value)
        assert res[0]["close"] == float(price.net_value)
        assert res[0]["high"] == float(price.net_value)
        assert res[0]["low"] == float(price.net_value)
        assert res[0]["volume"] == price.volume
        assert res[0]["market_capitalization"] == price.market_capitalization
        assert res[0]["outstanding_shares"] == float(price.outstanding_shares)

    def test_get_price(self, weekday, instrument_factory, instrument_price_factory):
        instrument = instrument_factory.create()
        other_instrument = instrument_factory.create()
        price_calculated = instrument_price_factory.create(date=weekday, instrument=instrument, calculated=True)

        instrument_price_factory.create(instrument=other_instrument)  # Noise
        assert instrument.get_price(weekday) == float(price_calculated.net_value)
        price_real = instrument_price_factory.create(date=weekday, instrument=instrument, calculated=False)
        assert instrument.get_price(weekday) == float(price_real.net_value)  # we prioritize real price
        assert instrument.get_price((weekday + BDay(1)).date()) == float(price_real.net_value)
        assert instrument.get_price((weekday + BDay(2)).date()) == float(price_real.net_value)
        assert instrument.get_price((weekday + BDay(3)).date()) == float(price_real.net_value)
        with pytest.raises(ValueError):
            instrument.get_price((weekday + BDay(4)).date())  # for return the latest valid price 3 days earlier.

        # if the instrument is considered cash, we always return a value of 1
        instrument.is_cash = True
        instrument.save()
        assert instrument.get_price(weekday) == Decimal(1)

    def test_extract_daily_performance_df(self):
        tidx = pd.date_range("2016-07-01", periods=4, freq="B")
        data = np.random.randn(4)
        df = pd.Series(data, index=tidx, name="close")
        res = Instrument.extract_daily_performance_df(df)
        assert res.performance[0] == df[1] / df[0] - 1

    def test_extract_monthly_performance_df(self):
        tidx = pd.date_range("2016-07-01", periods=4, freq="ME")
        data = np.random.randn(4)
        df = pd.Series(data, index=tidx, name="close")
        df.index = pd.to_datetime(df.index)
        res = Instrument.extract_monthly_performance_df(df)
        assert res.performance[0] == df[1] / df[0] - 1

    def test_extract_inception_performance_df(self):
        tidx = pd.date_range("2016-07-01", periods=4, freq="D")
        data = np.random.randn(4)
        df = pd.Series(data, index=tidx, name="close")
        res = Instrument.extract_inception_performance_df(df)

        assert res == df[3] / df[0] - 1

    def test_extract_annual_performance_df(self):
        tidx = pd.date_range("2016-07-01", periods=4, freq="BYE")
        data = np.random.randn(4)
        df = pd.Series(data, index=tidx, name="close")
        res = Instrument.extract_annual_performance_df(df)

        assert res.performance[0] == df[1] / df[0] - 1

    def test_get_monthly_return_summary(self, instrument, instrument_price_factory):
        instrument_price_factory.create_batch(10, instrument=instrument)
        res, calculated_mask = instrument.get_monthly_return_summary()
        assert "performance" in res.columns
        assert "month" in res.columns
        assert "year" in res.columns

    def test_get_monthly_return_summary_dict(self, instrument, instrument_price_factory):
        instrument_price_factory.create_batch(10, instrument=instrument)
        res = instrument.get_monthly_return_summary_dict()
        for year in res.keys():
            for month in res[year].keys():
                assert month in calendar.month_abbr or month == "annual"
                assert "performance" in res[year][month]
                if month == "annual":
                    assert res[year][month]["performance"] is not None

    def test_get_prices_df(self, instrument, instrument_price_factory):
        price = instrument_price_factory.create(instrument=instrument)
        previous_price = instrument_price_factory.create(  # noqa
            date=price.date - timedelta(days=1), instrument=instrument
        )
        assert instrument.get_prices_df(from_date=price.date)[0] == float(price.net_value)

    @patch.object(Instrument, "get_prices_df")
    def test_build_benchmark_df(self, mock_get_prices_df, instrument, instrument_factory, instrument_price_factory):
        instrument_price_factory.create_batch(5, instrument=instrument)
        start_val = InstrumentPrice.objects.earliest("date").date
        end_val = InstrumentPrice.objects.latest("date").date
        tidx = pd.date_range(start=start_val, end=end_val, freq="D")
        mock_data = pd.Series(data=np.random.random_sample((tidx.shape[0],)), index=tidx)
        mock_get_prices_df.return_value = mock_data

        # Test without risk or benchmark assigned to instrument
        res = instrument.build_benchmark_df(end_val)
        assert res.empty

        # Assign benchmark and risk instrument
        RelatedInstrumentThroughModel.objects.create(
            instrument=instrument,
            related_instrument=instrument_factory.create(),
            is_primary=True,
            related_type=RelatedInstrumentThroughModel.RelatedTypeChoices.BENCHMARK,
        )
        RelatedInstrumentThroughModel.objects.create(
            instrument=instrument,
            is_primary=True,
            related_instrument=instrument_factory.create(),
            related_type=RelatedInstrumentThroughModel.RelatedTypeChoices.RISK_INSTRUMENT,
        )
        instrument.refresh_from_db()
        res = instrument.build_benchmark_df(end_val)
        assert res.rate.equals(mock_data)
        assert res.benchmark_net_value.equals(mock_data)
        assert "net_value" in res.columns

    @patch.object(InstrumentDataloaderProxy, "market_data")
    def test_save_prices_in_db(self, mock_fct, instrument, instrument_price_factory, currency_fx_rates_factory):
        # we check that the import also handle missing data with a forward fill
        from_date = date(2024, 1, 1)
        to_date = date(2024, 1, 3)
        currency_fx_rates_factory.create(currency=instrument.currency, date=from_date)
        currency_fx_rates_factory.create(currency=instrument.currency, date=from_date + timedelta(days=1))
        currency_fx_rates_factory.create(currency=instrument.currency, date=to_date)
        mock_fct.return_value = [
            {
                "valuation_date": from_date,
                "close": 1,
                "volume": 1,
                "market_capitalization": 1,
                "instrument_id": instrument.id,
            },
            {
                "valuation_date": to_date,
                "close": 2,
                "volume": 2,
                "market_capitalization": 2,
                "instrument_id": instrument.id,
            },
        ]
        instrument.import_prices(from_date, to_date + timedelta(days=1))
        assert InstrumentPrice.objects.get(
            instrument=instrument, date=from_date, calculated=False
        ).net_value == Decimal(1)
        assert InstrumentPrice.objects.get(
            instrument=instrument, date=from_date + timedelta(days=1), calculated=True
        ).net_value == Decimal(1)
        assert InstrumentPrice.objects.get(instrument=instrument, date=to_date, calculated=False).net_value == Decimal(
            2
        )

    def test_security_instrument_type(self, instrument_factory, instrument_type_factory):
        company_type = instrument_type_factory.create(is_security=False)
        security_type = instrument_type_factory.create(is_security=True)
        quote_type = instrument_type_factory.create(is_security=False)

        company = instrument_factory.create(instrument_type=company_type)
        security = instrument_factory.create(instrument_type=security_type, parent=company)
        quote = instrument_factory.create(instrument_type=quote_type, parent=security)

        assert company.security_instrument_type == company_type
        assert security.security_instrument_type == security_type
        assert quote.security_instrument_type == security_type

    def test_pre_save(self, instrument, instrument_factory):
        parent = instrument_factory.create()
        instrument.parent = parent
        instrument.save()

        instrument.name_repr = "test"
        instrument.save()
        parent.refresh_from_db()
        assert parent.name_repr == "test"

        parent.name_repr = "test2"
        parent.save()
        instrument.refresh_from_db()
        assert instrument.name_repr == "test2"
