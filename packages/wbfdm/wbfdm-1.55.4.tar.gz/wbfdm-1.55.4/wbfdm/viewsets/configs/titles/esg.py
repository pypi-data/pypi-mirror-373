from wbcore.metadata.configs.titles import TitleViewConfig


class InstrumentESGPAITitleViewConfig(TitleViewConfig):
    def get_list_title(self):
        return f"{self.view.instrument} - PAI"


class InstrumentESGControversiesTitleViewConfig(TitleViewConfig):
    def get_list_title(self):
        return f"{self.view.instrument} - Controversies"
