from wbcore.metadata.configs.titles import TitleViewConfig


class ExchangeTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Exchanges"

    def get_instance_title(self):
        return "Exchange"

    def get_create_title(self):
        return "New Exchange"
