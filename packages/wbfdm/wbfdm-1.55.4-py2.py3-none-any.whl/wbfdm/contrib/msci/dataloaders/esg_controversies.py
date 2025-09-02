from datetime import datetime
from typing import Iterator

from django.conf import settings
from wbcore.contrib.dataloader.dataloaders import Dataloader

from wbfdm.dataloaders.protocols import ESGControversyProtocol
from wbfdm.dataloaders.types import ESGControversyDataDict

from ..client import MSCIClient

CONTROVERY_ASSESSMENT_MAP = {
    "Minor": "MINOR",
    "Moderate": "MODERATE",
    "Severe": "SEVERE",
    "Very Severe": "VERY_SEVERE",
}
CONTROVERSY_STATUS_MAP = {
    "Ongoing": "ONGOING",
    "Partially Concluded": "PARTIALLY_CONCLUDED",
    "Concluded": "CONCLUDED",
}
CONTROVERSY_TYPE_MAP = {
    "Structural": "STRUCTURAL",
    "Non-Structural": "NON_STRUCTURAL",
}

CONTROVERSY_FLAG_MAP = {
    "Green": "GREEN",
    "Yellow": "YELLOW",
    "Orange": "ORANGE",
    "Red": "RED",
    "Unknown": "UNKNOWN",
}


class MSCIESGControversyDataloader(ESGControversyProtocol, Dataloader):
    def esg_controversies(self) -> Iterator[ESGControversyDataDict]:
        msci_client_id = getattr(settings, "MSCI_CLIENT_ID", None)
        msci_client_secret = getattr(settings, "MSCI_CLIENT_SECRET", None)
        if msci_client_id and msci_client_secret:
            client = MSCIClient(msci_client_id, msci_client_secret)
            lookup = {k: v for k, v in self.entities.values_list("dl_parameters__esg_controversies__parameters", "id")}
            factors = [
                "CONTROVERSY_CASE_ID",
                "CONTROVERSY_CASE_HEADLINE",
                "CONTROVERSY_LAST_REVIEWED",
                "CONTROVERSY_CASE_NARRATIVE",
                "CONTROVERSY_CASE_SOURCE",
                "CONTROVERSY_CASE_STATUS",
                "CONTROVERSY_CASE_TYPE",
                "CONTROVERSY_CASE_ASSESSMENT",
                "CONTROVERSY_CASE_COMPANY_RESPONSE",
                "CONTROVERSY_CASE_DATE_INITIATED",
                "CONTROVERSY_CASE_FLAG",
            ]
            for row in client.controversies(list(lookup.keys()), factors):
                isin = row.get("CLIENT_IDENTIFIER", "")
                instrument_id = lookup.get(isin, "")

                headline = row.get("CONTROVERSY_CASE_HEADLINE", "")
                narrative = row.get("CONTROVERSY_CASE_NARRATIVE", "")
                reviewed = row.get("CONTROVERSY_LAST_REVIEWED", None)
                initiated = row.get("CONTROVERSY_CASE_DATE_INITIATED", None)
                controversy_id = row.get("CONTROVERSY_CASE_ID", f"{isin}-{hash(headline)}")
                if controversy_id and narrative and headline and isin and instrument_id:
                    yield ESGControversyDataDict(
                        id=controversy_id,
                        instrument_id=instrument_id,
                        headline=headline,
                        narrative=narrative,
                        source=row.get("CONTROVERSY_CASE_SOURCE", ""),
                        review=datetime.strptime(reviewed, "%Y%m%d").date() if reviewed else None,
                        initiated=datetime.strptime(initiated, "%Y%m%d").date() if initiated else None,
                        response=row.get("CONTROVERSY_CASE_COMPANY_RESPONSE", ""),
                        assessment=CONTROVERY_ASSESSMENT_MAP.get(
                            row.get("CONTROVERSY_CASE_ASSESSMENT", "Minor"), None
                        ),
                        status=CONTROVERSY_STATUS_MAP.get(row.get("CONTROVERSY_CASE_STATUS", "Ongoing"), None),
                        type=CONTROVERSY_TYPE_MAP.get(row.get("CONTROVERSY_CASE_TYPE", "Structural"), None),
                        flag=CONTROVERSY_FLAG_MAP.get(row.get("CONTROVERSY_CASE_FLAG", "Green"), None),
                    )
