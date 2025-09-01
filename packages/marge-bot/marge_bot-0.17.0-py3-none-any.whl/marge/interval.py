import datetime
import enum
import operator
import zoneinfo
from collections.abc import Iterable
from typing import Union

import dateutil.parser


# pylint: disable=invalid-name
@enum.unique
class WeekDay(enum.Enum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6


_DAY_NAMES = {day.name.lower(): day for day in WeekDay}
_DAY_NAMES.update((day.name.lower()[:3], day) for day in WeekDay)


def find_weekday(string_or_day: Union[WeekDay, str]) -> WeekDay:
    if isinstance(string_or_day, WeekDay):
        return string_or_day

    if isinstance(string_or_day, str):
        return _DAY_NAMES[string_or_day.lower()]

    raise ValueError(f"Not a week day: {string_or_day!r}")


class WeeklyInterval:
    def __init__(
        self,
        from_weekday: Union[WeekDay, str],
        from_time: datetime.time,
        to_weekday: Union[WeekDay, str],
        to_time: datetime.time,
    ):
        from_weekday = find_weekday(from_weekday)
        to_weekday = find_weekday(to_weekday)

        # the class invariant is that from_weekday <= to_weekday; so when this
        # is not the case (e.g. a Fri-Mon interval), we store the complement interval
        # (in the example, Mon-Fri), and invert the criterion
        self._is_complement_interval = from_weekday.value > to_weekday.value
        if self._is_complement_interval:
            self._from_weekday = to_weekday
            self._from_time = to_time
            self._to_weekday = from_weekday
            self._to_time = from_time
        else:
            self._from_weekday = from_weekday
            self._from_time = from_time
            self._to_weekday = to_weekday
            self._to_time = to_time

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WeeklyInterval):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __repr__(self) -> str:
        pat = "{class_name}({from_weekday}, {from_time}, {to_weekday}, {to_time})"
        if self._is_complement_interval:
            return pat.format(
                class_name=self.__class__.__name__,
                from_weekday=self._to_weekday,
                from_time=self._to_time,
                to_weekday=self._from_weekday,
                to_time=self._from_time,
            )
        return pat.format(
            class_name=self.__class__.__name__,
            from_weekday=self._from_weekday,
            from_time=self._from_time,
            to_weekday=self._to_weekday,
            to_time=self._to_time,
        )

    @classmethod
    def from_human(cls, string: str) -> "WeeklyInterval":
        from_, to_ = string.split("-")

        def parse_part(part: str) -> tuple[WeekDay, datetime.time]:
            part = part.replace("@", " ")
            parts = part.split()
            day_part = parts[0]
            time_part = parts[1]
            zone_part = parts[2] if len(parts) > 2 else "UTC"
            timezone = zoneinfo.ZoneInfo(zone_part)
            weekday = find_weekday(day_part)
            dt = dateutil.parser.parse(time_part).replace(tzinfo=timezone)
            time = dt.astimezone(datetime.timezone.utc).time()
            return weekday, time

        from_weekday, from_time = parse_part(from_)
        to_weekday, to_time = parse_part(to_)
        return cls(from_weekday, from_time, to_weekday, to_time)

    def covers(self, date: datetime.datetime) -> bool:
        return self._interval_covers(date) != self._is_complement_interval

    def _interval_covers(self, date: datetime.datetime) -> bool:
        weekday = date.date().weekday()
        time = date.time()
        before = operator.le if self._is_complement_interval else operator.lt

        if not self._from_weekday.value <= weekday <= self._to_weekday.value:
            return False

        if self._from_weekday.value == weekday and before(time, self._from_time):
            return False

        if self._to_weekday.value == weekday and before(self._to_time, time):
            return False

        return True


class IntervalUnion:
    def __init__(self, iterable: Iterable[WeeklyInterval]):
        self._intervals = list(iterable)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IntervalUnion):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __repr__(self) -> str:
        return "{o.__class__.__name__}({o._intervals})".format(o=self)

    @classmethod
    def empty(cls) -> "IntervalUnion":
        return cls(())

    @classmethod
    def from_human(cls, string: str) -> "IntervalUnion":
        strings = string.split(",")
        return cls(WeeklyInterval.from_human(s) for s in strings)

    def covers(self, date: datetime.datetime) -> bool:
        return any(interval.covers(date) for interval in self._intervals)
