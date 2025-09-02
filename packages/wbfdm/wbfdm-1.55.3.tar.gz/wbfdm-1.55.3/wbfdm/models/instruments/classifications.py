from typing import List, Optional

import roman
from django.contrib.postgres.expressions import ArraySubquery
from django.db import models
from django.db.models.functions import Cast
from django.db.models.signals import post_save
from django.dispatch import receiver
from mptt.models import MPTTModel, TreeForeignKey
from wbcore.models import WBModel
from wbcore.utils.models import ComplexToStringMixin

from .instrument_relationships import InstrumentClassificationThroughModel


class ClassificationGroup(WBModel):
    name = models.CharField(max_length=128, verbose_name="Name")
    is_primary = models.BooleanField(
        default=False,
        verbose_name="Primary",
        help_text="Set to True if this " "classification must be used as " "default if not specified " "otherwise",
    )
    max_depth = models.IntegerField(default=0, verbose_name="Maximum Depth")
    code_level_digits = models.IntegerField(default=2, verbose_name="The number of digits per code level")

    def __str__(self) -> str:
        return f'{self.name} ({"Primary" if self.is_primary else "Non Primary"})'

    def save(self, *args, **kwargs):
        qs = ClassificationGroup.objects.filter(is_primary=True).exclude(id=self.id)
        if self.is_primary:
            qs.update(is_primary=False)
        elif not qs.exists():
            self.is_primary = True
        return super().save(*args, **kwargs)

    def get_levels_representation(self) -> List[str]:
        return [
            self.classifications.filter(height=i).first().level_representation
            for i in range(self.max_depth + 1)
            if self.classifications.filter(height=i).exists()
        ]

    def get_fields_names(self, sep: str = "__") -> list[str]:
        return [f"parent{f'{sep}parent' * height}" for height in range(self.max_depth)]

    def annotate_queryset(
        self,
        queryset: models.QuerySet,
        classification_height: int,
        instrument_label_key: str,
        unique: bool = False,
        annotation_label: str = "classifications",
    ):
        ref_id = "classification__"
        if classification_height:
            ref_id += f"{'parent__' * classification_height}"
        ref_id += "id"
        if instrument_label_key:
            instrument_label_key += "__"
        base_subquery = InstrumentClassificationThroughModel.objects.filter(
            classification__group=self,
            instrument__tree_id=models.OuterRef(f"{instrument_label_key}tree_id"),
            instrument__lft__lte=models.OuterRef(f"{instrument_label_key}lft"),
            instrument__rght__gte=models.OuterRef(f"{instrument_label_key}rght"),
        )
        if unique:
            expression = models.Subquery(base_subquery.values(ref_id)[:1])
        else:
            expression = ArraySubquery(
                base_subquery.values(ref_id).distinct(ref_id)
            )  # we use distinct in order to remove duplicated classification (e.g. classification added to the parent as well as the children)

        return queryset.annotate(**{annotation_label: expression})

    class Meta:
        verbose_name = "Classification Group"
        verbose_name_plural = "Classification Groups"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbfdm:classificationgrouprepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{name}}"

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbfdm:classificationgroup"


