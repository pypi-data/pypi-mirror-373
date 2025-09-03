from datetime import datetime, timedelta, timezone
from re import compile
from time import time
from typing import Literal

from rudi_node_read.utils.serializable import Serializable

REGEX_ISO_FULL_DATE = compile(
    r"^([+-]?[1-9]\d{3})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12]\d)T(2[0-3]|[01]\d):([0-5]\d):([0-5]\d)(?:\.(\d{3}))?("
    r"?:Z|[+-](?:1[0-2]|0\d):[03]0)$"
)

REGEX_RANDOM_DATE = compile(
    r"^([1-9]\d{3})(?:[-./ ]?(1[0-2]|0[1-9])(?:[-./ ]?(3[01]|0[1-9]|[12]\d)(?:[-T ](2[0-3]|[01]\d)[.:hH](["
    r"0-5]\d)(?:[.:mM](?:([0-5]\d)[sS]?(?:\.(\d{3})(\d{3})?)?(?:Z|([+-])(1[0-2]|0\d)(?::([03]0))?)?)?)?)?)?)?$"
)

TimeSpec = Literal["seconds", "milliseconds", "microseconds"]


class Date(Serializable):
    def __init__(self, date_str: str | int | None):
        if date_str is None:
            date_str = Date.now_iso_str()
        elif not isinstance(date_str, str):
            date_str = str(date_str)
        reg_date = Date.parse_date_str(date_str)
        if not reg_date:
            raise ValueError(f"this is not a valid date: '{date_str}'")
        (
            year,
            month,
            day,
            hour,
            minute,
            second,
            ms,
            us,
            tz_sign,
            tz_hour,
            tz_minute,
        ) = reg_date.groups()

        self.year = self._to_int(year)
        self.month = self._to_int(month, 1)
        self.day = self._to_int(day, 1)
        self.hour = self._to_int(hour)
        self.minute = self._to_int(minute)
        self.second = self._to_int(second)
        self.ms = self._to_int(ms) if ms else None
        self.us = self._to_int(us) if us else None
        self.microseconds = self._to_int(ms) * 1000 + self._to_int(us)

        self.tz_info = timezone(
            (-1 if tz_sign == "-" else 1) * timedelta(hours=self._to_int(tz_hour), minutes=self._to_int(tz_minute))
        )
        self.timespec = "microseconds" if self.us else "milliseconds" if self.ms else "seconds"

        self._py_date = None
        self._iso_date = None

    @property
    def class_name(self):
        return self.__class__.__name__

    @property
    def datetime(self) -> datetime:
        if self._py_date is None:
            self._py_date = datetime(
                year=self.year,
                month=self.month,
                day=self.day,
                hour=self.hour,
                minute=self.minute,
                second=self.second,
                microsecond=self.microseconds,
                tzinfo=self.tz_info,
            )
        return self._py_date

    @property
    def iso(self) -> str:
        if self._iso_date is None:
            self._iso_date = self.datetime.isoformat(timespec=self.timespec)
        return self._iso_date

    def __str__(self) -> str:
        return self.iso

    def __eq__(self, other):
        if not isinstance(other, (Date, str, int)):
            return False
        other_date = Date(other) if isinstance(other, (int, str)) else other
        return self.datetime == other_date.datetime

    def __gt__(self, other):
        if isinstance(other, Date):
            other_date = other
        elif isinstance(other, (int, str)):
            other_date = Date(other)
        else:
            raise ValueError(f"Cannot compare a date and a '{other.__class__.__name__}' (got '{other}')")
        return self.datetime > other_date.datetime

    def __lt__(self, other):
        return not self > other

    def to_json_str(self, keep_nones: bool = False, ensure_ascii: bool = False, sort_keys: bool = False) -> str:
        return self.iso

    def to_json(self, keep_nones: bool = False) -> str:
        return self.iso

    @staticmethod
    def _to_int(val: str | None, default_val: int = 0):
        return int(val if val else default_val)

    @staticmethod
    def from_str(date_str: str | None = None, default_date: str | None = None, is_none_accepted: bool = True):
        if date_str is None:
            if default_date:
                return Date(default_date)
            elif is_none_accepted:
                return None
            else:
                raise ValueError("empty value not accepted")
        return Date(date_str)

    @staticmethod
    def from_json(o: str):  # type: ignore
        return Date.from_str(o)

    @staticmethod
    def time_epoch_s(delay_s: int = 0) -> int:
        return int(datetime.timestamp(datetime.now())) + delay_s

    @staticmethod
    def time_epoch_ms(delay_ms: int = 0):
        return int(1000 * datetime.timestamp(datetime.now())) + delay_ms

    @staticmethod
    def now_str() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def now():
        return Date(Date.now_str())

    @staticmethod
    def now_iso_str(timespec: TimeSpec = "seconds") -> str:
        return datetime.now().astimezone().isoformat(timespec=timespec)

    @staticmethod
    def now_iso():
        return Date(Date.now_iso_str())

    @staticmethod
    def is_iso_full_date_str(date_str: str) -> bool:
        return bool(REGEX_ISO_FULL_DATE.match(date_str))

    @staticmethod
    def parse_date_str(date_str: str):
        return REGEX_RANDOM_DATE.match(date_str)

    @staticmethod
    def is_date_str(date_str: str):
        return bool(REGEX_RANDOM_DATE.match(date_str))


if __name__ == "__main__":  # pragma: no cover
    tests = "date_tests"
    begin = time()

    date = "2023-01-01 20:23:34.041456+02:00"
    print(tests, "str_to_date:", f"'{date}'", "->", f"'{Date(date)}'")
    print(tests, "==", date == Date(date))
    date_list = [
        "2020",
        "2020-01",
        "202001",
        "2020-01-01",
        "2020-01-01 00:00",
        "2020-01-01 00:00:00",
        "2020-01-01T00:00:00",
        "2020-01-01T00:00:00Z",
        "2020-01-01T00:00:00+00:00",
        "2020-01-01T00:00:00.000Z",
        "2020-01-01T00:00:00.000+00:00",
        "20200101",
    ]
    for str_date in date_list:
        print(tests, f"Date('{str_date}')", Date(str_date))
    for str_date in date_list:
        print(tests, f"2020 == Date('{str_date}') ->", "2020" == Date(str_date))
    print(tests, "exec. time:", time() - begin)
