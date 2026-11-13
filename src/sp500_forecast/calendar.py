"""Local US equity session calendar, restricted to the 2020–2026 study span.

Adapted without mathematical changes from the archived calendar_rules.py.
Early closes count as sessions. Juneteenth starts in 2022; 9 January 2025 is
an exceptional closure. Saturday New Year's Day has no Friday observance.
Source SHA-256 and adaptations are documented in PROVENANCE.md.
"""
from datetime import date, timedelta

GOOD_FRIDAYS = {2020:(4,10), 2021:(4,2), 2022:(4,15), 2023:(4,7),
                2024:(3,29), 2025:(4,18), 2026:(4,3)}


def nth_weekday(year, month, weekday, number):
    first = date(year, month, 1)
    return first + timedelta(days=(weekday-first.weekday()) % 7 + 7*(number-1))


def observed(day):
    return day-timedelta(days=1) if day.weekday()==5 else day+timedelta(days=1) if day.weekday()==6 else day


def holidays(year):
    if year not in GOOD_FRIDAYS:
        raise ValueError('Calendar supports 2020 through 2026 only.')
    result = {nth_weekday(year,1,0,3):'Martin Luther King Jr. Day',
              nth_weekday(year,2,0,3):"Washington's Birthday",
              date(year,*GOOD_FRIDAYS[year]):'Good Friday',
              date(year,5,31)-timedelta(days=date(year,5,31).weekday()):'Memorial Day',
              observed(date(year,7,4)):'Independence Day',
              nth_weekday(year,9,0,1):'Labor Day',
              nth_weekday(year,11,3,4):'Thanksgiving',
              observed(date(year,12,25)):'Christmas'}
    new_year = date(year,1,1)
    if new_year.weekday()!=5:
        result[observed(new_year)]="New Year's Day"
    if year>=2022:
        result[observed(date(year,6,19))]='Juneteenth'
    if year==2025:
        result[date(2025,1,9)]='National Day of Mourning'
    return result


def is_session(day):
    return day.weekday()<5 and day not in holidays(day.year)


def sessions_between(first, last):
    if first>last:
        raise ValueError('Reversed calendar interval.')
    result=[]
    while first<=last:
        if is_session(first):
            result.append(first)
        first+=timedelta(days=1)
    return result


def target_session(origin, horizon=6):
    if not is_session(origin) or horizon<1:
        raise ValueError('A session origin and positive horizon are required.')
    current=origin
    for _ in range(horizon):
        current+=timedelta(days=1)
        while not is_session(current):
            current+=timedelta(days=1)
    return current

