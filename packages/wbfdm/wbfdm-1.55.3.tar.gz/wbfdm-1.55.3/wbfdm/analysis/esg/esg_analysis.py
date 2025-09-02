from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd
from django.utils.functional import cached_property
from wbcore.contrib.currency.models import Currency, CurrencyFXRates

from wbfdm.enums import ESG
from wbfdm.models import Instrument

from .enums import AggregationMethod, ESGAggregation
from .utils import get_esg_df


@dataclass
class Log:
    series: pd.Series
    label: str
    is_percent: bool = False
    precision: int = 4
    group: str | None = None


class DataLoader:
    def __init__(
        self, weights: pd.Series, esg_data: pd.Series, val_date: date, total_value_fx_usd: pd.Series | None = None
    ):
        self.weights = weights
        self.val_date = val_date
        try:
            self.fx_rate_usd_to_eur = float(
                CurrencyFXRates.objects.get(currency=Currency.objects.get(key="EUR"), date=val_date).value
            )
        except (CurrencyFXRates.DoesNotExist, Currency.DoesNotExist):
            self.fx_rate_usd_to_eur = 1.0
        self.total_value_fx_usd = total_value_fx_usd
        self.instruments = Instrument.objects.filter(id__in=self.weights.index)
        self.empty_series = pd.Series(1.0, index=weights.index, dtype="float64")
        self.esg_data = esg_data
        self.weights_in_coverage = (
            self.weights.loc[~esg_data.reindex(self.weights.index, fill_value=None).isnull()]
        ).rename("weights_in_coverage")
        self.intermediary_logs: list[Log] = []
        self.extra_esg_data_logs: list[Log] = []

    @cached_property
    def enterprise_value_included_cash(self) -> pd.Series:
        data = get_esg_df(self.instruments, ESG.EVIC_EUR) * 1000000
        self.extra_esg_data_logs.append(Log(series=data.rename("enterprise_value_included_cash"), label="EVIC (EUR)"))
        return data

    @cached_property
    def current_value_investment_factor(self) -> pd.Series:
        data = get_esg_df(self.instruments, ESG.CVI_FACTOR)
        data = data.reindex(self.weights.index, fill_value=1.0)
        self.extra_esg_data_logs.append(Log(series=data.rename("current_value_investment_factor"), label="CVI Factor"))
        return data

    @cached_property
    def nace_section_code(self) -> pd.Series:
        data = get_esg_df(self.instruments, ESG.NACE_SECTION_CODE)
        self.extra_esg_data_logs.append(Log(series=data.rename("nace_section_code"), label="NACE_SECTION_CODE"))
        return data

    def _get_percentage_sum(self, mask_value: str) -> pd.Series:
        df = self.weights_in_coverage.copy()
        df.loc[self.esg_data != mask_value] = 0.0
        return df.dropna()

    def _get_weighted_avg_normalized(self) -> pd.Series:
        weights_normalized = self.weights_in_coverage / self.weights_in_coverage.sum()
        self.intermediary_logs.append(
            Log(
                series=weights_normalized.rename("weights_normalized"),
                label="Rebased Weights",
                is_percent=True,
                precision=2,
            )
        )
        return (weights_normalized * self.esg_data).dropna()

    def _get_weighted_avg_normalized_per_category(self) -> pd.Series:
        df = pd.concat([self.weights, self.nace_section_code], keys=["weighting", "nace_section_code"], axis=1)
        sector_codes = ["C", "D", "F", "G", "J", "K", "M", "N", "Q", "S"]
        res = pd.Series(np.nan, index=df.index)
        rebased_weights_logs_per_sector = []
        weighted_average_logs_per_sector = []
        for sector_code in sector_codes:
            try:
                dff = df[df["nace_section_code"] == sector_code]
                weights_normalized_per_sector = dff["weighting"] / dff["weighting"].sum()
            except (TypeError, KeyError):
                weights_normalized_per_sector = pd.Series(np.nan, index=self.weights.index)

            rebased_weights_logs_per_sector.append(
                Log(
                    series=weights_normalized_per_sector.rename(f"weights_normalized_sector_{sector_code.lower()}"),
                    label=sector_code,
                    group="Weight rebased per NACE sector",
                    is_percent=True,
                    precision=2,
                )
            )
            weighted_average_per_sector = weights_normalized_per_sector * self.esg_data
            weighted_average_logs_per_sector.append(
                Log(
                    series=weighted_average_per_sector.rename(f"weighted_average_sector_{sector_code.lower()}"),
                    label=sector_code,
                    group="Weight Average per NACE sector",
                    precision=4,
                )
            )

            res[weighted_average_per_sector.dropna().index] = weighted_average_per_sector.dropna()
        self.intermediary_logs.extend(rebased_weights_logs_per_sector)
        self.intermediary_logs.extend(weighted_average_logs_per_sector)
        return res.dropna()

    def _get_investor_allocation(self, exposure: pd.Series) -> pd.Series:
        exposure_eur = exposure * self.fx_rate_usd_to_eur
        self.intermediary_logs.append(Log(series=exposure.rename("exposure"), label="Exposure"))
        self.intermediary_logs.append(Log(series=exposure_eur.rename("exposure_eur"), label="Exposure (EUR)"))

        evic_eur = self.enterprise_value_included_cash
        cvi_factor = self.current_value_investment_factor

        exposure_with_cvi = exposure_eur * cvi_factor
        self.intermediary_logs.append(
            Log(series=exposure_with_cvi.rename("exposure_with_cvi"), label="Exposure With CVI")
        )
        try:
            rebase_factor = exposure_with_cvi.loc[self.weights_in_coverage.index].sum() / exposure_with_cvi.sum()
            exposure_with_cvi_normalized = exposure_with_cvi.loc[self.weights_in_coverage.index] / rebase_factor
        except ZeroDivisionError:
            exposure_with_cvi_normalized = exposure_with_cvi

        self.intermediary_logs.append(
            Log(
                series=exposure_with_cvi_normalized.rename("exposure_with_cvi_normalized"),
                label="Exposure With CVI (Normalized)",
            )
        )

        attribution_factor = exposure_with_cvi_normalized / evic_eur
        self.intermediary_logs.append(
            Log(series=attribution_factor.rename("attribution_factor"), label="Attribution Factor", is_percent=True)
        )

        return (self.esg_data * attribution_factor).dropna()

    def _get_investor_allocation_per_million(self, exposure: pd.Series) -> pd.Series:
        self.intermediary_logs.append(Log(series=exposure.rename("exposure"), label="Exposure"))

        evic_eur = self.enterprise_value_included_cash
        cvi_factor = self.current_value_investment_factor

        exposure_with_cvi = exposure * cvi_factor
        self.intermediary_logs.append(
            Log(series=exposure_with_cvi.rename("exposure_with_cvi"), label="Exposure With CVI")
        )
        try:
            rebase_factor = exposure_with_cvi.loc[self.weights_in_coverage.index].sum() / exposure_with_cvi.sum()
            exposure_with_cvi_normalized = exposure_with_cvi.loc[self.weights_in_coverage.index] / rebase_factor
        except ZeroDivisionError:
            exposure_with_cvi_normalized = exposure_with_cvi

        self.intermediary_logs.append(
            Log(
                series=exposure_with_cvi_normalized.rename("exposure_with_cvi_normalized"),
                label="Exposure With CVI (Normalized)",
            )
        )

        weights_normalized = exposure_with_cvi_normalized / exposure_with_cvi_normalized.sum()
        self.intermediary_logs.append(
            Log(
                series=weights_normalized.rename("weights_normalized"),
                label="Weight based on CVI",
                is_percent=True,
                precision=2,
            )
        )
        cvi_based_exposure_per_million = weights_normalized * 1e6
        self.intermediary_logs.append(
            Log(
                series=cvi_based_exposure_per_million.rename("cvi_based_exposure_per_million"),
                label="CVI-based exposure for EUR 1mn",
            )
        )

        attribution_factor = cvi_based_exposure_per_million / evic_eur
        self.intermediary_logs.append(
            Log(series=attribution_factor.rename("attribution_factor"), label="Attribution Factor", is_percent=True)
        )

        return (self.esg_data * attribution_factor).dropna()

    def compute(self, esg_aggregation: ESGAggregation):
        aggregation_method = esg_aggregation.get_aggregation()
        if aggregation_method == AggregationMethod.PERCENTAGE_SUM:
            # we need to apply a mask
            if esg_aggregation in [ESGAggregation.LACK_OF_PROCESS_AND_COMPLIANCE_OF_UN_PRINCIPLES]:
                mask = "No Evidence"
            else:
                mask = "Yes"

            return self._get_percentage_sum(mask)
        if aggregation_method == AggregationMethod.WEIGHTED_AVG_NORMALIZED:
            return self._get_weighted_avg_normalized()
        if aggregation_method == AggregationMethod.WEIGHTED_AVG_CATEGORY_NORMALIZED:
            return self._get_weighted_avg_normalized_per_category()
        if aggregation_method == AggregationMethod.INVESTOR_ALLOCATION:
            return self._get_investor_allocation(self.total_value_fx_usd)
        if aggregation_method == AggregationMethod.INVESTOR_ALLOCATION_PER_MILLION:
            return self._get_investor_allocation_per_million(self.weights * 1000000)
        else:
            raise ValueError("Aggregation Method not supported")
