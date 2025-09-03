import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Type

from frogml._proto.qwak.feature_store.features.aggregation_pb2 import (
    TimeUnit as ProtoTimeUnit,
)
from frogml.core.exceptions import FrogmlException


class _WindowTimeUnitMapping(Enum):
    WEEKS = (ProtoTimeUnit.TIME_UNIT_WEEKS, 7 * 24 * 60 * 60, "w")
    DAYS = (ProtoTimeUnit.TIME_UNIT_DAYS, 24 * 60 * 60, "d")
    HOURS = (ProtoTimeUnit.TIME_UNIT_HOURS, 60 * 60, "h")
    MINUTES = (ProtoTimeUnit.TIME_UNIT_MINUTES, 60, "m")
    SECONDS = (ProtoTimeUnit.TIME_UNIT_SECONDS, 1, "s")

    # Aliases
    WEEK = WEEKS
    DAY = DAYS
    HOUR = HOURS
    MINUTE = MINUTES
    SECOND = SECONDS


@dataclass
class Window:
    length: int
    time_unit_proto: ProtoTimeUnit
    seconds_in_time_unit: int
    suffix: str

    def get_feature_suffix(self) -> str:
        return f"{self.length}{self.suffix}"

    @classmethod
    def _from_string(cls, *windows: str) -> List[Type["Window"]]:
        time_window_parser = re.compile(
            rf'(?P<length>\d+)\s+(?P<timeunit>{"|".join([name.lower() for name, member in _WindowTimeUnitMapping.__members__.items()])})$'
        )

        parsed_windows: List[Window] = list()
        for window in windows:
            match = time_window_parser.match(window.lower())
            if not match:
                raise FrogmlException(
                    f"""
                        Could not parse given time window: {window}.
                        Valid time windows should be of the form "X weeks/days/hours/minutes/seconds", where X is a number.
                        For example - "1 hour", "2 days", "1 week", etc.
                    """
                )

            m_dict = match.groupdict()
            proto, minutes_in_unit, suffix = getattr(
                _WindowTimeUnitMapping, m_dict["timeunit"].upper()
            ).value

            additional_window = cls(
                length=int(m_dict["length"]),
                seconds_in_time_unit=minutes_in_unit,
                time_unit_proto=proto,
                suffix=suffix,
            )

            if additional_window not in parsed_windows:
                parsed_windows.append(additional_window)

        return parsed_windows
