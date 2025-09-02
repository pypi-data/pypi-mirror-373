import re
from dataclasses import dataclass
from typing import IO

from bs4 import BeautifulSoup
from metaboatrace.models.race import (
    BoatSetting,
    CircumferenceExhibitionRecord,
    StartExhibitionRecord,
    WeatherCondition,
)
from metaboatrace.models.racer import RacerCondition

from metaboatrace.scrapers.official.website.exceptions import DataNotFound
from metaboatrace.scrapers.official.website.v1707.decorators import (
    no_content_handleable,
    race_cancellation_handleable,
)
from metaboatrace.scrapers.official.website.v1707.factories import MotorPartsFactory
from metaboatrace.scrapers.official.website.v1707.pages.race.common import (
    extract_weather_condition_base_data,
)
from metaboatrace.scrapers.official.website.v1707.pages.race.utils import parse_race_key_attributes


@no_content_handleable
@race_cancellation_handleable
def extract_start_exhibition_records(file: IO[str]) -> list[StartExhibitionRecord]:
    soup = BeautifulSoup(file, "html.parser")
    race_key_attributes = parse_race_key_attributes(soup)

    data = []
    for start_course, row in enumerate(soup.select(".table1")[2].select("tbody tr"), 1):
        if row.select_one("img") is None:
            # 画像がない場合は出遅れか展示不出走
            #
            # 出遅れが発生した展示
            # http://boatrace.jp/owpc/pc/race/beforeinfo?rno=2&jcd=17&hd=20170511
            continue

        m = re.search(r"_([1-6]{1}).png$", row.select_one("img")["src"])
        pit_number = int(m.group(1))  # type: ignore

        start_time_element = row.select("span")[-1]
        if m := re.search(r"F?\.(\d{2})$", start_time_element.text):
            start_time = float(f"0.{m.group(1)}")
            if "is-fBold" in start_time_element["class"]:
                # この場合はフライング
                start_time = start_time * -1
        elif start_time_element.text == "L":
            start_time = 1.0
        elif pit_number:
            # note: L マークが出てないけど舟の画像があり、周回展示には謎に出ているケース
            # https://boatrace.jp/owpc/pc/race/beforeinfo?rno=9&jcd=20&hd=20200621
            #
            # これは進入は大外で出遅れと判定する
            start_time = 1.0
        else:
            raise ValueError

        data.append(
            StartExhibitionRecord(
                **race_key_attributes,
                pit_number=pit_number,
                start_course=start_course,
                start_time=start_time,
            )
        )

    return data


@no_content_handleable
@race_cancellation_handleable
def extract_circumference_exhibition_records(
    file: IO[str],
) -> list[CircumferenceExhibitionRecord]:
    soup = BeautifulSoup(file, "html.parser")
    race_key_attributes = parse_race_key_attributes(soup)

    data = []
    for pit_number, row in enumerate(soup.select(".table1")[1].select("tbody"), 1):
        if "is-miss" in row["class"]:
            # 欠場
            continue

        try:
            exhibition_time = float(row.select("td")[4].text)
        except (TypeError, ValueError):
            # 欠場じゃなくても展示だけ不参加とか展示中に転覆とかだとNoneをfloatで評価した結果ここに来るかも？
            #
            # 以下のように、スタート展示だけ実施されたがその後の周回展示が中止になった場合
            # https://boatrace.jp/owpc/pc/race/beforeinfo?rno=8&jcd=03&hd=20240322
            #
            # この場合は `row.select("td")[4].text` の評価結果が '\xa0' になる
            # ('\xa0' は &nbsp の 数字文字参照)
            continue

        data.append(
            CircumferenceExhibitionRecord(
                **race_key_attributes,
                pit_number=pit_number,
                exhibition_time=exhibition_time,
            )
        )

    return data


@no_content_handleable
@race_cancellation_handleable
def extract_racer_conditions(file: IO[str]) -> list[RacerCondition]:
    soup = BeautifulSoup(file, "html.parser")

    # hack: 欲しいのは日付だけで場コードと何レース目かは不要なんだけどいったんこれで
    race_key_attributes = parse_race_key_attributes(soup)

    data = []
    for row in soup.select(".table1")[1].select("tbody"):
        if "is-miss" in row["class"]:
            # 欠場
            continue

        if m := re.search(r"toban=(\d{4})$", row.select("td")[2].select_one("a")["href"]):
            racer_registration_number = int(m.group(1))
        else:
            raise ValueError

        weight = float(row.select("td")[3].text[:-2])
        adjust = float(row.select("td")[12].text)

        data.append(
            RacerCondition(
                recorded_on=race_key_attributes["race_holding_date"],
                racer_registration_number=racer_registration_number,
                weight=weight,
                adjust=adjust,
            )
        )

    return data


@no_content_handleable
@race_cancellation_handleable
def extract_boat_settings(file: IO[str]) -> BoatSetting:
    NEW_PROPELLER_MARK = "新"
    MOTOR_PARTS_QUANTITY_DELIMITER = "×"

    soup = BeautifulSoup(file, "html.parser")
    race_key_attributes = parse_race_key_attributes(soup)
    race_holding_date = race_key_attributes["race_holding_date"]
    stadium_tel_code = race_key_attributes["stadium_tel_code"]
    race_number = race_key_attributes["race_number"]

    data = []

    for pit_number, row in enumerate(soup.select(".table1")[1].select("tbody"), 1):
        if "is-miss" in row["class"]:
            continue

        try:
            tilt = float(row.select("td")[5].text)
            is_new_propeller = row.select("td")[6].text.strip() == NEW_PROPELLER_MARK
        except ValueError:
            raise DataNotFound

        numbers = dict(zip(["１", "２", "３", "４", "５", "６", "７", "８", "９"], range(1, 10)))
        motor_parts_exchanges = []
        for li in row.select("td")[7].select("li"):
            if MOTOR_PARTS_QUANTITY_DELIMITER in li.get_text():
                parts_name, quantity_text = li.get_text().split(MOTOR_PARTS_QUANTITY_DELIMITER)
            else:
                # note: 'シャフト\xa0' みたいに非改行空白（non-breaking space）を表すエスケープシーケンスが混入している場合がある
                # https://boatrace.jp/owpc/pc/race/beforeinfo?rno=10&jcd=06&hd=20231124
                parts_name = li.get_text().replace("\xa0", "")
                quantity_text = None

            motor_parts_exchanges.append(
                (MotorPartsFactory.create(parts_name), numbers.get(quantity_text, 1))
            )

        data.append(
            BoatSetting(
                race_holding_date=race_holding_date,
                stadium_tel_code=stadium_tel_code,
                race_number=race_number,
                pit_number=pit_number,
                tilt=tilt,
                is_new_propeller=is_new_propeller,
                motor_parts_exchanges=motor_parts_exchanges,
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
        in_performance=False,
    )
