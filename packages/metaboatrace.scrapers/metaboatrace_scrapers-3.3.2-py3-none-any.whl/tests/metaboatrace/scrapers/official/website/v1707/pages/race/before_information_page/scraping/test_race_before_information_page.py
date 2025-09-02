import os
from datetime import date

import pytest
from metaboatrace.models.race import (
    CircumferenceExhibitionRecord,
    StartExhibitionRecord,
    Weather,
    WeatherCondition,
)
from metaboatrace.models.stadium import StadiumTelCode

from metaboatrace.scrapers.official.website.v1707.pages.race.before_information_page.scraping import (
    extract_circumference_exhibition_records,
    extract_start_exhibition_records,
    extract_weather_condition,
)

base_path = os.path.dirname(os.path.abspath(__file__))
fixture_dir_path = os.path.join(base_path, os.pardir, "fixtures")


def test_extract_start_exhibition_records() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20151116_23#_1R.html"))

    with open(file_path, mode="r") as file:
        data = extract_start_exhibition_records(file)

    assert data == [
        StartExhibitionRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=1,
            start_course=1,
            start_time=0.23,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=2,
            start_course=2,
            start_time=0.28,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=3,
            start_course=3,
            start_time=0.21,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=4,
            start_course=4,
            start_time=0.21,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=5,
            start_course=5,
            start_time=0.11,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=6,
            start_course=6,
            start_time=-0.04,
        ),
    ]


# レース欠場者とスタ展欠場者で場合分けした方がいいかと思ったがどちらも出力されるtableは同じなのでこれで網羅できたと見做す
def test_extract_start_exhibition_records_from_a_page_including_absent_racer() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20170625_06#_10R.html"))

    with open(file_path, mode="r") as file:
        data = extract_start_exhibition_records(file)

    assert data == [
        StartExhibitionRecord(
            race_holding_date=date(2017, 6, 25),
            stadium_tel_code=StadiumTelCode.HAMANAKO,
            race_number=10,
            pit_number=1,
            start_course=1,
            start_time=0.02,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2017, 6, 25),
            stadium_tel_code=StadiumTelCode.HAMANAKO,
            race_number=10,
            pit_number=2,
            start_course=2,
            start_time=0.32,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2017, 6, 25),
            stadium_tel_code=StadiumTelCode.HAMANAKO,
            race_number=10,
            pit_number=3,
            start_course=3,
            start_time=0.05,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2017, 6, 25),
            stadium_tel_code=StadiumTelCode.HAMANAKO,
            race_number=10,
            pit_number=4,
            start_course=4,
            start_time=0.19,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2017, 6, 25),
            stadium_tel_code=StadiumTelCode.HAMANAKO,
            race_number=10,
            pit_number=6,
            start_course=5,
            start_time=0.16,
        ),
    ]


# note: これはコースに入ったけど出遅れたケース
# https://boatrace.jp/owpc/pc/race/beforeinfo?rno=4&jcd=06&hd=20231125
def test_extract_start_exhibition_records_from_a_page_including_lateness_racer() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20231125_06#_4R.html"))

    with open(file_path, mode="r") as file:
        data = extract_start_exhibition_records(file)

    assert data == [
        StartExhibitionRecord(
            race_holding_date=date(2023, 11, 25),
            stadium_tel_code=StadiumTelCode.HAMANAKO,
            race_number=4,
            pit_number=1,
            start_course=1,
            start_time=0.04,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2023, 11, 25),
            stadium_tel_code=StadiumTelCode.HAMANAKO,
            race_number=4,
            pit_number=2,
            start_course=2,
            start_time=1,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2023, 11, 25),
            stadium_tel_code=StadiumTelCode.HAMANAKO,
            race_number=4,
            pit_number=3,
            start_course=3,
            start_time=0.02,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2023, 11, 25),
            stadium_tel_code=StadiumTelCode.HAMANAKO,
            race_number=4,
            pit_number=4,
            start_course=4,
            start_time=-0.07,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2023, 11, 25),
            stadium_tel_code=StadiumTelCode.HAMANAKO,
            race_number=4,
            pit_number=5,
            start_course=5,
            start_time=0.05,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2023, 11, 25),
            stadium_tel_code=StadiumTelCode.HAMANAKO,
            race_number=4,
            pit_number=6,
            start_course=6,
            start_time=0.05,
        ),
    ]


# note: コースに入ってすらいないから L マークが出てない？
# https://boatrace.jp/owpc/pc/race/beforeinfo?rno=9&jcd=20&hd=20200621
def test_extract_start_exhibition_records_from_a_page_including_not_entered_the_course_racer() -> (
    None
):
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20200621_20#_9R.html"))

    with open(file_path, mode="r") as file:
        data = extract_start_exhibition_records(file)

    assert data == [
        StartExhibitionRecord(
            race_holding_date=date(2020, 6, 21),
            stadium_tel_code=StadiumTelCode.WAKAMATSU,
            race_number=9,
            pit_number=1,
            start_course=1,
            start_time=-0.03,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2020, 6, 21),
            stadium_tel_code=StadiumTelCode.WAKAMATSU,
            race_number=9,
            pit_number=2,
            start_course=2,
            start_time=0.01,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2020, 6, 21),
            stadium_tel_code=StadiumTelCode.WAKAMATSU,
            race_number=9,
            pit_number=4,
            start_course=3,
            start_time=0.11,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2020, 6, 21),
            stadium_tel_code=StadiumTelCode.WAKAMATSU,
            race_number=9,
            pit_number=6,
            start_course=4,
            start_time=0.09,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2020, 6, 21),
            stadium_tel_code=StadiumTelCode.WAKAMATSU,
            race_number=9,
            pit_number=5,
            start_course=5,
            start_time=0.09,
        ),
        StartExhibitionRecord(
            race_holding_date=date(2020, 6, 21),
            stadium_tel_code=StadiumTelCode.WAKAMATSU,
            race_number=9,
            pit_number=3,
            start_course=6,
            start_time=1,
        ),
    ]


