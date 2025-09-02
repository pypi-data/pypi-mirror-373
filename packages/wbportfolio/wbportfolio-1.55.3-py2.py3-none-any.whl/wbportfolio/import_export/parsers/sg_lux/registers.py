import csv
from io import StringIO

import numpy as np
import pandas as pd
from wbcore.contrib.geography.models import Geography
from xlrd import xldate_as_datetime

from wbportfolio.models import Register

from .sylk import SYLK


def convert_string_to_number(string):
    try:
        return float(string.replace(" ", "").replace(",", ""))
    except ValueError:
        return 0.0


def parse(import_source):
    data = list()

    country_title_mapping_exception = import_source.source.import_parameters.get(
        "country_title_mapping_exception", {"great-britain": "GB", "united kingdom": "GB", "man (isle of)": "IM"}
    )

    sylk_handler = SYLK()
    for line in [_line.decode("cp1252") for _line in import_source.file.open("rb").readlines()]:
        sylk_handler.parseline(line)

    buffer = StringIO()
    csvwriter = csv.writer(buffer, quotechar="'", delimiter=";", lineterminator="\n", quoting=csv.QUOTE_ALL)
    for line in sylk_handler.stream_rows():
        csvwriter.writerow(line)

    buffer.seek(0)
    content = buffer.read().replace('""', "")
    df = pd.read_csv(
        StringIO(content),
        sep=";",
        quotechar="'",
        usecols=[
            2,
            3,
            4,
            5,
            8,
            9,
            10,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
            32,
            33,
            34,
            36,
            42,
            43,
            46,
            47,
            48,
            49,
            50,
            55,
            56,
            57,
            58,
        ],
    )

    # Convert timestamps to json conform date strings
    df["ESTABLISHMENT_DATE"] = df["ESTABLISHMENT_DATE"].apply(lambda x: xldate_as_datetime(x, datemode=0).date())
    df["ESTABLISHMENT_DATE"] = df["ESTABLISHMENT_DATE"].apply(lambda x: x.strftime("%Y-%m-%d"))

    df = df.replace(np.nan, "", regex=True)
    # df = df.astype(str)
    df["GLOBAL_REGISTER_NUMBER"] = df["GLOBAL_REGISTER_NUMBER"].apply(lambda x: str(int(x)) if x else "")

    # Merge TextFields
    df["custodian_address"] = df[["ADRESS_LINE_1_4", "ADRESS_LINE_2_4", "ADRESS_LINE_3_4", "ADRESS_LINE_4_4"]].apply(
        lambda x: "<br />".join(x.dropna().astype(str)), axis=1
    )

    def concat_status(x):
        status = []

        if code := x["BLOCK_CODE"]:
            try:
                status.append(f"{int(code):04}")
            except ValueError:
                status.append(code)
        if desc := x["BLOCK_CODE_DESCRIPTION"]:
            status.append(desc)

        for n in range(1, 5):
            if code := x[f"BLOCK_CODE_{n}"]:
                try:
                    status.append(f"{int(code):04}")
                except ValueError:
                    status.append(code)
            if desc := x[f"DESCRIPTION_BC{n}"]:
                status.append(desc)

        return "<br />".join(status)

    df["status_message"] = df.apply(concat_status, axis=1)

    # Map Status
    def apply_status(x):
        if x.get("status_message", None) and x["ACTIVE_INACTIVE"] != "INACTIVE":
            return Register.RegisterStatus.WARNING

        mapping = {
            "ACTIVE": Register.RegisterStatus.ACTIVE,
            "INACTIVE": Register.RegisterStatus.INACTIVE,
        }
        return mapping[x["ACTIVE_INACTIVE"]]

    df["status"] = df.apply(apply_status, axis=1)

    # Remove not used columns
    del df["ADRESS_LINE_1_4"]
    del df["ADRESS_LINE_2_4"]
    del df["ADRESS_LINE_3_4"]
    del df["ADRESS_LINE_4_4"]
    del df["BLOCK_CODE"]
    del df["BLOCK_CODE_DESCRIPTION"]
    del df["BLOCK_CODE_1"]
    del df["DESCRIPTION_BC1"]
    del df["BLOCK_CODE_2"]
    del df["DESCRIPTION_BC2"]
    del df["BLOCK_CODE_3"]
    del df["DESCRIPTION_BC3"]
    del df["BLOCK_CODE_4"]
    del df["DESCRIPTION_BC4"]
    del df["ACTIVE_INACTIVE"]

    # Map Countries
    country_code_mapping = {
        country["code_2"]: country["id"] for country in Geography.countries.all().values("id", "code_2")
    }
    country_code_mapping["XX"] = country_code_mapping["ZZ"]
    country_title_mapping = {
        country["name"].lower(): country["id"] for country in Geography.countries.all().values("id", "name")
    }
    for title, code in country_title_mapping_exception.items():
        country_title_mapping[title] = Geography.countries.get(code_2=code).id

    df["CITIZENSHIP"] = df["CITIZENSHIP"].apply(lambda x: country_code_mapping[x])
    df["RESIDENCE"] = df["RESIDENCE"].apply(lambda x: country_code_mapping[x])
    df["CPAYS"] = df["CPAYS"].apply(lambda x: country_code_mapping[x])
    df["COUNTRY"] = df["COUNTRY"].apply(lambda x: country_title_mapping[x.lower()])
    df["CITY"] = df["CITY"].str.title()
    # Map Investor Type
    investor_mapping = {
        "0006": Register.RegisterInvestorType.BANK,
        "0011": Register.RegisterInvestorType.NOMINEE,
        "0003": Register.RegisterInvestorType.GLOBAL,
        "0007": Register.RegisterInvestorType.NON_FINANCIAL_ENTITY,
    }
    df["INVESTOR_TYPE_CODE"] = df["INVESTOR_TYPE_CODE"].apply(lambda x: investor_mapping[f"{x:04}"])

    # Rename Columns
    df.columns = [
        "register_reference",
        "opened",
        "register_name_1",
        "register_name_2",
        "custodian_reference",
        "custodian_name_1",
        "custodian_name_2",
        "custodian_postcode",
        "custodian_city",
        "custodian_country",
        "investor_type",
        "global_register_reference",
        "citizenship",
        "residence",
        "external_register_reference",
        "sales_reference",
        "dealer_reference",
        "outlet_reference",
        "outlet_name",
        "outlet_address",
        "outlet_postcode",
        "outlet_country",
        "opened_reference_1",
        "opened_reference_2",
        "updated_reference_1",
        "updated_reference_1",
        "custodian_address",
        "status_message",
        "status",
    ]
    # Convert df to list of dicts
    data = list(df.T.to_dict().values())

    return {"data": data}
