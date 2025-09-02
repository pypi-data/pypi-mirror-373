from django.urls import include, path
from wbcore.routers import WBCoreRouter

from wbfdm import viewsets

router = WBCoreRouter()
router.register(r"instrument", viewsets.InstrumentModelViewSet, basename="instrument")
router.register(
    r"instrumentrepresentation", viewsets.InstrumentRepresentationViewSet, basename="instrumentrepresentation"
)
router.register(
    r"instrumenttyperepresentation",
    viewsets.InstrumentTypeRepresentationViewSet,
    basename="instrumenttyperepresentation",
)
router.register(r"exchange", viewsets.ExchangeModelViewSet, basename="exchange")
router.register(r"exchangerepresentation", viewsets.ExchangeRepresentationViewSet, basename="exchangerepresentation")

router.register(r"instrumentrequest", viewsets.InstrumentRequestModelViewSet, basename="instrumentrequest")
router.register(
    r"instrumentrequestrepresentation",
    viewsets.InstrumentRequestRepresentationViewSet,
    basename="instrumentrequestrepresentation",
)


router.register(
    r"favoritegrouprepresentation",
    viewsets.InstrumentFavoriteGroupRepresentationViewSet,
    basename="favoritegrouprepresentation",
)
router.register(r"favoritegroup", viewsets.InstrumentFavoriteGroupModelViewSet, basename="favoritegroup")

router.register(
    r"classificationrepresentation",
    viewsets.ClassificationRepresentationViewSet,
    basename="classificationrepresentation",
)
router.register(
    r"classificationgrouprepresentation",
    viewsets.ClassificationGroupRepresentationViewSet,
    basename="classificationgrouprepresentation",
)
router.register(r"classification", viewsets.ClassificationModelViewSet, basename="classification")
router.register(r"classificationgroup", viewsets.ClassificationGroupModelViewSet, basename="classificationgroup")
router.register(r"classifiedinstrument", viewsets.ClassifiedInstrumentModelViewSet, basename="classifiedinstrument")
router.register(
    r"instrumentlistrepresentation",
    viewsets.InstrumentListRepresentationModelViewSet,
    basename="instrumentlistrepresentation",
)
router.register(r"instrumentlist", viewsets.InstrumentListModelViewSet, basename="instrumentlist")
router.register(r"instrumentlistthrough", viewsets.InstrumentListThroughModelViewSet, basename="instrumentlistthrough")

# Financials viewsets


classification_router = WBCoreRouter()
classification_router.register(
    r"instrument", viewsets.ClassificationInstrumentThroughInstrumentModelViewSet, basename="classification-instrument"
)

classification_through_router = WBCoreRouter()
classification_through_router.register(
    "related_instrument", viewsets.InstrumentClassificationRelatedInstrumentModelViewSet, basename="related_instrument"
)
classification_through_router.register(
    "related_instrument_representation",
    viewsets.InstrumentClassificationRelatedInstrumentRepresentationViewSet,
    basename="related_instrument_representation",
)


classification_group_router = WBCoreRouter()
classification_group_router.register(
    r"classification",
    viewsets.ClassificationClassificationGroupModelViewSet,
    basename="classificationgroup-classification",
)
classification_group_router.register(
    r"treechart", viewsets.ClassificationTreeChartView, basename="classificationgroup-treechart"
)
classification_group_router.register(
    r"iciclechart", viewsets.ClassificationIcicleChartView, basename="classificationgroup-iciclechart"
)

parent_classification_router = WBCoreRouter()
parent_classification_router.register(
    r"classification",
    viewsets.ChildClassificationParentClassificationModelViewSet,
    basename="classificationparent-classification",
)


router.register(
    r"instrumentclassificationrelationship",
    viewsets.InstrumentClassificationThroughModelViewSet,
    basename="instrumentclassificationrelationship",
)
router.register(r"price", viewsets.InstrumentPriceModelViewSet, basename="price")


