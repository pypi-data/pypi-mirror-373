import logging
from contextlib import suppress
from datetime import date, timedelta
from typing import Callable

import pytz
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, connections
from django.db.models import Max, QuerySet
from django.template.loader import get_template
from jinjasql import JinjaSql  # type: ignore
from mptt.exceptions import InvalidMove
from psycopg.errors import UniqueViolation
from tqdm import tqdm
from wbcore.contrib.currency.models import Currency
from wbcore.contrib.dataloader.utils import dictfetchall, dictfetchone
from wbcore.contrib.geography.models import Geography
from wbcore.utils.cache import mapping
from wbfdm.models.exchanges.exchanges import Exchange
from wbfdm.models.instruments.instruments import Instrument, InstrumentType

logger = logging.getLogger("pms")

BATCH_SIZE: int = 10000
instrument_type_map = {
    "ADR": "american_depository_receipt",
    "CF": "close_ended_fund",
    "EQ": "equity",
    "ET": "exchange_traded_fund",
    "ETC": "exchange_traded_commodity",
    "ETN": "exchange_traded_note",
    "EWT": "warrant",
    "GDR": "global_depository_receipt",
    "GNSH": "genussschein",
    "INVT": "investment_trust",
    "NVDR": "non_voting_depository_receipt",
    "PREF": "preference_share",
    "UT": "abc",
}


def get_dataloader_parameters(
    quote_code: str | None = None,
    exchange_code: str | None = None,
    rkd_code: str | None = None,
    ibes_code: str | None = None,
) -> dict:
    dataloader_parameters = dict()
    if quote_code:
        dataloader_parameters["adjustments"] = {
            "path": "wbfdm.contrib.qa.dataloaders.adjustments.DatastreamAdjustmentsDataloader",
            "parameters": quote_code,
        }
        dataloader_parameters["corporate_actions"] = {
            "path": "wbfdm.contrib.qa.dataloaders.corporate_actions.DatastreamCorporateActionsDataloader",
            "parameters": quote_code,
        }
        if exchange_code:
            dataloader_parameters["market_data"] = {
                "path": "wbfdm.contrib.qa.dataloaders.market_data.DatastreamMarketDataDataloader",
                "parameters": [
                    quote_code,
                    exchange_code,
                ],
            }

    if rkd_code:
        dataloader_parameters["officers"] = {
            "path": "wbfdm.contrib.qa.dataloaders.officers.RKDOfficersDataloader",
            "parameters": rkd_code,
        }
        dataloader_parameters["statements"] = {
            "path": "wbfdm.contrib.qa.dataloaders.statements.RKDStatementsDataloader",
            "parameters": rkd_code,
        }

    if ibes_code:
        dataloader_parameters["financials"] = {
            "path": "wbfdm.contrib.qa.dataloaders.financials.IBESFinancialsDataloader",
            "parameters": ibes_code,
        }
        dataloader_parameters["reporting_dates"] = {
            "path": "wbfdm.contrib.qa.dataloaders.reporting_dates.IbesReportingDateDataloader",
            "parameters": ibes_code,
        }

    return dataloader_parameters


def convert_data(data, parent_source: str | None = None) -> dict:
    if len(data.keys()) == 0:
        return data
    data["country_id"] = mapping(Geography.countries, "code_2").get(data["country_id"])
    data["currency_id"] = mapping(Currency.objects).get(data["currency_id"])
    if instrument_type_id := data.pop("instrument_type_id"):
        try:
            data["instrument_type_id"] = mapping(InstrumentType.objects)[
                instrument_type_map.get(instrument_type_id, instrument_type_id)
            ]
        except KeyError:
            data["instrument_type_id"] = InstrumentType.objects.get_or_create(
                key=instrument_type_id.lower(),
                defaults={"name": instrument_type_id.title(), "short_name": instrument_type_id.title()},
            )[0].pk
    data["exchange_id"] = mapping(Exchange.objects, "source_id", source="qa-ds2-exchange").get(
        str(data["exchange_code"])
    )
    data["dl_parameters"] = get_dataloader_parameters(
        data.pop("quote_code"), data.pop("exchange_code"), data.pop("rkd_code"), data.pop("ibes_code")
    )
    data["additional_urls"] = urls.split(",") if (urls := data.get("additional_urls")) else []
    if parent_source:
        data["parent_id"] = mapping(Instrument.objects, "source_id", source=parent_source).get(str(data["parent_id"]))
    if (is_primary := data.get("is_primary")) and isinstance(is_primary, str):
        data["is_primary"] = is_primary.lower().strip() == "y"
    data.pop("phone")
    return data


def get_instrument_from_data(data, parent_source: str | None = None) -> Instrument | None:
    if len(data.keys()) == 0:
        return None

    defaults = convert_data(data, parent_source)
    try:
        instrument = Instrument.objects.get(source=defaults["source"], source_id=defaults["source_id"])
        instrument.dl_parameters.update(
            defaults.pop("dl_parameters")
        )  # we need to update the existing dl parameters to not override its existing value
        for k, v in defaults.items():
            setattr(instrument, k, v)

    except Instrument.DoesNotExist:
        instrument = Instrument(**defaults)

    instrument.pre_save()
    instrument.computed_str = instrument.compute_str()
    if (
        instrument.name and instrument.currency and instrument.instrument_type
    ):  # we return an instrument only if it contains the basic name, currency and type
        return instrument


