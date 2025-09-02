from metaboatrace.scrapers.official.website.v1707.pages.monthly_schedule_page.location import (
    create_monthly_schedule_page_url,
)


def test_create_monthly_schedule_page_url() -> None:
    assert (
        create_monthly_schedule_page_url(2022, 9)
        == "https://boatrace.jp/owpc/pc/race/monthlyschedule?ym=202209"
    )
