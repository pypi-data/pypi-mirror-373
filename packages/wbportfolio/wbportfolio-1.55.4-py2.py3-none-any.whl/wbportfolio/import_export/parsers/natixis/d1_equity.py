import xlrd


def get_isin(sheet):
    for row in sheet.get_rows():
        if row[0].value == "ISIN":
            return row[1].value


def parse(import_source):
    book = xlrd.open_workbook(file_contents=import_source.file.read())
    isin = get_isin(book.sheet_by_name("Certificate"))
    equity_sheet = book.sheet_by_name("Report - details")

    # date_column = None
    # net_value_column = None
    # shares_column = None

    data = list()

    first_row = None
    last_row = None

    for i, row in enumerate(equity_sheet.get_rows()):
        if row[0].value == "Date":
            first_row = i

        if first_row is not None and row[0].value == "":
            last_row = i

        if first_row is not None and last_row is not None:
            valuation_date = xlrd.xldate.xldate_as_datetime(equity_sheet.cell_value(first_row + 1, 0), 0).date()

            for _i in range(first_row + 3, last_row):
                initial_shares = equity_sheet.cell_value(_i, 2)
                isin = equity_sheet.cell_value(_i, 3)
                equity_sheet.cell_value(_i, 4)
                currency_key = equity_sheet.cell_value(_i, 5)
                initial_currency_fx_rate = equity_sheet.cell_value(_i, 6)
                initial_price = equity_sheet.cell_value(_i, 10)

                data.append(
                    {
                        "underlying_quote": {"instrument_type": "product", "isin": isin},
                        "currency__key": currency_key,
                        "date": valuation_date.strftime("%Y-%m-%d"),
                        "asset_valuation_date": valuation_date.strftime("%Y-%m-%d"),
                        "initial_price": initial_price,
                        "initial_currency_fx_rate": initial_currency_fx_rate,
                        "initial_shares": initial_shares,
                        "portfolio": {"isin": isin, "instrument_type": "product"},
                    }
                )

            data.append(
                {
                    "underlying_quote": {
                        "instrument_type": "cash",
                        "ticker": "CASH",
                    },
                    "date": valuation_date.strftime("%Y-%m-%d"),
                    "asset_valuation_date": valuation_date.strftime("%Y-%m-%d"),
                    "initial_price": 1.0,
                    "initial_currency_fx_rate": 1.0,
                    "initial_shares": equity_sheet.cell_value(first_row + 1, 6),
                    "portfolio": {"isin": isin, "instrument_type": "product"},
                }
            )

            first_row = None
            last_row = None

    return {"data": data}
