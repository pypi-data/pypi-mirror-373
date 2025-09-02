from contextlib import suppress
from itertools import batched
from typing import Iterator

import pypika as pk
from django.db import ProgrammingError, connections
from pypika import functions as fn
from pypika.analytics import RowNumber
from pypika.enums import SqlTypes
from pypika.terms import LiteralValue
from wbcore.contrib.dataloader.dataloaders import Dataloader
from wbcore.contrib.dataloader.utils import dictfetchall

from wbfdm.dataloaders.protocols import OfficersProtocol
from wbfdm.dataloaders.types import OfficerDataDict


class RKDOfficersDataloader(OfficersProtocol, Dataloader):
    def officers(
        self,
    ) -> Iterator[OfficerDataDict]:
        lookup = {k: v for k, v in self.entities.values_list("dl_parameters__officers__parameters", "id")}

        # Define tables
        designation = pk.Table("RKDFndCmpOffTitleChg")
        officer = pk.Table("RKDFndCmpOfficer")
        temp_codes = pk.Table("#rkd_codes")

        # Build the query
        query = (
            pk.MSSQLQuery.select(
                fn.Concat(designation.Code, "-", RowNumber().orderby(officer.OfficerRank)).as_("id"),
                designation.Code.as_("external_identifier"),
                designation.Title.as_("position"),
                fn.Concat(
                    officer.Prefix,
                    " ",
                    officer.FirstName,
                    " ",
                    officer.LastName,
                    pk.Case().when(officer.Suffix.isnull(), "").else_(fn.Concat(", ", officer.Suffix)),
                ).as_("name"),
                officer.Age.as_("age"),
                officer.Sex.as_("sex"),
                fn.Cast(designation.DesgStartDt, SqlTypes.DATE).as_("start"),
            )
            .from_(designation)
            .join(officer)
            .on((designation.Code == officer.Code) & (designation.OfficerID == officer.Officerid))
            .where(designation.Code.isin([LiteralValue("select code from #rkd_codes")]))
            .where(designation.DesgEndDt.isnull())
            .orderby(officer.OfficerRank)
        )

        with connections["qa"].cursor() as cursor:
            # Create and populate temporary table
            with suppress(ProgrammingError):
                cursor.execute(
                    pk.MSSQLQuery.create_table(temp_codes).columns(pk.Column("code", SqlTypes.INTEGER)).get_sql()
                )
                for batch in batched(lookup.keys(), 1000):
                    placeholders = ",".join(map(lambda x: f"('{x}')", batch))
                    cursor.execute(f"insert into #rkd_codes values {placeholders};")

            cursor.execute(query.get_sql())

            for row in dictfetchall(cursor, OfficerDataDict):
                row["instrument_id"] = lookup[row["external_identifier"]]
                yield row

            # Clean up temporary table
            cursor.execute(pk.MSSQLQuery.drop_table(temp_codes).get_sql())
