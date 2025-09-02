import os
from datetime import date

import pytest
from metaboatrace.models.stadium import Event, SeriesGrade, SeriesKind, StadiumTelCode

from metaboatrace.scrapers.official.website.exceptions import DataNotFound, ScrapingError
from metaboatrace.scrapers.official.website.v1707.pages.monthly_schedule_page.scraping import (
    extract_events,
)

base_path = os.path.dirname(os.path.abspath(__file__))


def test_extract_events_from_a_monthly_schedule_page() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/2015_11.html"))
    with open(file_path, mode="r") as file:
        data = extract_events(file)

    assert len(data) == 59
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.KIRYU, data))) == 3
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.TODA, data))) == 3
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.EDOGAWA, data))) == 3
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.HEIWAJIMA, data))) == 2
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.TAMAGAWA, data))) == 2
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.HAMANAKO, data))) == 3
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.GAMAGORI, data))) == 3
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.TOKONAME, data))) == 3
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.TSU, data))) == 3
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.MIKUNI, data))) == 3
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.BIWAKO, data))) == 3
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.SUMINOE, data))) == 3
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.AMAGASAKI, data))) == 2
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.NARUTO, data))) == 0
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.MARUGAME, data))) == 3
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.MIYAJIMA, data))) == 3
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.KOJIMA, data))) == 3
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.TOKUYAMA, data))) == 1
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.SHIMONOSEKI, data))) == 2
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.WAKAMATSU, data))) == 0
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.ASHIYA, data))) == 3
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.FUKUOKA, data))) == 3
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.KARATSU, data))) == 3
    assert len(list(filter(lambda x: x.stadium_tel_code == StadiumTelCode.OMURA, data))) == 2

    # 代表値（月を跨ぐ開催の次節）
    assert data[3] == Event(
        stadium_tel_code=StadiumTelCode.TODA,
        title="戸田ルーキーシリーズ第７戦",
        starts_on=date(2015, 11, 7),
        days=6,
        grade=SeriesGrade.NO_GRADE,
        kind=SeriesKind.ROOKIE,
    )

    # 代表値（1日が初日）
    assert data[6] == Event(
        stadium_tel_code=StadiumTelCode.EDOGAWA,
        title="ヴィーナスシリーズ第７戦\u3000江戸川ＪＩＮＲＯ\u3000ＣＵＰ",
        starts_on=date(2015, 11, 1),
        days=6,
        grade=SeriesGrade.NO_GRADE,
        kind=SeriesKind.VENUS,
    )

    # 代表値（下旬初日で月を跨ぐ節）
    assert data[15] == Event(
        stadium_tel_code=StadiumTelCode.HAMANAKO,
        title="公営レーシングプレスアタック",
        starts_on=date(2015, 11, 28),
        days=5,
        grade=SeriesGrade.NO_GRADE,
        kind=SeriesKind.UNCATEGORIZED,
    )

    # 代表値（SG）
    assert data[50] == Event(
        stadium_tel_code=StadiumTelCode.ASHIYA,
        title="ＳＧ１８回チャレンジカップ／ＧⅡ２回レディースＣＣ",
        starts_on=date(2015, 11, 24),
        days=6,
        grade=SeriesGrade.SG,
        kind=SeriesKind.UNCATEGORIZED,
    )

    # 代表値（グレードとカテゴリの取得）
    assert data[54] == Event(
        stadium_tel_code=StadiumTelCode.KARATSU,
        title="ＧⅢオールレディース\u3000ＲＫＢラジオ杯",
        starts_on=date(2015, 11, 7),
        days=6,
        grade=SeriesGrade.G3,
        kind=SeriesKind.ALL_LADIES,
    )


def test_extract_events_from_a_monthly_schedule_page_for_specified_stadium() -> None:
    file_path = os.path.normpath(os.path.join(base_path, "./fixtures/2016_03_14#.html"))

    with open(file_path, mode="r") as file:
        with pytest.raises(ScrapingError):
            extract_events(file)


def test_extract_events_from_a_no_contents_page() -> None:
    file_path = os.path.normpath(
        os.path.join(os.path.join(base_path, "./fixtures/data_not_found.html"))
    )

    with open(file_path, mode="r") as file:
        with pytest.raises(DataNotFound):
            extract_events(file)
