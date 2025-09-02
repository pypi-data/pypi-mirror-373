import codecs
import csv
import datetime
import logging
import re

from wbportfolio.import_export.utils import convert_string_to_number
from wbportfolio.models import Fees

logger = logging.getLogger("importers.parsers.sglux.perf_fees")


def parse(import_source):
    fee_file = import_source.file.open()
    fee_file = codecs.iterdecode(fee_file, "latin1")

    # Read file into a CSV Dict Reader
    # fee_reader = csv.DictReader(fee_file, delimiter=',')
    fee_reader = csv.reader(fee_file)
    isin = re.findall("([A-Z]{2}[A-Z0-9]{9}[0-9]{1})", import_source.file.name)[0]

    # Iterate through the CSV File and parse the data into a list
    data = list()

    for fee_data in fee_reader:
        date = datetime.datetime.strptime(fee_data[0], "%m/%d/%Y")
        data.append(
            {
                "product": {"isin": isin},
                "transaction_date": date.strftime("%Y-%m-%d"),
                "calculated": False,
                "transaction_subtype": Fees.Type.PERFORMANCE,
                "total_value": round(convert_string_to_number(fee_data[1]), 6),
            }
        )
        data.append(
            {
                "product": {"isin": isin},
                "transaction_date": date.strftime("%Y-%m-%d"),
                "calculated": False,
                "transaction_subtype": Fees.Type.PERFORMANCE_CRYSTALIZED,
                "total_value": round(convert_string_to_number(fee_data[2]), 6),
            }
        )

    fee_file.close()

    return {"data": data}
