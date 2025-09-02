from collections import OrderedDict, defaultdict
from typing import TYPE_CHECKING, Type

from django.db.models import Model

from .dto import MetricKey

if TYPE_CHECKING:
    from wbfdm.contrib.metric.backends.base import AbstractBackend


# The cached metric backend registry as a dictionary of dictionary (e.g. {key: {model_class: {backend_class}})
class BackendRegistry:
    _key_label_map: dict[str, str] = dict()
    _metric_key_map: dict[str, MetricKey] = dict()
    _overrode_model_class: dict[MetricKey, list[Type[Model]]] = defaultdict(list)
    registry: dict[MetricKey, OrderedDict] = defaultdict(OrderedDict)

    def __getitem__(self, index):
        key = index[0]
        if isinstance(key, str):
            key = self._metric_key_map[key]
        return self.registry[key][index[1]]

    def get_choices(self, keys: list[MetricKey] | None = None) -> list[tuple[str, str]]:
        if not keys:
            keys = list(self.registry.keys())
        return [(key.key, key.label) for key in keys]

    def set(
        self,
        metric_key: MetricKey,
        model_class: Type[Model],
        backend: Type,
        move_first: bool = False,
        override_backend: bool = False,
    ):
        self._metric_key_map[metric_key.key] = metric_key
        self._key_label_map[metric_key.key] = metric_key.label
        # we ensure that the registered key and model class pair are not already registered and lock as override
        if model_class not in self._overrode_model_class[metric_key]:
            self.registry[metric_key][model_class] = backend
            if move_first:
                self.registry[metric_key].move_to_end(model_class, last=False)
        if override_backend:
            self._overrode_model_class[metric_key].append(model_class)

    def get(
        self, metric_key: MetricKey | str | None = None, model_class: Type[Model] | None = None
    ) -> list[Type["AbstractBackend"]]:
        # Initialize the backend classes list to iterate over
        registry = self.registry
        if isinstance(metric_key, str):
            metric_key = self._metric_key_map[metric_key]
        if metric_key:
            # if key is provided, we return only the backends associated with that metric key
            if metric_key not in self.registry:
                raise ValueError(f"key {metric_key.key} does not belong to a registered backend")
            registry = {metric_key: registry[metric_key]}

        if model_class:
            # if the metric needs to be computed only for a specific basket, we filter out the backend classes related to his basket class
            registry = {
                key: {_class: _dataclass}
                for key, d in registry.items()
                for _class, _dataclass in d.items()
                if _class == model_class
            }
        backends = []
        for _, ordered_dict in registry.items():
            for _, backend in ordered_dict.items():
                if backend not in backends:
                    backends.append(backend)
        return backends

    def keys(self):
        return self._metric_key_map.keys()


backend_registry = BackendRegistry()
