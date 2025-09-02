from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pandas as pd
import pytest
from django.contrib.contenttypes.models import ContentType
from faker import Faker
from pandas.tseries.offsets import BDay

from wbfdm.models import Instrument, RelatedInstrumentThroughModel

fake = Faker()


@pytest.mark.django_db
class TestInstrumentPerformanceMetricBackend:
    @patch("wbfdm.contrib.metric.backends.performances.get_today")
    def test_compute_metrics(self, mock_fct, weekday, instrument, instrument_price_factory):
        from wbfdm.contrib.metric.backends.performances import (  # we import locally to avoid database access pytest error
            InstrumentPerformanceMetricBackend,
        )

        # mock_fct.return_value = weekday # return weekday as date.today
        backend = InstrumentPerformanceMetricBackend(weekday)

        price_intraday = instrument_price_factory(  # noqa
            instrument=instrument, calculated=False, date=(weekday + BDay(1)).date()
        )
        price_today = instrument_price_factory.create(instrument=instrument, calculated=False, date=weekday)
        price_yesterday = instrument_price_factory.create(
            instrument=instrument, calculated=False, date=weekday - BDay(1)
        )
        price_last_week = instrument_price_factory.create(
            instrument=instrument, calculated=False, date=(weekday - timedelta(days=7)) - BDay(0)
        )
        price_last_month = instrument_price_factory.create(
            instrument=instrument, calculated=False, date=(weekday - timedelta(days=30)) - BDay(1)
        )
        price_last_quarter = instrument_price_factory.create(
            instrument=instrument, calculated=False, date=(weekday - timedelta(days=120)) - BDay(1)
        )
        price_last_year = instrument_price_factory.create(
            instrument=instrument, calculated=False, date=(weekday - timedelta(days=365)) - BDay(1)
        )
        price_end_last_year = instrument_price_factory.create(
            instrument=instrument, calculated=False, date=weekday - pd.tseries.offsets.BYearEnd(1)
        )
        price_inception = instrument_price_factory.create(
            instrument=instrument, calculated=False, date=price_last_year.date - BDay(1)
        )

        instrument_price_factory.create(
            instrument=instrument, calculated=True, date=price_inception.date - BDay(1)
        )  # add noise
        instrument.inception_date = price_inception.date.date()
        instrument.save()
        instrument.update_last_valuation_date()
        base_metric = next(backend.compute_metrics(instrument))

        # Check base metric metadata
        assert base_metric.date is None
        assert base_metric.basket_id == instrument.id
        assert base_metric.basket_content_type_id == ContentType.objects.get_for_model(Instrument).id
        assert base_metric.key == "performance"
        assert base_metric.instrument_id is None

        assert base_metric.metrics["is_estimated"] is False
        assert base_metric.metrics["daily"] == pytest.approx(
            float(price_today.net_value / price_yesterday.net_value - Decimal(1)), abs=1e-5
        )
        assert base_metric.metrics["weekly"] == pytest.approx(
            float(price_today.net_value / price_last_week.net_value - Decimal(1)), abs=1e-5
        )
        assert base_metric.metrics["monthly"] == pytest.approx(
            float(price_today.net_value / price_last_month.net_value - Decimal(1)), abs=1e-5
        )
        assert base_metric.metrics["quarterly"] == pytest.approx(
            float(price_today.net_value / price_last_quarter.net_value - Decimal(1)), abs=1e-5
        )

        assert base_metric.metrics["yearly"] == pytest.approx(
            float(price_today.net_value / price_last_year.net_value - Decimal(1)), abs=1e-5
        )

        assert base_metric.metrics["year_to_date"] == pytest.approx(
            float(price_today.net_value / price_end_last_year.net_value - Decimal(1)), abs=1e-5
        )
        assert base_metric.metrics["inception"] == pytest.approx(
            float(price_today.net_value / price_inception.net_value - Decimal(1)), abs=1e-5
        )

    def test_compute_metrics_estimated(self, weekday, instrument, instrument_price_factory):
        from wbfdm.contrib.metric.backends.performances import (  # we import locally to avoid database access pytest error
            InstrumentPerformanceMetricBackend,
        )

        backend = InstrumentPerformanceMetricBackend(weekday)

        price_today = instrument_price_factory.create(instrument=instrument, calculated=True, date=weekday)
        price_yesterday = instrument_price_factory.create(
            instrument=instrument, calculated=False, date=weekday - BDay(1)
        )
        instrument.inception_date = price_yesterday.date.date()
        instrument.save()
        instrument.update_last_valuation_date()
        base_metric = next(backend.compute_metrics(instrument))

        assert base_metric.metrics["is_estimated"] is True
        assert base_metric.metrics["daily"] == pytest.approx(
            float(price_today.net_value / price_yesterday.net_value - Decimal(1)), abs=1e-5
        )

    def test_compute_metrics_with_peers(self, weekday, instrument_factory, instrument_price_factory):
        from wbfdm.contrib.metric.backends.performances import (  # we import locally to avoid database access pytest error
            InstrumentPerformanceMetricBackend,
        )

        instrument = instrument_factory.create()
        peer_1 = instrument_factory.create()
        RelatedInstrumentThroughModel.objects.create(
            related_type="PEER", instrument=instrument, related_instrument=peer_1
        )
        peer_2 = instrument_factory.create()
        RelatedInstrumentThroughModel.objects.create(
            related_type="PEER", instrument=instrument, related_instrument=peer_2
        )

        backend = InstrumentPerformanceMetricBackend(weekday)

        price_today = instrument_price_factory.create(instrument=instrument, calculated=False, date=weekday)
        price_yesterday = instrument_price_factory.create(
            instrument=instrument, calculated=False, date=weekday - BDay(1)
        )
        instrument.inception_date = price_yesterday.date.date()
        instrument.save()
        peer_1_price_today = instrument_price_factory.create(instrument=peer_1, calculated=False, date=weekday)
        peer_1_price_yesterday = instrument_price_factory.create(
            instrument=peer_1, calculated=False, date=weekday - BDay(1)
        )
        peer_1.inception_date = peer_1_price_yesterday.date.date()
        peer_1.save()
        peer_2_price_today = instrument_price_factory.create(instrument=peer_2, calculated=False, date=weekday)
        peer_2_price_yesterday = instrument_price_factory.create(
            instrument=peer_2, calculated=False, date=weekday - BDay(1)
        )
        peer_2.inception_date = peer_2_price_yesterday.date.date()
        peer_2.save()
        instrument.update_last_valuation_date()
        peer_1.update_last_valuation_date()
        peer_2.update_last_valuation_date()
        base_metric = next(backend.compute_metrics(instrument))
        daily_instrument_perf = float(price_today.net_value / price_yesterday.net_value - Decimal(1))
        assert base_metric.metrics["daily"] == pytest.approx(daily_instrument_perf, abs=1e-5)
        daily_peer_1_perf = float(peer_1_price_today.net_value / peer_1_price_yesterday.net_value - Decimal(1))
        daily_peer_2_perf = float(peer_2_price_today.net_value / peer_2_price_yesterday.net_value - Decimal(1))
        avg_daily_peer_perf = (daily_peer_1_perf + daily_peer_2_perf) / 2
        r = daily_instrument_perf - avg_daily_peer_perf
        assert base_metric.metrics["peer_daily"] == pytest.approx(r, abs=0.00001)
