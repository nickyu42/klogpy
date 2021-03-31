import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import cached_property
from typing import Optional, Union


class Serializable(ABC):
    @abstractmethod
    def serialize(self) -> str:
        pass


class Time(ABC):
    @property
    @abstractmethod
    def total_minutes(self) -> Optional[int]:
        pass


@dataclass
class Duration(Time, Serializable):
    is_neg: bool
    hours: int
    minutes: int

    @cached_property
    def total_minutes(self) -> int:
        total_minutes = self.hours * 60 + self.minutes
        return -total_minutes if self.is_neg else total_minutes

    def serialize(self) -> str:
        builder = []

        if self.is_neg:
            builder.append('-')

        builder.append(f'{self.hours}h{self.minutes}m')

        return ''.join(builder)


@dataclass
class Range(Time, Serializable):
    start: Optional[tuple[bool, datetime.time]]
    end: Optional[tuple[bool, datetime.time]]

    @cached_property
    def total_minutes(self) -> Optional[int]:
        # TODO
        return None

    def serialize(self) -> str:
        builder = []

        if self.start is not None:
            o, t = self.start
            builder.append(f'{"<" if o else ""}{t.hour:02}:{t.minute:02}')
        else:
            builder.append('?')

        builder.append(' - ')

        if self.end is not None:
            o, t = self.end
            builder.append(f'{t.hour:02}:{t.minute:02}{">" if o else ""}')
        else:
            builder.append('?')

        return ''.join(builder)


@dataclass
class Entry(Serializable):
    time: Union[Duration, Range]
    description: Optional[str]

    def serialize(self) -> str:
        s = self.time.serialize()
        if self.description is not None:
            s += f' {self.description}'

        return s


class ShouldTotal(Duration):
    pass


Property = Union[ShouldTotal]


@dataclass
class Record(Serializable):
    date: datetime.date
    properties: list[Property] = field(default_factory=list)
    summary: list[str] = field(default_factory=list)
    entries: list[Entry] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def total_time(self):
        return sum(e.time.total_minutes for e in self.entries)

    def serialize(self) -> str:
        builder = [self.date.strftime('%Y-%m-%d')]

        if len(self.properties) > 0:
            builder.append(
                f'({",".join(p.serialize() for p in self.properties)})')

        builder.append('\n')

        for line in self.summary:
            builder.append(line)
            builder.append('\n')

        for e in self.entries:
            builder.append(f'    {e.serialize()}\n')

        return ''.join(builder)
