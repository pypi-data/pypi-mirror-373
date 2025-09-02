from wbfdm.import_export.backends.refinitiv.fundamental import DEFAULT_MAPPING

from .utils import parse_periodic_fundamental_data


def parse(import_source):
    return parse_periodic_fundamental_data(
        import_source, DEFAULT_MAPPING, extra_normalization_map={"company_tax_rate": 0.01}
    )
