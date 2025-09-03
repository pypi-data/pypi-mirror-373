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

import json
import logging
import math
import operator
import re
import string
import threading
from abc import abstractmethod
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    MutableMapping,
    Optional,
    Sequence,
    TypeVar,
    Union,
)
from urllib.parse import urlparse
from uuid import UUID

import attrs
import requests
from packaging.version import parse as parse_version
from rich.status import Status
from tabulate import tabulate
from typing_extensions import Self

from data_diff.version import __version__

# -- Common --

entrypoint_name = "Python API"


def set_entrypoint_name(s) -> None:
    global entrypoint_name
    entrypoint_name = s


def join_iter(joiner: Any, iterable: Iterable) -> Iterable:
    it = iter(iterable)
    try:
        yield next(it)
    except StopIteration:
        return
    for i in it:
        yield joiner
        yield i


def safezip(*args):
    "zip but makes sure all sequences are the same length"
    lens = list(map(len, args))
    if len(set(lens)) != 1:
        raise ValueError(f"Mismatching lengths in arguments to safezip: {lens}")
    return zip(*args)


UUID_PATTERN = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)


def is_uuid(u: str) -> bool:
    # E.g., hashlib.md5(b'hello') is a 32-letter hex number, but not an UUID.
    # It would fail UUID-like comparison (< & >) because of casing and dashes.
    if not UUID_PATTERN.fullmatch(u):
        return False
    try:
        UUID(u)
    except ValueError:
        return False
    return True


def match_regexps(regexps: Dict[str, Any], s: str) -> Sequence[tuple]:
    for regexp, v in regexps.items():
        m = re.match(regexp + "$", s)
        if m:
            yield m, v


# -- Schema --

V = TypeVar("V")


class CaseAwareMapping(MutableMapping[str, V]):
    @abstractmethod
    def get_key(self, key: str) -> str: ...

    def new(self, initial=()) -> Self:
        return type(self)(initial)


class CaseInsensitiveDict(CaseAwareMapping):
    def __init__(self, initial) -> None:
        super().__init__()
        self._dict = {k.lower(): (k, v) for k, v in dict(initial).items()}

    def __getitem__(self, key: str) -> V:
        return self._dict[key.lower()][1]

    def __iter__(self) -> Iterator[V]:
        return iter(self._dict)

    def __len__(self) -> int:
        return len(self._dict)

    def __setitem__(self, key: str, value) -> None:
        k = key.lower()
        if k in self._dict:
            key = self._dict[k][0]
        self._dict[k] = key, value

    def __delitem__(self, key: str) -> None:
        del self._dict[key.lower()]

    def get_key(self, key: str) -> str:
        return self._dict[key.lower()][0]

    def __repr__(self) -> str:
        return repr(dict(self.items()))


class CaseSensitiveDict(dict, CaseAwareMapping):
    def get_key(self, key):
        self[key]  # Throw KeyError if key doesn't exist
        return key

    def as_insensitive(self):
        return CaseInsensitiveDict(self)


# -- Alphanumerics --

alphanums = " -" + string.digits + string.ascii_uppercase + "_" + string.ascii_lowercase


@attrs.define(frozen=True)
class ArithString:
    @classmethod
    def new(cls, *args, **kw) -> Self:
        return cls(*args, **kw)

    def range(self, other: "ArithString", count: int) -> List[Self]:
        assert isinstance(other, ArithString)
        checkpoints = split_space(self.int, other.int, count)
        return [self.new(int=i) for i in checkpoints]


def _any_to_uuid(v: Union[str, int, UUID, "ArithUUID"]) -> UUID:
    if isinstance(v, ArithUUID):
        return v.uuid
    elif isinstance(v, UUID):
        return v
    elif isinstance(v, str):
        return UUID(v)
    elif isinstance(v, int):
        return UUID(int=v)
    else:
        raise ValueError(f"Cannot convert a value to UUID: {v!r}")


def _any_to_datetime(v: Union[str, datetime, date, "ArithDateTime"]) -> datetime:
    """Convert various types to datetime object."""
    if isinstance(v, ArithDateTime):
        return v._dt
    elif isinstance(v, datetime):
        return v
    elif isinstance(v, date):
        return datetime.combine(v, time.min)
    elif isinstance(v, str):
        # Try specific formats first to preserve original precision
        try:
            # Handle format: YYYY-MM-DD HH:MM:SS.mmm (3-digit milliseconds)
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            try:
                # Handle format: YYYY-MM-DD HH:MM:SS
                return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    # Handle format: YYYY-MM-DD
                    return datetime.strptime(v, "%Y-%m-%d")
                except ValueError:
                    # Last resort: try ISO format parsing
                    try:
                        return datetime.fromisoformat(v.replace("Z", "+00:00"))
                    except ValueError:
                        raise ValueError(f"Cannot parse datetime string: {v!r}")
    else:
        raise ValueError(f"Cannot convert value to datetime: {v!r}")


