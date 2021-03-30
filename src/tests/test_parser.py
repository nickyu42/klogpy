import datetime

import pytest
from parsy import ParseError

from ..parser import date

test_dates = (
    ('2020-02-10', datetime.date(2020, 2, 10)),
    ('0001-01-01', datetime.date(1, 1, 1)),
    ('2020/12/30', datetime.date(2020, 12, 30)),
)


@pytest.mark.parametrize('s,expected', test_dates)
def test_simple_date(s, expected):
    res = date.parse('2020-01-01')
    assert res == datetime.date(2020, 1, 1)


@pytest.mark.parametrize('s', ('2020/01-01', '2000-00/01'))
def test_that_date_uses_same_separator(s):
    with pytest.raises(ParseError):
        date.parse(s)


@pytest.mark.parametrize('s', ('001-01-01', '2001-0-01', '2001-01-0'))
def test_that_date_accepts_correct_number_of_digits(s):
    with pytest.raises(ParseError):
        date.parse(s)
