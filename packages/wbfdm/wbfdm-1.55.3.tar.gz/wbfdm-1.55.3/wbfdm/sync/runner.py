from django.conf import settings
from django.utils.module_loading import import_string


def initialize_instruments():
    for sync in map(import_string, getattr(settings, "INSTRUMENT_SYNC", [])):
        sync().update()


def initialize_exchanges():
    for sync in map(import_string, getattr(settings, "EXCHANGE_SYNC", [])):
        sync().update()


def synchronize_instruments():
    for sync in map(import_string, getattr(settings, "INSTRUMENT_SYNC", [])):
        sync().trigger_partial_update()


def synchronize_exchanges():
    for sync in map(import_string, getattr(settings, "EXCHANGE_SYNC", [])):
        sync().trigger_partial_update()
