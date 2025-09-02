from decimal import Decimal
from unittest.mock import patch

import pytest
from faker import Faker

from wbfdm.dataloaders.proxies import InstrumentDataloaderProxy

fake = Faker()


@pytest.mark.django_db
class TestInstrumentFinancialStatisticsMetricBackend:
    @patch.object(InstrumentDataloaderProxy, "financials")
    def test_default_daily_statistics(self, mock_fct, weekday, instrument, instrument_price_factory):
        from wbfdm.contrib.metric.backends.statistics import (  # we import locally to avoid database access pytest error
            InstrumentFinancialStatisticsMetricBackend,
        )

        backend = InstrumentFinancialStatisticsMetricBackend(weekday)

        revenue_y_1 = fake.pyfloat()
        revenue_y0 = fake.pyfloat()
        revenue_y1 = fake.pyfloat()
        market_capitalization = fake.pyfloat()
        price = Decimal(150)
        volume_50d = fake.pyfloat()
        instrument_price_factory.create(
            instrument=instrument,
            calculated=False,
            date=weekday,
            net_value=price,
            volume_50d=volume_50d,
            market_capitalization=market_capitalization,
        )
        instrument.update_last_valuation_date()
        mock_fct.return_value = [
            {"year": weekday.year - 1, "value": revenue_y_1, "instrument_id": instrument.id},
            {"year": weekday.year, "value": revenue_y0, "instrument_id": instrument.id},
            {"year": weekday.year + 1, "value": revenue_y1, "instrument_id": instrument.id},
        ]
        metrics = next(backend.compute_metrics(instrument)).metrics

        assert metrics["revenue_y_1"] == revenue_y_1
        assert metrics["revenue_y0"] == revenue_y0
        assert metrics["revenue_y1"] == revenue_y1
        assert metrics["market_capitalization"] == market_capitalization
        assert metrics["price"] == price
        assert metrics["volume_50d"] == volume_50d
