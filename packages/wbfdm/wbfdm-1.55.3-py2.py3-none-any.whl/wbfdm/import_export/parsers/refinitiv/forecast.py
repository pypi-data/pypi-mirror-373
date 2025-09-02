from wbfdm.import_export.backends.refinitiv.forecast import DEFAULT_MAPPING

from .utils import parse_daily_fundamental_data


def parse(import_source):
    return parse_daily_fundamental_data(import_source, DEFAULT_MAPPING)
