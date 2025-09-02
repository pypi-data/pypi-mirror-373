import codecs
import csv
import datetime
import logging

from wbportfolio.import_export.utils import convert_string_to_number
from wbportfolio.models import Fees

logger = logging.getLogger("importers.parsers.sglux.fee")
# Shares class mapping between ticker to identifier
# {
#     "ATNRFRP": "UNIT/RG",
#     "ATNRFRC": "UNIT/RC",
#     "ATNRFRE": "UNIT/R1",
#     "ATNRFRU": "UNIT/R2",
#     "ATNRFPP": "UNIT/PG",
#     "ATNRFPC": "UNIT/PC",
#     "ATNRFPE": "UNIT/P1",
#     "ATNRFPU": "UNIT/P2",
#     "ATNRFZU": "UNIT/H",
#     "ATNRFAU": "UNIT/A",
#     "ATNRFBU": "UNIT/B",
#     "ATNRFFU": "UNIT/F"
# }


def parse(import_source):
    fee_file = import_source.file.open()
    fee_file = codecs.iterdecode(fee_file, "latin1")

    # Read file into a CSV Dict Reader
    fee_reader = csv.DictReader(fee_file, delimiter=",")

    # Iterate through the CSV File and parse the data into a list
    data = list()

    for fee_data in fee_reader:
        if (fee_description := fee_data["Fees description"]) and fee_description.startswith("Investment Manager fees"):
            share_class = fee_data["Class"]  # .split("\\")[1][0]
            date = datetime.datetime.strptime(fee_data["NAV Date"], "%Y/%m/%d")
            data.append(
                {
                    "product": {
                        "parent__identifier": fee_data["Code"],
                        "currency__key": fee_data["Local ccy"],
                        "identifier": share_class,
                    },
                    "fee_date": date.strftime("%Y-%m-%d"),
                    "calculated": False,
                    "transaction_subtype": Fees.Type.MANAGEMENT,
                    "total_value": round(convert_string_to_number(fee_data.get("Fees - Local ccy", 0)), 6),
                }
            )

    fee_file.close()
    return {"data": data}
