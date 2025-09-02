import re
from dataclasses import dataclass
from typing import IO

from bs4 import BeautifulSoup
from metaboatrace.models.racer import Gender, Racer, RacerRank

from metaboatrace.scrapers.official.website.v1707.decorators import no_content_handleable


@dataclass(frozen=True)
class EventEntry:
    racer_registration_number: int
    racer_gender: Gender
    racer_last_name: str
    racer_first_name: str
    racer_rank: RacerRank
    motor_number: int
    quinella_rate_of_motor: float
    boat_number: int
    quinella_rate_of_boat: float
    anterior_time: float


@no_content_handleable
def extract_racers(file: IO[str]) -> list[Racer]:
    soup = BeautifulSoup(file, "html.parser")

    data = []
    series_entry_rows = soup.select(".table1 table tbody tr")
    pattern_of_name_delimiter = re.compile(r"[　]+")

    for row in series_entry_rows:
        cells = row.select("td")
        try:
            racer_last_name, racer_first_name = pattern_of_name_delimiter.split(
                cells[2].get_text().strip()
            )
        except ValueError:
            racer_last_name = cells[2].get_text()
            racer_first_name = ""

        data.append(
            Racer(
                registration_number=int(cells[1].get_text()),
                last_name=racer_last_name,
                first_name=racer_first_name,
                gender=Gender.FEMALE if row.select_one("i.is-lady") else Gender.MALE,
                current_rating=RacerRank.from_string(cells[3].get_text().strip()),
            )
        )

    return data


@no_content_handleable
def extract_event_entries(file: IO[str]) -> list[EventEntry]:
    soup = BeautifulSoup(file, "html.parser")

    data = []
    series_entry_rows = soup.select(".table1 table tbody tr")
    pattern_of_name_delimiter = re.compile(r"[　]+")

    for row in series_entry_rows:
        cells = row.select("td")
        try:
            racer_last_name, racer_first_name = pattern_of_name_delimiter.split(
                cells[2].get_text().strip()
            )
        except ValueError:
            racer_last_name = cells[2].get_text()
            racer_first_name = ""

        data.append(
            EventEntry(
                racer_registration_number=int(cells[1].get_text()),
                racer_gender=Gender.FEMALE if row.select_one("i.is-lady") else Gender.MALE,
                racer_last_name=racer_last_name,
                racer_first_name=racer_first_name,
                racer_rank=RacerRank.from_string(cells[3].get_text().strip()),
                motor_number=int(cells[4].get_text().strip()),
                quinella_rate_of_motor=float(cells[5].get_text().strip()[:-1]),
                boat_number=int(cells[6].get_text().strip()),
                quinella_rate_of_boat=float(cells[7].get_text().strip()[:-1]),
                anterior_time=float(cells[8].get_text().strip()),
            )
        )

    return data
