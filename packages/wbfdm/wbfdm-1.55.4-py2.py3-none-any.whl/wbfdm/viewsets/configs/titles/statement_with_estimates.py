from wbcore.metadata.configs.titles import TitleViewConfig


class StatementTitleViewConfig(TitleViewConfig):
    def get_list_title(self):
        try:
            statement_label = self.view.financial_analysis_mapping[self.view.kwargs["statement"]][1]
            return f"{self.view.instrument} - {statement_label} Table"
        except KeyError:
            return f"{self.view.instrument} - Statement"
