from datetime import date

from metaboatrace.models.stadium import StadiumTelCode

from metaboatrace.scrapers.official.website.v1707.pages.pre_inspection_information_page.location import (
    create_event_entry_page_url,
)


def test_create_event_entry_page_url() -> None:
    assert (
        create_event_entry_page_url(StadiumTelCode.HEIWAJIMA, date(2022, 9, 15))
        == "https://boatrace.jp/owpc/pc/race/rankingmotor?jcd=04&hd=20220915"
    )
