from wbcore.metadata.configs.titles import TitleViewConfig


class InstrumentFavoriteGroupTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Instrument Favorite Groups"

    def get_instance_title(self):
        try:
            obj = self.view.get_object()
            return f"Favorite Group: {str(obj)}"
        except AssertionError:
            return "Instrument: {{name}}"

    def get_create_title(self):
        return "New Favorite Group"


class ClassifiedInstrumentTitleConfig(TitleViewConfig):
    def get_list_title(self) -> str:
        return "Classified Instruments"
