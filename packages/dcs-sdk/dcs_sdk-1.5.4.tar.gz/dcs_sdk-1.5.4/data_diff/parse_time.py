#  Copyright 2022-present, the Waterdip Labs Pvt. Ltd.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import re
from datetime import datetime, timedelta
from difflib import SequenceMatcher


class ParseError(ValueError):
    pass


TIME_UNITS = dict(
    seconds="seconds",
    minutes="minutes",
    hours="hours",
    days="days",
    weeks="weeks",
    months="months",
    years="years",
    # Shortcuts
    s="seconds",
    min="minutes",
    h="hours",
    d="days",
    w="weeks",
    mon="months",
    y="years",
)

EXTRAPOLATED = {"months": (30, "days"), "years": (365, "days")}
assert set(EXTRAPOLATED) <= set(TIME_UNITS)

TIME_RE = re.compile(r"(\d+)([a-z]+)")

UNITS_STR = ", ".join(sorted(TIME_UNITS.keys()))


def string_similarity(a, b) -> SequenceMatcher:
    return SequenceMatcher(None, a, b).ratio()


def parse_time_atom(count, unit):
    count = int(count)
    try:
        unit = TIME_UNITS[unit]
    except KeyError:
        most_similar = max(TIME_UNITS, key=lambda k: string_similarity(k, unit))
        raise ParseError(
            f"'{unit}' is not a recognized time unit. Did you mean '{most_similar}'?" f"\nSupported units: {UNITS_STR}"
        )

    if unit in EXTRAPOLATED:
        mul, unit = EXTRAPOLATED[unit]
        count *= mul
    return count, unit


def parse_time_delta(t: str) -> timedelta:
    time_dict = {}
    while t:
        m = TIME_RE.match(t)
        if not m:
            raise ParseError(f"Cannot parse '{t}': Not a recognized time delta")
        count, unit = parse_time_atom(*m.groups())
        if unit in time_dict:
            raise ParseError(f"Time unit {unit} specified more than once")
        time_dict[unit] = count
        t = t[m.end() :]

    if not time_dict:
        raise ParseError("No time difference specified")
    return timedelta(**time_dict)


def parse_time_before(time: datetime, delta: str) -> datetime:
    return time - parse_time_delta(delta)
