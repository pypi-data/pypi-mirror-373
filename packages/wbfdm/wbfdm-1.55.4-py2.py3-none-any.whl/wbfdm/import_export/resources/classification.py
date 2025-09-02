from import_export.widgets import ManyToManyWidget

from wbfdm.models import Classification, ClassificationGroup
from wbfdm.preferences import get_default_classification_group


class ClassificationManyToManyWidget(ManyToManyWidget):
    model = Classification
    field = "code_aggregated"

    def __init__(self, separator=None, field="code_aggregated", primary_classification_group=False, **kwargs):
        super().__init__(Classification, separator=separator, field=field, **kwargs)
        self.primary_classification_group = primary_classification_group

    def clean(self, value, row=None, **kwargs):
        if self.primary_classification_group:
            primary_classification_group = ClassificationGroup.objects.get(is_primary=True)
        else:
            primary_classification_group = get_default_classification_group()
        queryset = Classification.objects.filter(
            **{f"{self.field}__icontains": value, "group": primary_classification_group}
        )
        if queryset.count() == 1:
            return queryset
