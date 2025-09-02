from typing import Literal, Optional, cast

from metaboatrace.models.boat import MotorParts
from metaboatrace.models.race import Disqualification, Weather, WinningTrick
from metaboatrace.models.stadium import EventHoldingStatus


class DisqualificationFactory:
    @staticmethod
    def create(name: str) -> Optional[Disqualification]:
        if "転" in name:
            return Disqualification.CAPSIZE
        elif "落" in name:
            return Disqualification.FALL
        elif "沈" in name:
            return Disqualification.SINKING
        elif "妨" in name:
            return Disqualification.VIOLATION
        elif "失" in name:
            return Disqualification.DISQUALIFICATION_AFTER_START
        elif "エ" in name:
            return Disqualification.ENGINE_STOP
        elif "不" in name:
            return Disqualification.UNFINISHED
        elif "返" in name:
            return Disqualification.REPAYMENT_OTHER_THAN_FLYING_AND_LATENESS
        elif "Ｆ" in name:
            return Disqualification.FLYING
        elif "Ｌ" in name:
            return Disqualification.LATENESS
        elif "欠" in name:
            return Disqualification.ABSENT
        elif "＿" in name:
            # NOTE: これは失格ではない
            # レース不成立で着順が定まらなかったケース
            # 例)
            # http://boatrace.jp/owpc/pc/race/raceresult?rno=11&jcd=23&hd=20170429
            return None
        elif "　" in name:
            # NOTE: これは失格ではない
            # レース不成立で着順が定まらなかったケース
            # 例)
            # https://boatrace.jp/owpc/pc/race/raceresult?rno=2&jcd=23&hd=20160507
            return None
        else:
            raise ValueError


class MotorPartsFactory:
    @staticmethod
    def create(name: str) -> MotorParts:
        if "電気" in name:
            return MotorParts.ELECTRICAL_SYSTEM
        elif "キャブ" in name:
            return MotorParts.CARBURETOR
        elif "ピストン" == name:
            return MotorParts.PISTON
        elif "リング" in name:
            return MotorParts.PISTON_RING
        elif "シリンダ" in name:
            return MotorParts.CYLINDER
        elif "ギア" in name:
            return MotorParts.GEAR_CASE
        elif "ギヤ" in name:
            return MotorParts.GEAR_CASE
        elif "キャリ" in name:
            return MotorParts.CARRIER_BODY
        elif "シャフト" in name:
            return MotorParts.CRANKSHAFT
        else:
            raise ValueError


class RaceLapsFactory:
    METRE_PER_A_LAP = 600

    @classmethod
    def create(cls, metre: Literal[1200, 1800]) -> Literal[2, 3]:
        return cast(Literal[2, 3], metre // cls.METRE_PER_A_LAP)


class WinningTrickFactory:
    @staticmethod
    def create(name: str) -> WinningTrick:
        if "逃げ" == name:
            return WinningTrick.NIGE
        elif "差し" == name:
            return WinningTrick.SASHI
        elif "まくり" == name:
            return WinningTrick.MAKURI
        elif "まくり差し" == name:
            return WinningTrick.MAKURIZASHI
        elif "抜き" == name:
            return WinningTrick.NUKI
        elif "恵まれ" == name:
            return WinningTrick.MEGUMARE
        else:
            raise ValueError


class WeatherFactory:
    @staticmethod
    def create(name: str) -> Weather:
        if "晴" in name:
            return Weather.FINE
        elif "曇" in name:
            return Weather.CLOUDY
        elif "雨" in name:
            return Weather.RAINY
        elif "雪" in name:
            return Weather.SNOWY
        elif "台風" in name:
            return Weather.TYPHOON
        elif "霧" in name:
            return Weather.FOG
        else:
            raise ValueError


class EventHoldingStatusFactory:
    @staticmethod
    def create(text: str) -> Weather:
        if "中止" == text:
            return EventHoldingStatus.CANCELED
        elif "中止順延" == text:
            return EventHoldingStatus.POSTPONED
        else:
            return EventHoldingStatus.OPEN
