from metaboatrace.scrapers.official.website.v1707.pages.racer.profile_page.location import (
    create_racer_profile_page_url,
)


def test_create_event_entry_page_url() -> None:
    assert (
        create_racer_profile_page_url(4444)
        == "https://boatrace.jp/owpc/pc/data/racersearch/profile?toban=4444"
    )
