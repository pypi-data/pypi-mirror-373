import operator
from contextlib import suppress
from datetime import datetime
from functools import reduce
from typing import Any, Dict, Optional

from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError, models
from django.db.models import Q
from wbcore.contrib.currency.import_export.handlers import CurrencyImportHandler
from wbcore.contrib.geography.models import Geography
from wbcore.contrib.io.exceptions import DeserializationError
from wbcore.contrib.io.imports import ImportExportHandler, ImportState

from wbfdm.models.exchanges import Exchange


class InstrumentLookup:
    ORDERED_KEYS = [
        "instrument_type",
        "isin",
        "refinitiv_identifier_code",
        "refinitiv_mnemonic_code",
        "identifier",
        "ticker",
    ]

    def __init__(self, model, trigram_similarity_min_score: float = 0.8):
        self.cache = {}
        self.model = model
        self.trigram_similarity_min_score = trigram_similarity_min_score

    @classmethod
    def _get_cache_key(cls, **data):
        if data:
            return "-".join([f"{k}:{data.get(k, None)}" for k in cls.ORDERED_KEYS if data.get(k, None) is not None])

    def _lookup_instrument(
        self,
        instrument_type=None,
        currency=None,
        exchange=None,
        name=None,
        only_investable_universe: bool = False,
        exact_lookup: bool = False,
        **identifiers,
    ):
        identifiers = {k: v for k, v in identifiers.items() if v is not None}
        # General lookup, we try to gracefully find the instrument based on all available identifier fields
        cache_key = self._get_cache_key(**identifiers)
        if cache_key and cache_key in self.cache:
            return self.cache[cache_key]

        instrument = None

        # We need to lookup ticker because some provider gives us ticker with or without space in it
        exchange_lookup = {}
        if only_investable_universe:
            instruments = self.model.objects.filter(is_investable_universe=True)
            exchange_lookup = {"exchange": exchange} if exchange else {"is_primary": True}
        else:
            instruments = self.model.objects.filter(is_security=True)

        # Try exact lookup on the filtered out universe
        for identifier_key in [
            "isin",
            "refinitiv_identifier_code",
            "refinitiv_mnemonic_code",
            "sedol",
            "cusip",
            "identifier",
        ]:
            if identifier := identifiers.get(identifier_key, None):
                with suppress(self.model.DoesNotExist, MultipleObjectsReturned):
                    identifier = str(identifier)
                    if (
                        identifier_key != "refinitiv_identifier_code"
                    ):  # RIC cannot be uppercased because its symbology implies meaning for lowercase characters
                        identifier = identifier.upper()
                    # we try to lookup the instrument with the unique identifier
                    try:
                        instrument = instruments.get(**{identifier_key: identifier})
                        break
                    # if this return a multiple object exception, we assume there is at least one with the exchange provided or primary
                    except MultipleObjectsReturned:
                        instrument = instruments.get(**{identifier_key: identifier}, **exchange_lookup)
                        break
        if not instrument and not exact_lookup:
            if instrument_type:
                if isinstance(instrument_type, str):  # in case we receive a key as instrument type
                    instruments = instruments.filter(instrument_type__key=instrument_type)
                else:  # in case we receive a primary key as instrument type
                    instruments = instruments.filter(instrument_type=instrument_type)
            lookup_fields = [
                "isin",
                "refinitiv_identifier_code",
                "refinitiv_mnemonic_code",
                "refinitiv_ticker",
                "identifier",
                "ticker",
            ]

            conditions = []
            for field in lookup_fields:
                if field_value := identifiers.get(field, None):
                    conditions.append(Q(**{f"{field}": field_value}))
                    if field == "isin":
                        conditions.append(Q(old_isins__contains=[field_value]))
            if conditions:
                instruments = instruments.filter(reduce(operator.or_, conditions))

            if currency:  # if currency is provides, we use it as validator
                instruments = instruments.filter(currency=currency)

            if exchange:
                instruments_tmp = instruments.filter(exchange=exchange)
                if instruments_tmp.exists():
                    instruments = instruments_tmp
            # last chance
            if name and instruments.count() > 1:
                instruments = instruments.annotate(similarity_score=TrigramSimilarity("name", name))
                if instruments.filter(similarity_score__gt=self.trigram_similarity_min_score).count() == 1:
                    instruments = instruments.filter(similarity_score__gt=self.trigram_similarity_min_score)
            if instruments.count() == 1:
                instrument = instruments.first()
            elif instrument_type and identifiers:
                # if instrument type was provided but we still didn't find the security, we try without the instrument type in case it was mislabeled
                instrument = self._lookup_instrument(
                    only_investable_universe=only_investable_universe,
                    exact_lookup=exact_lookup,
                    currency=currency,
                    exchange=exchange,
                    **identifiers,
                )
            if not instrument and name and identifiers:
                # Sometime, identifier provided emptied the queryset of possible instruments. In a last chance approach, we try to only look for security with the given name
                instrument = self._lookup_instrument(
                    only_investable_universe=only_investable_universe,
                    exact_lookup=exact_lookup,
                    instrument_type=instrument_type,
                    currency=currency,
                    exchange=exchange,
                    name=name,
                )
        if instrument:
            self.cache[cache_key] = instrument
        return instrument

    def lookup(self, only_security: bool = False, exact_lookup: bool = False, **lookup_kwargs):
        # To speed up lookup process, we try to get the quote from the investable universe first
        security = self._lookup_instrument(only_investable_universe=True, exact_lookup=exact_lookup, **lookup_kwargs)
        if not security:
            security = self._lookup_instrument(
                only_investable_universe=False, exact_lookup=exact_lookup, **lookup_kwargs
            )
        if not only_security and security:
            quotes = security.children.all()
            if quotes.exists():
                # We try to find the quote for that security based on the given exchange (if provided). Otherwise, we default to the security primary exchange
                exchange = lookup_kwargs.get("exchange")
                if exchange and quotes.filter(exchange=exchange).exists():
                    return quotes.filter(exchange=exchange).first()
                else:
                    return quotes.filter(is_primary=True).first()
        return security


