import os
from datetime import date

import pytest
from metaboatrace.models.race import (
    BettingMethod,
    Disqualification,
    Payoff,
    RaceRecord,
    Weather,
    WeatherCondition,
    WinningTrick,
)
from metaboatrace.models.stadium import StadiumTelCode

from metaboatrace.scrapers.official.website.exceptions import DataNotFound, RaceCanceled
from metaboatrace.scrapers.official.website.v1707.pages.race.result_page.scraping import (
    extract_race_payoffs,
    extract_race_records,
    extract_weather_condition,
)

base_path = os.path.dirname(os.path.abspath(__file__))


def test_extract_race_payoffs() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/20151115_07#_12R.html"))
    with open(file_path, mode="r") as file:
        data = extract_race_payoffs(file)

    assert data == [
        Payoff(
            race_holding_date=date(2015, 11, 15),
            stadium_tel_code=StadiumTelCode.GAMAGORI,
            race_number=12,
            betting_method=BettingMethod.TRIFECTA,
            betting_numbers=[4, 3, 5],
            amount=56670,
        )
    ]


def test_extract_payoffs_from_a_race_which_has_an_absent() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/20151116_03#_11R.html"))
    with open(file_path, mode="r") as file:
        data = extract_race_payoffs(file)

    assert data == [
        Payoff(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.EDOGAWA,
            race_number=11,
            betting_method=BettingMethod.TRIFECTA,
            betting_numbers=[2, 3, 4],
            amount=3100,
        )
    ]


def test_extract_payoffs_from_a_race_which_has_a_tie() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/20181116_18#_7R.html"))

    with open(file_path, mode="r") as file:
        data = extract_race_payoffs(file)

    assert data == [
        Payoff(
            race_holding_date=date(2018, 11, 16),
            stadium_tel_code=StadiumTelCode.TOKUYAMA,
            race_number=7,
            betting_method=BettingMethod.TRIFECTA,
            betting_numbers=[1, 4, 2],
            amount=2230,
        ),
        Payoff(
            race_holding_date=date(2018, 11, 16),
            stadium_tel_code=StadiumTelCode.TOKUYAMA,
            race_number=7,
            betting_method=BettingMethod.TRIFECTA,
            betting_numbers=[4, 1, 2],
            amount=15500,
        ),
    ]


def test_extract_payoffs_from_a_race_which_has_four_disqualified_racers() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/20151114_02#_2R.html"))
    with open(file_path, mode="r") as file:
        data = extract_race_payoffs(file)

    assert data == []


def test_extract_payoffs_from_a_no_contents_page() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/data_not_found.html"))

    with open(file_path, mode="r") as file:
        with pytest.raises(DataNotFound):
            extract_race_payoffs(file)


def test_extract_payoffs_from_a_canceled_race() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/canceled.html"))

    with open(file_path, mode="r") as file:
        with pytest.raises(RaceCanceled):
            extract_race_payoffs(file)


def test_extract_weather_condition() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/20181116_18#_7R.html"))

    with open(file_path, mode="r") as file:
        data = extract_weather_condition(file)

    assert data == WeatherCondition(
        race_holding_date=date(2018, 11, 16),
        stadium_tel_code=StadiumTelCode.TOKUYAMA,
        race_number=7,
        in_performance=True,
        weather=Weather.CLOUDY,
        wavelength=1.0,
        wind_angle=135.0,
        wind_velocity=1.0,
        air_temperature=15.0,
        water_temperature=18.0,
    )


def test_extract_race_record_from_a_race_includes_lateness_on_course() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/20231204_16#_5R.html"))

    with open(file_path, mode="r") as file:
        data = extract_race_records(file)

    assert data == [
        RaceRecord(
            race_holding_date=date(2023, 12, 4),
            stadium_tel_code=StadiumTelCode.KOJIMA,
            race_number=5,
            pit_number=1,
            start_course=1,
            arrival=1,
            total_time=108.1,
            start_time=0.08,
            winning_trick=WinningTrick.NIGE,
            disqualification=None,
        ),
        RaceRecord(
            race_holding_date=date(2023, 12, 4),
            stadium_tel_code=StadiumTelCode.KOJIMA,
            race_number=5,
            pit_number=2,
            start_course=2,
            arrival=3,
            total_time=112.6,
            start_time=0.06,
            winning_trick=None,
            disqualification=None,
        ),
        RaceRecord(
            race_holding_date=date(2023, 12, 4),
            stadium_tel_code=StadiumTelCode.KOJIMA,
            race_number=5,
            pit_number=3,
            start_course=3,
            arrival=None,
            total_time=None,
            start_time=1,
            winning_trick=None,
            disqualification=Disqualification.LATENESS,
        ),
        RaceRecord(
            race_holding_date=date(2023, 12, 4),
            stadium_tel_code=StadiumTelCode.KOJIMA,
            race_number=5,
            pit_number=4,
            start_course=4,
            arrival=4,
            total_time=113.6,
            start_time=0.07,
            winning_trick=None,
            disqualification=None,
        ),
        RaceRecord(
            race_holding_date=date(2023, 12, 4),
            stadium_tel_code=StadiumTelCode.KOJIMA,
            race_number=5,
            pit_number=5,
            start_course=5,
            arrival=2,
            total_time=110.4,
            start_time=0.1,
            winning_trick=None,
            disqualification=None,
        ),
        RaceRecord(
            race_holding_date=date(2023, 12, 4),
            stadium_tel_code=StadiumTelCode.KOJIMA,
            race_number=5,
            pit_number=6,
            start_course=6,
            arrival=5,
            total_time=None,
            start_time=0.11,
            winning_trick=None,
            disqualification=None,
        ),
    ]


