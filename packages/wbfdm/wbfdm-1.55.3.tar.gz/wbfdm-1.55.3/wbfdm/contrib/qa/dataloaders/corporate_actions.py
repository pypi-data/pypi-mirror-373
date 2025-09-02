from contextlib import suppress
from datetime import date
from itertools import batched
from typing import Iterator

import pypika as pk
from django.db import ProgrammingError, connections
from pypika import functions as fn
from pypika.enums import SqlTypes
from pypika.terms import LiteralValue
from wbcore.contrib.dataloader.dataloaders import Dataloader
from wbcore.contrib.dataloader.utils import dictfetchall

from wbfdm.contrib.qa.dataloaders.utils import SOURCE_DS2
from wbfdm.dataloaders.protocols import CorporateActionsProtocol
from wbfdm.dataloaders.types import CorporateActionDataDict


class DatastreamCorporateActionsDataloader(CorporateActionsProtocol, Dataloader):
    def corporate_actions(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> Iterator[CorporateActionDataDict]:
        lookup = {k: v for k, v in self.entities.values_list("dl_parameters__corporate_actions__parameters", "id")}

        cap_event = pk.Table("Ds2CapEvent")
        effective_date = fn.Cast(cap_event.EffectiveDate, SqlTypes.DATE)
        infocode = pk.Table("#ds2infocode")

        query = (
            pk.MSSQLQuery.select(
                cap_event.InfoCode.as_("external_identifier"),
                fn.Concat(cap_event.InfoCode, "_", effective_date).as_("id"),
                effective_date.as_("valuation_date"),
                SOURCE_DS2,
                cap_event.ActionTypeCode.as_("action_code"),
                cap_event.EventStatusCode.as_("event_code"),
                cap_event.NumOldShares.as_("old_shares"),
                cap_event.NumNewShares.as_("new_shares"),
                cap_event.ISOCurrCode.as_("currency"),
            )
            .from_(cap_event)
            .where(cap_event.InfoCode.isin([LiteralValue("select infocode from #ds2infocode")]))
            .orderby(cap_event.EffectiveDate, order=pk.Order.desc)
        )

        if from_date:
            query = query.where(cap_event.EffectiveDate >= from_date)

        if to_date:
            query = query.where(cap_event.EffectiveDate <= to_date)

        with connections["qa"].cursor() as cursor:
            # Create temporary table if it doesn't exist
            with suppress(ProgrammingError):
                cursor.execute(
                    pk.MSSQLQuery.create_table(infocode).columns(pk.Column("infocode", SqlTypes.INTEGER)).get_sql()
                )
                for batch in batched(lookup.keys(), 1000):
                    cursor.execute(f"insert into #ds2infocode values {','.join(map(lambda x: f'({x})', batch))};")

            cursor.execute(query.get_sql())
            for row in dictfetchall(cursor, CorporateActionDataDict):
                row["instrument_id"] = lookup[row["external_identifier"]]
                yield row

            # Clean up temporary table
            cursor.execute(pk.MSSQLQuery.drop_table(infocode).get_sql())
