from wbcore.metadata.configs.titles import TitleViewConfig

from wbfdm.enums import MarketDataChartType


class PerformanceSummaryChartTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return f"{self.view.instrument} - Performance Summary"


class MarketDataChartTitleConfig(TitleViewConfig):
    def get_list_title(self):
        market_data_chart_type = MarketDataChartType(self.request.GET.get("chart_type", "close"))
        return f"{self.view.instrument} - {market_data_chart_type.label} Chart"
