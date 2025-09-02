from datetime import date

from metaboatrace.scrapers.official.website.v1707 import BASE_URL


def create_event_holding_page_url(date: date) -> str:
    formatted_date = f"{date.year:04d}{date.month:02d}{date.day:02d}"
    return f"{BASE_URL}/owpc/pc/race/index?hd={formatted_date}"
