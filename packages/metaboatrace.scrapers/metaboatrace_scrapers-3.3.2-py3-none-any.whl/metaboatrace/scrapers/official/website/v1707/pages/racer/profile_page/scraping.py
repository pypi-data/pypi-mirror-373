import re
from dataclasses import dataclass
from datetime import date
from typing import IO

from bs4 import BeautifulSoup
from metaboatrace.models.racer import Racer, RacerRank
from metaboatrace.models.region import Branch, BranchFactory, PrefectureFactory

from metaboatrace.scrapers.official.website.v1707.decorators import no_content_handleable


@no_content_handleable
def extract_racer_profile(file: IO[str]) -> Racer:
    soup = BeautifulSoup(file, "html.parser")

    full_name = soup.select_one(".racer1_bodyName").get_text()
    last_name, first_name = re.split(r"[\s　]+", full_name)

    dd_list = soup.select_one("dl.list3").select("dd")

    registration_number = int(dd_list[0].get_text())
    birth_date = date(*[int(ymd) for ymd in dd_list[1].get_text().split("/")])

    if m := re.match(r"(\d{3})cm", dd_list[2].get_text()):
        height = int(m.group(1))
    branch = Branch(BranchFactory.create(dd_list[5].get_text()))
    born_prefecture = PrefectureFactory.create(dd_list[6].get_text())
    if m := re.match(r"(\d{2,3})期", dd_list[7].get_text()):
        term = int(m.group(1))
    racer_rank = RacerRank.from_string(dd_list[8].get_text()[:2])

    return Racer(
        registration_number=registration_number,
        last_name=last_name,
        first_name=first_name,
        term=term,
        birth_date=birth_date,
        height=height,
        born_prefecture=born_prefecture,
        branch=branch,
        current_rating=racer_rank,
    )
