import os

from metaboatrace.scrapers.official.website.v1707.pages.race.entry_page.scraping import (
    is_deadline_changed,
)

base_path = os.path.dirname(os.path.abspath(__file__))
fixture_dir_path = os.path.join(base_path, os.pardir, "fixtures")


def test_scraping_in_not_deadline_changed_page() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20180301_07#_8R.html"))

    with open(file_path, mode="r") as file:
        assert is_deadline_changed(file) == False


def test_scraping_in_deadline_changed_page() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20240104_14#_8R.html"))

    with open(file_path, mode="r") as file:
        assert is_deadline_changed(file) == True
