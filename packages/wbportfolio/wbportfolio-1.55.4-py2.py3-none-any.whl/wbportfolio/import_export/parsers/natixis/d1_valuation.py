import xlrd


def get_isin(sheet):
    for row in sheet.get_rows():
        if row[0].value == "ISIN":
            return row[1].value


def parse(import_source):
    book = xlrd.open_workbook(file_contents=import_source.file.read())
    isin = get_isin(book.sheet_by_name("Certificate"))
    valuation_sheet = book.sheet_by_name("Report")

    date_column = None
    net_value_column = None

    data = list()
    for i, row in enumerate(valuation_sheet.get_rows()):
        if i == 0:
            for column in range(0, valuation_sheet.ncols):
                if "Date" in row[column].value:
                    date_column = column
                if "price" in row[column].value:
                    net_value_column = column
        else:
            valuation_date = xlrd.xldate.xldate_as_datetime(row[date_column].value, 0)
            net_value = row[net_value_column].value

            data.append(
                {
                    "instrument": {"instrument_type": "product", "isin": isin},
                    "date": valuation_date.strftime("%Y-%m-%d"),
                    "net_value": net_value,
                    "calculated": False,
                }
            )

    return {"data": data}
