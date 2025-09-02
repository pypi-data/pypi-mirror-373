from datetime import date

import numpy as np
import pandas as pd
from wbcore.contrib.geography.models import Geography

REPORT_TYPE_MAP = {1: "Q", 2: "6M", 3: "4M", 4: "Y"}


def get_exchange(code):
    return {"mic_code": code}


def get_country(code):
    country = Geography.countries.filter(code_2=code).first()
    return country.id if country else None


def _clean_and_return_dict(df, extra_normalization_map=None):
    # df = df.groupby(df.columns, axis=1).sum()
    if extra_normalization_map:
        for col, den in extra_normalization_map.items():
            if col in df.columns:
                df[col] *= den
    if percent_fields_columns := list(filter(lambda x: "margin" in x, df.columns)):
        df[percent_fields_columns] = (
            df[percent_fields_columns] / 100
        )  # margin/percent type of data are given in base 100 by refinitiv
    df["instrument"] = df["instrument"].str.replace("^<|>", "", regex=True)
    df = df.rename(columns={"instrument": "instrument__provider_id"})
    # df["instrument__refinitiv_identifier_code"] = df["instrument__provider_id"] # We add this for backward compatibility reason
    df = df.replace([np.inf, -np.inf, np.nan], None)
    return df.to_dict("records")


def parse_daily_fundamental_data(import_source, default_mapping, extra_normalization_map=None):
    df = pd.read_json(import_source.file, orient="records")
    df = df.replace([np.inf, -np.inf, np.nan], None)
    mapping = {**default_mapping, "Instrument": "instrument", "Dates": "date"}
    df = df.rename(columns=mapping).dropna(how="all", axis=1)
    df = df.drop(columns=df.columns.difference(mapping.values()))
    data = list()
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], utc=True, unit="ms")
        df = df.sort_values(by="date", ascending=True)
        df.date = df.date.dt.strftime("%Y-%m-%d")
        data = _clean_and_return_dict(df, extra_normalization_map=extra_normalization_map)
    return {"data": data}


def parse_periodic_fundamental_data(import_source, default_mapping, extra_normalization_map=None):
    def _get_fiscal_period(_date, frequency):
        fiscal_period = 0
        for index, p in enumerate(
            pd.period_range(start=date(_date.year, 1, 1), end=date(_date.year, 12, 31), freq=frequency)
        ):
            if _date >= p.start_time.date() and _date <= p.end_time.date():
                fiscal_period = index + 1
        return fiscal_period

    df = pd.read_json(import_source.file, orient="records")
    df = df.replace([np.inf, -np.inf, np.nan], None)
    mapping = {**default_mapping, "Instrument": "instrument", "Dates": "date"}
    df = df.rename(columns=mapping).dropna(how="all", axis=1)

    df = df.drop(columns=df.columns.difference([*mapping.values(), "period__period_interim"]))
    df = df.dropna(
        how="all",
        subset=df.columns.difference(
            ["instrument", "date", "period__period_interim", "period__period_end_date", "period__period_type"]
        ),
    )
    df = df.dropna(
        how="any",
        subset=df.columns.intersection(["instrument", "date", "period__period_end_date", "period__period_type"]),
    )
    data = list()
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], utc=True, unit="ms")
        df["period__period_end_date"] = pd.to_datetime(df["period__period_end_date"], utc=True)
        df["period__period_year"] = df.date.dt.year
        df["period__period_type"] = df["period__period_type"].map(REPORT_TYPE_MAP)
        df["period__period_type"] = df["period__period_type"].fillna("Q")  # Assuming empty period type is quaterly
        df["period__period_index"] = df[["date", "period__period_type"]].apply(
            lambda x: _get_fiscal_period(x["date"].date(), x["period__period_type"]), axis=1
        )
        del df["date"]

        df["period__period_end_date"] = df["period__period_end_date"] + pd.offsets.MonthEnd(0)
        df["period__period_end_date"] = df["period__period_end_date"].dt.strftime("%Y-%m-%d")
        df = df.sort_values(by="period__period_end_date")

        if "employee_count" in df.columns:
            df["employee_count"] = df["employee_count"].bfill()
        data = _clean_and_return_dict(df, extra_normalization_map=extra_normalization_map)
    return {"data": data}
