from django.conf import settings
from wbcore.utils.importlib import import_from_dotted_path
from .instruments import (
    InstrumentModelViewSet,
    InstrumentRepresentationViewSet,
    InstrumentTypeRepresentationViewSet,
    ChildrenInstrumentModelViewSet,
)
from .instrument_prices import (
    InstrumentPriceModelViewSet,
    InstrumentPriceInstrumentModelViewSet,
    InstrumentPriceInstrumentStatisticsChartView,
    FinancialStatisticsInstrumentPandasView,
    InstrumentPriceInstrumentDistributionReturnsChartView,
    BestAndWorstReturnsInstrumentPandasView,
)

from .classifications import (
    ClassificationClassificationGroupModelViewSet,
    ClassificationGroupModelViewSet,
    ClassificationGroupRepresentationViewSet,
    ClassificationIcicleChartView,
    ClassificationInstrumentThroughInstrumentModelViewSet,
    ClassificationRepresentationViewSet,
    ClassificationTreeChartView,
    InstrumentClassificationThroughInstrumentModelViewSet,
    InstrumentClassificationThroughModelViewSet,
)
from .financials_analysis import (
    CashFlowAnalysisInstrumentBarChartViewSet,
    CashFlowAnalysisInstrumentTableViewSet,
    EarningsInstrumentChartViewSet,
    FinancialsGraphInstrumentChartViewSet,
    NetDebtAndEbitdaInstrumentChartViewSet,
    ProfitabilityRatiosInstrumentChartViewSet,
    SummaryTableInstrumentChartViewSet,
    ValuationRatiosChartView,
)
from .instrument_lists import (
    InstrumentListModelViewSet,
    InstrumentListRepresentationModelViewSet,
    InstrumentListThroughModelViewSet,
    InstrumentListThroughModelInstrumentListViewSet,
    InstrumentListThroughModelInstrumentViewSet,
)

from .instrument_requests import (
    InstrumentRequestModelViewSet,
    InstrumentRequestRepresentationViewSet,
)
from .instruments_relationships import (
    InstrumentClassificationRelatedInstrumentModelViewSet,
    InstrumentClassificationRelatedInstrumentRepresentationViewSet,
    InstrumentFavoriteGroupModelViewSet,
    InstrumentFavoriteGroupRepresentationViewSet,
    RelatedInstrumentThroughInstrumentModelViewSet,
)


ClassificationModelViewSet = import_from_dotted_path(
    getattr(
        settings,
        "DEFAULT_CLASSIFICATION_MODEL_VIEWSET",
        "wbfdm.viewsets.instruments.classifications.ClassificationModelViewSet",
    )
)
ChildClassificationParentClassificationModelViewSet = import_from_dotted_path(
    getattr(
        settings,
        "DEFAULT_PARENT_CLASSIFICATION_MODEL_VIEWSET",
        "wbfdm.viewsets.instruments.classifications.ChildClassificationParentClassificationModelViewSet",
    )
)
ClassifiedInstrumentModelViewSet = import_from_dotted_path(
    getattr(
        settings,
        "DEFAULT_CLASSIFICATION_INSTRUMENT_MODEL_VIEWSET",
        "wbfdm.viewsets.instruments.instruments_relationships.ClassifiedInstrumentModelViewSet",
    )
)