def test_extract_race_record_from_a_race_includes_lateness_not_on_course() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/20151116_09#_7R.html"))

    with open(file_path, mode="r") as file:
        data = extract_race_records(file)

    assert data == [
        RaceRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.TSU,
            race_number=7,
            pit_number=1,
            start_course=1,
            arrival=2,
            total_time=110.9,
            start_time=0.06,
            winning_trick=None,
            disqualification=None,
        ),
        RaceRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.TSU,
            race_number=7,
            pit_number=2,
            start_course=None,
            arrival=None,
            total_time=None,
            start_time=None,
            winning_trick=None,
            disqualification=Disqualification.LATENESS,
        ),
        RaceRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.TSU,
            race_number=7,
            pit_number=3,
            start_course=3,
            arrival=3,
            total_time=112.5,
            start_time=0.22,
            winning_trick=None,
            disqualification=None,
        ),
        RaceRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.TSU,
            race_number=7,
            pit_number=4,
            start_course=4,
            arrival=1,
            total_time=109.9,
            start_time=0.21,
            winning_trick=WinningTrick.SASHI,
            disqualification=None,
        ),
        RaceRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.TSU,
            race_number=7,
            pit_number=5,
            start_course=5,
            arrival=4,
            total_time=113.5,
            start_time=0.23,
            winning_trick=None,
            disqualification=None,
        ),
        RaceRecord(
            race_holding_date=date(2015, 11, 16),
            stadium_tel_code=StadiumTelCode.TSU,
            race_number=7,
            pit_number=6,
            start_course=2,
            arrival=5,
            total_time=None,
            start_time=0.1,
            winning_trick=None,
            disqualification=None,
        ),
    ]


def test_extract_race_records_from_a_race_which_has_a_tie() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/20181116_18#_7R.html"))

    with open(file_path, mode="r") as file:
        data = extract_race_records(file)

    assert data == [
        RaceRecord(
            race_holding_date=date(2018, 11, 16),
            stadium_tel_code=StadiumTelCode.TOKUYAMA,
            race_number=7,
            pit_number=1,
            start_course=1,
            arrival=1,
            total_time=111.4,
            start_time=0.1,
            winning_trick=WinningTrick.NUKI,
            disqualification=None,
        ),
        RaceRecord(
            race_holding_date=date(2018, 11, 16),
            stadium_tel_code=StadiumTelCode.TOKUYAMA,
            race_number=7,
            pit_number=2,
            start_course=2,
            arrival=3,
            total_time=114.3,
            start_time=0.16,
            winning_trick=None,
            disqualification=None,
        ),
        RaceRecord(
            race_holding_date=date(2018, 11, 16),
            stadium_tel_code=StadiumTelCode.TOKUYAMA,
            race_number=7,
            pit_number=3,
            start_course=3,
            arrival=4,
            total_time=114.6,
            start_time=0.15,
            winning_trick=None,
            disqualification=None,
        ),
        RaceRecord(
            race_holding_date=date(2018, 11, 16),
            stadium_tel_code=StadiumTelCode.TOKUYAMA,
            race_number=7,
            pit_number=4,
            start_course=4,
            arrival=1,
            total_time=111.4,
            start_time=0.17,
            winning_trick=WinningTrick.NUKI,
            disqualification=None,
        ),
        RaceRecord(
            race_holding_date=date(2018, 11, 16),
            stadium_tel_code=StadiumTelCode.TOKUYAMA,
            race_number=7,
            pit_number=5,
            start_course=5,
            arrival=6,
            total_time=None,
            start_time=0.19,
            winning_trick=None,
            disqualification=None,
        ),
        RaceRecord(
            race_holding_date=date(2018, 11, 16),
            stadium_tel_code=StadiumTelCode.TOKUYAMA,
            race_number=7,
            pit_number=6,
            start_course=6,
            arrival=5,
            total_time=None,
            start_time=0.19,
            winning_trick=None,
            disqualification=None,
        ),
    ]


