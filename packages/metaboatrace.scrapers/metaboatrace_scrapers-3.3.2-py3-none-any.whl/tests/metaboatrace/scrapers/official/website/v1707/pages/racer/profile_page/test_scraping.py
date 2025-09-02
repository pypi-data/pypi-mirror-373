import os
from datetime import date

import pytest
from metaboatrace.models.racer import Racer, RacerRank
from metaboatrace.models.region import Branch, Prefecture

from metaboatrace.scrapers.official.website.exceptions import DataNotFound
from metaboatrace.scrapers.official.website.v1707.pages.racer.profile_page.scraping import (
    Racer,
    extract_racer_profile,
)

base_path = os.path.dirname(os.path.abspath(__file__))


def test_extract_racer_profile() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/4444.html"))

    with open(file_path, mode="r") as file:
        data = extract_racer_profile(file)

    assert data == Racer(
        registration_number=4444,
        last_name="桐生",
        first_name="順平",
        term=100,
        birth_date=date(1986, 10, 7),
        height=162,
        born_prefecture=Prefecture.FUKUSHIMA,
        branch=Branch.SAITAMA,
        current_rating=RacerRank.A1,
    )


def test_scrape_a_no_contents_page() -> None:
    file_path = os.path.normpath(
        os.path.join(os.path.join(base_path, "./fixtures/data_not_found.html"))
    )

    with open(file_path, mode="r") as file:
        with pytest.raises(DataNotFound):
            extract_racer_profile(file)
