import json

import pandas as pd
from django.contrib.contenttypes.models import ContentType

from wbfdm.models import Instrument


def parse(import_source):
    content = json.load(import_source.file)
    data = []
    equity_content_type_id = ContentType.objects.get_for_model(Instrument).id
    for org_data in content:
        if (revenue_data := org_data.get("orgRevenue", None)) and not (df := pd.DataFrame(revenue_data)).empty:
            df = df[["revenueFiscalYear", "revenueMin", "revenueMax"]]
            df["revenue"] = (df.revenueMin + df.revenueMax) * 1e6 / 2
            df = df[["revenue", "revenueFiscalYear"]].rename(
                columns={"revenueFiscalYear": "period__period_year", "revenue": "revenue"}
            )
            df = df.groupby("period__period_year").mean().reset_index()
            df.period__period_year = df.period__period_year.astype(int)
            df["period__period_type"] = "FiscalPeriod.PeriodTypeChoice.ANNUAL"  # TODO REFACTORING
            df["period__period_interim"] = True
            df["period__period_end_date"] = df.period__period_year.apply(lambda x: f"{x}-12-31")
            df["instrument__provider_id"] = org_data["orgId"]
            df["instrument__content_type"] = equity_content_type_id
            data.extend(df.to_dict("records"))
        elif (
            (kpi_data := org_data.get("orgKPIs", None))
            and (last_revenue_max := kpi_data.get("latestRevenueMax", None))
            and (last_revenue_min := kpi_data.get("latestRevenueMin", None))
            and (last_revenue_year := kpi_data.get("latestRevenueFiscalYear", None))
        ):
            fiscal_year = int(last_revenue_year)
            data.append(
                {
                    "revenue": (last_revenue_max + last_revenue_min) / 2,
                    "period__period_type": "FiscalPeriod.PeriodTypeChoice.ANNUAL",  # TODO REFACTORING,
                    "period__period_interim": True,
                    "period__period_year": fiscal_year,
                    "period__period_end_date": f"{fiscal_year}-12-31",
                    "instrument__provider_id": org_data["orgId"],
                    "instrument__content_type": equity_content_type_id,
                }
            )
    return {"data": data}
