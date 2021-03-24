import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Optional, Union


class Time(ABC):
    @property
    @abstractmethod
    def total_minutes(self) -> Optional[int]:
        pass


@dataclass
class Duration(Time):
    is_neg: bool
    hours: int
    minutes: int

    @cached_property
    def total_minutes(self) -> int:
        total_minutes = self.hours * 60 + self.minutes
        return -total_minutes if self.is_neg else total_minutes


@dataclass
class Range(Time):
    start: Optional[tuple[bool, datetime.time]]
    end: Optional[tuple[bool, datetime.time]]

    @cached_property
    def total_minutes(self) -> Optional[int]:
        # TODO
        return None


@dataclass
class Entry:
    time: Union[Duration, Range]
    description: Optional[str]


class ShouldTotal(Duration):
    pass


Property = Union[ShouldTotal]


@dataclass
class Record:
    date: datetime.date
    properties: list[Property]
    summary: list[str]
    entries: list[Entry]
    tags: list[str]

    def total_time(self):
        return sum(e.time.total_minutes for e in self.entries)

