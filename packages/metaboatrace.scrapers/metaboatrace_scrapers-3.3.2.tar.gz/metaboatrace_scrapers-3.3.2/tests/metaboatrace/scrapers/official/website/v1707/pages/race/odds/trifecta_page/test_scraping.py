import os
from datetime import date

import pytest
from metaboatrace.models.race import BettingMethod, Odds
from metaboatrace.models.stadium import StadiumTelCode

from metaboatrace.scrapers.official.website.exceptions import DataNotFound, RaceCanceled
from metaboatrace.scrapers.official.website.v1707.pages.race.odds.trifecta_page.scraping import (
    extract_odds,
)

base_path = os.path.dirname(os.path.abspath(__file__))


def test_extract_odds() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/20170919_19#_11R.html"))

    with open(file_path, mode="r") as file:
        data = extract_odds(file)

    assert len(data) == 60
    assert data[0] == Odds(
        race_holding_date=date(2017, 9, 19),
        stadium_tel_code=StadiumTelCode.SHIMONOSEKI,
        race_number=11,
        betting_method=BettingMethod.TRIFECTA,
        betting_numbers=[1, 2, 3],
        ratio=6.1,
    )
    assert data[-1] == Odds(
        race_holding_date=date(2017, 9, 19),
        stadium_tel_code=StadiumTelCode.SHIMONOSEKI,
        race_number=11,
        betting_method=BettingMethod.TRIFECTA,
        betting_numbers=[5, 4, 3],
        ratio=413.5,
    )
    assert len([odds for odds in data if "6" in str(odds.betting_numbers)]) == 0


def test_extarct_odds_from_a_no_contents_page() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/20170102_01#_1R.html"))

    with open(file_path, mode="r") as file:
        with pytest.raises(DataNotFound):
            extract_odds(file)


def test_extract_odds_from_a_canceled_race() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/20180103_03#_11R.html"))

    with open(file_path, mode="r") as file:
        with pytest.raises(RaceCanceled):
            extract_odds(file)
