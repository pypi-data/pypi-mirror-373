from wbcore.metadata.configs.titles import TitleViewConfig


class InstrumentPriceTitleViewConfig(TitleViewConfig):
    def get_list_title(self):
        return f"{self.view.instrument} - Prices"

    def get_delete_title(self) -> str:
        return None

    # def get_instance_title(self) -> str:
    #     return None

    def get_create_title(self) -> str:
        return None
