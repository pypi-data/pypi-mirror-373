import calendar
import re
from datetime import date, timedelta
from typing import IO, Optional

from bs4 import BeautifulSoup
from metaboatrace.models.stadium import Event, SeriesGrade, SeriesKind, StadiumTelCode

from metaboatrace.scrapers.official.website.exceptions import ScrapingError
from metaboatrace.scrapers.official.website.v1707.decorators import no_content_handleable


@no_content_handleable
# note: 命名について
# scrape_events にしようと思ったが scrape の目的語はスクレイピング対象のWebページだから違和感ある
# get_events はアクセサメソッド見たいなニュアンスがあって違和感ある
# 引数のWebページのHTMLからデータを抜き出すという意味で extract が合ってると思ったので以下の名前にした
def extract_events(file: IO[str]) -> list[Event]:
    soup = BeautifulSoup(file, "html.parser")

    schedule_rows = soup.select("table.is-spritedNone1 tbody tr")
    if len(schedule_rows) != 24:
        # 公式サイトの仕様では場を指定できるが、用途がまだないのでYAGNI原則を遵守して未実装
        raise ScrapingError

    _, current_month = _parse_calendar(soup)
    offset_day = _parse_offset_date(soup)

    data = []

    for stadium_tel_code, row in enumerate(schedule_rows, 1):
        date_pointer = offset_day

        for series_cell in row.select("td"):
            series_days_str = series_cell.get("colspan")
            if series_days_str is None:
                date_pointer = date_pointer + timedelta(1)
                continue

            series_days = int(series_days_str)
            title = series_cell.get_text()

            if title and (date_pointer.month == current_month):
                data.append(
                    Event(
                        stadium_tel_code=StadiumTelCode(stadium_tel_code),
                        starts_on=date_pointer,
                        days=series_days,
                        grade=_parse_race_grade_from_html_class(series_cell["class"][0])
                        or _parse_race_grade_from_event_title(title)
                        or SeriesGrade.NO_GRADE,
                        kind=_parse_race_kind_from_html_class(series_cell["class"][0])
                        or _parse_race_kind_from_event_title(title)
                        or SeriesKind.UNCATEGORIZED,
                        title=title,
                    )
                )

            date_pointer = date_pointer + timedelta(series_days)

    return data


def _parse_calendar(soup: BeautifulSoup) -> tuple[int, int]:
    """どの年月の月間スケジュールかを返す

    Args:
        soup (BeautifulSoup): bs4でパースされた月間スケジュールのHTML

    Returns:
        tuple[int, int]: 西暦と月のタプル
    """
    if match := re.search(r"\?ym=(\d{6})", soup.select_one("li.title2_navsLeft a")["href"]):
        return calendar._nextmonth(year=int(match.group(1)[:4]), month=int(match.group(1)[4:]))  # type: ignore
    else:
        raise ScrapingError


def _parse_offset_date(soup: BeautifulSoup) -> date:
    """月間スケジュールの起点となる日付を返す

    例えば、スクレイピング対象の月間スケジュールが2015年11月の場合でも、カレンダーは11/01から始まっているとは限らない
    前月の28日などから始まっている可能性があり、月により開始日はまちまちである。それを動的に取得する

    Args:
        soup (BeautifulSoup): bs4でパースされた月間スケジュールのHTML

    Returns:
        date: 月間スケジュールの起点となる日付
    """
    year, month = _parse_calendar(soup)

    if match := re.search(
        r"(\d{1,2})", soup.select_one("table thead tr").select("th")[1].get_text()
    ):
        start_day = int(match.group(1))
        if start_day == 1:
            return date(year, month, 1)
        else:
            year_of_last_month, last_month = calendar._prevmonth(year, month)  # type: ignore
            return date(year_of_last_month, last_month, start_day)

    else:
        raise ScrapingError


def _parse_race_grade_from_event_title(event_title: str) -> Optional[SeriesGrade]:
    if match := re.search(r"G[1-3]{1}", event_title.translate(str.maketrans("ＧⅠⅡⅢ１２３", "G123123"))):
        try:
            return SeriesGrade(match.group(0))
        except ValueError:
            return None
    else:
        return None


def _parse_race_grade_from_html_class(html_class: str) -> Optional[SeriesGrade]:
    if match := re.match(r"is-gradeColor(SG|G[123])", html_class):
        return SeriesGrade.from_string(match.group(1))

    if html_class == "is-gradeColorLady":
        return SeriesGrade.G3

    return None


def _parse_race_kind_from_event_title(event_title: str) -> Optional[SeriesKind]:
    if match := re.search(r"男女[wWＷ]優勝戦", event_title):
        return SeriesKind.DOUBLE_WINNER
    else:
        return None


def _parse_race_kind_from_html_class(html_class: str) -> Optional[SeriesKind]:
    if html_class == "is-gradeColorRookie":
        return SeriesKind.ROOKIE
    elif html_class == "is-gradeColorVenus":
        return SeriesKind.VENUS
    elif html_class == "is-gradeColorLady":
        return SeriesKind.ALL_LADIES
    elif html_class == "is-gradeColorTakumi":
        return SeriesKind.SENIOR
    else:
        return None
