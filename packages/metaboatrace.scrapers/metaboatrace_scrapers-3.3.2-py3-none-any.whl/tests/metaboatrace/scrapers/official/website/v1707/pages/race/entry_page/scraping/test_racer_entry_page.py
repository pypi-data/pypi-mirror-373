import os

from metaboatrace.models.racer import Racer, RacerRank

from metaboatrace.scrapers.official.website.v1707.pages.race.entry_page.scraping import (
    extract_racers,
)

base_path = os.path.dirname(os.path.abspath(__file__))
fixture_dir_path = os.path.join(base_path, os.pardir, "fixtures")


def test_extract_racers_from_an_entry_page() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20180301_07#_8R.html"))

    with open(file_path, mode="r") as file:
        data = extract_racers(file)

    assert data == [
        Racer(
            registration_number=4190,
            first_name="万記",
            last_name="長嶋",
            current_rating=RacerRank.A1,
        ),
        Racer(
            registration_number=4240,
            first_name="裕梨",
            last_name="今井",
            current_rating=RacerRank.B1,
        ),
        Racer(
            registration_number=4419,
            first_name="加央理",
            last_name="原",
            current_rating=RacerRank.B1,
        ),
        Racer(
            registration_number=3175,
            first_name="千草",
            last_name="渡辺",
            current_rating=RacerRank.A2,
        ),
        Racer(
            registration_number=3254,
            first_name="千春",
            last_name="柳澤",
            current_rating=RacerRank.B1,
        ),
        Racer(
            registration_number=4843,
            first_name="巴恵",
            last_name="深尾",
            current_rating=RacerRank.B1,
        ),
    ]


def test_extract_racers_from_an_entry_page_of_a_race_including_absent() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20151116_03#_11R.html"))

    with open(file_path, mode="r") as file:
        data = extract_racers(file)

    assert data == [
        Racer(
            registration_number=3872,
            first_name="憲行",
            last_name="岡田",
            current_rating=RacerRank.A1,
        ),
        Racer(
            registration_number=3880,
            first_name="宗孝",
            last_name="浅見",
            current_rating=RacerRank.B1,
        ),
        Racer(
            registration_number=3793,
            first_name="真吾",
            last_name="高橋",
            current_rating=RacerRank.B1,
        ),
        Racer(
            registration_number=4357,
            first_name="和也",
            last_name="田中",
            current_rating=RacerRank.A1,
        ),
        Racer(
            registration_number=4037,
            first_name="正幸",
            last_name="別府",
            current_rating=RacerRank.A2,
        ),
        Racer(
            registration_number=3797,
            first_name="繁",
            last_name="岩井",
            current_rating=RacerRank.A2,
        ),
    ]
