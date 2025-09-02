import numpy as np
import pandas as pd
import pytest
from faker import Faker
from wbcore.contrib.currency.factories import CurrencyFXRatesFactory
from wbcore.contrib.currency.models import CurrencyFXRates

from wbfdm.analysis.esg.enums import ESGAggregation
from wbfdm.analysis.esg.esg_analysis import DataLoader

fake = Faker()

WEIGHTS = [0.15, 0.05, 0.2, 0.1, 0.5]
ENTERPRISE_VALUE_INCLUDED_CASH = [1e6, 2e6, 3e6, 4e6, 1e6]
CURRENT_VALUE_INVESTMENT_FACTOR = [1.0, 1.0, 1.0, 1.2, 0.2]


@pytest.mark.django_db
class TestESGDataLoader:
    @pytest.fixture
    def dataloader(self, weekday):
        index = [1, 2, 3, 4, 5]

        weight = pd.Series(WEIGHTS, index=index)
        esg_data = pd.Series(np.random.randint(1, 100, size=4), index=[1, 2, 3, 4])  # we remove one data point
        total_value_fx_usd = pd.Series(np.random.randint(1, 100, size=5))  # we remove one data point
        CurrencyFXRatesFactory.create(currency__key="EUR", date=weekday)

        dataloader = DataLoader(weight, esg_data, weekday, total_value_fx_usd=total_value_fx_usd)
        dataloader.__dict__["enterprise_value_included_cash"] = pd.Series(ENTERPRISE_VALUE_INCLUDED_CASH, index=index)
        dataloader.__dict__["current_value_investment_factor"] = pd.Series(
            CURRENT_VALUE_INVESTMENT_FACTOR, index=index
        )
        dataloader.__dict__["nace_section_code"] = pd.Series(["C", "C", "J", "M", "M"], index=index)
        return dataloader

    def test_dataloader(self, dataloader):
        assert dataloader.weights_in_coverage.to_dict() == {1: 0.15, 2: 0.05, 3: 0.2, 4: 0.1}

    def test_get_percentage_sum(self, dataloader):
        dataloader.esg_data = pd.Series(["Yes", "No Evidence", "No", "No", "No"], index=[1, 2, 3, 4, 5])
        res = dataloader._get_percentage_sum("No Evidence")
        assert res.tolist() == [0.0, 0.05, 0.0, 0.0]

    def test_get_weighted_avg_normalized(self, dataloader):
        res = dataloader._get_weighted_avg_normalized()
        log = dataloader.intermediary_logs[0]

        # ensure the intermediary log data is set properly
        assert log.series.name == "weights_normalized"
        assert log.series.to_dict() == {1: 0.3, 2: 0.1, 3: 0.4, 4: 0.2}
        assert res.to_dict() == {
            1: 0.3 * dataloader.esg_data.iloc[0],
            2: 0.1 * dataloader.esg_data.iloc[1],
            3: 0.4 * dataloader.esg_data.iloc[2],
            4: 0.2 * dataloader.esg_data.iloc[3],
        }

    def test_get_weighted_avg_normalized_per_category(self, dataloader):
        res = dataloader._get_weighted_avg_normalized_per_category()
        intermediary_logs = list(filter(lambda x: not x.series.empty, dataloader.intermediary_logs))
        log_c = intermediary_logs[0]
        log_j = intermediary_logs[1]
        log_m = intermediary_logs[2]
        weights_normalized = [
            0.15 / (0.15 + 0.05),
            0.05 / (0.15 + 0.05),
            0.2 / 0.2,
            0.1 / (0.1 + 0.5),
            0.5 / (0.1 + 0.5),
        ]
        # ensure the intermediary log data is set properly
        assert log_c.series.name == "weights_normalized_sector_c"
        assert log_c.series.to_dict() == {
            1: weights_normalized[0],
            2: weights_normalized[1],
            # 3: weights_normalized[2],
            # 4: weights_normalized[3],
            #             5: weights_normalized[4],
        }
        assert log_j.series.name == "weights_normalized_sector_j"
        assert log_j.series.to_dict() == {
            3: weights_normalized[2],
        }
        assert log_m.series.name == "weights_normalized_sector_m"
        assert log_m.series.to_dict() == {
            4: weights_normalized[3],
            5: weights_normalized[4],
        }
        assert res.to_dict() == {
            1: weights_normalized[0] * dataloader.esg_data.iloc[0],
            2: weights_normalized[1] * dataloader.esg_data.iloc[1],
            3: weights_normalized[2] * dataloader.esg_data.iloc[2],
            4: weights_normalized[3] * dataloader.esg_data.iloc[3],
        }

    def test_get_investor_allocation(self, dataloader):
        exposure = pd.Series(np.random.rand(5), index=dataloader.weights.index)
        res = dataloader._get_investor_allocation(exposure)
        fx_rate = CurrencyFXRates.objects.get(currency__key="EUR", date=dataloader.val_date)
        exposure_eur = exposure * float(fx_rate.value)

        assert dataloader.intermediary_logs[0].series.to_dict() == exposure.to_dict()
        assert (
            dataloader.intermediary_logs[1].series.to_dict() == exposure_eur.to_dict()
        )  # exposure converted into eur

        exposure_with_cvi = [exposure_eur.iloc[i] * CURRENT_VALUE_INVESTMENT_FACTOR[i] for i in range(5)]
        assert dataloader.intermediary_logs[2].series.tolist() == exposure_with_cvi

        rebase_factor = sum(exposure_with_cvi[:4]) / sum(exposure_with_cvi)

        exposure_normalized = [exposure_with_cvi[i] / rebase_factor for i in range(4)]
        assert dataloader.intermediary_logs[3].series.tolist() == exposure_normalized

        attribution_factor = [exposure_normalized[i] / ENTERPRISE_VALUE_INCLUDED_CASH[i] for i in range(4)]
        assert dataloader.intermediary_logs[4].series.dropna().tolist() == attribution_factor

        assert res.to_dict() == {
            1: dataloader.esg_data.iloc[0] * attribution_factor[0],
            2: dataloader.esg_data.iloc[1] * attribution_factor[1],
            3: dataloader.esg_data.iloc[2] * attribution_factor[2],
            4: dataloader.esg_data.iloc[3] * attribution_factor[3],
        }

    def test_compute_percentage_sum(self, dataloader):
        pd.testing.assert_series_equal(
            dataloader.compute(ESGAggregation.FOSSIL_FUEL_EXPOSURE),
            dataloader._get_percentage_sum("Yes"),
            check_exact=True,
        )

    def test_compute_weighted_avg_normalized(self, dataloader):
        res = dataloader.compute(ESGAggregation.GHG_INTENSITY_OF_COMPAGNIES)
        assert res.empty is not None
        pd.testing.assert_series_equal(
            dataloader.compute(ESGAggregation.GHG_INTENSITY_OF_COMPAGNIES),
            dataloader._get_weighted_avg_normalized(),
            check_exact=True,
        )

    def test_compute_weighted_avg_normalized_per_category(self, dataloader):
        res = dataloader.compute(ESGAggregation.ENERGY_CONSUMPTION_INTENSITY_PER_SECTOR)
        assert res.empty is not None
        pd.testing.assert_series_equal(res, dataloader._get_weighted_avg_normalized_per_category(), check_exact=True)

    def test_compute_investor_allocation(self, dataloader):
        res = dataloader.compute(ESGAggregation.GHG_EMISSIONS_SCOPE_1)
        assert res.empty is not None
        pd.testing.assert_series_equal(
            res, dataloader._get_investor_allocation(dataloader.total_value_fx_usd), check_exact=True
        )

        res = dataloader.compute(ESGAggregation.GHG_EMISSIONS_SCOPE_1)
        assert res.empty is not None
        pd.testing.assert_series_equal(
            dataloader.compute(ESGAggregation.EMISSIONS_TO_WATER),
            dataloader._get_investor_allocation_per_million(dataloader.weights * 1000000),
            check_exact=True,
        )
