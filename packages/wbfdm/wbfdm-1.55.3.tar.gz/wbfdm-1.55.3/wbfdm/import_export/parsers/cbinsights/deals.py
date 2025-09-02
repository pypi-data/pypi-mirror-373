import numpy as np
import pandas as pd

from wbfdm.models import Deal

COLUMNS_MAP = {
    "dealDate": "date",
    "fundedOrg": "equity__provider_id",
    "dealSizeInMillions": "transaction_amount",
    "investors": "investors",
    "fundingRound": "funding_round",
    "fundingRoundCategory": "funding_round_category",
    "valuationInMillions": "valuation",
    "valuationIsEstimate": "valuation_estimated",
    "valuationSourceType": "valuation_source_type",
    "valuationSourceUrls": "valuation_media_mention_source_urls",
    "dealId": "external_id",
}


def parse(import_source):
    def _parse_investors(investors):
        return [{"provider_id": investor["orgId"]} for investor in investors]

    data = []
    df = pd.read_json(import_source.file, orient="records")

    df = df.rename(columns=COLUMNS_MAP)
    df["equity__provider_id"] = df["equity__provider_id"].apply(lambda x: x["orgId"])
    df["type"] = Deal.Types.DEAL
    if not df.empty:
        df["investors"] = df.investors.apply(lambda x: _parse_investors(x))
        df["valuation"] *= 1e6
        df["transaction_amount"] *= 1e6
        df = df.drop(columns=df.columns.difference(COLUMNS_MAP.values()))
        df = df.replace([np.inf, -np.inf, np.nan], None)
        df = df[~df["transaction_amount"].isnull()]
        data.extend(df.to_dict("records"))

    return {"data": data}
