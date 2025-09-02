import os
from datetime import date

from metaboatrace.models.racer import RacerCondition

from metaboatrace.scrapers.official.website.v1707.pages.race.before_information_page.scraping import (
    extract_racer_conditions,
)

base_path = os.path.dirname(os.path.abspath(__file__))
fixture_dir_path = os.path.join(base_path, os.pardir, "fixtures")


def test_extract_racer_conditions() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20151116_23#_1R.html"))

    with open(file_path, mode="r") as file:
        data = extract_racer_conditions(file)

    assert data == [
        RacerCondition(
            recorded_on=date(2015, 11, 16),
            racer_registration_number=4096,
            weight=52.5,
            adjust=0.0,
        ),
        RacerCondition(
            recorded_on=date(2015, 11, 16),
            racer_registration_number=4693,
            weight=51.0,
            adjust=0.0,
        ),
        RacerCondition(
            recorded_on=date(2015, 11, 16),
            racer_registration_number=2505,
            weight=50.0,
            adjust=1.0,
        ),
        RacerCondition(
            recorded_on=date(2015, 11, 16),
            racer_registration_number=4803,
            weight=54.4,
            adjust=0.0,
        ),
        RacerCondition(
            recorded_on=date(2015, 11, 16),
            racer_registration_number=3138,
            weight=51.9,
            adjust=0.0,
        ),
        RacerCondition(
            recorded_on=date(2015, 11, 16),
            racer_registration_number=4221,
            weight=50.0,
            adjust=1.0,
        ),
    ]


def test_extract_racer_conditions_including_race_absent_racer() -> None:
    file_path = os.path.normpath(
        # 1号艇が欠場
        os.path.join(
            fixture_dir_path,
            "20151116_03#_11R.html",
        )
    )

    with open(file_path, mode="r") as file:
        data = extract_racer_conditions(file)

    assert data == [
        RacerCondition(
            recorded_on=date(2015, 11, 16),
            racer_registration_number=3880,
            weight=55.8,
            adjust=0.0,
        ),
        RacerCondition(
            recorded_on=date(2015, 11, 16),
            racer_registration_number=3793,
            weight=56.5,
            adjust=0.0,
        ),
        RacerCondition(
            recorded_on=date(2015, 11, 16),
            racer_registration_number=4357,
            weight=52.8,
            adjust=0.0,
        ),
        RacerCondition(
            recorded_on=date(2015, 11, 16),
            racer_registration_number=4037,
            weight=51.2,
            adjust=0.0,
        ),
        RacerCondition(
            recorded_on=date(2015, 11, 16),
            racer_registration_number=3797,
            weight=58.3,
            adjust=0.0,
        ),
    ]