def test_extract_circumference_exhibition_records() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20151116_23#_1R.html"))

    with open(file_path, mode="r") as file:
        data = extract_circumference_exhibition_records(file)

    assert data == [
        CircumferenceExhibitionRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=1,
            exhibition_time=6.7,
        ),
        CircumferenceExhibitionRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=2,
            exhibition_time=6.81,
        ),
        CircumferenceExhibitionRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=3,
            exhibition_time=6.84,
        ),
        CircumferenceExhibitionRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=4,
            exhibition_time=6.86,
        ),
        CircumferenceExhibitionRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=5,
            exhibition_time=6.83,
        ),
        CircumferenceExhibitionRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=1,
            pit_number=6,
            exhibition_time=6.81,
        ),
    ]


def test_extarct_circumference_exhibition_records_including_st_absent_racer() -> None:
    file_path = os.path.normpath(
        # 5号艇がスタ展出てない
        os.path.join(
            fixture_dir_path,
            "20170625_06#_10R.html",
        )
    )

    with open(file_path, mode="r") as file:
        data = extract_circumference_exhibition_records(file)

    assert data == [
        CircumferenceExhibitionRecord(
            race_holding_date=date(2017, 6, 25),
            stadium_tel_code=StadiumTelCode.HAMANAKO,
            race_number=10,
            pit_number=1,
            exhibition_time=6.66,
        ),
        CircumferenceExhibitionRecord(
            race_holding_date=date(2017, 6, 25),
            stadium_tel_code=StadiumTelCode.HAMANAKO,
            race_number=10,
            pit_number=2,
            exhibition_time=6.76,
        ),
        CircumferenceExhibitionRecord(
            race_holding_date=date(2017, 6, 25),
            stadium_tel_code=StadiumTelCode.HAMANAKO,
            race_number=10,
            pit_number=3,
            exhibition_time=6.71,
        ),
        CircumferenceExhibitionRecord(
            race_holding_date=date(2017, 6, 25),
            stadium_tel_code=StadiumTelCode.HAMANAKO,
            race_number=10,
            pit_number=4,
            exhibition_time=6.77,
        ),
        CircumferenceExhibitionRecord(
            race_holding_date=date(2017, 6, 25),
            stadium_tel_code=StadiumTelCode.HAMANAKO,
            race_number=10,
            pit_number=5,
            exhibition_time=6.73,
        ),
        CircumferenceExhibitionRecord(
            race_holding_date=date(2017, 6, 25),
            stadium_tel_code=StadiumTelCode.HAMANAKO,
            race_number=10,
            pit_number=6,
            exhibition_time=6.73,
        ),
    ]


def test_extract_circumference_exhibition_records_including_race_absent_racer() -> None:
    file_path = os.path.normpath(
        # 1号艇が欠場
        os.path.join(
            fixture_dir_path,
            "20151116_03#_11R.html",
        )
    )

    with open(file_path, mode="r") as file:
        data = extract_circumference_exhibition_records(file)

    assert data == [
        CircumferenceExhibitionRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            race_number=11,
            pit_number=2,
            exhibition_time=6.91,
        ),
        CircumferenceExhibitionRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            race_number=11,
            pit_number=3,
            exhibition_time=7.04,
        ),
        CircumferenceExhibitionRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            race_number=11,
            pit_number=4,
            exhibition_time=7,
        ),
        CircumferenceExhibitionRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            race_number=11,
            pit_number=5,
            exhibition_time=7.16,
        ),
        CircumferenceExhibitionRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            race_number=11,
            pit_number=6,
            exhibition_time=6.78,
        ),
    ]


def test_extract_records_with_only_start_exhibition_and_canceled_circumference_exhibition() -> None:
    file_path = os.path.normpath(
        # 周回展示直前で中止決定
        os.path.join(
            fixture_dir_path,
            "20240322_03#_8R.html",
        )
    )

    with open(file_path, mode="r") as file:
        data = extract_circumference_exhibition_records(file)

    assert data == []


def test_extract_weather_condition() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20151115_07#_12R.html"))

    with open(file_path, mode="r") as file:
        data = extract_weather_condition(file)

    assert data == WeatherCondition(
        race_holding_date=date(2015, 11, 15),
        stadium_tel_code=StadiumTelCode.GAMAGORI,
        race_number=12,
        in_performance=False,
        weather=Weather.FINE,
        wavelength=2.0,
        wind_angle=315.0,
        wind_velocity=4.0,
        air_temperature=17.0,
        water_temperature=17.0,
    )


def test_extract_weather_condition_from_incomplete_information() -> None:
    file_path = os.path.normpath(os.path.join(fixture_dir_path, "20171030_03#_1R.html"))

    with open(file_path, mode="r") as file:
        with pytest.raises(ValueError):
            # 0:00現在表示があったら欠損値があるはずなのでこの例外になる
            extract_weather_condition(file)
