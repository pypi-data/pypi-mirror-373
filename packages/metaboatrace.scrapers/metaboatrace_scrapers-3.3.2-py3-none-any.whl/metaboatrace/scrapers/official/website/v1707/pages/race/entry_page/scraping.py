import re
from datetime import datetime
from typing import IO, Literal, cast

import pytz
from bs4 import BeautifulSoup
from metaboatrace.models.boat import BoatPerformance, MotorPerformance
from metaboatrace.models.race import RaceEntry, RaceInformation
from metaboatrace.models.racer import Racer, RacerPerformance, RacerRank

from metaboatrace.scrapers.official.website.exceptions import ScrapingError
from metaboatrace.scrapers.official.website.v1707.decorators import no_content_handleable
from metaboatrace.scrapers.official.website.v1707.factories import RaceLapsFactory
from metaboatrace.scrapers.official.website.v1707.pages.race.utils import parse_race_key_attributes


@no_content_handleable
def extract_race_information(file: IO[str]) -> RaceInformation:
    soup = BeautifulSoup(file, "html.parser")
    race_key_attributes = parse_race_key_attributes(soup)
    race_holding_date = race_key_attributes["race_holding_date"]
    stadium_tel_code = race_key_attributes["stadium_tel_code"]
    race_number = race_key_attributes["race_number"]

    deadline_table = soup.select_one(".table1")
    deadline_text = deadline_table.select("tbody tr")[-1].select("td")[race_number].get_text()
    hour, minute = [int(t) for t in deadline_text.split(":")]
    jst = pytz.timezone("Asia/Tokyo")
    deadline_at_jst = jst.localize(
        datetime(
            race_holding_date.year,
            race_holding_date.month,
            race_holding_date.day,
            hour,
            minute,
        )
    )
    deadline_at = deadline_at_jst.astimezone(pytz.utc)

    if m := re.match(
        # note: r"(\w+)\s*(1200|1800)m" だと 'ガチ勝゛ち８\u3000\n\t\t1800m' みたいなのがパースできない
        r"(.+?)\s*(1200|1800)m",
        soup.select_one("h3.title16_titleDetail__add2020").get_text().strip(),
    ):
        title = m.group(1)
        metre = cast(Literal[1200, 1800], int(m.group(2)))
    else:
        raise ScrapingError

    return RaceInformation(
        race_holding_date=race_holding_date,
        stadium_tel_code=stadium_tel_code,
        race_number=race_number,
        title=title,
        number_of_laps=RaceLapsFactory.create(metre),
        deadline_at=deadline_at,
        is_course_fixed="進入固定" in soup.body.get_text(),
        use_stabilizer="安定板使用" in soup.body.get_text(),
    )


@no_content_handleable
def extract_race_entries(file: IO[str]) -> list[RaceEntry]:
    soup = BeautifulSoup(file, "html.parser")
    race_key_attributes = parse_race_key_attributes(soup)

    data = []
    for pit_number, row in enumerate(soup.select(".table1")[-1].select("tbody"), 1):
        racer_photo_path = row.select_one("tr").select("td")[1].select_one("img")["src"]
        if m := re.search(r"(\d+)\.jpe?g$", racer_photo_path):
            racer_registration_number = int(m.group(1))
        else:
            raise ScrapingError

        motor_number = int(row.select_one("tr").select("td")[6].text.strip().split()[0])
        boat_number = int(row.select_one("tr").select("td")[7].text.strip().split()[0])

        is_absent = "is-miss" in row["class"]

        data.append(
            RaceEntry(
                **race_key_attributes,
                racer_registration_number=racer_registration_number,
                pit_number=pit_number,
                is_absent=is_absent,
                motor_number=motor_number,
                boat_number=boat_number,
            )
        )

    return data


