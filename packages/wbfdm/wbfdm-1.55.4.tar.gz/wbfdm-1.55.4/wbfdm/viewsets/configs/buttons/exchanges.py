from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig


class ExchangeButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return set()

    def get_custom_instance_buttons(self):
        return set()
