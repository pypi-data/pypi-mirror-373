import re
import unicodedata
from typing import IO

from bs4 import BeautifulSoup
from metaboatrace.models.race import BettingMethod, Payoff, RaceRecord, WeatherCondition

from metaboatrace.scrapers.official.website.v1707.decorators import (
    no_content_handleable,
    race_cancellation_handleable,
)
from metaboatrace.scrapers.official.website.v1707.factories import (
    DisqualificationFactory,
    WinningTrickFactory,
)
from metaboatrace.scrapers.official.website.v1707.pages.race.common import (
    extract_weather_condition_base_data,
)
from metaboatrace.scrapers.official.website.v1707.pages.race.utils import parse_race_key_attributes


@race_cancellation_handleable
@no_content_handleable
def extract_race_payoffs(file: IO[str]) -> list[Payoff]:
    soup = BeautifulSoup(file, "html.parser")
    race_key_attributes = parse_race_key_attributes(soup)
    race_holding_date = race_key_attributes["race_holding_date"]
    stadium_tel_code = race_key_attributes["stadium_tel_code"]
    race_number = race_key_attributes["race_number"]

    payment_table = soup.select(".table1")[3]
    # YAGNI原則に則って今の所三連単だけ対応
    trifecta_tbody = payment_table.select_one("tbody")
    rowspan = int(trifecta_tbody.select_one("td")["rowspan"])

    data = []
    for tr in trifecta_tbody.select("tr"):
        tds = tr.select(f'td:not([rowspan="{rowspan}"])')

        betting_numbers = tds[0].select("span.numberSet1_number")
        if len(betting_numbers) == 0:
            continue

        data.append(
            Payoff(
                race_holding_date=race_holding_date,
                stadium_tel_code=stadium_tel_code,
                race_number=race_number,
                betting_method=BettingMethod.TRIFECTA,
                betting_numbers=map(int, [span.get_text() for span in betting_numbers]),
                amount=int(re.match(r"¥([\d]+)", tds[1].get_text().replace(",", "")).group(1)),  # type: ignore # todo: fix type
            )
        )

    return data


@no_content_handleable
@race_cancellation_handleable
def extract_weather_condition(file: IO[str]) -> WeatherCondition:
    soup = BeautifulSoup(file, "html.parser")
    race_key_attributes = parse_race_key_attributes(soup)

    file.seek(0)
    weather_condition_base_attributes = extract_weather_condition_base_data(file)

    return WeatherCondition(
        **race_key_attributes,
        **weather_condition_base_attributes,
        in_performance=True,
    )


@no_content_handleable
@race_cancellation_handleable
def extract_race_records(file: IO[str]) -> RaceRecord:
    soup = BeautifulSoup(file, "html.parser")
    race_key_attributes = parse_race_key_attributes(soup)

    # データがテーブル横断で存在しているため分けてとる
    # これは順位のテーブル
    data_originated_record_table = []
    for row in soup.select(".table1")[1].select("tbody"):
        pit_number = int(row.select("td")[1].text)

        arrival_mark = row.select("td")[0].text
        try:
            arrival = int(unicodedata.normalize("NFKC", arrival_mark))
            disqualification = None
        except ValueError:
            # note: 失格はレース不成立で着順が定まらなかったケースにNoneになり得る
            arrival = None
            disqualification = DisqualificationFactory.create(arrival_mark)

        time_text = row.select("td")[3].text
        if m := re.search(r'(\d{1})\'(\d{2})"(\d{1})', time_text):
            total_time = 60 * int(m.group(1)) + 1 * int(m.group(2)) + 0.1 * int(m.group(3))
        else:
            total_time = None

        data_originated_record_table.append(
            {
                "pit_number": pit_number,
                "arrival": arrival,
                "total_time": total_time,
                "disqualification": disqualification,
            }
        )

    # ここからはスリットのテーブル
    data_originated_slit_table = []
    for start_course, row in enumerate(soup.select(".table1")[2].select("tbody tr"), 1):
        pit_number = int(row.select_one(".table1_boatImage1Number").text)

        time_text = row.select_one(".table1_boatImage1TimeInner").text.strip()
        if m := re.search(r"([\u4E00-\u9FD0あ-ん]+)", time_text):
            winning_trick = WinningTrickFactory.create(m.group(1))
        else:
            winning_trick = None

        if m := re.search(r"(F?)\.(\d{1,2})", time_text):
            start_time = float(f"0.{m.group(2)}")
            if m.group(1):
                # フライングは負の数で返す
                # disqualification でフライングかどうかはわかるが、正常なスタートと同じ値で返すのは違和感あるため
                start_time = start_time * -1
        elif time_text == "L":
            # note: 出遅れはここに出るケースと出ないケースがある
            # 出るケース -> https://boatrace.jp/owpc/pc/race/raceresult?rno=5&jcd=16&hd=20231204
            # 出ないケース -> https://boatrace.jp/owpc/pc/race/raceresult?rno=7&jcd=09&hd=20151116
            start_time = 1
        else:
            raise ValueError

        data_originated_slit_table.append(
            {
                "pit_number": pit_number,
                "start_course": start_course,
                "start_time": start_time,
                "winning_trick": winning_trick,
            }
        )

    # 表別に取っておいたデータをマージする
    data = [
        RaceRecord(
            **dict(
                race_key_attributes,
                **dict(
                    next(
                        (
                            d
                            for d in data_originated_record_table
                            if d.get("pit_number") == pit_number
                        ),
                        {},
                    ),
                    **next(
                        (
                            d
                            for d in data_originated_slit_table
                            if d.get("pit_number") == pit_number
                        ),
                        {},
                    ),
                ),
            )
        )
        for pit_number in range(1, 7)
    ]

    return data
