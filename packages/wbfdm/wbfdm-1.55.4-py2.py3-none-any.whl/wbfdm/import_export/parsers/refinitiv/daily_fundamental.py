from wbfdm.import_export.backends.refinitiv.daily_fundamental import DEFAULT_MAPPING

from .utils import parse_daily_fundamental_data


def parse(import_source):
    return parse_daily_fundamental_data(import_source, DEFAULT_MAPPING, extra_normalization_map={"free_cash": 1000})