def _delist_existing_duplicates(instrument: Instrument) -> None:
    """Handle duplicate instruments by delisting existing entries"""
    unique_identifiers = ["refinitiv_identifier_code", "refinitiv_mnemonic_code", "isin", "sedol", "valoren", "cusip"]

    for identifier_field in unique_identifiers:
        if identifier := getattr(instrument, identifier_field):
            with suppress(Instrument.DoesNotExist):
                duplicate = Instrument.objects.get(
                    is_security=True, delisted_date__isnull=True, **{identifier_field: identifier}
                )
                duplicate.delisted_date = date.today() - timedelta(days=1)
                duplicate.save()


def _save_single_instrument(instrument: Instrument) -> None:
    """Attempt to save an instrument with duplicate handling"""
    try:
        instrument.save()
    except (UniqueViolation, IntegrityError) as e:
        if instrument.is_security:
            _delist_existing_duplicates(instrument)
            try:
                instrument.save()
                logger.info(f"{instrument} successfully saved after automatic delisting")
            except (UniqueViolation, IntegrityError) as e:
                logger.error(f"Persistent integrity error: {e}")
        else:
            logger.error(f"Non-security instrument error: {e}")


def _bulk_create_instruments_chunk(instruments: list[Instrument], update_unique_identifiers: bool = False):
    update_fields = [
        "name",
        "dl_parameters",
        "description",
        "country",
        "currency",
        "parent",
        "primary_url",
        "additional_urls",
        "headquarter_address",
        "inception_date",
        "delisted_date",
        "exchange",
        "instrument_type",
        "computed_str",
        "search_vector",
        "trigram_search_vector",
        "is_primary",
    ]
    bulk_update_kwargs = {"update_conflicts": True}
    if update_unique_identifiers:
        update_fields.extend(
            [
                "refinitiv_identifier_code",
                "refinitiv_mnemonic_code",
                "isin",
                "sedol",
                "valoren",
                "cusip",
            ]
        )
        bulk_update_kwargs = {"ignore_conflicts": True}
    try:
        Instrument.objects.bulk_create(
            instruments, update_fields=update_fields, unique_fields=["source", "source_id"], **bulk_update_kwargs
        )
    except IntegrityError:
        # we caught an integrity error on the bulk save, so we try to save one by one
        logger.info(
            "we detected an integrity error while bulk saving instruments. We save them one by one and delist the already existing instrument from the db if we can. "
        )
        for instrument in instruments:
            _save_single_instrument(instrument)


def update_instruments(sql_name: str, parent_source: str | None = None, context=None, debug: bool = False, **kwargs):
    template = get_template(sql_name, using="jinja").template  # type: ignore
    if context is None:
        context = {}
    query, params = JinjaSql(param_style="format").prepare_query(template, context)
    instruments = []

    gen = dictfetchall(connections["qa"].cursor().execute(query, params))
    if debug:
        gen = tqdm(gen)
    # we update in batch to be sure to not exhaust resources
    for row in gen:
        with suppress(TypeError):  # we don't fail if the given data doesn't satisfy the schema
            if instrument := get_instrument_from_data(row, parent_source=parent_source):
                instruments.append(instrument)

        if len(instruments) >= BATCH_SIZE:
            _bulk_create_instruments_chunk(instruments, **kwargs)
            instruments = []

    _bulk_create_instruments_chunk(instruments, **kwargs)


def update_or_create_item(
    external_id: int, get_item: Callable, source: str, parent_source: str | None = None
) -> Instrument | None:
    defaults = convert_data(get_item(external_id), parent_source=parent_source)

    dl_parameters = defaults.pop("dl_parameters", {})
    defaults.pop("source", None)
    defaults.pop("source_id", None)
    try:
        instrument, _ = Instrument.objects.update_or_create(
            source=source,
            source_id=external_id,
            defaults=defaults,
        )
        instrument.dl_parameters.update(dl_parameters)
        _save_single_instrument(instrument)
        return instrument

    except (
        InvalidMove,
        ObjectDoesNotExist,
    ):  # we might encounter a object does not exist error in case the inserted parent does not exist yet in our db which might happen if it was just deleted because invalid
        logger.warning(
            f"We encountered a MPTT ill-formed node for source ID {external_id}. Rebuilding the tree might be necessary."
        )


def get_item(external_id: int, template_name: str) -> dict:
    template = get_template(template_name, using="jinja").template  # type: ignore
    query, params = JinjaSql(param_style="format").prepare_query(template, {"source_id": external_id})
    return dictfetchone(connections["qa"].cursor().execute(query, params))


def trigger_partial_update(
    queryset: QuerySet,
    last_update_field: str,
    id_field: str,
    table_change_name: str,
    update: Callable,
    update_or_create_item: Callable,
):
    max_last_updated = queryset.aggregate(max_last_updated=Max(last_update_field)).get("max_last_updated")

    if max_last_updated is None:
        update()

    else:
        with connections["qa"].cursor() as cursor:
            cursor.execute(
                f"SELECT MAX(last_user_update) FROM sys.dm_db_index_usage_stats WHERE OBJECT_NAME(object_id) = '{table_change_name}'"
            )
            max_last_updated_qa = (
                pytz.timezone(settings.TIME_ZONE).localize(result[0]) if (result := cursor.fetchone()) else None
            )
            if max_last_updated_qa and max_last_updated_qa > max_last_updated:
                for _, security_id in cursor.execute(
                    f"SELECT UpdateFlag_, {id_field} FROM {table_change_name}"
                ).fetchall():
                    update_or_create_item(security_id)
