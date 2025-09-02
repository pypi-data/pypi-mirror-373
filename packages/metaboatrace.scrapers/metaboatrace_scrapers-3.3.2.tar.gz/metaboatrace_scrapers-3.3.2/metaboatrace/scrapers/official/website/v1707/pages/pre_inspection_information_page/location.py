import urllib.parse
from datetime import date

from metaboatrace.models.stadium import StadiumTelCode

from metaboatrace.scrapers.official.website.v1707 import BASE_URL
from metaboatrace.scrapers.official.website.v1707.utils import (
    format_date_for_query_string,
    format_stadium_tel_code_for_query_string,
)


def create_event_entry_page_url(stadium_tel_code: StadiumTelCode, event_starts_on: date) -> str:
    return f"{BASE_URL}/owpc/pc/race/rankingmotor?{urllib.parse.urlencode({'jcd': format_stadium_tel_code_for_query_string(stadium_tel_code), 'hd': format_date_for_query_string(event_starts_on)})}"
