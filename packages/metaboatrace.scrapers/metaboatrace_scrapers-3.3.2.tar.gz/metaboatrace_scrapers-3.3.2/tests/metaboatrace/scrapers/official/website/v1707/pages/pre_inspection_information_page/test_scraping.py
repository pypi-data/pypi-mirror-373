import os

import pytest
from metaboatrace.models.racer import Gender, Racer, RacerRank

from metaboatrace.scrapers.official.website.exceptions import DataNotFound
from metaboatrace.scrapers.official.website.v1707.pages.pre_inspection_information_page.scraping import (
    extract_racers,
    extract_event_entries,
    EventEntry,
)

base_path = os.path.dirname(os.path.abspath(__file__))


def test_extract_racers_a_pre_inspection_information_page() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/20151112_23#.html"))
    with open(file_path, mode="r") as file:
        data = extract_racers(file)

    assert len(data) == 44
    # 件数的に全件確認は辛いので代表値のみチェック
    assert data[0] == Racer(
        registration_number=3470,
        last_name="新田",
        first_name="芳美",
        gender=Gender.FEMALE,
        current_rating=RacerRank.A1,
    )
    assert data[-1] == Racer(
        registration_number=3518,
        last_name="倉田",
        first_name="郁美",
        gender=Gender.FEMALE,
        current_rating=RacerRank.A2,
    )


def test_extract_racers_from_a_no_contents_page() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/data_not_found.html"))

    with open(file_path, mode="r") as file:
        with pytest.raises(DataNotFound):
            extract_racers(file)


def test_extract_racers_a_pre_inspection_information_of_parallel_series() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/20191218_12#.html"))
    with open(file_path, mode="r") as file:
        data = extract_racers(file)

    assert len(data) == 59
    assert data[0] == Racer(
        registration_number=4320,
        last_name="峰",
        first_name="竜太",
        gender=Gender.MALE,
        current_rating=RacerRank.A1,
    )
    assert data[-1] == Racer(
        registration_number=3942,
        last_name="寺田",
        first_name="祥",
        gender=Gender.MALE,
        current_rating=RacerRank.A1,
    )


def test_extract_event_entries_from_a_no_contents_page() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/data_not_found.html"))

    with open(file_path, mode="r") as file:
        with pytest.raises(DataNotFound):
            extract_event_entries(file)


def test_extract_event_entries_a_pre_inspection_information_page() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/20151112_23#.html"))
    with open(file_path, mode="r") as file:
        data = extract_event_entries(file)

    assert len(data) == 44
    assert data[0] == EventEntry(
        racer_registration_number=3470,
        racer_gender=Gender.FEMALE,
        racer_last_name="新田",
        racer_first_name="芳美",
        racer_rank=RacerRank.A1,
        motor_number=70,
        quinella_rate_of_motor=61.6,
        boat_number=35,
        quinella_rate_of_boat=39.2,
        anterior_time=7.07,
    )
    assert data[-1] == EventEntry(
        racer_registration_number=3518,
        racer_gender=Gender.FEMALE,
        racer_last_name="倉田",
        racer_first_name="郁美",
        racer_rank=RacerRank.A2,
        motor_number=44,
        quinella_rate_of_motor=20.3,
        boat_number=36,
        quinella_rate_of_boat=31.7,
        anterior_time=6.96,
    )
