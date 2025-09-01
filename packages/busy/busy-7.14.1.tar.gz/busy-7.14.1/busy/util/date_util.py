# Various utilities related to date handling

import functools
import re
from datetime import date as Date
from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta

# Isolate the function so it can easily be patched for testing.

today = Date.today
now = DateTime.now


# The string format we always use to express a date is YYYY-MM-DD

FORMAT = re.compile(r'^(\d{4})(?:\-|\/)(\d{1,2})(?:\-|\/)(\d{1,2})$')


def absolute_date(info):
    """Cast other types to datetime.date or None"""
    if not info:
        return None
    if isinstance(info, Date):
        return info
    elif isinstance(info, tuple):
        return Date(*info)
    elif isinstance(info, str) and FORMAT.match(info):
        return Date(*(int(x) for x in FORMAT.match(info).groups()))


# Refactored to only accept a string

def relative_date(value: str):
    """Given a string like "tomorrow" or "in 4 days", return a date"""
    value = value.lower()
    result = next(filter(None, (h(value) for h in HANDLERS)), None)
    if result:
        return result
    else:
        return absolute_date(value)


# Used during import to bring in different handlers for relative dates. Called
# during import.
HANDLERS = []


def _register(expression=r'(.*)'):
    compiled = re.compile(expression)

    def chain(func):
        @functools.wraps(func)
        def wrapper(string):
            match = compiled.match(string)
            if match:
                return func(today(), *match.groups())
        HANDLERS.append(wrapper)
        return wrapper
    return chain


# The actual different types of expressions for relative dates.

@_register(r'today')
def _match_today(today):
    return today


@_register(r'tomorrow')
def _match_tomorrow(today):
    return today + TimeDelta(1)


@_register(r'^(\d+)\s+days?$')
def _match_days(today, days):
    return today + TimeDelta(int(days))


@_register(r'^(\d+)d$')
def _match_d(today, days):
    return today + TimeDelta(int(days))


@_register(r'^(\d{1,2})$')
def _match_day_num(today, day):
    if today.day < int(day):
        return Date(today.year, today.month, int(day))
    else:
        year = today.year + (today.month // 12)
        month = (today.month % 12) + 1
        return Date(year, month, int(day))


@_register(r'(\d{1,2})(?:\-|\/)(\d{1,2})$')
def _match_month_day_num(today, month, day):
    if today < Date(today.year, int(month), int(day)):
        return Date(today.year, int(month), int(day))
    else:
        return Date(today.year + 1, int(month), int(day))


@_register(r'^(mon?|tue?s?|wed?n?e?s?|thu?r?s?|fri?|sat?u?r?|sun?)(?:day)?$')
def _match_weekday(today, weekday):
    index = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su'].index(weekday[0:2])
    days = (6 - today.weekday() + index) % 7 + 1
    return today + TimeDelta(days)
