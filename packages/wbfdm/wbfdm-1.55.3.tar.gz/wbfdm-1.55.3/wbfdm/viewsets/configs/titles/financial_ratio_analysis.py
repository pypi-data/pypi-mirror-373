from wbcore.metadata.configs.titles import TitleViewConfig


class ValuationRatioChartTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return f"{str(self.view.instrument)} - Financial Statistics Chart"
