import re
from typing import IO, Optional

from bs4 import BeautifulSoup
from metaboatrace.models.stadium import EventHolding, EventHoldingStatus, StadiumTelCode

from metaboatrace.scrapers.official.website.v1707.factories import EventHoldingStatusFactory

CANCELED_TEXTS = ["中止順延", "中止"]


def extract_event_holdings(file: IO[str]) -> list[EventHolding]:
    soup = BeautifulSoup(file, "html.parser")

    data = []
    for tbody in soup.select(".table1 table tbody"):
        text = tbody.get_text()
        html_string = str(tbody)

        if _canceled(text) and (day_text := _cancel_text(text)):
            status = EventHoldingStatusFactory.create(day_text)
            progress_day = None
        else:
            status = EventHoldingStatus.OPEN
            progress_day = _progress_day(text)

        data.append(
            EventHolding(
                stadium_tel_code=_stadium_tel_code(html_string),
                date=None,
                status=status,
                progress_day=progress_day,
            )
        )

    return data


def _canceled(text: str) -> bool:
    if re.search(r"\d+R以降中止", text):
        return False
    return any(ct in text for ct in CANCELED_TEXTS)


def _cancel_text(text: str) -> Optional[str]:
    if re.search(r"\d+R以降中止", text):
        return None
    for ct in CANCELED_TEXTS:
        if ct in text:
            return ct
    return None


def _stadium_tel_code(html_string: str) -> StadiumTelCode:
    match = re.search(r"\?jcd=(\d{2})", html_string)
    if not match:
        raise ValueError("Invalid file format")
    return StadiumTelCode(int(match.group(1)))


def _day_text(text: str) -> Optional[str]:
    match = re.search(r"(初日|[\d１２３４５６７]日目|最終日)", text)
    return match.group(0) if match else None


def _progress_day(text: str) -> Optional[int]:
    match = re.search(r"(初日|[\d１２３４５６７]日目|最終日)", text)

    if not match:
        return None

    day_text = match.group(0)
    if day_text == "初日":
        return 1
    elif day_text == "最終日":
        return -1
    else:
        return int(day_text[0].translate(str.maketrans("１２３４５６７", "1234567")))