def _any_to_date(v: Union[str, datetime, date, "ArithDate"]) -> date:
    """Convert various types to date object."""
    if isinstance(v, ArithDate):
        return v._date
    elif isinstance(v, date):
        return v
    elif isinstance(v, datetime):
        return v.date()
    elif isinstance(v, str):
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00")).date()
        except ValueError:
            try:
                return datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(f"Cannot parse date string: {v!r}")
    else:
        raise ValueError(f"Cannot convert value to date: {v!r}")


@attrs.define(frozen=True, eq=False, order=False)
class ArithDateTime(ArithString):
    """A datetime that supports basic arithmetic and range operations for database diffing."""

    _dt: datetime = attrs.field(converter=_any_to_datetime)

    def range(self, other: "ArithDateTime", count: int) -> List[Self]:
        """Generate evenly spaced datetime checkpoints between self and other."""
        assert isinstance(other, ArithDateTime)

        start_ts = self._dt.timestamp()
        end_ts = other._dt.timestamp()

        checkpoints = split_space(start_ts, end_ts, count)
        return [self.new(datetime.fromtimestamp(ts)) for ts in checkpoints]

    def __int__(self) -> int:
        """Convert to timestamp for arithmetic operations."""
        return int(self._dt.timestamp())

    def __add__(self, other: Union[int, float]) -> Self:
        """Add seconds to the datetime."""
        if isinstance(other, (int, float)):
            new_ts = self._dt.timestamp() + other
            return self.new(datetime.fromtimestamp(new_ts))
        return NotImplemented

    def __sub__(self, other: Union["ArithDateTime", int, float]):
        """Subtract seconds or another datetime."""
        if isinstance(other, (int, float)):
            new_ts = self._dt.timestamp() - other
            return self.new(datetime.fromtimestamp(new_ts))
        elif isinstance(other, ArithDateTime):
            return self._dt.timestamp() - other._dt.timestamp()
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ArithDateTime):
            return self._dt == other._dt
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        if isinstance(other, ArithDateTime):
            return self._dt != other._dt
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, ArithDateTime):
            return self._dt > other._dt
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, ArithDateTime):
            return self._dt < other._dt
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if isinstance(other, ArithDateTime):
            return self._dt >= other._dt
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, ArithDateTime):
            return self._dt <= other._dt
        return NotImplemented

    def __str__(self) -> str:
        """Return ISO format string."""
        return self._dt.isoformat()

    def __repr__(self) -> str:
        return f"ArithDateTime({self._dt!r})"


@attrs.define(frozen=True, eq=False, order=False)
class ArithDate(ArithString):
    """A date that supports basic arithmetic and range operations for database diffing."""

    _date: date = attrs.field(converter=_any_to_date)

    def range(self, other: "ArithDate", count: int) -> List[Self]:
        """Generate evenly spaced date checkpoints between self and other."""
        assert isinstance(other, ArithDate)

        start_ordinal = self._date.toordinal()
        end_ordinal = other._date.toordinal()

        checkpoints = split_space(start_ordinal, end_ordinal, count)
        return [self.new(date.fromordinal(int(ordinal))) for ordinal in checkpoints]

    def __int__(self) -> int:
        """Convert to ordinal for arithmetic operations."""
        return self._date.toordinal()

    def __add__(self, other: int) -> Self:
        """Add days to the date."""
        if isinstance(other, int):
            new_ordinal = self._date.toordinal() + other
            return self.new(date.fromordinal(new_ordinal))
        return NotImplemented

    def __sub__(self, other: Union["ArithDate", int]):
        """Subtract days or another date."""
        if isinstance(other, int):
            new_ordinal = self._date.toordinal() - other
            return self.new(date.fromordinal(new_ordinal))
        elif isinstance(other, ArithDate):
            return self._date.toordinal() - other._date.toordinal()
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ArithDate):
            return self._date == other._date
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        if isinstance(other, ArithDate):
            return self._date != other._date
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, ArithDate):
            return self._date > other._date
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, ArithDate):
            return self._date < other._date
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if isinstance(other, ArithDate):
            return self._date >= other._date
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, ArithDate):
            return self._date <= other._date
        return NotImplemented

    def __str__(self) -> str:
        """Return ISO format date string."""
        return self._date.isoformat()

    def __repr__(self) -> str:
        return f"ArithDate({self._date!r})"


