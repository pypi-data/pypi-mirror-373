import os

import dateparser
from xlrd.xldate import xldate_as_datetime


def get_fields_name(model):
    return [field.name for field in model._meta.get_fields()]


def get_file_extension(file):
    name, extension = os.path.splitext(file.name)
    return extension.lower()


def convert_string_to_number(string):
    if string == "nan" or not string:
        return 0.0
    if type(string) in (int, float):
        return float(string)
    try:
        return float(string.replace(" ", "").replace(",", ""))
    except ValueError:
        return 0.0


def parse_date(date, formats=[]):
    if isinstance(date, int) or isinstance(date, float):
        return xldate_as_datetime(int(date), 0).date()
    if isinstance(date, str):
        if format:
            return dateparser.parse(date, date_formats=formats).date()
        else:
            return dateparser.parse(date).date()


def extract_exchange_ticker(bbg_ticker):
    try:
        ticker, exchange = bbg_ticker.split(" ")[0:2]
    except Exception:
        ticker, exchange = bbg_ticker, None
    return ticker, exchange
