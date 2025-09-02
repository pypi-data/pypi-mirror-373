from datetime import date

from metaboatrace.scrapers.official.website.v1707.pages.event_holding_page.location import (
    create_event_holding_page_url,
)


def test_create_event_holding_page_url() -> None:
    a_date = date(2023, 12, 12)
    assert (
        create_event_holding_page_url(a_date)
        == "https://boatrace.jp/owpc/pc/race/index?hd=20231212"
    )
