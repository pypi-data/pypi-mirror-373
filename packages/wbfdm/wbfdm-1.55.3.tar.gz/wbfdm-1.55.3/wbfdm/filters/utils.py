from datetime import date

from pandas.tseries.offsets import BDay, BMonthBegin, BMonthEnd
from psycopg.types.range import DateRange
from wbcore.utils.date import current_quarter_date_start

from wbfdm.models import Classification, Instrument
from wbfdm.preferences import get_default_classification_group


def _get_default_classification_group_id(field, request, view, **kwargs):
    if classification_id := view.kwargs.get("classification_id", None):
        return Classification.objects.get(id=classification_id).group.id
    if group := get_default_classification_group():
        return group.id
    return None


def get_earliest_date(field, request, view):
    instrument_id = None
    if "instrument_id" in view.kwargs:
        instrument_id = view.kwargs["instrument_id"]
    if "instrument_id" in request.GET:
        instrument_id = request.GET["instrument_id"]
    if instrument_id:
        _date = Instrument.objects.get(id=instrument_id).inception_date
    else:
        _date = current_quarter_date_start()
    return (_date + BDay(0)).date()


def get_latest_date(field, request, view, **kwargs):
    instrument_id = None
    if "instrument_id" in view.kwargs:
        instrument_id = view.kwargs["instrument_id"]
    if "instrument_id" in request.GET:
        instrument_id = request.GET["instrument_id"]
    if instrument_id and (instrument := Instrument.objects.get(id=instrument_id)) and instrument.delisted_date:
        _date = instrument.delisted_date
    else:
        _date = date.today()
    return (_date - BDay(0)).date()


def last_period_start(*args, **kwargs):
    return (date.today() - BMonthBegin(1)).date()


def last_period_end(*args, **kwargs):
    return (date.today() + BMonthEnd(1)).date()


def last_period_date_range(*args, **kwargs):
    return DateRange(last_period_start(*args, **kwargs), last_period_end(*args, **kwargs))
