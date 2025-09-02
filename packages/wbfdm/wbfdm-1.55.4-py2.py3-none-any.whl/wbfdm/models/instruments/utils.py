import re
from functools import lru_cache

from wbcore.contrib.currency.models import Currency
from wbcore.contrib.geography.models import Geography

from wbfdm.preferences import get_non_ticker_words

START_DELIMITER = r"(?:^|(?<=[(\s\.\-<]))"
END_DELIMITER = r"(?=[\s\.)\-\>'’,]|$)"


@lru_cache()
def non_ticker_words():
    return (
        list(Geography.countries.values_list("code_2", flat=True))
        + list(Geography.countries.values_list("code_3", flat=True))
        + list(Currency.objects.values_list("key", flat=True))
        + get_non_ticker_words()
    )


def re_ric(input: str):
    # [(\s<]([A-Z]{2}[A-Za-z0-9_.-]+\.[A-Za-z]+)[(\s>] led to too many false positive (e.g. end of sentence when whitespace are missing. We refined by considering only uppercase code
    return set(re.findall(START_DELIMITER + r"([A-Z0-9]{2}[A-Z0-9_.-]+\.[A-Z]+)" + END_DELIMITER, input))


def re_bloomberg(input: str):
    return set(
        filter(
            lambda x: x not in non_ticker_words(),
            re.findall(START_DELIMITER + r"([A-Z]{2,5}(?:\-[A-Z]{2})?)" + END_DELIMITER, input),
        )
    )


def re_isin(input: str):
    return set(re.findall(START_DELIMITER + r"([A-Z]{2}[A-Z0-9]{9}[0-9])" + END_DELIMITER, input))


def re_mnemonic(input: str):
    return set(re.findall(START_DELIMITER + r"([A-Z]+:[A-Z]+)" + END_DELIMITER, input))
