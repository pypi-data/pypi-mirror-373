from itertools import batched
from typing import Iterator

from django.db import connections
from jinjasql import JinjaSql
from wbcore.contrib.dataloader.dataloaders import Dataloader
from wbcore.contrib.dataloader.utils import dictfetchall

from wbfdm.dataloaders.protocols import ReportDateProtocol
from wbfdm.dataloaders.types import ReportDateDataDict


class IbesReportingDateDataloader(ReportDateProtocol, Dataloader):
    def reporting_dates(self, only_next: bool = True) -> Iterator[ReportDateDataDict]:
        lookup = {k: v for k, v in self.entities.values_list("dl_parameters__reporting_dates__parameters", "id")}

        sql = """
            with next_events as (
                select
                    *,
                    row_number() over (partition by EstPermID, PerType order by PerEndDate) as rn
                from TREExpectedRptDate
                where StartDate > getdate()
            )

            select
                rp.EstPermID as external_id,
                'qa-ibes' as source,
                convert(date, rp.PerEndDate) as per_end_date,
                convert(date, rp.StartDate) as start_date,
                convert(date, rp.EndDate) as end_date,
                iif(rp.PerType=4, 0, 1) as interim,
                case
                    when rp.MarketPhase = 'AMC' then 'after_market'
                    when rp.MarketPhase = 'BMO' then 'before_market'
                    else null
                end as market_phase,
                lower(rp.Status) as status
            {% if only_next %}
                from next_events as rp
            {% else %}
                from TREExpectedRptDate as rp
            {% endif %}
            where rp.EstPermID in (
            {% for instrument in instruments %}
                {{instrument}} {% if not loop.last %}, {% endif %}
            {% endfor %}
            )
            {% if only_next %}
                AND rp.rn = 1
            {% endif %}
        """
        for batch in batched(lookup.keys(), 500):
            query, bind_params = JinjaSql(param_style="format").prepare_query(
                sql,
                {
                    "instruments": batch,
                    "only_next": only_next,
                },
            )
            with connections["qa"].cursor() as cursor:
                cursor.execute(
                    query,
                    bind_params,
                )
                for row in dictfetchall(cursor):
                    row["instrument_id"] = lookup[row["external_id"]]
                    row["interim"] = bool(row["interim"])
                    yield row
