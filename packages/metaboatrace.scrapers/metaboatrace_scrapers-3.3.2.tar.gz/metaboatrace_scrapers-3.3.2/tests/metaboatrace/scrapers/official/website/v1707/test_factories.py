from typing import Literal, Optional, Type, Union

import pytest
from metaboatrace.models.boat import MotorParts
from metaboatrace.models.race import Disqualification, Weather, WinningTrick
from metaboatrace.models.stadium import EventHoldingStatus

from metaboatrace.scrapers.official.website.v1707.factories import (
    DisqualificationFactory,
    EventHoldingStatusFactory,
    MotorPartsFactory,
    RaceLapsFactory,
    WeatherFactory,
    WinningTrickFactory,
)


@pytest.mark.parametrize(
    "name,expected",
    [
        ("転", Disqualification.CAPSIZE),
        ("落", Disqualification.FALL),
        ("沈", Disqualification.SINKING),
        ("妨", Disqualification.VIOLATION),
        ("失", Disqualification.DISQUALIFICATION_AFTER_START),
        ("エ", Disqualification.ENGINE_STOP),
        ("不", Disqualification.UNFINISHED),
        ("返", Disqualification.REPAYMENT_OTHER_THAN_FLYING_AND_LATENESS),
        ("Ｆ", Disqualification.FLYING),
        ("Ｌ", Disqualification.LATENESS),
        ("欠", Disqualification.ABSENT),
        ("＿", None),
        ("誤", ValueError),
    ],
)
def test_disqualification_factory(
    name: str, expected: Union[Optional[Disqualification], Type[ValueError]]
) -> None:
    if expected is ValueError:
        with pytest.raises(expected):
            DisqualificationFactory.create(name)
    else:
        assert DisqualificationFactory.create(name) == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("電気", MotorParts.ELECTRICAL_SYSTEM),
        ("キャブ", MotorParts.CARBURETOR),
        ("ピストン", MotorParts.PISTON),
        ("リング", MotorParts.PISTON_RING),
        ("シリンダ", MotorParts.CYLINDER),
        ("ギア", MotorParts.GEAR_CASE),
        ("ギヤ", MotorParts.GEAR_CASE),
        ("キャリ", MotorParts.CARRIER_BODY),
        ("シャフト", MotorParts.CRANKSHAFT),
        ("バルブ", ValueError),
    ],
)
def test_motor_parts_factory(name: str, expected: Union[MotorParts, Type[ValueError]]) -> None:
    if expected is ValueError:
        with pytest.raises(expected):
            MotorPartsFactory.create(name) == expected
    else:
        assert MotorPartsFactory.create(name) == expected


@pytest.mark.parametrize(
    "metre,expected",
    [
        (1200, 2),
        (1800, 3),
    ],
)
def test_race_laps_factory(metre: Literal[1200, 1800], expected: Literal[2, 3]) -> None:
    assert RaceLapsFactory.create(metre) == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("逃げ", WinningTrick.NIGE),
        ("差し", WinningTrick.SASHI),
        ("まくり", WinningTrick.MAKURI),
        ("まくり差し", WinningTrick.MAKURIZASHI),
        ("抜き", WinningTrick.NUKI),
        ("恵まれ", WinningTrick.MEGUMARE),
        ("ツケマイ", ValueError),
    ],
)
def test_winning_trick_factory(name: str, expected: Union[WinningTrick, Type[ValueError]]) -> None:
    if expected is ValueError:
        with pytest.raises(expected):
            WinningTrickFactory.create(name) == expected
    else:
        assert WinningTrickFactory.create(name) == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("晴", Weather.FINE),
        ("曇", Weather.CLOUDY),
        ("雨", Weather.RAINY),
        ("雪", Weather.SNOWY),
        ("台風", Weather.TYPHOON),
        ("霧", Weather.FOG),
        ("嵐", ValueError),
    ],
)
def test_weather_factory(name: str, expected: Union[Weather, Type[ValueError]]) -> None:
    if expected is ValueError:
        with pytest.raises(expected):
            WeatherFactory.create(name) == expected
    else:
        assert WeatherFactory.create(name) == expected


def test_event_holding_status_factory() -> None:
    assert EventHoldingStatusFactory.create("中止") == EventHoldingStatus.CANCELED

    assert EventHoldingStatusFactory.create("中止順延") == EventHoldingStatus.POSTPONED

    assert EventHoldingStatusFactory.create("開催") == EventHoldingStatus.OPEN
    assert EventHoldingStatusFactory.create("不明") == EventHoldingStatus.OPEN
    assert EventHoldingStatusFactory.create("") == EventHoldingStatus.OPEN
