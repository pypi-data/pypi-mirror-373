from wbcore.metadata.configs.titles import TitleViewConfig


class InstrumentRequestTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Instrument Requests"

    def get_instance_title(self):
        try:
            obj = self.view.get_object()
            return f"Instrument Request: {str(obj)}"
        except AssertionError:
            return "Instrument Request: {{status}}"

    def get_create_title(self):
        return "New Instrument Request"
