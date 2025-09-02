from wbfdm.import_export.backends.refinitiv.geographic_segment import DEFAULT_MAPPING

from .utils import parse_periodic_fundamental_data


def parse(import_source):
    return parse_periodic_fundamental_data(import_source, DEFAULT_MAPPING)
