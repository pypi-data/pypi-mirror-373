from wbcore.metadata.configs.titles import TitleViewConfig

from wbfdm.models import Instrument


class SummaryTableInstrumentChartTitle(TitleViewConfig):
    def get_list_title(self) -> str:
        instrument = Instrument.objects.get(id=self.view.kwargs["instrument_id"])
        return f"{instrument.name_repr} - Financial Summary Table"


class FinancialsGraphInstrumentChartTitle(TitleViewConfig):
    def get_list_title(self) -> str:
        instrument = Instrument.objects.get(id=self.view.kwargs["instrument_id"])
        return f"{instrument.name_repr} - Financials Graph Chart"


class ProfitabilityRatiosInstrumentChartTitle(TitleViewConfig):
    def get_list_title(self) -> str:
        instrument = Instrument.objects.get(id=self.view.kwargs["instrument_id"])
        return f"{instrument.name_repr} - Profitability Ratios Chart"


class CashFlowAnalysisInstrumentTableChartTitle(TitleViewConfig):
    def get_list_title(self) -> str:
        instrument = Instrument.objects.get(id=self.view.kwargs["instrument_id"])
        return f"{instrument.name_repr} - Cash Flow Analysis Table"


class CashFlowAnalysisInstrumentBarChartTitle(TitleViewConfig):
    def get_list_title(self) -> str:
        instrument = Instrument.objects.get(id=self.view.kwargs["instrument_id"])
        return f"{instrument.name_repr} - Cash Flow Analysis Bar Chart"


class NetDebtAndEbitdaInstrumentChartTitle(TitleViewConfig):
    def get_list_title(self) -> str:
        instrument = Instrument.objects.get(id=self.view.kwargs["instrument_id"])
        return f"{instrument.name_repr} - Net debt and EBITDA Chart"


class EarningsInstrumentChartTitle(TitleViewConfig):
    def get_list_title(self) -> str:
        instrument = Instrument.objects.get(id=self.view.kwargs["instrument_id"])
        return f"{instrument.name_repr} - Earnings Analysis Chart"


class FinancialAnalysisGeneratorTitleConfig(TitleViewConfig):
    def get_list_title(self):
        instrument = Instrument.objects.get(id=self.view.kwargs["instrument_id"])
        return f"Ratios for {str(instrument)}"
