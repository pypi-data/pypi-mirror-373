def register(move_first: bool = False, override_backend: bool = False):
    """
    Decorator to register the metric backend
    """
    from wbfdm.contrib.metric.registry import backend_registry

    def _model_wrapper(backend):
        for key in backend.keys:
            backend_registry.set(
                key, backend.BASKET_MODEL_CLASS, backend, move_first=move_first, override_backend=override_backend
            )
        return backend

    return _model_wrapper
