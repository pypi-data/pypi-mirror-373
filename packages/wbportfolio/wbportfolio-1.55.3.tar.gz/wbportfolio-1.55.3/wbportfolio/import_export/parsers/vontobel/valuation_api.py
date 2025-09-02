import json
from contextlib import suppress
from datetime import datetime

from wbportfolio.models import Product


def parse(import_source):
    data = []
    with suppress(KeyError):
        series_data = json.loads(import_source.file.read())["payload"]["series"]
        for series in series_data:
            try:
                isin = series["key"]["priceIdentifier"]
            except KeyError:
                isin = series["priceIdentifier"]
            if Product.objects.filter(isin=isin).exists():  # ensure the timeseries contain data for products we handle
                for point in series["points"]:
                    data.append(
                        {
                            "instrument": {"isin": isin},
                            "date": datetime.fromtimestamp(int(point["timestamp"]) / 1000).strftime("%Y-%m-%d"),
                            "net_value": point["close"],
                        }
                    )
    return {"data": data}
