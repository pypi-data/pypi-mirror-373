from wbcore.utils.enum import ChoiceEnum

from wbfdm.enums import ESG

from .utils import get_esg_df


class AggregationMethod(ChoiceEnum):
    PERCENTAGE_SUM = "Percentage Sum"
    WEIGHTED_AVG_NORMALIZED = "Weighted Avg Normalized"
    WEIGHTED_AVG_CATEGORY_NORMALIZED = "Weighted Avg Weighted (Per Category)"
    INVESTOR_ALLOCATION = "Investor Allocation"
    INVESTOR_ALLOCATION_PER_MILLION = "Investor Allocation Per Million"


class ESGAggregation(ChoiceEnum):
    GHG_EMISSIONS_SCOPE_1 = "GHG Emissions Scope 1"
    GHG_EMISSIONS_SCOPE_2 = "GHG Emissions Scope 2"
    GHG_EMISSIONS_SCOPE_3 = "GHG Emissions Scope 3"
    GHG_EMISSIONS_SCOPE_123 = "GHG Emissions Scope 123"
    CARBON_FOOTPRINT = "Carbon Footprint"
    GHG_INTENSITY_OF_COMPAGNIES = "GHG intensity of investee companies"
    FOSSIL_FUEL_EXPOSURE = "Exposure to companies active in the fossil fuel sector"
    SHARE_OF_NONRENEWABLE_ENERGY = "Share of nonrenewable energy consumption and production"
    ENERGY_CONSUMPTION_INTENSITY = "Energy consumption intensity"
    ENERGY_CONSUMPTION_INTENSITY_PER_SECTOR = "Energy consumption intensity per high-impact climate sector"
    ACTIVITY_NEGATIVELY_IMPACTING_BIODIVERSITY = "Activities negatively affecting biodiversity sensitive areas"
    EMISSIONS_TO_WATER = "Emissions to water"
    HAZARDOUS_WASTE_RATIO = "Hazardous Waste Ratio"
    VIOLATION_OF_UN_PRINCIPLES = "Violations of UN Global Compact principles and Organisation for Economic Cooperation and Development (OECD) Guidelines for Multinational Enterprises"
    LACK_OF_PROCESS_AND_COMPLIANCE_OF_UN_PRINCIPLES = "Lack of processes and compliance mechanisms to monitor compliance with UN Global Compact principles and OECD Guidelines for Multinational Enterprises"
    UNADJUSTED_GENDER_PAY_GAP = "Unadjusted gender pay gap"
    BOARD_GENDER_DIVERSITY = "Board Gender Diversity"
    CONTROVERSIAL_WEAPONS_EXPOSURE = "Exposure to controversial weapons (antipersonnel mines, cluster munitions, chemical weapons and biological weapons)"

    def get_aggregation(self) -> AggregationMethod:
        return {
            "GHG_EMISSIONS_SCOPE_1": AggregationMethod.INVESTOR_ALLOCATION,
            "GHG_EMISSIONS_SCOPE_2": AggregationMethod.INVESTOR_ALLOCATION,
            "GHG_EMISSIONS_SCOPE_3": AggregationMethod.INVESTOR_ALLOCATION,
            "GHG_EMISSIONS_SCOPE_123": AggregationMethod.INVESTOR_ALLOCATION,
            "CARBON_FOOTPRINT": AggregationMethod.INVESTOR_ALLOCATION_PER_MILLION,
            "GHG_INTENSITY_OF_COMPAGNIES": AggregationMethod.WEIGHTED_AVG_NORMALIZED,
            "FOSSIL_FUEL_EXPOSURE": AggregationMethod.PERCENTAGE_SUM,
            "SHARE_OF_NONRENEWABLE_ENERGY": AggregationMethod.WEIGHTED_AVG_NORMALIZED,
            "ENERGY_CONSUMPTION_INTENSITY": AggregationMethod.WEIGHTED_AVG_NORMALIZED,
            "ENERGY_CONSUMPTION_INTENSITY_PER_SECTOR": AggregationMethod.WEIGHTED_AVG_CATEGORY_NORMALIZED,
            "ACTIVITY_NEGATIVELY_IMPACTING_BIODIVERSITY": AggregationMethod.PERCENTAGE_SUM,
            "EMISSIONS_TO_WATER": AggregationMethod.INVESTOR_ALLOCATION_PER_MILLION,
            "HAZARDOUS_WASTE_RATIO": AggregationMethod.INVESTOR_ALLOCATION_PER_MILLION,
            "VIOLATION_OF_UN_PRINCIPLES": AggregationMethod.PERCENTAGE_SUM,
            "LACK_OF_PROCESS_AND_COMPLIANCE_OF_UN_PRINCIPLES": AggregationMethod.PERCENTAGE_SUM,
            "UNADJUSTED_GENDER_PAY_GAP": AggregationMethod.WEIGHTED_AVG_NORMALIZED,
            "BOARD_GENDER_DIVERSITY": AggregationMethod.WEIGHTED_AVG_NORMALIZED,
            "CONTROVERSIAL_WEAPONS_EXPOSURE": AggregationMethod.PERCENTAGE_SUM,
        }.get(self.name, AggregationMethod.WEIGHTED_AVG_NORMALIZED)  # default to weighted avg normalized

    def get_esg_code(self) -> ESG:
        return {
            "GHG_EMISSIONS_SCOPE_1": ESG.CARBON_EMISSIONS_SCOPE_1,
            "GHG_EMISSIONS_SCOPE_2": ESG.CARBON_EMISSIONS_SCOPE_2,
            "GHG_EMISSIONS_SCOPE_3": ESG.CARBON_EMISSIONS_SCOPE_3_TOTAL,
            "GHG_EMISSIONS_SCOPE_123": ESG.CARBON_EMISSIONS_SCOPE123,
            "CARBON_FOOTPRINT": ESG.CARBON_EMISSIONS_SCOPE123,
            "GHG_INTENSITY_OF_COMPAGNIES": ESG.CARBON_EMISSIONS_SALES_EUR_SCOPE_ALL,
            "FOSSIL_FUEL_EXPOSURE": ESG.ACTIVE_FF_SECTOR_EXPOSURE,
            "SHARE_OF_NONRENEWABLE_ENERGY": ESG.PCT_NON_RENEW_CONSUMPTION_PRODUCTION,
            "ENERGY_CONSUMPTION_INTENSITY": ESG.ENERGY_CONSUMPTION_INTENSITY_EUR,
            "ENERGY_CONSUMPTION_INTENSITY_PER_SECTOR": ESG.ENERGY_CONSUMPTION_INTENSITY_EUR,
            "ACTIVITY_NEGATIVELY_IMPACTING_BIODIVERSITY": ESG.OPS_BIODIV_CONTROVERSITIES,
            "EMISSIONS_TO_WATER": ESG.WATER_EMISSIONS,
            "HAZARDOUS_WASTE_RATIO": ESG.HAZARD_WASTE,
            "VIOLATION_OF_UN_PRINCIPLES": ESG.OECD_ALIGNMENT,
            "LACK_OF_PROCESS_AND_COMPLIANCE_OF_UN_PRINCIPLES": ESG.COMPLIANCE_GLOBAL_IMPACT,
            "UNADJUSTED_GENDER_PAY_GAP": ESG.GENDER_PAY_GAP_RATIO,
            "BOARD_GENDER_DIVERSITY": ESG.PCT_FEMALE_DIRECTORS,
            "CONTROVERSIAL_WEAPONS_EXPOSURE": ESG.CONTROVERSIAL_WEAPONS,
        }[self.name]

    def get_esg_data(self, instruments):
        return get_esg_df(instruments, self.get_esg_code())
