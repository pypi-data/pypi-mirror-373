import codecs
import csv
import datetime
import re


def file_name_parse(file_name):
    dates = re.findall(r"([0-9]{4}-[0-9]{2}-[0-9]{2})", file_name)
    isin = re.findall(r"\.([a-zA-Z0-9]*)_", file_name)

    assert len(dates) == 2, "Not 2 dates found in the filename"
    assert len(isin) == 1, "Not exactly 1 isin found in the filename"

    return {
        "isin": isin[0],
        "valuation_date": datetime.datetime.strptime(dates[0], "%Y-%m-%d").date(),
        "generation_date": datetime.datetime.strptime(dates[1], "%Y-%m-%d").date(),
    }


def parse(import_source):
    # Load file into a CSV DictReader
    csv_file = import_source.file.open()
    # csv_file_type = type(csv_file.read())

    # # If the file is a byte string, then we need to convert it.
    # if csv_file_type is bytes:
    csv_file = codecs.iterdecode(csv_file, "latin1")

    # # Read file into a CSV Dict Reader
    csv_reader = csv.DictReader(csv_file, delimiter=";")

    # # Iterate through the CSV File and parse the data into a list
    data = list()

    for valuation in csv_reader:
        valuation_date = datetime.datetime.strptime(valuation["Bewertungsdatum"], "%Y%m%d").date()
        isin = valuation["ISIN"]
        if valuation_date.weekday() not in [5, 6]:
            data.append(
                {
                    "instrument": {"instrument_type": "product", "isin": isin},
                    "date": valuation_date.strftime("%Y-%m-%d"),
                    "net_value": float(valuation["Nettoinventarwert"]),
                    "calculated": False,
                }
            )

    csv_file.close()
    return {"data": data}