@attrs.define(frozen=True, eq=False, order=False)
class ArithTimestamp(ArithDateTime):
    """A timestamp that inherits from ArithDateTime but with explicit timestamp semantics."""

    def __repr__(self) -> str:
        return f"ArithTimestamp({self._dt!r})"


@attrs.define(frozen=True, eq=False, order=False)
class ArithTimestampTZ(ArithDateTime):
    """A timezone-aware timestamp that extends ArithDateTime."""

    def __repr__(self) -> str:
        return f"ArithTimestampTZ({self._dt!r})"

    def __str__(self) -> str:
        """Return ISO format string with timezone info."""
        return self._dt.isoformat()


@attrs.define(frozen=True, eq=False, order=False)
class ArithUnicodeString(ArithString):
    """A Unicode string for arbitrary text keys, supporting lexicographical ordering and checkpoint generation across databases."""

    _str: str = attrs.field(converter=str)

    @staticmethod
    def split_space(start: int, end: int, count: int) -> List[int]:
        """Split the space between start and end into count checkpoints."""
        if count <= 0:
            return []
        if count == 1:
            return [(start + end) // 2]
        step = (end - start) // (count + 1)
        return [start + step * (i + 1) for i in range(count)]

    def _str_to_int(self) -> int:
        """Convert string to an integer for interpolation, handling empty strings and Unicode."""
        if not self._str:
            return 0  # Handle empty string
        result = 0
        for char in self._str:
            result = result * 256 + ord(char)
        return result

    def _int_to_str(self, value: int) -> str:
        """Convert an integer to a string using printable ASCII characters."""
        if value <= 0:
            return "a"  # Fallback for zero/negative values (empty string case)
        chars = []
        while value > 0:
            value, remainder = divmod(value, 256)
            # Use printable ASCII (32-126) to avoid control characters
            chars.append(chr(max(32, min(126, remainder))))
        return "".join(chars[::-1]) or "a"

    def range(self, other: "ArithUnicodeString", count: int) -> List[Self]:
        """Generate a range of ArithUnicodeString objects between self and other."""
        assert isinstance(other, ArithUnicodeString), "Other must be an ArithUnicodeString"

        # Handle edge case: same or empty strings
        if self._str == other._str or count <= 0:
            return []
        if not self._str or not other._str:
            return [self.new("a") for _ in range(count)] if count > 0 else []

        # Ensure min_key < max_key
        min_key = self if self < other else other
        max_key = other if self < other else self

        # Convert strings to integers for interpolation
        start_int = min_key._str_to_int()
        end_int = max_key._str_to_int()

        # If the range is too small, return empty list
        if end_int - start_int <= count:
            return []

        # Generate checkpoints
        checkpoints_int = self.split_space(start_int, end_int, count)

        # Convert back to strings and create instances
        checkpoints = []
        for i in checkpoints_int:
            # Ensure checkpoint is valid and within bounds
            if start_int < i < end_int:
                checkpoint_str = self._int_to_str(i)
                checkpoint = self.new(checkpoint_str)
                # Double-check the string comparison bounds
                if min_key < checkpoint < max_key:
                    checkpoints.append(checkpoint)

        return checkpoints

    def __int__(self) -> int:
        """Convert to integer representation for arithmetic."""
        return self._str_to_int()

    def __add__(self, other: int) -> Self:
        """Add an integer to the string's numeric representation."""
        if isinstance(other, int):
            new_int = self._str_to_int() + other
            return self.new(self._int_to_str(new_int))
        return NotImplemented

    def __sub__(self, other: Union["ArithUnicodeString", int]):
        """Subtract an integer or another ArithUnicodeString."""
        if isinstance(other, int):
            new_int = self._str_to_int() - other
            return self.new(self._int_to_str(new_int))
        elif isinstance(other, ArithUnicodeString):
            return self._str_to_int() - other._str_to_int()
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        """Check equality with another ArithUnicodeString."""
        if isinstance(other, ArithUnicodeString):
            return self._str == other._str
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        """Check inequality with another ArithUnicodeString."""
        if isinstance(other, ArithUnicodeString):
            return self._str != other._str
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        """Check if greater than another ArithUnicodeString."""
        if isinstance(other, ArithUnicodeString):
            return self._str > other._str
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        """Check if less than another ArithUnicodeString."""
        if isinstance(other, ArithUnicodeString):
            return self._str < other._str
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        """Check if greater than or equal to another ArithUnicodeString."""
        if isinstance(other, ArithUnicodeString):
            return self._str >= other._str
        return NotImplemented

    def __le__(self, other: object) -> bool:
        """Check if less than or equal to another ArithUnicodeString."""
        if isinstance(other, ArithUnicodeString):
            return self._str <= other._str
        return NotImplemented

    def __str__(self) -> str:
        """Return the string representation, escaped for SQL."""
        return self._str.replace("'", "''")

    def __repr__(self) -> str:
        """Return a detailed representation."""
        return f"ArithUnicodeString(string={self._str!r})"


@attrs.define(frozen=True, eq=False, order=False)
class ArithUUID(ArithString):
    "A UUID that supports basic arithmetic (add, sub)"

    uuid: UUID = attrs.field(converter=_any_to_uuid)
    lowercase: Optional[bool] = None
    uppercase: Optional[bool] = None

    def range(self, other: "ArithUUID", count: int) -> List[Self]:
        assert isinstance(other, ArithUUID)
        checkpoints = split_space(self.uuid.int, other.uuid.int, count)
        return [attrs.evolve(self, uuid=i) for i in checkpoints]

    def __int__(self) -> int:
        return self.uuid.int

    def __add__(self, other: int) -> Self:
        if isinstance(other, int):
            return attrs.evolve(self, uuid=self.uuid.int + other)
        return NotImplemented

    def __sub__(self, other: Union["ArithUUID", int]):
        if isinstance(other, int):
            return attrs.evolve(self, uuid=self.uuid.int - other)
        elif isinstance(other, ArithUUID):
            return self.uuid.int - other.uuid.int
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ArithUUID):
            return self.uuid == other.uuid
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        if isinstance(other, ArithUUID):
            return self.uuid != other.uuid
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, ArithUUID):
            return self.uuid > other.uuid
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, ArithUUID):
            return self.uuid < other.uuid
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if isinstance(other, ArithUUID):
            return self.uuid >= other.uuid
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, ArithUUID):
            return self.uuid <= other.uuid
        return NotImplemented


