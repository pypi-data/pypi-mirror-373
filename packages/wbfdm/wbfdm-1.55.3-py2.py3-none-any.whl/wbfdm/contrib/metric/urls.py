from django.urls import include, path
from wbcore.routers import WBCoreRouter

from . import viewsets

router = WBCoreRouter()

# Representations
router.register(
    r"instrumentmetricrepresentation",
    viewsets.InstrumentMetricRepresentationViewSet,
    basename="instrumentmetricrepresentation",
)

router.register(r"instrumentmetric", viewsets.InstrumentMetricViewSet, basename="instrumentmetric")

urlpatterns = [
    path("", include(router.urls)),
]
