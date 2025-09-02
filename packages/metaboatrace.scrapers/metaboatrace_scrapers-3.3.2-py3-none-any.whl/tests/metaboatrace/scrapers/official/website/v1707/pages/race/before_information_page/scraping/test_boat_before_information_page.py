# note: ファイル名について
#
# test_boat.py でいいと思うが他に同じファイルがあるとバグる
#
# 以下は同じファイル名だがこれらは正常にパスする
# - tests/metaboatrace/scrapers/official/website/v1707/pages/monthly_schedule_page/test_scraping.py
# - tests/metaboatrace/scrapers/official/website/v1707/pages/pre_inspection_information_page/test_scraping.py
#
# かといってこのディレクトリのテストを全て test_scraping.py に集約するとファイルが肥大化するので分割は維持する
# とはいえテストは通さなきゃいけないのでテストファイルに接尾辞をつける


import os
from datetime import date

import pytest
from metaboatrace.models.boat import MotorParts
from metaboatrace.models.race import BoatSetting
from metaboatrace.models.stadium import StadiumTelCode

from metaboatrace.scrapers.official.website.exceptions import DataNotFound
from metaboatrace.scrapers.official.website.v1707.pages.race.before_information_page.scraping import (
    extract_boat_settings,
)

base_path = os.path.dirname(os.path.abspath(__file__))
fixture_dir_path = os.path.join(base_path, os.pardir, "fixtures")


def test_extract_boat_settings() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20151116_23#_1R.html"))

    with open(file_path, mode="r") as file:
        data = extract_boat_settings(file)

    assert data == [
        BoatSetting(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=1,
            tilt=-0.5,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=2,
            tilt=-0.5,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=3,
            tilt=-0.5,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=4,
            tilt=-0.5,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=5,
            tilt=-0.5,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=6,
            tilt=-0.5,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
    ]


def test_extract_boat_settings_including_propeller_exchanges() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20180619_04#_4R.html"))

    with open(file_path, mode="r") as file:
        data = extract_boat_settings(file)

    assert data == [
        BoatSetting(
            race_holding_date=date(2018, 6, 19),
            stadium_tel_code=StadiumTelCode.HEIWAJIMA,
            race_number=4,
            pit_number=1,
            tilt=-0.5,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2018, 6, 19),
            stadium_tel_code=StadiumTelCode.HEIWAJIMA,
            race_number=4,
            pit_number=2,
            tilt=-0.5,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2018, 6, 19),
            stadium_tel_code=StadiumTelCode.HEIWAJIMA,
            race_number=4,
            pit_number=3,
            tilt=-0.5,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2018, 6, 19),
            stadium_tel_code=StadiumTelCode.HEIWAJIMA,
            race_number=4,
            pit_number=4,
            tilt=-0.5,
            is_new_propeller=True,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2018, 6, 19),
            stadium_tel_code=StadiumTelCode.HEIWAJIMA,
            race_number=4,
            pit_number=5,
            tilt=-0.5,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2018, 6, 19),
            stadium_tel_code=StadiumTelCode.HEIWAJIMA,
            race_number=4,
            pit_number=6,
            tilt=-0.5,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
    ]


def test_extract_boat_settings_including_absent_racers() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20151116_03#_11R.html"))

    with open(file_path, mode="r") as file:
        data = extract_boat_settings(file)

    assert data == [
        BoatSetting(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            race_number=11,
            pit_number=2,
            tilt=0,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            race_number=11,
            pit_number=3,
            tilt=0,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            race_number=11,
            pit_number=4,
            tilt=0,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            race_number=11,
            pit_number=5,
            tilt=0,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            race_number=11,
            pit_number=6,
            tilt=0.5,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
    ]


def test_extract_boat_settings_data_not_found() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20200630_12#_12R.html"))

    with open(file_path, mode="r") as file:
        with pytest.raises(DataNotFound):
            extract_boat_settings(file)


def test_scrape_boat_settings_including_motor_parts_exchanges() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20151116_23#_12R.html"))

    with open(file_path, mode="r") as file:
        data = extract_boat_settings(file)

    assert data == [
        BoatSetting(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=12,
            pit_number=1,
            tilt=-0.5,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=12,
            pit_number=2,
            tilt=-0.5,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=12,
            pit_number=3,
            tilt=-0.5,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=12,
            pit_number=4,
            tilt=0,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
        BoatSetting(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=12,
            pit_number=5,
            tilt=-0.5,
            is_new_propeller=False,
            motor_parts_exchanges=[
                (MotorParts.PISTON, 2),
                (MotorParts.PISTON_RING, 3),
                (MotorParts.ELECTRICAL_SYSTEM, 1),
                (MotorParts.GEAR_CASE, 1),
            ],
        ),
        BoatSetting(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=12,
            pit_number=6,
            tilt=-0.5,
            is_new_propeller=False,
            motor_parts_exchanges=[],
        ),
    ]
