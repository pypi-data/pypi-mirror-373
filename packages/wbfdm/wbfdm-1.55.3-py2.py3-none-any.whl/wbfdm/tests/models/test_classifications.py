import pytest

from wbfdm.models.instruments import (
    Classification,
    ClassificationGroup,
    InstrumentClassificationThroughModel,
)


@pytest.mark.django_db
class TestClassificationGroupModel:
    def test_init(self, classification_group):
        assert classification_group.id is not None

    def test_primary(self, classification_group_factory):
        g1 = classification_group_factory.create()
        assert g1.is_primary
        g2 = ClassificationGroup.objects.create(is_primary=True, name="Other group")
        g1.refresh_from_db()
        assert g2.is_primary
        assert not g1.is_primary

    def test_get_levels_representation(self, classification_group_factory, classification_factory):
        group = classification_group_factory.create(max_depth=2)
        c0 = classification_factory.create(name="c0", group=group, level=0, parent=None)
        c1, created = Classification.objects.update_or_create(group=group, level=1, parent=c0, defaults={"name": "c1"})
        c2, created = Classification.objects.update_or_create(group=group, level=2, parent=c1, defaults={"name": "c2"})
        assert set(group.get_levels_representation()) == {
            c0.level_representation,
            c1.level_representation,
            c2.level_representation,
        }


@pytest.mark.django_db
class TestClassificationModel:
    def test_init(self, classification_factory):
        classification = classification_factory.create()
        assert classification.id is not None

    def test_str(self, classification_factory):
        classification = classification_factory.create()
        assert str(classification) == classification.computed_str

    def test_get_instruments(self, classification_factory, instrument_factory, classification_group):
        ind1 = classification_factory.create(group=classification_group)
        subind1 = classification_factory.create(parent=ind1, group=classification_group)
        subind2 = classification_factory.create(parent=ind1, group=classification_group)

        e1 = instrument_factory.create(classifications=(subind1,))
        e2 = instrument_factory.create(classifications=(subind2,))
        InstrumentClassificationThroughModel.objects.filter(instrument=e2, classification=subind2).update(
            is_favorite=True
        )

        assert ind1.get_classified_instruments().count() == 2
        assert subind1.get_classified_instruments().first() == e1
        assert subind2.get_classified_instruments().first() == e2

        assert ind1.get_classified_instruments(only_favorites=True).count() == 1
        assert subind1.get_classified_instruments(only_favorites=True).first() is None
        assert subind2.get_classified_instruments(only_favorites=True).first() == e2

    @pytest.mark.parametrize("classification_group__code_level_digits", [1, 2, 3, 4])
    def test_get_next_valid_code(self, classification_factory, classification_group):
        parent_classification = classification_factory.create(group=classification_group, code_aggregated=None)
        assert parent_classification.code_aggregated == f"{1:0{classification_group.code_level_digits}}"
        c1 = Classification.objects.filter(parent=parent_classification, group=classification_group).first()
        assert (
            c1.code_aggregated
            == f"{1:0{classification_group.code_level_digits}}" + f"{1:0{classification_group.code_level_digits}}"
        )
        c2 = classification_factory.create(
            parent=parent_classification, group=classification_group, code_aggregated=None
        )
        assert (
            c2.code_aggregated
            == f"{1:0{classification_group.code_level_digits}}" + f"{2:0{classification_group.code_level_digits}}"
        )

    def test_get_default_level_representation(self, classification_factory, classification_group_factory):
        classification_group = classification_group_factory.create(max_depth=2)

        # Parent Classification has a default "Level 0" level representation.
        parent_classification = classification_factory.create(group=classification_group)
        assert parent_classification.level_representation == "Level 0"

        # If no siblings, default is the roman style representation of parent level + 1.
        c1 = Classification.objects.filter(parent=parent_classification, group=classification_group).first()
        assert c1.level_representation == "Level I"

        # C1 is the parent of C2, we write our own level representation for level 2 classifications.
        c2 = Classification.objects.filter(parent=c1, group=classification_group).first()
        assert c2.level_representation == "Level II"
        c2.level_representation = "Level B"
        c2.save()

        # If we now create a new level 2 classification, it will take the same representation of its siblings.
        c22 = classification_factory.create(parent=c1, group=classification_group)
        assert c22.level_representation == "Level B"
