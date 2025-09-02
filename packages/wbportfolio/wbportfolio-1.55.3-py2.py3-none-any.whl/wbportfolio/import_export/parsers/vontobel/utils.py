def get_perf_fee_isin(source):
    default_perf_fee_isin = "CH0040602242"
    if source:
        return source.import_parameters.get("performance_fees_instrument_isin", default_perf_fee_isin)
    return default_perf_fee_isin