class Classification(MPTTModel, ComplexToStringMixin):
    parent = TreeForeignKey(
        "self",
        related_name="children",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Parent Classification",
    )
    height = models.PositiveIntegerField(
        default=0,
        verbose_name="The height (leaf node have height 0)",
    )
    group = models.ForeignKey(
        ClassificationGroup,
        related_name="classifications",
        on_delete=models.CASCADE,
        verbose_name="Classification Group",
    )

    level_representation = models.CharField(max_length=256, verbose_name="Level Representation")

    name = models.CharField(max_length=128, verbose_name="Name")
    code_aggregated = models.CharField(max_length=64, verbose_name="Code Aggregated")

    investable = models.BooleanField(default=True, help_text="Is this classification investable for us?")

    description = models.TextField(
        default="",
        blank=True,
        help_text="Give a basic definition and description",
        verbose_name="Definition/Description",
    )

    @classmethod
    def dict_to_model(cls, classification_data):
        if isinstance(classification_data, int):
            return cls.objects.filter(id=classification_data).first()
        res = cls.objects.all()
        if code_aggregated := classification_data.get("code_aggregated", None):
            res = res.filter(code_aggregated=code_aggregated)
        if group_id := classification_data.get("group", None):
            res = res.filter(group=group_id)
        if res.count() == 1:
            return res.first()

    def __str__(self):
        if self.computed_str:
            return self.computed_str
        return f"{self.code_aggregated} {self.name}"

    def get_classified_instruments(self, only_favorites: bool = False) -> models.QuerySet:
        childs_classifications = self.get_descendants(include_self=True)
        params = {"classifications__in": childs_classifications}
        if only_favorites:
            params["classifications_through__is_favorite"] = True

        from wbfdm.models import Instrument

        return Instrument.objects.filter(**params).distinct()

    def save(self, *args, **kwargs):
        if self.parent:
            self.group = self.parent.group
        if not self.code_aggregated:
            self.code_aggregated = self.get_next_valid_code(self.group, self.parent)
        if not self.level_representation:
            self.level_representation = self.get_default_level_representation(self.group, self.parent)
        return super().save(*args, **kwargs)

    def compute_str(self) -> str:
        if parent := self.parent:
            tree_titles = parent.name
            while parent and (parent := parent.parent):
                tree_titles += f" - {parent.name}"
            return f"{self.code_aggregated} {self.name} [{tree_titles}] ({self.group.name})"
        return f"{self.code_aggregated} {self.name} ({self.group.name})"

    class Meta:
        verbose_name = "Classification"
        verbose_name_plural = "Classifications"
        constraints = [models.UniqueConstraint(fields=["group", "code_aggregated"], name="unique_classification")]

    @classmethod
    def get_next_valid_code(cls, group: "ClassificationGroup", parent: "Classification | None" = None) -> str:
        """
        Return the next valid classification code given the classification parent and its group parameters
        Args:
            group: The classification group the estimated code belongs to
            parent: The classification parent (if any)

        Returns:
            The next valid and unused aggregated classification code
        """
        if not group:
            raise ValueError("This method needs a group")
        siblings_classifications = (
            Classification.objects.filter(parent=parent, group=group)
            .annotate(casted_code=Cast("code_aggregated", models.BigIntegerField()))
            .order_by("-casted_code")
        )
        parent_level = parent.level + 1 if parent else 0
        code_aggregated_digits = group.code_level_digits * (parent_level + 1)
        if last_classification := siblings_classifications.first():
            for i in range(0, 100 - last_classification.casted_code % 10**group.code_level_digits):
                if not siblings_classifications.filter(casted_code=last_classification.casted_code + i).exists():
                    last_valid_code = last_classification.casted_code + i
                    return f"{last_valid_code:0{code_aggregated_digits}}"
        if parent:
            return parent.code_aggregated + f"{1:0{group.code_level_digits}}"
        return f"{1:0{group.code_level_digits}}"

    @classmethod
    def get_default_level_representation(
        cls, group: "ClassificationGroup", parent: Optional["Classification"] = None
    ) -> str:
        """
        Return the default level representation, extracted from the classification siblings
        Args:
            group: The classification group the estimated code belongs to
            parent: The classification parent (if any)

        Returns:
            A default level representation (e.g. Industry)
        """
        level = parent.level + 1 if parent else None
        siblings_classifications = cls.objects.filter(level=level, group=group).order_by("id")
        if siblings_classifications.exists():
            return siblings_classifications.last().level_representation
        level = roman.toRoman(level) if level else 0
        return f"Level {level}"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbfdm:classificationrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbfdm:classification"


@receiver(post_save, sender="wbfdm.Classification")
def post_save_parent_classification(sender, instance, created, raw, **kwargs):
    # Recursively call the parent save function to recompute its parameters
    if not raw and instance.parent:
        instance.parent.save()
    if instance.level is not None:
        update_fields = {"height": instance.group.max_depth - instance.level}
        Classification.objects.filter(id=instance.id).update(**update_fields)
        instance.refresh_from_db()
    # # Ensure initial parent classifcation span the proper classification tree structure
    if instance.group and not instance.get_descendants().exists() and instance.level < instance.group.max_depth:
        Classification.objects.create(
            parent=instance,
            group=instance.group,
            name=f"{instance.name} (Level {instance.level})",
        )
    """
    If a parent classification is not investable, therefore its "children" become non investable too, by cascade.
    If a child classification becomes investable and one of its parent is non investable, therefore he cannot be
    investable as long as its parent is non investable. (-> in the serializer)
    """
    if not raw and not instance.investable and instance.get_descendants().exists():
        descandants = instance.get_descendants()
        descandants.update(investable=False)