def test_extract_race_records_from_a_race_which_has_four_disqualified_racers() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/20151114_02#_2R.html"))
    with open(file_path, mode="r") as file:
        data = extract_race_records(file)

    assert [
        RaceRecord(
            race_holding_date=date(2015, 11, 14),
            stadium_tel_code=StadiumTelCode.TODA,
            race_number=2,
            pit_number=1,
            start_course=1,
            arrival=2,
            total_time=112.7,
            start_time=0.35,
            winning_trick=None,
            disqualification=None,
        ),
        RaceRecord(
            race_holding_date=date(2015, 11, 14),
            stadium_tel_code=StadiumTelCode.TODA,
            race_number=2,
            pit_number=2,
            start_course=2,
            arrival=1,
            total_time=111.8,
            start_time=0.11,
            winning_trick=WinningTrick.MEGUMARE,
            disqualification=None,
        ),
        RaceRecord(
            race_holding_date=date(2015, 11, 14),
            stadium_tel_code=StadiumTelCode.TODA,
            race_number=2,
            pit_number=3,
            start_course=3,
            arrival=None,
            total_time=None,
            start_time=-0.01,
            winning_trick=None,
            disqualification=Disqualification.FLYING,
        ),
        RaceRecord(
            race_holding_date=date(2015, 11, 14),
            stadium_tel_code=StadiumTelCode.TODA,
            race_number=2,
            pit_number=4,
            start_course=4,
            arrival=None,
            total_time=None,
            start_time=-0.01,
            winning_trick=None,
            disqualification=Disqualification.FLYING,
        ),
        RaceRecord(
            race_holding_date=date(2015, 11, 14),
            stadium_tel_code=StadiumTelCode.TODA,
            race_number=2,
            pit_number=5,
            start_course=5,
            arrival=None,
            total_time=None,
            start_time=-0.01,
            winning_trick=None,
            disqualification=Disqualification.FLYING,
        ),
        RaceRecord(
            race_holding_date=date(2015, 11, 14),
            stadium_tel_code=StadiumTelCode.TODA,
            race_number=2,
            pit_number=6,
            start_course=6,
            arrival=None,
            total_time=None,
            start_time=-0.01,
            winning_trick=None,
            disqualification=Disqualification.FLYING,
        ),
    ]


def test_extract_race_records_from_a_no_contents_page() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/data_not_found.html"))

    with open(file_path, mode="r") as file:
        with pytest.raises(DataNotFound):
            extract_race_records(file)


def test_extract_race_records_from_a_canceled_race() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/canceled.html"))

    with open(file_path, mode="r") as file:
        with pytest.raises(RaceCanceled):
            extract_race_records(file)


def test_extract_payoffs_from_a_race_with_mass_flying() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/20160507_23#_2R.html"))

    with open(file_path, mode="r") as file:
        data = extract_race_payoffs(file)

    assert data == []


def test_extract_race_records_from_a_race_with_mass_flying() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/20160507_23#_2R.html"))

    with open(file_path, mode="r") as file:
        data = extract_race_records(file)

    assert data == [
        RaceRecord(
            race_holding_date=date(2016, 5, 7),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=2,
            pit_number=1,
            start_course=1,
            arrival=None,
            total_time=None,
            start_time=-0.01,
            winning_trick=None,
            disqualification=Disqualification.FLYING,
        ),
        RaceRecord(
            race_holding_date=date(2016, 5, 7),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=2,
            pit_number=2,
            start_course=2,
            arrival=None,
            total_time=None,
            start_time=-0.01,
            winning_trick=None,
            disqualification=Disqualification.FLYING,
        ),
        RaceRecord(
            race_holding_date=date(2016, 5, 7),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=2,
            pit_number=3,
            start_course=3,
            arrival=None,
            total_time=None,
            start_time=-0.01,
            winning_trick=None,
            disqualification=Disqualification.FLYING,
        ),
        RaceRecord(
            race_holding_date=date(2016, 5, 7),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=2,
            pit_number=4,
            start_course=6,
            arrival=None,
            total_time=None,
            start_time=0.03,
            winning_trick=None,
            disqualification=None,
        ),
        RaceRecord(
            race_holding_date=date(2016, 5, 7),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=2,
            pit_number=5,
            start_course=4,
            arrival=None,
            total_time=None,
            start_time=-0.01,
            winning_trick=None,
            disqualification=Disqualification.FLYING,
        ),
        RaceRecord(
            race_holding_date=date(2016, 5, 7),
            stadium_tel_code=StadiumTelCode.KARATSU,
            race_number=2,
            pit_number=6,
            start_course=5,
            arrival=None,
            total_time=None,
            start_time=-0.05,
            winning_trick=None,
            disqualification=Disqualification.FLYING,
        ),
    ]
