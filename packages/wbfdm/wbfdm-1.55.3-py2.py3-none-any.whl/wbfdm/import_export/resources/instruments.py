from django.db.models import Q
from import_export import fields
from import_export.widgets import CharWidget, ForeignKeyWidget, ManyToManyWidget
from wbcore.contrib.currency.models import Currency
from wbcore.contrib.geography.import_export.resources.geography import (
    CountryForeignKeyWidget,
)
from wbcore.contrib.io.resources import FilterModelResource

from wbfdm.models import Exchange, Instrument, InstrumentClassificationThroughModel

from .classification import ClassificationManyToManyWidget


class TypeWidget(CharWidget):
    def clean(self, value, row=None, **kwargs):
        return super().clean(value.lower().name(), row=row, **kwargs)


class InstrumentResource(FilterModelResource):
    """
    The resource to download AssetPositions
    """

    instrument_type = fields.Field(column_name="instrument_type", attribute="instrument_type", widget=TypeWidget())

    country = fields.Field(
        column_name="country",
        attribute="country",
        widget=CountryForeignKeyWidget(),
    )

    exchanges = fields.Field(
        column_name="exchanges",
        attribute="exchanges",
        m2m_add=True,
        widget=ManyToManyWidget(Exchange, field="mic_code"),
    )

    currency = fields.Field(
        column_name="currency",
        attribute="currency",
        widget=ForeignKeyWidget(Currency, field="key__iexact"),
    )

    primary_classifications = fields.Field(
        column_name="primary_classifications",
        attribute="classifications",
        m2m_add=True,
        widget=ClassificationManyToManyWidget(primary_classification_group=True),
    )
    default_classifications = fields.Field(
        column_name="default_classifications",
        attribute="classifications",
        m2m_add=True,
        widget=ClassificationManyToManyWidget(primary_classification_group=False),
    )

    def save_m2m(self, obj, data, using_transactions, dry_run):
        """
        override save m2m to define what to to with the nested classification instrument through model values
        """
        if (not using_transactions and dry_run) or self._meta.use_bulk:
            # we don't have transactions and we want to do a dry_run
            # OR use_bulk is enabled (m2m operations are not supported for bulk operations)
            pass
        else:
            for field in self.get_import_fields():
                if isinstance(field.widget, ClassificationManyToManyWidget):
                    defaults = {
                        "is_favorite": str(data.get(f"{field.column_name}__is_favorite", "")).lower()
                        in ["1", "true", "yes"],
                        "reason": data.get(f"{field.column_name}__reason", None),
                        "pure_player": data.get(f"{field.column_name}__pure_player", None),
                        "top_player": data.get(f"{field.column_name}__top_player", None),
                        "percent_of_revenue": data.get(f"{field.column_name}__percent_of_revenue", None),
                    }
                    defaults = {k: v for k, v in defaults.items() if v is not None}
                    for classification in field.clean(data):
                        InstrumentClassificationThroughModel.objects.update_or_create(
                            instrument=obj, classification=classification, defaults=defaults
                        )
                elif isinstance(field.widget, ManyToManyWidget):
                    self.import_field(field, obj, data, True)

    def get_instance(self, instance_loader, row):
        try:
            return Instrument.objects.get(
                Q(isin=row["isin"]) | Q(refinitiv_identifier_code=row["refinitiv_identifier_code"])
            )
        except Instrument.DoesNotExist:
            return None

    class Meta:
        import_id_fields = ("isin",)
        fields = (
            "id",
            "founded_year",
            "inception_date",
            "delisted_date",
            "identifier",
            "name",
            "name_repr",
            "description",
            "isin",
            "ticker",
            "refinitiv_ticker",
            "refinitiv_identifier_code",
            "refinitiv_mnemonic_code",
            "sedol",
            "valoren",
            "headquarter_address",
            "primary_url",
            "is_cash",
            "instrument_type",
            "country",
            "exchanges",
            "currency",
            "primary_classifications",
            "default_classifications",
        )
        export_order = fields
        model = Instrument
