import random
from datetime import date
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from faker import Faker

from wbfdm.analysis.financial_analysis.utils import FinancialAnalysisResult, Loader
from wbfdm.dataloaders.proxies import InstrumentDataloaderProxy
from wbfdm.enums import Financial, MarketData

fake = Faker()


@pytest.mark.django_db
class TestLoader:
    @pytest.fixture
    def data(self, value, year):
        """
        Data Fixture for the Loader class
        """
        year = int(year)
        data = []
        fake_key = fake.word()
        for year_delta in [0, 1]:
            for interim in range(1, 5):
                data.append(
                    {
                        "year": year + year_delta,
                        "interim": interim,
                        "period_type": "Q",
                        "period_end_date": date(year, interim * 3, 1),
                        "estimate": fake.pybool(),
                        "source": "dsws",
                        "financial": value,
                        "value": fake.pyfloat(),
                        fake_key: fake.word(),  # add noise key
                    }
                )
        # add a uncomplete year for year - 2
        data.append(
            {
                "year": year - 1,
                "interim": 1,
                "period_type": "Q",
                "period_end_date": date(year, 3, 1),
                "estimate": fake.pybool(),
                "source": "dsws",
                "financial": value,
                "value": fake.pyfloat(),
                fake_key: fake.word(),  # add noise key
            }
        )
        return data

    @pytest.fixture()
    def loader(self, instrument, value):
        return Loader(instrument, [Financial(value)])

    @pytest.mark.parametrize("value, year", [(random.choice(Financial.values()), fake.year())])
    @patch.object(InstrumentDataloaderProxy, "financials")
    def test_load(self, mock_fct, value, year, data, loader):
        # Test that the load method returnn the normalized dataframe

        mock_fct.return_value = data
        pd.testing.assert_frame_equal(loader.load(), loader._normalize_df(*loader._get_base_df()), check_exact=True)

    @pytest.mark.parametrize("value, year", [(random.choice(Financial.values()), fake.year())])
    @patch.object(InstrumentDataloaderProxy, "financials")
    def test_load_no_data(self, mock_fct, value, year, data, loader):
        # Test that the load method returnn the normalized dataframe

        mock_fct.return_value = []
        assert loader.load().empty

    @pytest.mark.parametrize("value, year", [(random.choice(Financial.values()), fake.year())])
    @patch.object(InstrumentDataloaderProxy, "financials")
    def test__get_base_df(self, mock_fct, value, year, data, loader):
        year = int(year)
        mock_fct.return_value = data
        df, source_df = loader._get_base_df()
        time_idx = df.index.droplevel([3, 4])
        # Test if the _get_base_df private method returned tuple have the same index
        pd.testing.assert_index_equal(time_idx, source_df.index)

        # Test if the _get_base_df private method returned dataframe index corresponds to the expected year and interim
        assert time_idx.tolist() == [
            (year - 1, 1, "Q"),
            (year, 1, "Q"),
            (year, 2, "Q"),
            (year, 3, "Q"),
            (year, 4, "Q"),
            (year + 1, 1, "Q"),
            (year + 1, 2, "Q"),
            (year + 1, 3, "Q"),
            (year + 1, 4, "Q"),
        ]
        assert source_df.unique() == "dsws"
        assert df.columns == [value]

    @pytest.mark.parametrize("market_value", [random.choice(MarketData.values())])
    @patch.object(InstrumentDataloaderProxy, "market_data")
    def test__annotate_market_data(self, mock_fct, instrument, market_value):
        # test if annotation market data works and are merged properly to the initial dataframe
        d1 = date(2021, 3, 30)
        d2 = date(2023, 3, 31)
        p1 = fake.pyfloat()
        p2 = fake.pyfloat()

        df = pd.DataFrame(
            [
                {
                    "year": d1.year,
                    "estimate": False,
                    "interim": 1,
                    "period_type": "P",
                    "period_end_date": d1,
                    "financial": "financial",
                    "value": fake.pyfloat(),
                },
                {
                    "year": d2.year,
                    "estimate": False,
                    "interim": 1,
                    "period_type": "P",
                    "period_end_date": d2,
                    "financial": "financial",
                    "value": fake.pyfloat(),
                },
            ]
        )
        df["period_end_date"] = pd.to_datetime(df["period_end_date"])
        df = df.pivot_table(
            index=["year", "interim", "period_type", "estimate", "period_end_date"],
            columns="financial",
            values="value",
        )
        mock_fct.return_value = [{"valuation_date": d1, market_value: p1}, {"valuation_date": d2, market_value: p2}]
        res = Loader(instrument, [])._annotate_market_data(df, [MarketData(market_value)])
        assert res.loc[(d1.year, 1, "P", False, "2021-03-30"), market_value] == p1
        assert res.loc[(d2.year, 1, "P", False, "2023-03-31"), market_value] == p2

    @pytest.mark.parametrize("statement_value", [random.choice(Financial.values())])
    @patch.object(InstrumentDataloaderProxy, "statements")
    def test__annotate_statement_data(self, mock_fct, instrument, statement_value):
        # test if annotation statement works and are merged properly to the initial dataframe

        d1 = date(2021, 3, 30)
        d2 = date(2023, 3, 31)
        value = fake.pyfloat()

        df = pd.DataFrame(
            [
                {
                    "year": d1.year,
                    "estimate": False,
                    "interim": 1,
                    "period_type": "P",
                    "period_end_date": d1,
                    "financial": "base",
                    "value": fake.pyfloat(),
                },
                {
                    "year": d2.year,
                    "estimate": False,
                    "interim": 1,
                    "period_type": "P",
                    "period_end_date": d2,
                    "financial": "base",
                    "value": fake.pyfloat(),
                },
            ]
        )
        df["period_end_date"] = pd.to_datetime(df["period_end_date"])
        df = df.pivot_table(
            index=["year", "interim", "period_type", "estimate", "period_end_date"],
            columns="financial",
            values="value",
        )
        mock_fct.return_value = [
            {
                "year": d1.year,
                "estimate": False,
                "interim": 1,
                "period_type": "P",
                "period_end_date": d1,
                "financial": statement_value,
                "value": value,
            }
        ]

        res = Loader(instrument, [])._annotate_statement_data(df, [Financial(statement_value)])
        assert res.loc[(d1.year, 1, "P", False, "2021-03-30"), statement_value] == value
        assert np.isnan(res.loc[(d2.year, 1, "P", False, "2023-03-31"), statement_value])

    def test__normalize_df(self, instrument):
        d1 = date(2021, 3, 30)
        df = pd.DataFrame(
            [
                {
                    "source": "dsws",
                    "year": d1.year,
                    "estimate": False,
                    "interim": 1,
                    "period_end_date": d1,
                    "period_type": "S",
                    "financial": "base",
                    "value": fake.pyfloat(),
                },
                {
                    "source": "dsws",
                    "year": d1.year,
                    "estimate": False,
                    "interim": 2,
                    "period_end_date": d1,
                    "period_type": "S",
                    "financial": "base",
                    "value": fake.pyfloat(),
                },
            ]
        )
        source_df = df.source
        df["period_end_date"] = pd.to_datetime(df["period_end_date"])
        df = df.pivot_table(
            index=["year", "interim", "period_type", "estimate", "period_end_date"],
            columns="financial",
            values="value",
        )
        res = Loader(instrument, [])._normalize_df(df, source_df)
        # Test if normalize appends the missing "yearly" row and convert the interim into their verbose representation
        assert res.index.tolist() == [
            (d1.year, "Y"),
            (d1.year, "S1"),
            (d1.year, "S2"),
        ]  # We test that the missing yearly row is reindexed
        assert np.isnan(res.loc[(d1.year, "Y"), "base"])  # check that the extrapolated data is nan

    def test__normalize_df_with_duplicates(self, instrument):
        # we test if normalize detects the duplicates, remove it by taking the first and add the interim into the errors list
        d1 = date(2021, 3, 30)
        v1 = fake.pyfloat()
        v2 = fake.pyfloat()
        df = pd.DataFrame(
            [
                {
                    "source": "dsws",
                    "year": d1.year,
                    "estimate": False,
                    "interim": 1,
                    "period_end_date": d1,
                    "financial": "base",
                    "period_type": "P",
                    "value": v1,
                },
                {
                    "source": "dsws",
                    "year": d1.year,
                    "estimate": False,
                    "interim": 1,
                    "period_end_date": date(2021, 1, 30),
                    "financial": "base",
                    "period_type": "P",
                    "value": v2,
                },
            ]
        )
        source_df = df[["year", "interim", "source"]].groupby(["year", "interim"]).first().source
        df["period_end_date"] = pd.to_datetime(df["period_end_date"])
        df = df.pivot_table(
            index=["year", "interim", "period_type", "estimate", "period_end_date"],
            columns="financial",
            values="value",
        )
        loader = Loader(instrument, [])
        res = loader._normalize_df(df, source_df)
        assert res.index.tolist() == [(d1.year, "Y"), (d1.year, "P1")]
        assert (
            res.loc[(d1.year, "P1"), "base"] == v2
        )  # check that the retained value is the first one (with ordered index)
        assert loader.errors["duplicated_interims"] == [f"{d1.year} Interim P1"]


