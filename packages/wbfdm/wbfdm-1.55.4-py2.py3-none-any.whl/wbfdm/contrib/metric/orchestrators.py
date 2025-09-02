from contextlib import suppress
from datetime import date
from typing import Any, Generator

from django.db import models
from django.db.utils import DataError
from tqdm import tqdm

from .backends.base import AbstractBackend
from .dto import Metric
from .exceptions import MetricInvalidParameterException
from .models import InstrumentMetric
from .registry import backend_registry


class MetricOrchestrator:
    """
    Orchestrator class responsible to gather the proper metric backends and their respective queryset of baskets

    For each parameters, the orchestrator is responsible to compute and store the generated metrics
    """

    def __init__(self, val_date: date | None, key: str | None = None, basket: Any | None = None, **kwargs):
        self.basket = basket
        self.val_date = val_date
        self.backend_classes = backend_registry.get(metric_key=key, model_class=basket.__class__ if basket else None)

    def _iterate_baskets(self, backend: AbstractBackend) -> models.QuerySet:
        """
        Retrieve and filter the queryset of baskets from the given backend.

        Args:
            backend (AbstractBackend): The backend from which to retrieve the queryset of baskets.

        Returns:
            models.QuerySet: A queryset of baskets, filtered by the current basket if specified.
        """
        qs = backend.get_queryset()
        if self.basket:
            qs = qs.filter(id=self.basket.id)
        return qs

    def _get_parameters(self) -> list[tuple[AbstractBackend, Any]]:
        """
        Generate a list of parameters consisting of metric backend instances and baskets.

        This method initializes backends for each backend class with the validation date,
        iterates through the baskets, and creates a list of tuples containing the backend
        and each basket.

        Returns:
            List[Tuple[AbstractBackend, Any]]: A list of tuples where each tuple contains
            an instance of a instantiated metric backend and a corresponding basket to compute metrics from.
        """
        parameters = []
        for backend_class in self.backend_classes:
            backend = backend_class(self.val_date)
            for basket in self._iterate_baskets(backend):
                parameters.append((backend, basket))
        return parameters

    def get_results(self, debug: bool = False) -> Generator[Metric, None, None]:
        """
        Compute and yield metrics based on the parameters obtained from `_get_parameters`

        Args:
            debug (bool, optional): If True, wraps the parameters list in a tqdm generator for progress tracking. Defaults to False.

        Yields:
            Metric: Each DTO metric computed by the backend for the given baskets.
        """
        parameters = self._get_parameters()
        if debug:
            # if debug mode is enabled, we wrap the parameters list into a tqdm generator
            parameters = tqdm(parameters)
        for parameters in parameters:
            with suppress(MetricInvalidParameterException):
                yield from parameters[0].compute_metrics(parameters[1])

    def process(self, debug: bool = False):
        """
        Process the computation of metrics and update or create InstrumentMetric instances accordingly.

        Side Effects:
            - Updates or creates InstrumentMetric instances based on the computed metrics.
        """
        # we need to see how one threaded loop is fast enough
        errors = []
        for metric in self.get_results(debug=debug):
            try:
                InstrumentMetric.update_or_create_from_metric(metric)
            except DataError:
                errors.append(metric)
        return errors