class InstrumentImportHandler(ImportExportHandler):
    MODEL_APP_LABEL: str = "wbfdm.Instrument"
    allow_update_save_failure = True
    exclude_update_fields = ["name", "isin", "country"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instrument_lookup = InstrumentLookup(self.model)
        self.currency_handler = CurrencyImportHandler(self.import_source)

    def _deserialize(self, data: Dict[str, Any]):
        from wbfdm.models import Classification, InstrumentType

        if isinstance(data, int):
            data = dict(id=data)
        if data.get("currency", None):
            data["currency"] = self.currency_handler.process_object(
                data["currency"], read_only=True, raise_exception=False
            )[0]
        if instrument_type := data.get("instrument_type", None):
            if isinstance(instrument_type, str):
                data["instrument_type"] = InstrumentType.objects.get_or_create(
                    key=instrument_type,
                    defaults={"name": instrument_type.title(), "short_name": instrument_type.title()},
                )[0]
            elif isinstance(instrument_type, int):
                data["instrument_type"] = InstrumentType.objects.get(id=instrument_type)
        if data.get("country", None):
            data["country"] = Geography.dict_to_model(data["country"])
        if data.get("headquarter_city", None):
            data["headquarter_city"] = Geography.dict_to_model(data["headquarter_city"], level=Geography.Level.CITY)
        if inception_date := data.get("inception_date", None):
            data["inception_date"] = datetime.strptime(inception_date, "%Y-%m-%d").date()
        if classifications := data.pop("classifications", None):
            data["classifications"] = [Classification.dict_to_model(c) for c in classifications]
        if (exchange_data := data.pop("exchange", None)) and isinstance(exchange_data, dict):
            sanitized_dict = {k: v for k, v in exchange_data.items() if v is not None}
            if sanitized_dict:
                data["exchange"] = Exchange.dict_to_model(sanitized_dict)

    def _get_instance(
        self,
        data: Dict[str, Any],
        history: Optional[models.QuerySet] = None,
        only_security: bool = False,
        **kwargs,
    ) -> models.Model:
        if isinstance(data, self.model):
            return data
        if instrument_id := data.pop("id", None):
            try:
                return self.model.objects.get(id=instrument_id)
            except self.model.DoesNotExist:
                raise DeserializationError("Instrument id does not match an existing instrument")
        else:
            return self.instrument_lookup.lookup(only_security=only_security, **data)

    def _create_instance(self, data: Dict[str, Any], **kwargs) -> models.Model:
        from wbfdm.models.instruments.instruments import Instrument

        if not data.get("name", None):
            raise DeserializationError("Can't create an instrument without at least a name")
        classifications = data.pop("classifications", None)
        try:
            obj = Instrument.objects.create(
                **data,
                import_source=self.import_source,
            )
            if classifications:
                obj.classifications.set([c for c in classifications if c])
            return obj
        except IntegrityError:
            self.import_source.log += f"\nError while creating new instrument with data {data}"

        return None

    def process_object(self, underlying_instrument_data, **kwargs):
        if underlying_instrument_data:
            if isinstance(underlying_instrument_data, self.model):
                return underlying_instrument_data, ImportState.UNMODIFIED
            if isinstance(underlying_instrument_data, int):
                underlying_instrument_data = dict(id=underlying_instrument_data)
        return super().process_object(
            underlying_instrument_data,
            include_update_fields=[
                "isin",
                "ticker",
                "refinitiv_mnemonic_code",
                "refinitiv_identifier_code",
                "country",
                "exchange",
            ],
            **kwargs,
        )
