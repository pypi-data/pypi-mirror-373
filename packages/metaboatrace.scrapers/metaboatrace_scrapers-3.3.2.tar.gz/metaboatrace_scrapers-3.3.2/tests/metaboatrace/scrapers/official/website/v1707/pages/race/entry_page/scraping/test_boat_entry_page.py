import os
from datetime import date

from metaboatrace.models.boat import BoatPerformance, MotorPerformance
from metaboatrace.models.stadium import StadiumTelCode

from metaboatrace.scrapers.official.website.v1707.pages.race.entry_page.scraping import (
    extract_boat_performances,
    extract_motor_performances,
)

base_path = os.path.dirname(os.path.abspath(__file__))
fixture_dir_path = os.path.join(base_path, os.pardir, "fixtures")


def test_extract_boat_performances() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20180301_07#_8R.html"))

    with open(file_path, mode="r") as file:
        data = extract_boat_performances(file)

    assert data == [
        BoatPerformance(
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            recorded_date=date(2018, 3, 1),
            number=40,
            quinella_rate=39.18,
            trio_rate=57.22,
        ),
        BoatPerformance(
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            recorded_date=date(2018, 3, 1),
            number=43,
            quinella_rate=37.65,
            trio_rate=55.29,
        ),
        BoatPerformance(
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            recorded_date=date(2018, 3, 1),
            number=74,
            quinella_rate=35.62,
            trio_rate=54.79,
        ),
        BoatPerformance(
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            recorded_date=date(2018, 3, 1),
            number=13,
            quinella_rate=29.78,
            trio_rate=45.51,
        ),
        BoatPerformance(
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            recorded_date=date(2018, 3, 1),
            number=65,
            quinella_rate=27.43,
            trio_rate=50.86,
        ),
        BoatPerformance(
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            recorded_date=date(2018, 3, 1),
            number=68,
            quinella_rate=28.49,
            trio_rate=45.35,
        ),
    ]


def test_extract_boat_performances_including_missing_values() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20151116_03#_11R.html"))

    with open(file_path, mode="r") as file:
        data = extract_boat_performances(file)

    assert data == [
        BoatPerformance(
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            recorded_date=date(2015, 11, 16),
            number=25,
            quinella_rate=30.3,
            trio_rate=None,
        ),
        BoatPerformance(
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            recorded_date=date(2015, 11, 16),
            number=31,
            quinella_rate=31.9,
            trio_rate=None,
        ),
        BoatPerformance(
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            recorded_date=date(2015, 11, 16),
            number=60,
            quinella_rate=30.4,
            trio_rate=None,
        ),
        BoatPerformance(
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            recorded_date=date(2015, 11, 16),
            number=43,
            quinella_rate=33.5,
            trio_rate=None,
        ),
        BoatPerformance(
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            recorded_date=date(2015, 11, 16),
            number=46,
            quinella_rate=31.3,
            trio_rate=None,
        ),
        BoatPerformance(
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            recorded_date=date(2015, 11, 16),
            number=69,
            quinella_rate=29,
            trio_rate=None,
        ),
    ]


def test_extract_motor_performances() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20180301_07#_8R.html"))

    with open(file_path, mode="r") as file:
        data = extract_motor_performances(file)

    assert data == [
        MotorPerformance(
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            recorded_date=date(2018, 3, 1),
            number=66,
            quinella_rate=38.1,
            trio_rate=51.9,
        ),
        MotorPerformance(
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            recorded_date=date(2018, 3, 1),
            number=41,
            quinella_rate=36.5,
            trio_rate=51,
        ),
        MotorPerformance(
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            recorded_date=date(2018, 3, 1),
            number=58,
            quinella_rate=33.17,
            trio_rate=51.49,
        ),
        MotorPerformance(
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            recorded_date=date(2018, 3, 1),
            number=33,
            quinella_rate=39.72,
            trio_rate=55.61,
        ),
        MotorPerformance(
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            recorded_date=date(2018, 3, 1),
            number=71,
            quinella_rate=29.51,
            trio_rate=46.72,
        ),
        MotorPerformance(
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            recorded_date=date(2018, 3, 1),
            number=40,
            quinella_rate=33.16,
            trio_rate=49.49,
        ),
    ]


def test_extract_motor_performances_including_missing_values() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20151116_03#_11R.html"))

    with open(file_path, mode="r") as file:
        data = extract_motor_performances(file)

    assert data == [
        MotorPerformance(
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            recorded_date=date(2015, 11, 16),
            number=62,
            quinella_rate=31.5,
            trio_rate=None,
        ),
        MotorPerformance(
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            recorded_date=date(2015, 11, 16),
            number=61,
            quinella_rate=34.4,
            trio_rate=None,
        ),
        MotorPerformance(
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            recorded_date=date(2015, 11, 16),
            number=56,
            quinella_rate=27.8,
            trio_rate=None,
        ),
        MotorPerformance(
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            recorded_date=date(2015, 11, 16),
            number=68,
            quinella_rate=48.3,
            trio_rate=None,
        ),
        MotorPerformance(
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            recorded_date=date(2015, 11, 16),
            number=26,
            quinella_rate=30.2,
            trio_rate=None,
        ),
        MotorPerformance(
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            recorded_date=date(2015, 11, 16),
            number=20,
            quinella_rate=40.1,
            trio_rate=None,
        ),
    ]
