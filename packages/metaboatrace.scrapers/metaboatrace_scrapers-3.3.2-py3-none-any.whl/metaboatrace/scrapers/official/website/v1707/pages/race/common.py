import re
from typing import IO, Dict

import numpy as np
from bs4 import BeautifulSoup

from metaboatrace.scrapers.official.website.v1707.factories import WeatherFactory


def extract_weather_condition_base_data(file: IO[str]):  # type: ignore # todo: fix typ
    soup = BeautifulSoup(file, "html.parser")

    WIND_ICON_IDS = list(range(1, 17))
    NO_WIND_ICON_ID = 17

    data_container = soup.select_one(".weather1")
    if m := re.search(
        r"is-wind(\d{1,2})",
        "".join(data_container.select_one(".is-windDirection p")["class"]),
    ):
        wind_direction_id_in_official = int(m.group(1))
        # NOTE: 方位を角度としてとった風向きの配列。スリットの北が0度。
        # http://boatrace.jp/static_extra/pc/images/icon_wind1_1.png
        #
        # 先頭の要素は0°で、以降22.5°ずつ増えていく
        # wind_clock_angles[0]
        # => 0.0
        # wind_clock_angles[1]
        # => 22.5
        # wind_clock_angles[2]
        # => 90.0
        # wind_clock_angles[15]
        # => 337.5
        wind_angles = np.arange(0, 361, (360 / len(WIND_ICON_IDS)))
        wind_angle = (
            None
            if wind_direction_id_in_official == NO_WIND_ICON_ID
            else wind_angles[wind_direction_id_in_official - 1]
        )

    else:
        raise ValueError

    weather = WeatherFactory.create(data_container.select_one(".is-weather").text.strip())

    # NOTE: 数年に一度ぐらいの頻度ではあるが波高が入っていないケースがある
    # https://www.boatrace.jp/owpc/pc/race/raceresult?rno=9&jcd=23&hd=20200209
    wavelength_str = (
        data_container.select(".weather1_bodyUnitLabelData")[3].text.strip().replace("cm", "")
    )
    wavelength = float(wavelength_str) if wavelength_str else 0.0

    wind_velocity = float(
        data_container.select(".weather1_bodyUnitLabelData")[1].text.strip().replace("m", "")
    )
    air_temperature = float(
        data_container.select(".weather1_bodyUnitLabelData")[0].text.strip().replace("℃", "")
    )
    water_temperature = float(
        data_container.select(".weather1_bodyUnitLabelData")[2].text.strip().replace("℃", "")
    )

    return {
        "weather": weather,
        "wavelength": wavelength,
        "wind_angle": wind_angle,
        "wind_velocity": wind_velocity,
        "air_temperature": air_temperature,
        "water_temperature": water_temperature,
    }
