import json

BASE_MAPPING = {
    "isin": "instrument__isin",
    "certificatePosition": "outstanding_shares",
    "currency": "instrument__currency__key",
    "aum": "market_capitalization",
    "rpl": "net_value",
}


def parse(import_source):
    content = json.load(import_source.file)
    data = {}
    if (amc := content.get("amc", None)) and (val_date := content.get("asOfDate", None)):
        data = {"date": val_date}
        for k, v in amc.items():
            if k in BASE_MAPPING:
                data[BASE_MAPPING[k]] = v
    return {"data": [data]}