instrument_router = WBCoreRouter()
instrument_router.register(r"price", viewsets.InstrumentPriceInstrumentModelViewSet, basename="instrument-price")
instrument_router.register(r"children", viewsets.ChildrenInstrumentModelViewSet, basename="instrument-children")
instrument_router.register(
    r"relatedinstrument",
    viewsets.RelatedInstrumentThroughInstrumentModelViewSet,
    basename="instrument-relatedinstrument",
)
instrument_router.register(
    r"pricestatisticchart",
    viewsets.InstrumentPriceInstrumentStatisticsChartView,
    basename="instrument-pricestatisticchart",
)
instrument_router.register(
    r"distributionreturnschart",
    viewsets.InstrumentPriceInstrumentDistributionReturnsChartView,
    basename="instrument-distributionreturnschart",
)
instrument_router.register(
    r"bestandworstreturns",
    viewsets.BestAndWorstReturnsInstrumentPandasView,
    basename="instrument-bestandworstreturns",
)
instrument_router.register(
    r"financialstatistics",
    viewsets.FinancialStatisticsInstrumentPandasView,
    basename="instrument-financialstatistics",
)
instrument_router.register(
    r"summarytablechart", viewsets.SummaryTableInstrumentChartViewSet, basename="instrument-summarytablechart"
)

instrument_router.register(
    r"financialsgraphchart", viewsets.FinancialsGraphInstrumentChartViewSet, basename="instrument-financialsgraphchart"
)

instrument_router.register(
    r"profitabilityratioschart",
    viewsets.ProfitabilityRatiosInstrumentChartViewSet,
    basename="instrument-profitabilityratioschart",
)

instrument_router.register(
    r"cashflowanalysistablechart",
    viewsets.CashFlowAnalysisInstrumentTableViewSet,
    basename="instrument-cashflowanalysistablechart",
)

instrument_router.register(
    r"cashflowanalysisbarchart",
    viewsets.CashFlowAnalysisInstrumentBarChartViewSet,
    basename="instrument-cashflowanalysisbarchart",
)

instrument_router.register(
    r"netdebtandebitdachart",
    viewsets.NetDebtAndEbitdaInstrumentChartViewSet,
    basename="instrument-netdebtandebitdachart",
)

instrument_router.register(
    r"earningschart",
    viewsets.EarningsInstrumentChartViewSet,
    basename="instrument-earningschart",
)

instrument_router.register(
    r"classification",
    viewsets.InstrumentClassificationThroughInstrumentModelViewSet,
    basename="instrument-classification",
)
instrument_router.register(
    r"valuationratios", viewsets.ValuationRatiosChartView, basename="instrument-valuationratios"
)

instrument_router.register(
    r"instrumentlistthrough",
    viewsets.InstrumentListThroughModelInstrumentViewSet,
    basename="instrument-instrumentlistthrough",
)

instrument_router.register(r"controversies", viewsets.InstrumentESGControversiesViewSet, basename="controversies")
instrument_router.register(r"pai", viewsets.InstrumentESGPAIViewSet, basename="pai")
instrument_router.register(r"officers", viewsets.OfficerViewSet, basename="officers")
instrument_router.register(r"market_data", viewsets.MarketDataChartViewSet, basename="market_data")
instrument_router.register(
    r"performance_summary", viewsets.PerformanceSummaryChartViewSet, basename="performance_summary"
)
instrument_router.register(
    r"financial_metric_analysis", viewsets.FinancialMetricAnalysisPandasViewSet, basename="financial_metric_analysis"
)
instrument_router.register(
    r"monthly_performances", viewsets.MonthlyPerformancesInstrumentPandasViewSet, basename="monthly_performances"
)
instrument_router.register(r"valuation_ratios", viewsets.ValuationRatioChartViewSet, basename="valuation_ratios")
instrument_router.register(r"prices", viewsets.InstrumentPriceViewSet, basename="prices")
instrument_router.register(r"financial-summary", viewsets.FinancialSummary, basename="financial-summary")

instrument_statement_router = WBCoreRouter()
instrument_statement_router.register(
    r"statementwithestimates", viewsets.StatementWithEstimatesPandasViewSet, basename="statementwithestimates"
)
instrument_statement_router.register(r"statement", viewsets.StatementPandasViewSet, basename="statement")

instrument_list = WBCoreRouter()
instrument_list.register(
    r"instrumentlistthrough",
    viewsets.InstrumentListThroughModelInstrumentListViewSet,
    basename="instrumentlist-instrumentlistthrough",
)


urlpatterns = [
    path("", include(router.urls)),
    path("instrument/<int:instrument_id>/", include(instrument_router.urls)),
    path("classificationgroup/<int:group_id>/", include(classification_group_router.urls)),
    path("classificationparent/<int:parent_id>/", include(parent_classification_router.urls)),
    path("classification/<int:classification_id>/", include(classification_router.urls)),
    path("classification_through/<int:classified_instrument_id>/", include(classification_through_router.urls)),
    path("instrument_list/<int:instrument_list_id>/", include(instrument_list.urls)),
    path("instrument/<int:instrument_id>/<str:statement>/", include(instrument_statement_router.urls)),
]
