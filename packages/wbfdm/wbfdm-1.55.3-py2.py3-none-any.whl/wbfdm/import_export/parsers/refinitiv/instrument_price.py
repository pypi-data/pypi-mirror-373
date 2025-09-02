import numpy as np
import pandas as pd

from wbfdm.import_export.backends.refinitiv.instrument_price import DEFAULT_MAPPING

from .utils import _clean_and_return_dict


def parse(import_source):
    # Read Json as dataframe
    df = pd.read_json(import_source.file, orient="records")
    df = df.replace([np.inf, -np.inf, np.nan], None)
    # Sanitize df and rename columns to model knowledge's
    df = (
        df.replace({"NA": None})
        .rename(columns=DEFAULT_MAPPING)
        .rename(columns={"Instrument": "instrument", "Dates": "date"})
    )
    # Sanitize
    df = df.replace([np.inf, -np.inf, np.nan], None)
    df = df.dropna(how="all", subset=df.columns.difference(["instrument"]))

    df["date"] = pd.to_datetime(df["date"], utc=True, unit="ms")
    df = df.sort_values(by="date", ascending=True)
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df = df.replace([np.inf, -np.inf, np.nan], None)
    return {"data": _clean_and_return_dict(df)}
