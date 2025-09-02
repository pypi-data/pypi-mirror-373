import numpy as np
import pandas as pd


def parse(import_source):
    data = []
    if (
        (data_backend := import_source.source.data_backend)
        and (backend_class := data_backend.backend_class)
        and (default_mapping := getattr(backend_class, "DEFAULT_MAPPING"))
    ):
        df = pd.read_json(import_source.file, orient="records")
        if not df.empty:
            if date_label := getattr(backend_class, "DATE_LABEL", None):
                df[date_label] = pd.to_datetime(df[date_label])
                df = df.sort_values(by=date_label, ascending=True)
                if reindex_method := getattr(backend_class, "REINDEX_METHOD", None):
                    df = df.set_index(date_label)
                    timeline = pd.date_range(start=df.index.min(), end=df.index.max(), freq="B")
                    df = df.reindex(timeline, method=reindex_method)
                    df = df.reset_index(names=date_label)
                df[date_label] = df[date_label].dt.strftime("%Y-%m-%d")
        df = df.replace([np.inf, -np.inf, np.nan], None).rename(columns=default_mapping)
        df = df.drop(columns=df.columns.difference([*default_mapping.values()]))

        if none_nullable_fields := getattr(backend_class, "NONE_NULLABLE_FIELDS", None):
            df = df.dropna(subset=none_nullable_fields, how="any")

        data = df.to_dict("records")
    return {"data": data}
