def register(model_name: str):
    """
    Decorator to include when a backend need automatic registration
    """
    from wbportfolio.models.rebalancing import RebalancingModel

    def _decorator(backend_class):
        defaults = {
            "name": model_name,
        }
        RebalancingModel.objects.update_or_create(
            class_path=backend_class.__module__ + "." + backend_class.__name__,
            defaults=defaults,
        )
        return backend_class

    return _decorator
