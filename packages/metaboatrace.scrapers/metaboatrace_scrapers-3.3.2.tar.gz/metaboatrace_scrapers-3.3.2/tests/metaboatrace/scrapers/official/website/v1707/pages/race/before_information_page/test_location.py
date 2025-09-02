from datetime import date

from metaboatrace.models.stadium import StadiumTelCode

from metaboatrace.scrapers.official.website.v1707.pages.race.before_information_page.location import (
    create_race_before_information_page_url,
)


def test_create_race_before_information_page_url() -> None:
    assert (
        create_race_before_information_page_url(
            race_holding_date=date(2022, 9, 19),
            stadium_tel_code=StadiumTelCode.HEIWAJIMA,
            race_number=12,
        )
        == "https://boatrace.jp/owpc/pc/race/beforeinfo?rno=12&jcd=04&hd=20220919"
    )