class TestFinancialAnalysisResult:
    @pytest.fixture()
    def df(self, year, value):
        df = pd.DataFrame(
            [
                {
                    "year": year,
                    "estimate": False,
                    "interim": "P1",
                    "period_end_date": date(int(year), 3, 1),
                    "financial": value,
                    "value": fake.pyfloat(),
                },
                {
                    "year": year,
                    "estimate": True,
                    "interim": "Y",
                    "period_end_date": date(int(year), 3, 1),
                    "financial": value,
                    "value": fake.pyfloat(),
                },
            ]
        )
        df = df.pivot_table(
            index=["year", "interim", "estimate", "period_end_date"], columns="financial", values="value"
        )
        return df.reset_index(level=[2, 3])

    @pytest.mark.parametrize("value, year", [(random.choice(Financial.values()), fake.year())])
    def test_class(self, value, year, df):
        """
        Test the basic esthetic transform (Transposing + group key addition + convertion of multi index to representation
        """
        res = FinancialAnalysisResult(df)
        assert res.formatted_df.loc[0, f"{year}-P1"] == df.loc[(year, "P1"), value]
        assert res.formatted_df.loc[0, f"{year}-Y"] == df.loc[(year, "Y"), value]
        assert res.formatted_df.loc[0, "financial"] == Financial.name_mapping()[value]
        assert res.formatted_df.loc[0, "_group_key"] == value
        assert res.estimated_mapping == {f"{year}-P1": False, f"{year}-Y": True}
