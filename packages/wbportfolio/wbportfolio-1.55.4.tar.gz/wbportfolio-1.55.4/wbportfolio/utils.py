import re

from fuzzywuzzy import process as fuzzywuzzy_process
from fuzzywuzzy import utils


def string_matching(s1, s2):
    best_result = ("", 0)
    for _s1 in s1.split(" "):
        if _s1 in ["&"]:
            continue
        # validate query
        if utils.full_process(_s1):
            matches = fuzzywuzzy_process.extract(_s1, s2)
            if matches[0][1] > best_result[1]:
                best_result = matches[0]

    return best_result


def re_ric(input: str):
    return set(re.findall(r"([A-Za-z0-9]{1,6}\.[A-Z]{1,2})(?:.)(?<!\.)", input))


def re_bloomberg(input: str):
    return set(re.findall(r"[A-Z]{2,5}(?:\-[A-Z]{2})?", input))


def re_isin(input: str):
    return set(re.findall(r"[A-Z]{2}[A-Z0-9]{9}[0-9]", input))