def numberToAlphanum(num: int, base: str = alphanums) -> str:
    digits = []
    while num > 0:
        num, remainder = divmod(num, len(base))
        digits.append(remainder)
    return "".join(base[i] for i in digits[::-1])


def alphanumToNumber(alphanum: str, base: str = alphanums) -> int:
    num = 0
    for c in alphanum:
        num = num * len(base) + base.index(c)
    return num


def justify_alphanums(s1: str, s2: str):
    max_len = max(len(s1), len(s2))
    s1 = s1.ljust(max_len)
    s2 = s2.ljust(max_len)
    return s1, s2


def alphanums_to_numbers(s1: str, s2: str):
    s1, s2 = justify_alphanums(s1, s2)
    n1 = alphanumToNumber(s1)
    n2 = alphanumToNumber(s2)
    return n1, n2


@attrs.define(frozen=True, eq=False, order=False, repr=False)
class ArithAlphanumeric(ArithString):
    _str: str
    _max_len: Optional[int] = None

    def __attrs_post_init__(self) -> None:
        if self._str is None:
            raise ValueError("Alphanum string cannot be None")
        if self._max_len and len(self._str) > self._max_len:
            raise ValueError(f"Length of alphanum value '{str}' is longer than the expected {self._max_len}")

        for ch in self._str:
            if ch not in alphanums:
                raise ValueError(f"Unexpected character {ch} in alphanum string")

    # @property
    # def int(self):
    #     return alphanumToNumber(self._str, alphanums)

    def __str__(self) -> str:
        s = self._str
        if self._max_len:
            s = s.rjust(self._max_len, alphanums[0])
        return s

    def __len__(self) -> int:
        return len(self._str)

    def __repr__(self) -> str:
        return f'alphanum"{self._str}"'

    def __add__(self, other: "Union[ArithAlphanumeric, int]") -> Self:
        if isinstance(other, int):
            if other != 1:
                raise NotImplementedError("not implemented for arbitrary numbers")
            num = alphanumToNumber(self._str)
            return self.new(numberToAlphanum(num + 1))

        return NotImplemented

    def range(self, other: "ArithAlphanumeric", count: int) -> List[Self]:
        assert isinstance(other, ArithAlphanumeric)
        n1, n2 = alphanums_to_numbers(self._str, other._str)
        split = split_space(n1, n2, count)
        return [self.new(numberToAlphanum(s)) for s in split]

    def __sub__(self, other: "Union[ArithAlphanumeric, int]") -> float:
        if isinstance(other, ArithAlphanumeric):
            n1, n2 = alphanums_to_numbers(self._str, other._str)
            return n1 - n2

        return NotImplemented

    def __ge__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._str >= other._str

    def __lt__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._str < other._str

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._str == other._str

    def new(self, *args, **kw) -> Self:
        return type(self)(*args, **kw, max_len=self._max_len)


