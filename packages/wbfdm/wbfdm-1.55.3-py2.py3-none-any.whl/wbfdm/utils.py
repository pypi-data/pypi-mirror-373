from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas.core.indexes.base import Index


def rename_period_index_level_to_repr(df):
    """
    given a dataframe with multi index (year, interim, **other), with interim as a index number from 0 - 4, rename the level 1 index to its string representation (e.g. Q for quarter, S for semester, T for trimister and Y for yearly)

    Returns:
        The dataframe whose index level 1 has been renamed according to its period representation

    """

    if "period_type" in df.index.names:
        df = df.reset_index()
        df["interim"] = df["period_type"] + df["interim"].astype(str)
        df.loc[df["interim"] == "Y0", "interim"] = "Y"
        df = df.drop(columns=["period_type"])
        df = df.set_index(["year", "interim"])
    else:
        renamed_index = []
        for row in df.index:
            if row[1] == 0:
                period_repr = "Y"
            else:
                interim_count = (
                    df.drop(0, level=1, errors="ignore")
                    .loc[(row[0], slice(None), slice(None)), :]
                    .index.get_level_values(1)
                    .max()
                )
                if interim_count == 2:
                    period_repr = f"S{row[1]}"
                elif interim_count == 3:
                    period_repr = f"T{row[1]}"
                elif interim_count == 4:
                    period_repr = f"Q{row[1]}"
                else:
                    period_repr = f"P{row[1]}"

            renamed_index.append((row[0], period_repr, *(row[2:] if len(row) > 2 else ())))
        df = df.set_index([renamed_index])
    return df


def rename_date_columns(columns: "Index", fmt: str) -> dict[str, str]:
    column_mapping = dict()
    for col in filter(lambda col: isinstance(col, date), columns):
        column_mapping[col] = col.strftime(fmt)

    return column_mapping
