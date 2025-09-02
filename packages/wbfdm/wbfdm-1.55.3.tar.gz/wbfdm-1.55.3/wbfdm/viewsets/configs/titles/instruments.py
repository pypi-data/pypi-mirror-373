from wbcore.metadata.configs.titles import TitleViewConfig


class InstrumentTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Instruments"

    def get_instance_title(self):
        try:
            obj = self.view.get_object()
            instrument_type = obj.instrument_type.name if obj.instrument_type else "Instrument"
            return f"{instrument_type}: {str(obj)}"
        except AssertionError:
            return "Instrument: {{name}}"

    def get_create_title(self):
        return "New Instrument"


class SubviewInstrumentTitleViewConfig(TitleViewConfig):
    def get_list_title(self):
        return f"{str(self.view.instrument)} - {self.view.SUBVIEW_NAME} "

    def get_delete_title(self) -> str:
        return None

    def get_instance_title(self) -> str:
        return None

    def get_create_title(self) -> str:
        return None