def number_to_human(n):
    millnames = ["", "k", "m", "b"]
    n = float(n)
    millidx = max(
        0,
        min(len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))),
    )

    return "{:.0f}{}".format(n / 10 ** (3 * millidx), millnames[millidx])


def split_space(start, end, count) -> List[int]:
    if isinstance(start, float) or isinstance(end, float):
        step = (end - start) / (count + 1)
        return [start + step * i for i in range(1, count + 1)]
    size = end - start
    assert count <= size, (count, size)
    return list(range(start, end, (size + 1) // (count + 1)))[1 : count + 1]


def remove_passwords_in_dict(d: dict, replace_with: str = "***"):
    for k, v in d.items():
        if k == "password":
            d[k] = replace_with
        elif k == "filepath":
            if "motherduck_token=" in v:
                d[k] = v.split("motherduck_token=")[0] + f"motherduck_token={replace_with}"
        elif isinstance(v, dict):
            remove_passwords_in_dict(v, replace_with)
        elif k.startswith("database"):
            d[k] = remove_password_from_url(v, replace_with)


def _join_if_any(sym, args):
    args = list(args)
    if not args:
        return ""
    return sym.join(str(a) for a in args if a)


def remove_password_from_url(url: str, replace_with: str = "***") -> str:
    if "motherduck_token=" in url:
        replace_token_url = url.split("motherduck_token=")[0] + f"motherduck_token={replace_with}"
        return replace_token_url
    else:
        parsed = urlparse(url)
        account = parsed.username or ""
        if parsed.password:
            account += ":" + replace_with
        host = _join_if_any(":", filter(None, [parsed.hostname, parsed.port]))
        netloc = _join_if_any("@", filter(None, [account, host]))
        replaced = parsed._replace(netloc=netloc)
        return replaced.geturl()


def match_like(pattern: str, strs: Sequence[str]) -> Iterable[str]:
    reo = re.compile(pattern.replace("%", ".*").replace("?", ".") + "$")
    for s in strs:
        if reo.match(s):
            yield s


def accumulate(iterable, func=operator.add, *, initial=None):
    "Return running totals"
    # Taken from https://docs.python.org/3/library/itertools.html#itertools.accumulate, to backport 'initial' to 3.7
    it = iter(iterable)
    total = initial
    if initial is None:
        try:
            total = next(it)
        except StopIteration:
            return
    yield total
    for element in it:
        total = func(total, element)
        yield total


def run_as_daemon(threadfunc, *args):
    th = threading.Thread(target=threadfunc, args=args)
    th.daemon = True
    th.start()
    return th


def getLogger(name):
    return logging.getLogger(name.rsplit(".", 1)[-1])


def eval_name_template(name):
    def get_timestamp(_match):
        return datetime.now().isoformat("_", "seconds").replace(":", "_")

    return re.sub("%t", get_timestamp, name)


def truncate_error(error: str):
    first_line = error.split("\n", 1)[0]
    return re.sub("'(.*?)'", "'***'", first_line)


def get_from_dict_with_raise(dictionary: Dict, key: str, exception: Exception):
    if dictionary is None:
        raise exception
    result = dictionary.get(key)
    if result is None:
        raise exception
    return result


class Vector(tuple):
    """Immutable implementation of a regular vector over any arithmetic value

    Implements a product order - https://en.wikipedia.org/wiki/Product_order

    Partial implementation: Only the needed functionality is implemented
    """

    def __lt__(self, other: "Vector") -> bool:
        if isinstance(other, Vector):
            return all(a < b for a, b in safezip(self, other))
        return NotImplemented

    def __le__(self, other: "Vector") -> bool:
        if isinstance(other, Vector):
            return all(a <= b for a, b in safezip(self, other))
        return NotImplemented

    def __gt__(self, other: "Vector") -> bool:
        if isinstance(other, Vector):
            return all(a > b for a, b in safezip(self, other))
        return NotImplemented

    def __ge__(self, other: "Vector") -> bool:
        if isinstance(other, Vector):
            return all(a >= b for a, b in safezip(self, other))
        return NotImplemented

    def __eq__(self, other: "Vector") -> bool:
        if isinstance(other, Vector):
            return all(a == b for a, b in safezip(self, other))
        return NotImplemented

    def __sub__(self, other: "Vector") -> "Vector":
        if isinstance(other, Vector):
            return Vector((a - b) for a, b in safezip(self, other))
        raise NotImplementedError()

    def __repr__(self) -> str:
        return "(%s)" % ", ".join(str(k) for k in self)


def diff_int_dynamic_color_template(diff_value: int) -> str:
    if not isinstance(diff_value, int):
        return diff_value

    if diff_value > 0:
        return f"[green]+{diff_value}[/]"
    elif diff_value < 0:
        return f"[red]{diff_value}[/]"
    else:
        return "0"


def _jsons_equiv(a: str, b: str):
    try:
        return json.loads(a) == json.loads(b)
    except (ValueError, TypeError, json.decoder.JSONDecodeError):  # not valid jsons
        return False


def diffs_are_equiv_jsons(diff: list, json_cols: dict):
    overriden_diff_cols = set()
    if (len(diff) != 2) or ({diff[0][0], diff[1][0]} != {"+", "-"}):
        return False, overriden_diff_cols
    match = True
    for i, (col_a, col_b) in enumerate(safezip(diff[0][1][1:], diff[1][1][1:])):  # index 0 is extra_columns first elem
        # we only attempt to parse columns of JSON type, but we still need to check if non-json columns don't match
        match = col_a == col_b
        if not match and (i in json_cols):
            if _jsons_equiv(col_a, col_b):
                overriden_diff_cols.add(json_cols[i])
                match = True
        if not match:
            break
    return match, overriden_diff_cols


def columns_removed_template(columns_removed: set) -> str:
    columns_removed_str = f"[red]Columns removed [-{len(columns_removed)}]:[/] [blue]{columns_removed}[/]\n"
    return columns_removed_str


def columns_added_template(columns_added: set) -> str:
    columns_added_str = f"[green]Columns added [+{len(columns_added)}]: {columns_added}[/]\n"
    return columns_added_str


def columns_type_changed_template(columns_type_changed) -> str:
    columns_type_changed_str = f"Type changed [{len(columns_type_changed)}]: [green]{columns_type_changed}[/]\n"
    return columns_type_changed_str


def no_differences_template() -> str:
    return "[bold][green]No row differences[/][/]\n"


def print_version_info() -> None: ...


class LogStatusHandler(logging.Handler):
    """
    This log handler can be used to update a rich.status every time a log is emitted.
    """

    def __init__(self) -> None:
        super().__init__()
        self.status = Status("")
        self.prefix = ""
        self.diff_status = {}

    def emit(self, record):
        log_entry = self.format(record)
        if self.diff_status:
            self._update_diff_status(log_entry)
        else:
            self.status.update(self.prefix + log_entry)

    def set_prefix(self, prefix_string):
        self.prefix = prefix_string

    def diff_started(self, model_name):
        self.diff_status[model_name] = "[yellow]In Progress[/]"
        self._update_diff_status()

    def diff_finished(self, model_name):
        self.diff_status[model_name] = "[green]Finished   [/]"
        self._update_diff_status()

    def _update_diff_status(self, log=None):
        status_string = "\n"
        for model_name, status in self.diff_status.items():
            status_string += f"{status} {model_name}\n"
        self.status.update(f"{status_string}{log or ''}")


class UnknownMeta(type):
    def __instancecheck__(self, instance):
        return instance is Unknown

    def __repr__(self) -> str:
        return "Unknown"


class Unknown(metaclass=UnknownMeta):
    def __bool__(self) -> bool:
        raise TypeError()

    def __new__(class_, *args, **kwargs):
        raise RuntimeError("Unknown is a singleton")


@dataclass
class SybaseDriverTypes:
    is_ase: bool = False
    is_iq: bool = False
    is_freetds: bool = False
