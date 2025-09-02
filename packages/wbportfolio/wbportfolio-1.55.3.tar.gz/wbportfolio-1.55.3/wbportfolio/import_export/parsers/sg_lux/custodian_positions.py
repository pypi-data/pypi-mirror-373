from typing import TYPE_CHECKING

import pandas as pd
from pandas.tseries.offsets import BDay
from schwifty import IBAN

from wbportfolio.models.portfolio import Portfolio

if TYPE_CHECKING:
    from wbcore.contrib.io.models import ImportSource

# Bank specific Information for Societe Generale Luxembourg
BANK_COUNTRY_CODE = "LU"
BANK_CODE = "060"


def get_underlying_instrument(row: pd.Series) -> dict[str, str]:
    """Get the underlying instrument from the row"""
    return {
        "instrument_type": "equity",
        "isin": str(row["isin"]),
        "name": str(row["name"]),
    }


def get_portfolio_id(row: pd.Series) -> int:
    """Get the portfolio id from the bank account number

    Raises: Portfolio.DoesNotExist: We raise an error intentionally if the portfolio does not exist to make the import fail
    """
    iban = str(IBAN.generate(BANK_COUNTRY_CODE, bank_code=BANK_CODE, account_code=str(row["account_number"])))
    return Portfolio.all_objects.get(bank_accounts__iban=iban).id


def parse(import_source: "ImportSource") -> dict:
    """Parse the custodian positions file into a dictionary"""

    # Get df from csv and rename columns and group by account number, isin, and date to sum the shares per date, account, and isin
    df = pd.read_csv(import_source.file.open(), encoding="latin1").rename(  # type: ignore
        columns={
            "Account number": "account_number",
            "ISIN code": "isin",
            "Quantity": "initial_shares",
            "Position date": "date",
            "Security name": "name",
        }
    )

    df = pd.DataFrame(
        df[["account_number", "isin", "initial_shares", "date", "name"]]
        .groupby(["account_number", "isin", "date", "name"])
        .sum()
    )

    # add weight per account number
    df["weighting"] = df.groupby(["account_number", "date"])["initial_shares"].transform(lambda x: x / x.sum())

    # reset index to remove the multi index from the groupby
    df = df.reset_index()

    # parse datetime string to date string and set to 1 day earlier
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y %I:%M:%S %p") - BDay(1)
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    df["underlying_instrument"] = df.apply(get_underlying_instrument, axis=1)
    df["portfolio"] = df.apply(get_portfolio_id, axis=1)
    df["estimated"] = True

    # remove name column
    df = df.drop(columns=["name", "account_number"])
    return {"data": df.to_dict("records")}