@no_content_handleable
def extract_racers(file: IO[str]) -> list[Racer]:
    soup = BeautifulSoup(file, "html.parser")

    data = []
    for _, row in enumerate(soup.select(".table1")[-1].select("tbody"), 1):
        racer_photo_path = row.select_one("tr").select("td")[1].select_one("img")["src"]
        if m := re.search(r"(\d+)\.jpe?g$", racer_photo_path):
            racer_registration_number = int(m.group(1))
        else:
            raise ScrapingError

        racer_full_name = row.select_one("tr").select("td")[2].select_one("a").text.strip()
        racer_last_name, racer_first_name = re.split(r"[　 ]+", racer_full_name)

        racer_rank = RacerRank.from_string(
            row.select_one("tr").select("td")[2].select_one("span").text.strip()
        )

        data.append(
            # note: 出走表から性別は取れない
            Racer(
                registration_number=racer_registration_number,
                last_name=racer_last_name,
                first_name=racer_first_name,
                current_rating=racer_rank,
            )
        )

    return data


@no_content_handleable
def extract_boat_performances(file: IO[str]) -> list[BoatPerformance]:
    soup = BeautifulSoup(file, "html.parser")
    race_key_attributes = parse_race_key_attributes(soup)

    PLACE_HOLDER_OF_UNRECORDED_DATA = "-"

    data = []
    for _, row in enumerate(soup.select(".table1")[-1].select("tbody"), 1):
        data_strings = row.select_one("tr").select("td")[7].text.strip().split()
        number = int(data_strings[0])
        quinella_rate = (
            float(data_strings[1]) if data_strings[1] != PLACE_HOLDER_OF_UNRECORDED_DATA else None
        )
        trio_rate = (
            float(data_strings[2]) if data_strings[2] != PLACE_HOLDER_OF_UNRECORDED_DATA else None
        )

        data.append(
            BoatPerformance(
                stadium_tel_code=race_key_attributes["stadium_tel_code"],
                recorded_date=race_key_attributes["race_holding_date"],
                number=number,
                quinella_rate=quinella_rate,
                trio_rate=trio_rate,
            )
        )

    return data


@no_content_handleable
def extract_motor_performances(file: IO[str]) -> list[MotorPerformance]:
    soup = BeautifulSoup(file, "html.parser")
    race_key_attributes = parse_race_key_attributes(soup)

    PLACE_HOLDER_OF_UNRECORDED_DATA = "-"

    data = []
    for _, row in enumerate(soup.select(".table1")[-1].select("tbody"), 1):
        motor_data_strings = row.select_one("tr").select("td")[6].text.strip().split()
        number = int(motor_data_strings[0])
        quinella_rate = (
            float(motor_data_strings[1])
            if motor_data_strings[1] != PLACE_HOLDER_OF_UNRECORDED_DATA
            else None
        )
        trio_rate = (
            float(motor_data_strings[2])
            if motor_data_strings[2] != PLACE_HOLDER_OF_UNRECORDED_DATA
            else None
        )

        data.append(
            MotorPerformance(
                stadium_tel_code=race_key_attributes["stadium_tel_code"],
                recorded_date=race_key_attributes["race_holding_date"],
                number=number,
                quinella_rate=quinella_rate,
                trio_rate=trio_rate,
            )
        )

    return data


@no_content_handleable
def extract_racer_performances(file: IO[str]) -> list[RacerPerformance]:
    soup = BeautifulSoup(file, "html.parser")
    race_key_attributes = parse_race_key_attributes(soup)
    race_holding_date = race_key_attributes["race_holding_date"]

    data = []
    for _, row in enumerate(soup.select(".table1")[-1].select("tbody"), 1):
        racer_photo_path = row.select_one("tr").select("td")[1].select_one("img")["src"]
        if m := re.search(r"(\d+)\.jpe?g$", racer_photo_path):
            racer_registration_number = int(m.group(1))
        else:
            raise ScrapingError

        rate_in_all_stadium = float(row.select_one("tr").select("td")[4].text.strip().split()[0])
        rate_in_event_going_stadium = float(
            row.select_one("tr").select("td")[5].text.strip().split()[0]
        )

        data.append(
            RacerPerformance(
                racer_registration_number=racer_registration_number,
                aggregated_on=race_holding_date,
                rate_in_all_stadium=rate_in_all_stadium,
                rate_in_event_going_stadium=rate_in_event_going_stadium,
            )
        )

    return data


@no_content_handleable
def is_deadline_changed(file: IO[str]) -> bool:
    soup = BeautifulSoup(file, "html.parser")
    return "締切予定時刻が変更されております。ご注意ください。" in soup.select_one(".l-main").get_text().strip()
