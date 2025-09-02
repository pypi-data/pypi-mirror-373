import datetime
import re

import xlrd


def file_name_parse(file_name):
    isin = re.findall("([A-Z]{2}[A-Z0-9]{9}[0-9]{1})", file_name)

    assert len(isin) == 1, "Not exactly 1 isin found in the filename"

    return {"isin": isin[0]}


def parse(import_source):
    book = xlrd.open_workbook(file_contents=import_source.file.read())

    parts = file_name_parse(import_source.file.name)
    isin = parts["isin"]

    equity_sheet = book.sheet_by_name("Equity")
    cash_sheet = book.sheet_by_name("Cash")

    date = None
    first_row = None
    last_row = None

    for row_index, row in enumerate(equity_sheet.get_rows()):
        if "Statement as at Close of Business" in row[1].value:
            date = datetime.datetime.strptime(row[1].value.split(":")[1].strip(), "%d-%b-%Y").date()

        if "Instrument" in row[1].value:
            first_row = row_index + 1

        if row[1].value == "" and first_row is not None:
            last_row = row_index
            break

    data = list()
    for row in range(first_row, last_row, 1):
        initial_shares = round(equity_sheet.cell_value(row, 8), 4)
        close = round(equity_sheet.cell_value(row, 9), 4)
        initial_currency_fx_rate = round(equity_sheet.cell_value(row, 11), 14)

        bbg = equity_sheet.cell_value(row, 3)
        ric = equity_sheet.cell_value(row, 2)
        try:
            ticker, exchange = bbg.split(" ")[0:2]
        except Exception:
            ticker, exchange = bbg, None
        exchange_data = {"bbg_exchange_codes": exchange}
        data.append(
            {
                "underlying_quote": {
                    "instrument_type": "equity",
                    "ticker": ticker,
                    "exchange": exchange_data,
                    "name": equity_sheet.cell_value(row, 1),
                    "currency__key": equity_sheet.cell_value(row, 10),
                    "refinitiv_identifier_code": ric,
                },
                "portfolio": {"instrument_type": "product", "isin": isin},
                "is_estimated": False,
                "exchange": exchange_data,
                "initial_shares": initial_shares,
                "date": date.strftime("%Y-%m-%d"),
                "asset_valuation_date": date.strftime("%Y-%m-%d"),
                "initial_price": close,
                "currency__key": equity_sheet.cell_value(row, 10),
                "initial_currency_fx_rate": initial_currency_fx_rate,
            }
        )

    for row_index, row in enumerate(cash_sheet.get_rows()):
        if "Currency" == row[1].value:
            data.append(
                {
                    "underlying_quote": {
                        "instrument_type": "cash",
                        "currency__key": cash_sheet.cell_value(row_index + 1, 1),
                    },
                    "portfolio": {"instrument_type": "product", "isin": isin},
                    "is_estimated": False,
                    "name": cash_sheet.cell_value(row_index + 1, 1),
                    "initial_shares": round(cash_sheet.cell_value(row_index + 1, 2), 4),
                    "date": date.strftime("%Y-%m-%d"),
                    "asset_valuation_date": date.strftime("%Y-%m-%d"),
                    "initial_price": 1.0,
                    "currency__key": cash_sheet.cell_value(row_index + 1, 1),
                    "initial_currency_fx_rate": 1.0,
                }
            )
            break

    return {"data": data}
