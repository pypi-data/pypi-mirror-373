import numpy as np
import pandas as pd

from wbfdm.import_export.backends.refinitiv.instrument import DEFAULT_MAPPING
from wbfdm.models import ClassificationGroup

from .utils import get_country, get_exchange


def get_instrument_type(_type):
    if _type == "BD":
        return "bond"
    elif _type in ["EQ", "ADR", "ET", "GDR", "INVT", "CF"]:
        return "equity"
    elif _type in ["CF"]:
        return "close_ended_fund"
    elif _type == "EQIND":
        return "index"
    elif _type == "OP":
        return "option"
    elif _type == "SWAPS":
        return "swaps"
    elif _type == "CMD":
        return "commodity"
    elif _type == "INT":
        return "interest_rate_derivative"
    elif _type == "FT":
        return "future"


def parse(import_source):
    # Read Json as dataframe
    df = pd.read_json(import_source.file, orient="records")
    # Sanitize df and rename columns to model knowledge's
    data = list()
    if not df.empty:
        df = (
            df.replace({"NA": None})
            .rename(columns={**DEFAULT_MAPPING, "Instrument": "instrument"})
            .set_index("instrument")
        )
        df = df.drop(columns=df.columns.difference(DEFAULT_MAPPING.values()))
        df = df.replace([np.inf, -np.inf, np.nan], None)
        df["ticker"] = df["ticker"].astype(str)
        df = df.dropna(how="all", subset=df.columns)
        df = df.groupby(level=0, axis=1).first()
        df["inception_date"] = pd.to_datetime(df["inception_date"], format="%Y%m%d", errors="coerce").dt.strftime(
            "%Y-%m-%d"
        )
        df = df.replace([np.inf, -np.inf, np.nan, pd.NaT], None).replace({"None": None}).dropna(how="all")
        for row in df.to_dict("records"):
            exchanges = []
            if exchanges_str := row.pop("exchanges", None):
                exchanges = [get_exchange(e) for e in exchanges_str.split(" ")]
            if exchange := row.pop("exchange", None):
                exchanges.append(get_exchange(exchange))
            row["instrument_type"] = get_instrument_type(row.get("instrument_type", None))
            if ticker := row.get("ticker", None):
                row["ticker"] = ticker.replace("'", "").split("-")[0]

            row["exchanges"] = exchanges
            row["country"] = get_country(row.get("country", None))
            classifications = []
            if gics_classification := row.pop("gics_classification", None):
                classifications.append(
                    {
                        "code_aggregated": gics_classification,
                        "group": ClassificationGroup.objects.get(is_primary=True).id,
                    }
                )
            if trbc_classification := row.pop("trbc_classification", None):
                group, created = ClassificationGroup.objects.get_or_create(name="TRBC")
                classifications.append({"code_aggregated": trbc_classification, "group": group.id})
            row["classification"] = classifications
            data.append({k: v for k, v in row.items() if v})
    return {"data": data}
