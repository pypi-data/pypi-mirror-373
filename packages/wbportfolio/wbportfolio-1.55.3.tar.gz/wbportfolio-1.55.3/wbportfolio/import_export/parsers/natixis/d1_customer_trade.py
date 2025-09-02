import datetime

import xlrd

from wbportfolio.models import Trade


def get_isin(sheet):
    for row in sheet.get_rows():
        if row[0].value == "ISIN":
            return row[1].value


def parse(import_source):
    book = xlrd.open_workbook(file_contents=import_source.file.read())

    product_sheet = book.sheet_by_name("Certificate")
    valuation_sheet = book.sheet_by_name("Report")
    isin = get_isin(product_sheet)

    date_column = None
    net_value_column = None
    nominal_column = None

    max_date = datetime.date(1900, 1, 1)

    data = list()
    for i, row in enumerate(valuation_sheet.get_rows()):
        if i == 0:
            for column in range(0, valuation_sheet.ncols):
                if "Date" in row[column].value:
                    date_column = column
                if "price" in row[column].value:
                    net_value_column = column
                if "Nominal" == row[column].value:
                    nominal_column = column

        else:
            transaction_date = xlrd.xldate.xldate_as_datetime(row[date_column].value, 0).date()
            max_date = max(max_date, transaction_date)
            net_value = row[net_value_column].value

            nominal_today = row[nominal_column].value

            try:
                nominal_yesterday = valuation_sheet.cell_value(i + 1, nominal_column)
                trade = nominal_today - nominal_yesterday
            except IndexError:
                trade = nominal_today

            if trade and trade != 0:
                data.append(
                    {
                        "underlying_instrument": {"isin": "isin", "instrument_type": "product"},
                        "transaction_date": transaction_date.strftime("%Y-%m-%d"),
                        "nominal": trade,
                        "transaction_subtype": Trade.Type.REDEMPTION if trade < 0 else Trade.Type.SUBSCRIPTION,
                        "bank": "Natixis Internal Trade",
                        "price": net_value,
                    }
                )

    return {
        "data": data,
        "history": {"underlying_instrument": {"isin": isin}, "transaction_date": max_date.strftime("%Y-%m-%d")},
    }
