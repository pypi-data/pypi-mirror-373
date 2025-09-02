from wbcore.metadata.configs.titles import TitleViewConfig

from wbfdm.models import Classification, ClassificationGroup, Instrument


class ClassificationTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Classifications"

    def get_instance_title(self):
        try:
            obj = self.view.get_object()
            return f"Classification: {str(obj)}"
        except AssertionError:
            return "Classification: {{name}}"

    def get_create_title(self):
        return "New Classification"


class ClassificationGroupTitleConfig(TitleViewConfig):
    def get_list_title(self):
        return "Classification Groups"

    def get_instance_title(self):
        return "Classification Group"

    def get_create_title(self):
        return "New Classification Group"


class ChildClassificationParentClassificationTitleConfig(ClassificationTitleConfig):
    def get_list_title(self):
        classification = Classification.objects.get(id=self.view.kwargs["parent_id"])
        return f"Child Classifications of {classification.name}"

    def get_create_title(self):
        classification = Classification.objects.get(id=self.view.kwargs["parent_id"])
        return f"New Child Classification {classification.name}"


class ClassificationClassificationGroupTitleConfig(ClassificationTitleConfig):
    def get_list_title(self):
        group = ClassificationGroup.objects.get(id=self.view.kwargs["group_id"])
        return f"Entry Level Classifications for group {group.name}"

    def get_create_title(self):
        group = ClassificationGroup.objects.get(id=self.view.kwargs["group_id"])
        return f"New Classification for group {group.name}"


class ClassificationTreeChartTitleConfig(TitleViewConfig):
    def get_list_title(self):
        group = ClassificationGroup.objects.get(id=self.view.kwargs["group_id"])
        return f"Classification Tree for group {group.name}"


class ClassificationIcicleChartTitleConfig(TitleViewConfig):
    def get_list_title(self):
        group = ClassificationGroup.objects.get(id=self.view.kwargs["group_id"])
        return f"Classification Icicle Chart for group {group.name}"


class InstrumentClassificationThroughTitleConfig(TitleViewConfig):
    def get_create_title(self) -> str:
        if instrument_id := self.view.kwargs.get("instrument_id", None):
            return f"Classification for {Instrument.objects.get(id=instrument_id)}"
        elif classification_id := self.view.kwargs.get("classification_id", None):
            return f"Instrument for {Classification.objects.get(id=classification_id)}"
        else:
            return super().get_create_title()

    def get_instance_title(self):
        try:
            obj = self.view.get_object()
            if obj.classification and obj.instrument:
                return f"Relationship: {str(obj.classification.name)} <-> {str(obj.instrument.name)}"
            return str(obj)
        except AssertionError:
            return super().get_instance_title()
