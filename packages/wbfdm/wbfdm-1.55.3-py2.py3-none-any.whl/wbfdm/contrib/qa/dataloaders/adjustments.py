from contextlib import suppress
from datetime import date
from itertools import batched
from typing import Iterator

import pypika as pk
from django.db import ProgrammingError, connections
from pypika import functions as fn
from pypika.enums import Order, SqlTypes
from pypika.terms import LiteralValue
from wbcore.contrib.dataloader.dataloaders import Dataloader
from wbcore.contrib.dataloader.utils import dictfetchall

from wbfdm.contrib.qa.dataloaders.utils import SOURCE_DS2
from wbfdm.dataloaders.protocols import AdjustmentsProtocol
from wbfdm.dataloaders.types import AdjustmentDataDict


class DatastreamAdjustmentsDataloader(AdjustmentsProtocol, Dataloader):
    def adjustments(self, from_date: date | None = None, to_date: date | None = None) -> Iterator[AdjustmentDataDict]:
        lookup = {k: v for k, v in self.entities.values_list("dl_parameters__adjustments__parameters", "id")}

        adj = pk.Table("DS2Adj")
        adj_date = fn.Cast(adj.AdjDate, SqlTypes.DATE).as_("adjustment_date")
        adj_end_date = fn.Cast(adj.EndAdjDate, SqlTypes.DATE).as_("adjustment_end_date")

        infocode = pk.Table("#ds2infocode")

        query = (
            pk.MSSQLQuery.select(
                adj.InfoCode.as_("external_identifier"),
                fn.Concat(adj.InfoCode, "_", adj_date).as_("id"),
                adj_date,
                adj_end_date,
                SOURCE_DS2,
                adj.AdjFactor.as_("adjustment_factor"),
                adj.CumAdjFactor.as_("cumulative_adjustment_factor"),
            )
            .from_(adj)
            .where(adj.AdjType == 2)
            .where(adj.InfoCode.isin([LiteralValue("select infocode from #ds2infocode")]))
            .orderby(adj.AdjDate, order=Order.desc)
        )

        if from_date:
            query = query.where(adj.AdjDate >= from_date)

        if to_date:
            query = query.where(adj.AdjDate <= to_date)

        with connections["qa"].cursor() as cursor:
            # we suppress an error here, because if the temporary table already exists
            # then we do not want to fail. It should not fail, but if a previous run did
            # not clean up the table properly, then at least we do not get stuck here
            with suppress(ProgrammingError):
                cursor.execute(
                    pk.MSSQLQuery.create_table(infocode).columns(pk.Column("infocode", SqlTypes.INTEGER)).get_sql()
                )
                for batch in batched(lookup.keys(), 1000):
                    cursor.execute(f"insert into #ds2infocode values {",".join(map(lambda x: f"({x})", batch))};")

            cursor.execute(query.get_sql())

            for row in dictfetchall(cursor, AdjustmentDataDict):
                row["instrument_id"] = lookup[row["external_identifier"]]
                yield row

            # here we remove the temporary table again to avoid data spillage
            # cursor.execute(pk.MSSQLQuery.drop_table(infocode).get_sql())
