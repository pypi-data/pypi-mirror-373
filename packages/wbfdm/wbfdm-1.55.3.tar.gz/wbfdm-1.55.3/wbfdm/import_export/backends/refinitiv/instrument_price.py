from datetime import datetime
from io import BytesIO
from typing import Optional

import pandas as pd
from django.db import models
from pandas.tseries.offsets import BDay
from wbcore.contrib.io.backends import AbstractDataBackend, register

from .mixin import DataBackendMixin
from .utils import Controller

DEFAULT_MAPPING = {
    "MV": "market_capitalization",
    "MVC": "market_capitalization_consolidated",
    "VO": "volume",
    "MAV#(X(VO),-50D,R)": "volume_50d",
    "BETA": "beta",
    "NOSH": "outstanding_shares",
    "IBNOSH": "outstanding_shares_consolidated",
    "P": "close",
    "PI": "price_index",
    "RY": "yield_redemption",
    "NR": "net_return",
    "IO": "offered_rate",
}

MUTUAL_FUND_TIMEDELTA_DAY_SHIFT = 7


@register("Instrument Price", provider_key="refinitiv", save_data_in_import_source=False, passive_only=False)
class DataBackend(DataBackendMixin, AbstractDataBackend):
    def __init__(self, import_credential: Optional[models.Model] = None, **kwargs):
        self.controller = Controller(import_credential.username, import_credential.password)

    def get_files(
        self,
        execution_time: datetime,
        obj_external_ids: list[str] = None,
        **kwargs,
    ) -> BytesIO:
        execution_date = execution_time.date()

        start = kwargs.get("start", (execution_date - BDay(2)).date())

        delayed_instrument_ids = list(
            filter(
                lambda x: True,
                obj_external_ids,
            )
        )
        obj_external_ids = list(filter(lambda v: v not in delayed_instrument_ids, obj_external_ids))
        # we get all active instruments even these were we are not suppose to fetch prices.
        fields = list(DEFAULT_MAPPING.keys())
        if obj_external_ids or delayed_instrument_ids:
            df_list = []
            if obj_external_ids:
                df_list.append(
                    self.controller.get_data(obj_external_ids, fields, start, execution_date, ibes_fields=["IBNOSH"])
                )
            if delayed_instrument_ids:
                # we need to get mutual fund price in a different batch because there is a price delay and the windows approach can't handle it otherwise
                df_list.append(
                    self.controller.get_data(
                        delayed_instrument_ids,
                        fields,
                        start - BDay(MUTUAL_FUND_TIMEDELTA_DAY_SHIFT),
                        execution_date,
                        ibes_fields=["IBNOSH"],
                    )
                )
            df = pd.concat(df_list, axis=0, ignore_index=True)
            if not df.empty:
                content_file = BytesIO()
                df.to_json(content_file, orient="records")
                file_name = f"instrument_price_{start:%Y-%m-%d}-{execution_date:%Y-%m-%d}_{datetime.timestamp(execution_time)}.json"
                yield file_name, content_file
