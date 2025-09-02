from unittest.mock import patch

from faker import Faker

from ..dispatch import compute_metrics
from ..orchestrators import MetricOrchestrator
from ..tasks import compute_metrics_as_task

fake = Faker()


@patch.object(MetricOrchestrator, "process")
def test_dispatch_compute_metrics(mock_fct):
    key = "performance"
    basket = object()
    val_date = fake.date_object()
    compute_metrics(val_date, key=key, basket=basket)
    mock_fct.assert_called_once()


@patch.object(MetricOrchestrator, "process")
def test_periodically_compute_all_metrics(mock_fct):
    compute_metrics_as_task()
    mock_fct.assert_called_once()
