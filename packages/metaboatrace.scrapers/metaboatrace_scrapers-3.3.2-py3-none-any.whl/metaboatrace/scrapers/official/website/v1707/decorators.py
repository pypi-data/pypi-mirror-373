import re
from typing import IO, Protocol, TypeVar, cast

from bs4 import BeautifulSoup

from metaboatrace.scrapers.official.website.exceptions import DataNotFound, RaceCanceled


class FuncProtocol(Protocol):
    def __call__(self, file: IO[str]) -> BeautifulSoup:
        ...


F = TypeVar("F", bound=FuncProtocol)


def no_content_handleable(func: F) -> F:
    def wrapper(file: IO[str]) -> BeautifulSoup:
        soup = BeautifulSoup(file, "html.parser")

        if re.match(r"データ[がは]ありません", soup.select_one(".l-main").get_text().strip()):
            raise DataNotFound

        if "※ データはありません。" in soup.body.get_text():
            raise DataNotFound

        if "※ データが存在しないのでページを表示できません。" in soup.body.get_text():
            raise DataNotFound

        file.seek(0)
        return func(file)

    return cast(F, wrapper)


def race_cancellation_handleable(func: F) -> F:
    def wrapper(file: IO[str]) -> BeautifulSoup:
        soup = BeautifulSoup(file, "html.parser")

        if re.search(r"レース[は]?中止", soup.select_one(".l-main").get_text().strip()):
            raise RaceCanceled

        file.seek(0)
        return func(file)

    return cast(F, wrapper)
