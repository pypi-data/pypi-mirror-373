import re
from datetime import date
from operator import itemgetter
from typing import TypedDict
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
from metaboatrace.models.stadium import StadiumTelCode

from metaboatrace.scrapers.official.website.exceptions import ScrapingError

RaceKey = TypedDict(
    "RaceKey",
    {"race_holding_date": date, "stadium_tel_code": StadiumTelCode, "race_number": int},
)


def parse_race_key_attributes(soup: BeautifulSoup) -> RaceKey:
    todays_race_list_url = soup.select_one("body > div.l-header > ul > li:nth-child(3) > a")["href"]

    stadiutm_tel_codes, dates = itemgetter("jcd", "hd")(
        parse_qs(urlparse(todays_race_list_url).query)
    )

    if len(stadiutm_tel_codes) != 1 or len(dates) != 1:
        raise ScrapingError
    stadiutm_tel_code = StadiumTelCode(int(stadiutm_tel_codes[0]))

    date_string = dates[0]
    race_holding_date = date(int(date_string[:4]), int(date_string[4:6]), int(date_string[6:]))

    deadline_table = soup.select_one(".table1")
    deadline_table.select_one("tr th:not([class])").text
    if m := re.match(r"(\d{1,2})R", deadline_table.select_one("tr th:not([class])").text):
        race_number = int(m.group(1))
    else:
        raise ScrapingError

    return {
        "race_holding_date": race_holding_date,
        "stadium_tel_code": stadiutm_tel_code,
        "race_number": race_number,
    }
