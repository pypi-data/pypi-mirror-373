import codecs
import csv
import datetime

from wbportfolio.import_export.utils import convert_string_to_number

from .utils import file_name_parse_isin


def parse(import_source):
    # Load file into a CSV DictReader
    csv_file = import_source.file.open(mode="rt")
    csv_file_type = type(csv_file.read())

    # If the file is a byte string, then we need to convert it.
    if csv_file_type is bytes:
        csv_file = codecs.iterdecode(csv_file, "utf-8")

    # Read file into a CSV Dict Reader
    csv_reader = csv.DictReader(csv_file, delimiter=";")

    # Parse the Parts of the filename into the different parts
    parts = file_name_parse_isin(import_source.file.name)

    # Get the valuation date and investment from the parts list
    product_data = parts["product"]

    # Iterate through the CSV File and parse the data into a list
    data = list()

    for valuation in csv_reader:
        date = datetime.datetime.strptime(valuation["Date"], "%d/%m/%Y").date()
        if date.weekday() not in [5, 6]:
            data.append(
                {
                    "instrument": {"instrument_type": "product", **product_data},
                    "date": date.strftime("%Y-%m-%d"),
                    "net_value": round(convert_string_to_number(valuation["Index Value in%"]), 6),
                    "gross_value": round(convert_string_to_number(valuation["Index gross in%"]), 6),
                    "calculated": False,
                }
            )

    csv_file.close()
    return {"data": data}
