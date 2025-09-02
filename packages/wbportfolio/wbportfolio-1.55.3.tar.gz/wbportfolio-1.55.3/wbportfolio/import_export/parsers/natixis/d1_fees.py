import xlrd

from wbportfolio.models import Fees


def get_isin(sheet):
    for row in sheet.get_rows():
        if row[0].value == "ISIN":
            return row[1].value


def parse(import_source):
    book = xlrd.open_workbook(file_contents=import_source.file.read())
    isin = get_isin(book.sheet_by_name("Certificate"))
    valuation_sheet = book.sheet_by_name("Report")

    date_column = None
    bank_fees_column = None
    management_fees_column = None
    performance_fees_gross_column = None

    data = list()
    for i, row in enumerate(valuation_sheet.get_rows()):
        if i == 0:
            for column in range(0, valuation_sheet.ncols):
                if "Date" in row[column].value:
                    date_column = column
                if "Mngt Fees Natixis" == row[column].value:
                    bank_fees_column = column
                if "Mngt Fees Y" == row[column].value:
                    management_fees_column = column
                if "Performance Fees" in row[column].value:
                    performance_fees_gross_column = column
        else:
            valuation_date = xlrd.xldate.xldate_as_datetime(row[date_column].value, 0)
            bank_fees = row[bank_fees_column].value
            management_fees = row[management_fees_column].value

            base_data = {
                "product": {"isin": isin},
                "fee_date": valuation_date.strftime("%Y-%m-%d"),
                "calculated": False,
            }
            if management_fees != 0:
                data.append({"transaction_subtype": Fees.Type.MANAGEMENT, "total_value": management_fees, **base_data})
            if bank_fees != 0:
                data.append({"transaction_subtype": Fees.Type.ISSUER, "total_value": bank_fees, **base_data})
            if performance_fees_gross_column and row[performance_fees_gross_column].value != 0:
                data.append(
                    {
                        "transaction_subtype": Fees.Type.PERFORMANCE,
                        "total_value_gross": row[performance_fees_gross_column].value,
                        **base_data,
                    }
                )

    return {"data": data}
