from datetime import date

from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import DatePreference, IntPreference, StringPreference

fdm = Section("wbfdm")


@global_preferences_registry.register
class DefaultClassificationGroup(IntPreference):
    section = fdm
    name = "default_classification_group"
    default = 0

    verbose_name = "Default Classification Group"


@global_preferences_registry.register
class DefaultStartDateHistoricalImport(DatePreference):
    section = fdm
    name = "default_start_date_historical_import"
    default = date(2015, 1, 1)

    verbose_name = "Default Start Date"
    help_text = "Default start date in historical import"


@global_preferences_registry.register
class NonTickerWords(StringPreference):
    section = fdm
    name = "non_ticker_words"
    default = ""

    verbose_name = "Non Ticker Words"
    help_text = "Comma Separated list of non-ticker words"


class FinancialSummarySectionName(StringPreference):
    section = fdm
    name = "financial_summary_section_name"
    default = "Financial Summary"

    verbose_name = "Financial Summary Section Name"
    help_text = "This name set the tab section name shown from the instance view"
