from contextlib import suppress

import numpy as np
from django.conf import settings
from django.contrib.messages import warning
from django.utils.functional import cached_property
from wbcore.cache.decorators import cache_table
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.pandas import fields as pf
from wbcore.serializers.fields.types import DisplayMode
from wbcore.utils.date import get_next_day_timedelta

from wbfdm.analysis.financial_analysis.statement_with_estimates import (
    StatementWithEstimates,
)
from wbfdm.enums import CalendarType
from wbfdm.filters import StatementWithEstimateFilter
from wbfdm.models.instruments import Instrument
from wbfdm.viewsets.configs.display.statement_with_estimates import (
    StatementWithEstimatesDisplayViewConfig,
)
from wbfdm.viewsets.configs.endpoints.statements import StatementsEndpointViewConfig
from wbfdm.viewsets.configs.titles.statement_with_estimates import (
    StatementTitleViewConfig,
)

from ..mixins import InstrumentMixin


@cache_table(
    timeout=lambda view: get_next_day_timedelta(),
    key_prefix=lambda view: f"_{view.instrument.id}_{view.financial_analysis_key}_{view.calendar_type}",
)
class StatementWithEstimatesPandasViewSet(InstrumentMixin, ExportPandasAPIViewSet):
    queryset = Instrument.objects.none()
    display_config_class = StatementWithEstimatesDisplayViewConfig
    endpoint_config_class = StatementsEndpointViewConfig
    title_config_class = StatementTitleViewConfig
    filterset_class = StatementWithEstimateFilter

    financial_analysis_mapping = {
        "income": ("income_statement_with_estimate", "Income Statement"),
        "balancesheet": ("balance_sheet_with_estimate", "Balance Sheet"),
        "cashflow": ("cash_flow_statement_with_estimate", "Cash Flow Statement"),
        "ratios": ("ratios_with_estimate", "Ratios"),
        "summary": ("summary_with_estimate", "Summary"),
        "margins": ("margins_with_estimates", "Margins"),
        "cashflow-ratios": ("cashflow_ratios_with_estimates", "Cashflow Ratios"),
        "asset-turnover-ratios": ("asset_turnover_with_estimates", "Asset-Turnover Ratios"),
        "credit": ("credit_with_estimates", "Credit"),
        "long-term-solvency": ("long_term_solvency_with_estimates", "Long-term Solvency"),
        "short-term-liquidity": ("short_term_liquidity_with_estimates", "Short-term Liquidity"),
    }

    def get_queryset(self):
        return Instrument.objects.filter(id=self.instrument.id)

    def get_pandas_fields(self, request):
        return pf.PandasFields(
            fields=[
                *[pf.FloatField(key=field, label=field, display_mode=DisplayMode.SHORTENED) for field in self.columns],
                pf.PKField(key="id", label="ID"),
                pf.CharField(key="financial", label="Financial"),
                pf.CharField(key="_group_key", label="Group Key"),
                pf.JsonField(key="_overwrites", label="Overwrites"),
                pf.SparklineField(key="progress", label="Yearly Trend", dimension="double"),
            ]
        )

    def get_dataframe(self, request, queryset, **kwargs):
        statement_with_estimate = StatementWithEstimates(self.instrument, calendar_type=self.calendar_type)
        financial_analysis_result = getattr(
            statement_with_estimate, self.financial_analysis_mapping[self.financial_analysis_key][0]
        )
        df = financial_analysis_result.formatted_df

        year_columns = list(filter(lambda col: "Y" in col, df.columns))
        if year_columns:
            df["progress"] = (
                df[year_columns]
                .replace([np.inf, -np.inf, np.nan], None)
                .apply(lambda x: list(x.to_dict().items()), axis=1)
            )

        self.extra_cache_kwargs["_estimate_mapping"] = financial_analysis_result.estimated_mapping
        self.extra_cache_kwargs["_columns"] = df.columns
        self.extra_cache_kwargs["_errors"] = financial_analysis_result.errors

        if financial_analysis_result.errors.get("duplicated_interims", []) and not settings.DEBUG:
            with suppress(ModuleNotFoundError):
                from sentry_sdk import capture_message

                capture_message(
                    f"Duplicate index detected for instrument {self.instrument} (id: {self.instrument.id})",
                    level="error",
                )
        return df

    def add_messages(self, request, instance=None, **kwargs):
        if self.errors:
            message = """
            <p>While gathering the financial data, we detected the following issues from the data vendor:</p>
            <ul>
            """
            if duplicated_interim := self.errors.get("duplicated_interim", []):
                message += f"""
                <li>Duplicated data for for interim period <strong>{', '.join(duplicated_interim)}</strong>
                    <ul>
                    <li>First available data was used and the rest was ignored
                    </li>
                    </ul>
                </li>
                """
            if missing_data := self.errors.get("missing_data", []):
                for error in missing_data:
                    message += f"<li>{error}</li>"
            message += "</ul>"
            warning(request, message, extra_tags="auto_close=0")

    # Cached attributes as properties
    @cached_property
    def calendar_type(self):
        return CalendarType(self.request.GET.get("calendar_type", CalendarType.FISCAL.value))

    @cached_property
    def financial_analysis_key(self):
        return self.kwargs.get("statement", "income")

    @cached_property
    def estimate_mapping(self):
        return getattr(self, "_estimate_mapping", {})

    @cached_property
    def errors(self):
        return getattr(self, "_errors", {})

    @cached_property
    def columns(self):
        return self.df.columns

    def get_ordering_fields(self):
        return self.columns

    @cached_property
    def year_columns(self):
        return list(filter(lambda col: "Y" in col, self.columns))

    @cached_property
    def interim_columns(self):
        return list(filter(lambda col: "Y" not in col, self.columns))
