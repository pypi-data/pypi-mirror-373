import pandas as pd

from wbfdm.enums import ESG
from wbfdm.models.instruments.instruments import InstrumentQuerySet


def get_esg_df(instruments: InstrumentQuerySet, esg: ESG, **kwargs) -> pd.Series:
    df = pd.DataFrame(instruments.dl.esg(values=[esg]))
    if not df.empty:
        return df.pivot_table(
            index="instrument_id", values="value", columns="factor_code", aggfunc="first", dropna=False
        )[esg.value]
    else:
        return pd.Series(dtype="float64")
