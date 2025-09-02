from contextlib import suppress
from datetime import date, timedelta

from celery import shared_task
from django.db import transaction
from django.db.models import ProtectedError, Q
from pandas.tseries.offsets import BDay
from tqdm import tqdm

from wbfdm.models import Instrument, InstrumentPrice
from wbfdm.sync.runner import (  # noqa: F401
    initialize_exchanges,
    initialize_instruments,
    synchronize_exchanges,
    synchronize_instruments,
)

from .signals import investable_universe_updated


@shared_task(queue="portfolio")
def update_of_investable_universe_data(
    start: date | None = None,
    end: date | None = None,
    with_background_tasks: bool = True,
    instrument_ids: list[int] | None = None,
):
    """
    Update the investable universe data on a daily basis.

    Parameters:
    - start (date | None): The start date for updating data. If None, defaults to three business days before 'end'.
    - end (date | None): The end date for updating data. If None, defaults to the current date.
    - with_background_tasks (bool | True): If true, will trigger the post import background tasks automatically.
    - instrument_ids (list[int] | None): if specified, narrow down the instrument queryset with this list ids

    Notes:
    - The function resets the investable universe by marking all instruments as not in the investable universe.
    - It then updates all instruments marked as part of the investable universe.
    - If 'end' is not provided, it defaults to the current date.
    - If 'start' is not provided, it defaults to three business days before 'end'.

    Returns:
    None
    """
    if not end:
        end = (
            date.today() - BDay(1)
        ).date()  # we don't import today price in case the dataloader returns duplicates (e.g. DSWS)
    if not start:
        start = (end - BDay(3)).date()  # override three last day by default
    Instrument.investable_universe.update(
        is_investable_universe=True
    )  # ensure all the investable universe is marked as such
    instruments = Instrument.active_objects.filter(is_investable_universe=True, delisted_date__isnull=True).exclude(
        Q(is_managed=True)
        | Q(dl_parameters__market_data__path="wbfdm.contrib.internal.dataloaders.market_data.MarketDataDataloader")
    )  # we exclude product and index managed to avoid circular import
    if instrument_ids:
        instruments = instruments.filter(id__in=instrument_ids)
    prices = list(instruments.get_instrument_prices_from_market_data(start, end))
    Instrument.bulk_save_instrument_prices(prices)
    investable_universe_updated.send(sender=Instrument, end_date=end)
    if with_background_tasks:
        daily_update_instrument_price_statistics.delay(from_date=start, to_date=end)
        update_instrument_metrics_as_task.delay()


@shared_task(queue="portfolio")
def update_instrument_metrics_as_task():
    instruments = Instrument.active_objects.filter(is_investable_universe=True)
    for instrument in tqdm(instruments, total=instruments.count()):
        instrument.update_last_valuation_date()


@shared_task(queue="portfolio")
def synchronize_instruments_as_task():
    synchronize_instruments()


@shared_task(queue="portfolio")
def synchronize_exchanges_as_task():
    synchronize_exchanges()


@shared_task(queue="portfolio")
def full_synchronization_as_task():
    # we get all instrument without name or where we would expect a parent and consider them for clean up.
    qs = Instrument.objects.filter(prices__isnull=True).filter(
        (Q(name="") & Q(name_repr="")) | (Q(source__in=["qa-ds2-security", "qa-ds2-quote"]) & Q(parent__isnull=True))
    )
    for instrument in qs:
        with suppress(ProtectedError):
            instrument.delete()
    initialize_exchanges()
    initialize_instruments()
    with transaction.atomic():
        Instrument.objects.rebuild()  # rebuild MPTT tree


# Daily synchronization tasks.
# This tasks needs to be ran at maximum once a day in order to guarantee data consitency in
# case of change in change (e.g. reimport).
@shared_task(queue="portfolio")
def daily_update_instrument_price_statistics(from_date: date = None, to_date: date = None):
    if not to_date:
        to_date = date.today()
    if not from_date:
        from_date = to_date - timedelta(days=3)
    # We query for the last 7 days unsynch instrument prices.
    prices = InstrumentPrice.objects.filter(date__gte=from_date, date__lte=to_date)
    objs = []
    for p in tqdm(prices.iterator(), total=prices.count()):
        p.compute_and_update_statistics()
        objs.append(p)
    InstrumentPrice.objects.bulk_update(
        objs,
        fields=["sharpe_ratio", "correlation", "beta", "annualized_daily_volatility", "volume_50d", "volume_200d"],
        batch_size=1000,
    )
