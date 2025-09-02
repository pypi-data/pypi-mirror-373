from datetime import datetime
from io import BytesIO

from wbcore.contrib.io.backends import register

from .fundamental import DataBackend as ParentDataBackend

DEFAULT_MAPPING = {
    "WC19601": "segment_1_sales",
    "WC19600 ": "segment_1_description",
    "WC19611": "segment_2_sales",
    "WC19610 ": "segment_2_description",
    "WC19621": "segment_3_sales",
    "WC19620 ": "segment_3_description",
}


@register("Geographic Segment", provider_key="refinitiv", save_data_in_import_source=False, passive_only=False)
class DataBackend(ParentDataBackend):
    def get_files(
        self,
        execution_time: datetime,
        obj_external_ids: list[str] = None,
        **kwargs,
    ) -> BytesIO:
        yield from super().get_files(
            execution_time,
            obj_external_ids=obj_external_ids,
            fields=list(DEFAULT_MAPPING.keys()),
            filename="geographic_segment",
            **kwargs,
        )
