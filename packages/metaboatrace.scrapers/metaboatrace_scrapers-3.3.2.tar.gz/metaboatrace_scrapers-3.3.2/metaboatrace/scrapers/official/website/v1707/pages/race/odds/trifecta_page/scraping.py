from functools import reduce
from itertools import zip_longest
from typing import IO, Generator

from bs4 import BeautifulSoup, ResultSet, Tag
from metaboatrace.models.race import BettingMethod, Odds

from metaboatrace.scrapers.official.website.v1707.decorators import (
    no_content_handleable,
    race_cancellation_handleable,
)
from metaboatrace.scrapers.official.website.v1707.pages.race.utils import parse_race_key_attributes


def _grouper(n: int, iterable: ResultSet[Tag], fillvalue=None):  # type: ignore
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


@no_content_handleable
@race_cancellation_handleable
def extract_odds(file: IO[str]) -> list[Odds]:
    soup = BeautifulSoup(file, "html.parser")
    race_key_attributes = parse_race_key_attributes(soup)

    odds_table = soup.select(".table1")[1]
    if len(odds_table.select("tbody tr td.oddsPoint")) != 120:
        # 今の所三連単しか対応してないので、
        # オッズのページであっても三連単以外のファイルが渡されたらエラーとする
        raise TypeError

    second_arrived_cells = odds_table.select('tbody tr td[rowspan="4"]')
    second_arrived_numbers = reduce(
        lambda a, b: a + b,
        [[int(cell.text) for cell in cells] * 4 for cells in _grouper(6, second_arrived_cells)],
    )
    third_arrived_numbers = [
        int(td.text) for td in odds_table.select('tbody tr td[class^="is-boatColor"]')
    ]

    data = []
    for i, td in enumerate(odds_table.select("tbody tr td.oddsPoint"), 0):
        if td.text == "欠場":
            # データ自体を作らない
            # ratio を 0.0 にしてdtoを作ったりしてたこともあったが、0.0だとベットしたら0円になるってことだし
            # それも不自然なためデータ自体が作らないのが違和感がないため
            continue

        data.append(
            Odds(
                **race_key_attributes,
                betting_method=BettingMethod.TRIFECTA,
                betting_numbers=[(i % 6) + 1, second_arrived_numbers[i], third_arrived_numbers[i]],
                ratio=float(td.text),
            )
        )

    return data
