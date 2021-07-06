"""
Simple parser for the Klog plaintext format, generates a high level object of a Klog file.
Is not optimized to be fast, but since the format is simple, it should be fast enough.
"""

import datetime
import re
from dataclasses import asdict
from functools import cache

from parsy import Parser, Result, fail, generate, regex, seq, string, whitespace

from .syntax import Duration, Entry, Range, Record, ShouldTotal

TAG_REGEX = re.compile(r'#\S+')
EOL = regex(r'\s*\n')


@cache
def c_regex(exp, flags=0, group=0) -> Parser:
    """
    Memoized version of ``parsy.regex``.
    Can be used for caching expensive regexes, saves some compiling time.

    The difference in cost is ultimately negligible, since compiling on the fly
    is quick, but it shaves off a little time.

    :return: parsy.Parser object.
    """
    if isinstance(exp, (str, bytes)):
        exp = re.compile(exp, flags)
    if isinstance(group, (str, int)):
        group = (group,)

    @Parser
    def regex_parser(stream, index):
        match = exp.match(stream, index)
        if match:
            return Result.success(match.end(), match.group(*group))
        else:
            return Result.failure(index, exp.pattern)

    return regex_parser


@generate
def date():
    y = yield c_regex(r'\d{4}').map(int)
    sep = yield string('-') | string('/')
    m = yield c_regex(r'\d{2}').map(int)
    yield string(sep)
    d = yield c_regex(r'\d{2}').map(int)
    return datetime.date(y, m, d)


@generate
def duration():
    sign = yield (string('-') | string('+')).optional()

    hours = yield c_regex(r'(\d+)h', group=1).optional()
    minutes = yield c_regex(r'(\d+)m', group=1).optional()

    if hours is None and minutes is None:
        return fail('Duration value should have a minutes or hours value.')

    return Duration(
        is_neg=sign is not None and sign == '-',
        hours=0 if hours is None else hours,
        minutes=0 if minutes is None else minutes,
    )


@generate
def should_total():
    d = yield duration << string('!')
    return ShouldTotal(**asdict(d))


# TODO: dont allow duplicates
properties = should_total


@generate
def time():
    h = yield c_regex(r'\d{1,2}').map(int)
    yield string(':')
    m = yield c_regex(r'\d{1,2}').map(int)
    suffix = yield regex(r'(:?a|p)m').optional()

    is_pm = suffix is not None and suffix == 'pm'

    # Convert 12 hour clock to 24 hour if suffix is set
    if is_pm and h != 12:
        h += 12
    elif not is_pm and h == 12:
        h = 0

    return datetime.time(hour=h, minute=m)


@generate
def time_range():
    start_time = seq(
        string('<').optional().map(lambda x: x is not None),
        time
    )

    start = yield start_time | c_regex(r'\?+').result(None)

    yield c_regex(r'\s*-\s*')

    end_time = seq(
        time,
        (string('>').optional().map(lambda x: x is not None))
    ).map(lambda t: (t[1], t[0]))

    end = yield end_time | c_regex(r'\?+').result(None)

    # Check that, if start and end are time values, that they are in the correct order
    if (
        isinstance(start, tuple)
        and isinstance(end, tuple)
        and start[1] > end[1]
    ):
        return fail('Time in range must be in chronological order')

    return Range(
        start=start,
        end=end,
    )


@generate
def entry():
    # Indent
    yield c_regex(r'(( {3,4})|\t)')

    t = yield time_range | duration

    description = yield c_regex(r' *') >> c_regex('.*')
    yield EOL

    return Entry(
        time=t,
        description=description,
    )


@generate
def record():
    d = yield date

    prop = yield (
        whitespace
        >> string('(')
        >> properties
        << string(')')
    ).optional()

    yield EOL

    summary = yield c_regex(r'(\w.*)\n', group=1).many()
    entries = yield entry.many()

    tags = TAG_REGEX.findall(' '.join(summary))

    return Record(
        date=d,
        properties=[prop],
        summary=summary,
        entries=entries,
        tags=tags,
    )


def parse(inp: str) -> list[Record]:
    padded_record = EOL.many() >> record << EOL.many()
    records = padded_record.many().parse(inp)
    return records
