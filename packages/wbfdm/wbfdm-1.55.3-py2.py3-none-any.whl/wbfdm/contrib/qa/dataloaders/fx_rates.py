from datetime import date, timedelta
from typing import Iterator

import pypika as pk
from django.db import connections
from pypika import Case
from pypika import functions as fn
from pypika.enums import Order, SqlTypes
from wbcore.contrib.dataloader.dataloaders import Dataloader
from wbcore.contrib.dataloader.utils import dictfetchall

from wbfdm.dataloaders.protocols import FXRateProtocol
from wbfdm.dataloaders.types import FXRateDict


class DatastreamFXRatesDataloader(FXRateProtocol, Dataloader):
    def fx_rates(
        self,
        from_date: date,
        to_date: date,
        target_currency: str,
    ) -> Iterator[FXRateDict]:
        currencies = list(self.entities.values_list("currency__key", flat=True))
        # Define tables
        fx_rate = pk.Table("DS2FxRate")
        fx_code = pk.Table("DS2FxCode")

        # Base query to get data we always need unconditionally
        query = (
            pk.MSSQLQuery.from_(fx_rate)
            # We join on _codes, which removes all instruments not in _codes - implicit where
            .join(fx_code)
            .on(fx_rate.ExRateIntCode == fx_code.ExRateIntCode)
            .where((fx_rate.ExRateDate >= from_date) & (fx_rate.ExRateDate <= to_date + timedelta(days=1)))
            .where((fx_code.ToCurrCode == target_currency) & fx_code.FromCurrCode.isin(currencies))
            .orderby(fx_rate.ExRateDate, order=Order.desc)
            .select(
                fn.Cast(fx_rate.ExRateDate, SqlTypes.DATE).as_("fx_date"),
                fn.Concat(fx_code.FromCurrCode, fx_code.ToCurrCode).as_("currency_pair"),
                (Case().when(fx_code.FromCurrCode == target_currency, 1).else_(1 / fx_rate.midrate)).as_("fx_rate"),
            )
        )
        with connections["qa"].cursor() as cursor:
            cursor.execute(query.get_sql())
            yield from dictfetchall(cursor, FXRateDict)
