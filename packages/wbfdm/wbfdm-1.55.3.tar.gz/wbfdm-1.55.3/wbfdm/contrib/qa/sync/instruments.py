from django.db import connections
from wbfdm.contrib.qa.sync.utils import (
    get_item,
    trigger_partial_update,
    update_instruments,
    update_or_create_item,
)
from wbfdm.models import Instrument
from wbfdm.sync.abstract import Sync


class QACompanySync(Sync[Instrument]):
    SOURCE = "qa-ds2-company"

    def update(self, **kwargs):
        update_instruments("qa/sql/companies.sql", **kwargs)

    def update_or_create_item(self, external_id: int) -> Instrument:
        return update_or_create_item(external_id, self.get_item, self.SOURCE)

    def update_item(self, item: Instrument) -> Instrument:
        return self.update_or_create_item(item.source_id)

    def get_item(self, external_id: int) -> dict:
        return get_item(external_id, "qa/sql/companies.sql")

    def trigger_partial_update(self):
        trigger_partial_update(
            Instrument.objects.filter(source=self.SOURCE),
            "last_update",
            "DsCmpyCode",
            "DS2Company_changes",
            self.update,
            self.update_or_create_item,
        )


class QAInstrumentSync(Sync[Instrument]):
    SOURCE = "qa-ds2-security"

    def update(self, **kwargs):
        update_instruments("qa/sql/instruments.sql", parent_source="qa-ds2-company", **kwargs)

    def update_or_create_item(self, external_id: int) -> Instrument:
        return update_or_create_item(external_id, self.get_item, self.SOURCE, "qa-ds2-company")

    def update_item(self, item: Instrument) -> Instrument:
        return self.update_or_create_item(item.source_id)

    def get_item(self, external_id: int) -> dict:
        return get_item(external_id, "qa/sql/instruments.sql")

    def trigger_partial_update(self):
        trigger_partial_update(
            Instrument.objects.filter(source=self.SOURCE),
            "last_update",
            "DsSecCode",
            "DS2Security_changes",
            self.update,
            self.update_or_create_item,
        )


class QAQuoteSync(Sync[Instrument]):
    SOURCE = "qa-ds2-quote"

    def update(self, **kwargs):
        count = connections["qa"].cursor().execute("SELECT COUNT(*) FROM DS2ExchQtInfo").fetchone()[0]
        for offset in range(0, count, 100_000):
            update_instruments(
                "qa/sql/quotes.sql",
                parent_source="qa-ds2-security",
                context={"offset": offset, "batch": 100_000},
                **kwargs,
            )

    def update_or_create_item(self, external_id: int) -> Instrument:
        return update_or_create_item(external_id, self.get_item, self.SOURCE, "qa-ds2-security")

    def update_item(self, item: Instrument) -> Instrument:
        return self.update_or_create_item(item.source_id)

    def get_item(self, external_id: int) -> dict:
        return get_item(external_id, "qa/sql/quotes.sql")

    def trigger_partial_update(self):
        trigger_partial_update(
            Instrument.objects.filter(source=self.SOURCE),
            "last_update",
            "CONCAT(InfoCode, '-', ExchIntCode)",
            "DS2ExchQtInfo_changes",
            self.update,
            self.update_or_create_item,
        )
