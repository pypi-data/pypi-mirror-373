import os
from datetime import date, datetime

import pytz
from metaboatrace.models.race import RaceEntry, RaceInformation
from metaboatrace.models.racer import RacerPerformance
from metaboatrace.models.stadium import StadiumTelCode

from metaboatrace.scrapers.official.website.v1707.pages.race.entry_page.scraping import (
    extract_race_entries,
    extract_race_information,
    extract_racer_performances,
)

base_path = os.path.dirname(os.path.abspath(__file__))
fixture_dir_path = os.path.join(base_path, os.pardir, "fixtures")

jst = pytz.timezone("Asia/Tokyo")


def test_extract_race_information_from_an_entry_page() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20151016_08#_2R.html"))
    with open(file_path, mode="r") as file:
        data = extract_race_information(file)

    assert data == RaceInformation(
        race_holding_date=date(2015, 10, 16),
        stadium_tel_code=StadiumTelCode.TOKONAME,
        race_number=2,
        title="予選",
        number_of_laps=3,
        deadline_at=jst.localize(datetime(2015, 10, 16, 11, 13)).astimezone(pytz.utc),
        is_course_fixed=False,
        use_stabilizer=False,
    )


def test_extract_race_information_using_stabilizers_from_an_entry_page() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20180301_07#_8R.html"))
    with open(file_path, mode="r") as file:
        data = extract_race_information(file)

    assert data == RaceInformation(
        race_holding_date=date(2018, 3, 1),
        stadium_tel_code=StadiumTelCode.GAMAGORI,
        race_number=8,
        title="一般戦",
        number_of_laps=3,
        deadline_at=jst.localize(datetime(2018, 3, 1, 18, 26)).astimezone(pytz.utc),
        is_course_fixed=False,
        use_stabilizer=True,
    )


def test_extract_course_fixed_race_information_from_an_entry_page() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20180301_07#_7R.html"))
    with open(file_path, mode="r") as file:
        data = extract_race_information(file)

    assert data == RaceInformation(
        race_holding_date=date(2018, 3, 1),
        stadium_tel_code=StadiumTelCode.GAMAGORI,
        race_number=7,
        title="一般戦",
        number_of_laps=3,
        deadline_at=jst.localize(datetime(2018, 3, 1, 17, 57)).astimezone(pytz.utc),
        is_course_fixed=True,
        use_stabilizer=True,
    )


def test_extract_two_laps_race_information_from_an_entry_page() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20180301_15#_12R.html"))
    with open(file_path, mode="r") as file:
        data = extract_race_information(file)

    assert data == RaceInformation(
        race_holding_date=date(2018, 3, 1),
        stadium_tel_code=StadiumTelCode.MARUGAME,
        race_number=12,
        title="一般選抜",
        number_of_laps=2,
        deadline_at=jst.localize(datetime(2018, 3, 1, 20, 42)).astimezone(pytz.utc),
        is_course_fixed=False,
        use_stabilizer=True,
    )


def test_extract_race_entries_from_an_entry_page() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20180301_07#_8R.html"))

    with open(file_path, mode="r") as file:
        data = extract_race_entries(file)

    assert data == [
        RaceEntry(
            race_holding_date=date(2018, 3, 1),
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            race_number=8,
            pit_number=1,
            racer_registration_number=4190,
            is_absent=False,
            motor_number=66,
            boat_number=40,
        ),
        RaceEntry(
            race_holding_date=date(2018, 3, 1),
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            race_number=8,
            pit_number=2,
            racer_registration_number=4240,
            is_absent=False,
            motor_number=41,
            boat_number=43,
        ),
        RaceEntry(
            race_holding_date=date(2018, 3, 1),
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            race_number=8,
            pit_number=3,
            racer_registration_number=4419,
            is_absent=False,
            motor_number=58,
            boat_number=74,
        ),
        RaceEntry(
            race_holding_date=date(2018, 3, 1),
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            race_number=8,
            pit_number=4,
            racer_registration_number=3175,
            is_absent=False,
            motor_number=33,
            boat_number=13,
        ),
        RaceEntry(
            race_holding_date=date(2018, 3, 1),
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            race_number=8,
            pit_number=5,
            racer_registration_number=3254,
            is_absent=False,
            motor_number=71,
            boat_number=65,
        ),
        RaceEntry(
            race_holding_date=date(2018, 3, 1),
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            race_number=8,
            pit_number=6,
            racer_registration_number=4843,
            is_absent=False,
            motor_number=40,
            boat_number=68,
        ),
    ]


def test_extract_race_entries_from_an_entry_page_of_a_race_including_absent() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20151116_03#_11R.html"))

    with open(file_path, mode="r") as file:
        data = extract_race_entries(file)

    assert data == [
        RaceEntry(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            race_number=11,
            pit_number=1,
            racer_registration_number=3872,
            is_absent=True,
            motor_number=62,
            boat_number=25,
        ),
        RaceEntry(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            race_number=11,
            pit_number=2,
            racer_registration_number=3880,
            is_absent=False,
            motor_number=61,
            boat_number=31,
        ),
        RaceEntry(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            race_number=11,
            pit_number=3,
            racer_registration_number=3793,
            is_absent=False,
            motor_number=56,
            boat_number=60,
        ),
        RaceEntry(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            race_number=11,
            pit_number=4,
            racer_registration_number=4357,
            is_absent=False,
            motor_number=68,
            boat_number=43,
        ),
        RaceEntry(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            race_number=11,
            pit_number=5,
            racer_registration_number=4037,
            is_absent=False,
            motor_number=26,
            boat_number=46,
        ),
        RaceEntry(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            race_number=11,
            pit_number=6,
            racer_registration_number=3797,
            is_absent=False,
            motor_number=20,
            boat_number=69,
        ),
    ]


def test_extract_racer_performances() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20231102_16#_2R.html"))

    with open(file_path, mode="r") as file:
        data = extract_racer_performances(file)

    assert data == [
        RacerPerformance(
            racer_registration_number=4708,
            aggregated_on=date(2023, 11, 2),
            rate_in_all_stadium=4.47,
            rate_in_event_going_stadium=3.7,
        ),
        RacerPerformance(
            racer_registration_number=3401,
            aggregated_on=date(2023, 11, 2),
            rate_in_all_stadium=4.51,
            rate_in_event_going_stadium=5.69,
        ),
        RacerPerformance(
            racer_registration_number=4200,
            aggregated_on=date(2023, 11, 2),
            rate_in_all_stadium=4.6,
            rate_in_event_going_stadium=4.49,
        ),
        RacerPerformance(
            racer_registration_number=4957,
            aggregated_on=date(2023, 11, 2),
            rate_in_all_stadium=5.09,
            rate_in_event_going_stadium=5.16,
        ),
        RacerPerformance(
            racer_registration_number=3910,
            aggregated_on=date(2023, 11, 2),
            rate_in_all_stadium=4.24,
            rate_in_event_going_stadium=4.37,
        ),
        RacerPerformance(
            racer_registration_number=5317,
            aggregated_on=date(2023, 11, 2),
            rate_in_all_stadium=0,
            rate_in_event_going_stadium=0,
        ),
    ]
