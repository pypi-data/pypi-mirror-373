from dynamic_preferences.registries import global_preferences_registry


def get_monthly_nnm_target(*args, **kwargs) -> int:
    global_preferences = global_preferences_registry.manager()
    return global_preferences["wbportfolio__monthly_nnm_target"]


def get_product_termination_notice_period(*args, **kwargs) -> int:
    global_preferences = global_preferences_registry.manager()
    return global_preferences["wbportfolio__product_termination_notice_period"]
