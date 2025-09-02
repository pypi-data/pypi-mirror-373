from wbcore import filters as wb_filters

from wbfdm.models import Exchange


class ExchangeFilterSet(wb_filters.FilterSet):
    class Meta:
        model = Exchange
        fields = {
            "name": ["exact", "icontains"],
            "mic_code": ["exact", "icontains"],
            "operating_mic_code": ["exact", "icontains"],
            "bbg_composite_primary": ["exact"],
            "bbg_composite": ["exact", "icontains"],
            "refinitiv_identifier_code": ["exact", "icontains"],
            "refinitiv_mnemonic": ["exact", "icontains"],
            "country": ["exact"],
            "city": ["exact"],
            "website": ["exact", "icontains"],
            "comments": ["exact", "icontains"],
            "opening_time": ["exact", "gte", "lte"],
            "closing_time": ["exact", "gte", "lte"],
        }
