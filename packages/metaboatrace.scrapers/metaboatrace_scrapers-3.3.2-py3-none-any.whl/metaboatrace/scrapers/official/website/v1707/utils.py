from datetime import date

from metaboatrace.models.stadium import StadiumTelCode


def format_stadium_tel_code_for_query_string(stadium_tel_code: StadiumTelCode) -> str:
    return str(stadium_tel_code.value).zfill(2)


def format_date_for_query_string(date: date) -> str:
    return date.strftime("%Y%m%d")
