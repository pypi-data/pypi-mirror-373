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

import logging
import time
from decimal import Decimal
from itertools import product
from typing import Container, Dict, List, Optional, Sequence, Tuple

import attrs
import numpy as np
from loguru import logger
from typing_extensions import Self

from data_diff.abcs.database_types import DbKey, DbPath, DbTime, IKey, NumericType
from data_diff.databases.base import Database
from data_diff.queries.api import (
    SKIP,
    Code,
    Count,
    Expr,
    and_,
    max_,
    min_,
    or_,
    table,
    this,
)
from data_diff.queries.extras import (
    ApplyFuncAndNormalizeAsString,
    Checksum,
    NormalizeAsString,
)
from data_diff.schema import RawColumnInfo, Schema, create_schema
from data_diff.utils import (
    ArithDate,
    ArithDateTime,
    ArithString,
    ArithTimestamp,
    ArithTimestampTZ,
    ArithUnicodeString,
    Vector,
    safezip,
    split_space,
)

# logger = logging.getLogger("table_segment")

RECOMMENDED_CHECKSUM_DURATION = 20


def split_key_space(min_key: DbKey, max_key: DbKey, count: int) -> List[DbKey]:
    assert min_key < max_key

    if max_key - min_key <= count:
        count = 1

    # Handle arithmetic string types (including temporal types)
    if isinstance(
        min_key, (ArithString, ArithUnicodeString, ArithDateTime, ArithDate, ArithTimestamp, ArithTimestampTZ)
    ):
        assert type(min_key) is type(max_key)
        checkpoints = min_key.range(max_key, count)
    else:
        # Handle numeric types
        if isinstance(min_key, Decimal):
            min_key = float(min_key)
        if isinstance(max_key, Decimal):
            max_key = float(max_key)
        checkpoints = split_space(min_key, max_key, count)

    assert all(min_key < x < max_key for x in checkpoints)
    return [min_key] + checkpoints + [max_key]


def int_product(nums: List[int]) -> int:
    p = 1
    for n in nums:
        p *= n
    return p


def split_compound_key_space(mn: Vector, mx: Vector, count: int) -> List[List[DbKey]]:
    """Returns a list of split-points for each key dimension, essentially returning an N-dimensional grid of split points."""
    return [split_key_space(mn_k, mx_k, count) for mn_k, mx_k in safezip(mn, mx)]


def create_mesh_from_points(*values_per_dim: list) -> List[Tuple[Vector, Vector]]:
    """Given a list of values along each axis of N dimensional space,
    return an array of boxes whose start-points & end-points align with the given values,
    and together consitute a mesh filling that space entirely (within the bounds of the given values).

    Assumes given values are already ordered ascending.

    len(boxes) == ∏i( len(i)-1 )

    Example:
        ::
            >>> d1 = 'a', 'b', 'c'
            >>> d2 = 1, 2, 3
            >>> d3 = 'X', 'Y'
            >>> create_mesh_from_points(d1, d2, d3)
            [
                [('a', 1, 'X'), ('b', 2, 'Y')],
                [('a', 2, 'X'), ('b', 3, 'Y')],
                [('b', 1, 'X'), ('c', 2, 'Y')],
                [('b', 2, 'X'), ('c', 3, 'Y')]
            ]
    """
    assert all(len(v) >= 2 for v in values_per_dim), values_per_dim

    # Create tuples of (v1, v2) for each pair of adjacent values
    ranges = [list(zip(values[:-1], values[1:])) for values in values_per_dim]

    assert all(a <= b for r in ranges for a, b in r)

    # Create a product of all the ranges
    res = [tuple(Vector(a) for a in safezip(*r)) for r in product(*ranges)]

    expected_len = int_product(len(v) - 1 for v in values_per_dim)
    assert len(res) == expected_len, (len(res), expected_len)
    return res


@attrs.define(frozen=True)
class TableSegment:
    """Signifies a segment of rows (and selected columns) within a table

    Parameters:
        database (Database): Database instance. See :meth:`connect`
        table_path (:data:`DbPath`): Path to table in form of a tuple. e.g. `('my_dataset', 'table_name')`
        key_columns (Tuple[str]): Name of the key column, which uniquely identifies each row (usually id)
        update_column (str, optional): Name of updated column, which signals that rows changed.
                                       Usually updated_at or last_update. Used by `min_update` and `max_update`.
        extra_columns (Tuple[str, ...], optional): Extra columns to compare
        transform_columns (Dict[str, str], optional): A dictionary mapping column names to SQL transformation expressions.
                                                      These expressions are applied directly to the specified columns within the
                                                      comparison query, *before* the data is hashed or compared. Useful for
                                                      on-the-fly normalization (e.g., type casting, timezone conversions) without
                                                      requiring intermediate views or staging tables. Defaults to an empty dict.
        min_key (:data:`Vector`, optional): Lowest key value, used to restrict the segment
        max_key (:data:`Vector`, optional): Highest key value, used to restrict the segment
        min_update (:data:`DbTime`, optional): Lowest update_column value, used to restrict the segment
        max_update (:data:`DbTime`, optional): Highest update_column value, used to restrict the segment
        where (str, optional): An additional 'where' expression to restrict the search space.

        case_sensitive (bool): If false, the case of column names will adjust according to the schema. Default is true.

    """

    # Location of table
    database: Database
    table_path: DbPath

    # Columns
    key_columns: Tuple[str, ...]
    update_column: Optional[str] = None
    extra_columns: Tuple[str, ...] = ()
    transform_columns: Dict[str, str] = {}
    ignored_columns: Container[str] = frozenset()

    # Restrict the segment
    min_key: Optional[Vector] = None
    max_key: Optional[Vector] = None
    min_update: Optional[DbTime] = None
    max_update: Optional[DbTime] = None
    where: Optional[str] = None

    case_sensitive: Optional[bool] = True
    _schema: Optional[Schema] = None

    query_stats: Dict = attrs.Factory(
        lambda: {
            "count_queries_stats": {
                "total_queries": 0,
                "min_time_ms": 0.0,
                "max_time_ms": 0.0,
                "avg_time_ms": 0.0,
                "p90_time_ms": 0.0,
                "total_time_taken_ms": 0.0,
                "_query_times": [],
            },
            "checksum_queries_stats": {
                "total_queries": 0,
                "min_time_ms": 0.0,
                "max_time_ms": 0.0,
                "avg_time_ms": 0.0,
                "p90_time_ms": 0.0,
                "total_time_taken_ms": 0.0,
                "_query_times": [],
            },
            "row_fetch_queries_stats": {
                "total_queries": 0,
                "min_time_ms": 0.0,
                "max_time_ms": 0.0,
                "avg_time_ms": 0.0,
                "p90_time_ms": 0.0,
                "total_time_taken_ms": 0.0,
                "_query_times": [],
            },
            "schema_queries_stats": {
                "total_queries": 0,
                "min_time_ms": 0.0,
                "max_time_ms": 0.0,
                "avg_time_ms": 0.0,
                "p90_time_ms": 0.0,
                "total_time_taken_ms": 0.0,
                "_query_times": [],
            },
        }
    )

    def __attrs_post_init__(self) -> None:
        if not self.update_column and (self.min_update or self.max_update):
            raise ValueError("Error: the min_update/max_update feature requires 'update_column' to be set.")

        if self.min_key is not None and self.max_key is not None and self.min_key >= self.max_key:
            raise ValueError(f"Error: min_key expected to be smaller than max_key! ({self.min_key} >= {self.max_key})")

        if self.min_update is not None and self.max_update is not None and self.min_update >= self.max_update:
            raise ValueError(
                f"Error: min_update expected to be smaller than max_update! ({self.min_update} >= {self.max_update})"
            )

    def _update_stats(self, stats_key: str, query_time_ms: float) -> None:
        logger.info(f"Query time for {stats_key.replace('_stats', '')}: {query_time_ms:.2f} ms")
        stats = self.query_stats[stats_key]
        stats["total_queries"] += 1
        stats["_query_times"].append(query_time_ms)
        stats["total_time_taken_ms"] += query_time_ms
        stats["min_time_ms"] = min(stats["_query_times"]) if stats["_query_times"] else 0.0
        stats["max_time_ms"] = max(stats["_query_times"]) if stats["_query_times"] else 0.0
        if stats["_query_times"]:
            times = np.array(stats["_query_times"])
            stats["avg_time_ms"] = float(np.mean(times))
            stats["p90_time_ms"] = float(np.percentile(times, 90, method="linear"))
        else:
            stats["avg_time_ms"] = 0.0
            stats["p90_time_ms"] = 0.0

    def _where(self) -> Optional[str]:
        return f"({self.where})" if self.where else None

    def _with_raw_schema(self, raw_schema: Dict[str, RawColumnInfo]) -> Self:
        schema = self.database._process_table_schema(self.table_path, raw_schema, self.relevant_columns, self._where())
        # return self.new(schema=create_schema(self.database.name, self.table_path, schema, self.case_sensitive))
        return self.new(
            schema=create_schema(self.database.name, self.table_path, schema, self.case_sensitive),
            transform_columns=self.transform_columns,
        )

    def with_schema(self) -> Self:
        "Queries the table schema from the database, and returns a new instance of TableSegment, with a schema."
        if self._schema:
            return self

        start_time = time.monotonic()
        raw_schema = self.database.query_table_schema(self.table_path)
        query_time_ms = (time.monotonic() - start_time) * 1000
        self._update_stats("schema_queries_stats", query_time_ms)
        return self._with_raw_schema(raw_schema)

    def get_schema(self) -> Dict[str, RawColumnInfo]:
        return self.database.query_table_schema(self.table_path)

    def _make_key_range(self):
        if self.min_key is not None:
            for mn, k in safezip(self.min_key, self.key_columns):
                yield mn <= this[k]
        if self.max_key is not None:
            for k, mx in safezip(self.key_columns, self.max_key):
                yield this[k] < mx

    def _make_update_range(self):
        if self.min_update is not None:
            yield self.min_update <= this[self.update_column]
        if self.max_update is not None:
            yield this[self.update_column] < self.max_update

    @property
    def source_table(self):
        return table(*self.table_path, schema=self._schema)

    def make_select(self):
        return self.source_table.where(
            *self._make_key_range(), *self._make_update_range(), Code(self._where()) if self.where else SKIP
        )

    def get_values(self) -> list:
        "Download all the relevant values of the segment from the database"
        # Fetch all the original columns, even if some were later excluded from checking.

        # fetched_cols = [NormalizeAsString(this[c]) for c in self.relevant_columns]
        # select = self.make_select().select(*fetched_cols)

        select = self.make_select().select(*self._relevant_columns_repr)
        start_time = time.monotonic()
        result = self.database.query(select, List[Tuple])
        query_time_ms = (time.monotonic() - start_time) * 1000
        self._update_stats("row_fetch_queries_stats", query_time_ms)

        return result

    # def get_sample_data(self, limit: int = 100) -> list:
    #     "Download all the relevant values of the segment from the database"

    #     exprs = []
    #     for c in self.key_columns:
    #         quoted = self.database.dialect.quote(c)
    #         exprs.append(NormalizeAsString(Code(quoted), self._schema[c]))
    #     if self.where:
    #         select = self.source_table.select(*self._relevant_columns_repr).where(Code(self._where())).limit(limit)
    #         self.key_columns
    #     else:
    #         select = self.source_table.select(*self._relevant_columns_repr).limit(limit)

    #     start_time = time.monotonic()
    #     result = self.database.query(select, List[Tuple])
    #     query_time_ms = (time.monotonic() - start_time) * 1000
    #     self._update_stats("row_fetch_queries_stats", query_time_ms)

    def get_sample_data(self, limit: int = 100, sample_keys: Optional[List[List[DbKey]]] = None) -> list:
        """
        Download relevant values of the segment from the database.
        If `sample_keys` is provided, it filters rows matching those composite keys.

        Parameters:
            limit (int): Maximum number of rows to return (default: 100).
            sample_keys (Optional[List[List[DbKey]]]): List of composite keys to filter rows.
                Each inner list must match the number of key_columns.

        Returns:
            list: List of tuples containing the queried row data.
        """
        select = self.make_select().select(*self._relevant_columns_repr)

        filters = []

        if sample_keys:
            key_exprs = []
            for key_values in sample_keys:
                and_exprs = []
                for col, val in safezip(self.key_columns, key_values):
                    quoted = self.database.dialect.quote(col)
                    schema = self._schema[col]
                    if val is None:
                        and_exprs.append(Code(quoted + " IS NULL"))
                        continue
                    mk_v = schema.make_value(val)
                    constant_val = self.database.dialect._constant_value(mk_v)

                    # Special handling for Sybase timestamp equality to handle precision mismatches
                    if hasattr(self.database.dialect, "timestamp_equality_condition") and hasattr(
                        mk_v, "_dt"
                    ):  # Check if it's a datetime-like object
                        where_expr = self.database.dialect.timestamp_equality_condition(quoted, constant_val)
                    else:
                        where_expr = f"{quoted} = {constant_val}"

                    and_exprs.append(Code(where_expr))
                if and_exprs:
                    key_exprs.append(and_(*and_exprs))
            if key_exprs:
                filters.append(or_(*key_exprs))
        if filters or self.where:
            select = select.where(*filters)
        else:
            logger.warning("No filters applied; fetching up to {} rows without key restrictions", limit)

        select = select.limit(limit)

        start_time = time.monotonic()
        result = self.database.query(select, List[Tuple])
        query_time_ms = (time.monotonic() - start_time) * 1000
        self._update_stats("row_fetch_queries_stats", query_time_ms)

        return result

    def choose_checkpoints(self, count: int) -> List[List[DbKey]]:
        "Suggests a bunch of evenly-spaced checkpoints to split by, including start, end."

        assert self.is_bounded

        # Take Nth root of count, to approximate the appropriate box size
        count = int(count ** (1 / len(self.key_columns))) or 1

        return split_compound_key_space(self.min_key, self.max_key, count)

    def segment_by_checkpoints(self, checkpoints: List[List[DbKey]]) -> List["TableSegment"]:
        "Split the current TableSegment to a bunch of smaller ones, separated by the given checkpoints"
        return [self.new_key_bounds(min_key=s, max_key=e) for s, e in create_mesh_from_points(*checkpoints)]

    def new(self, **kwargs) -> Self:
        """Creates a copy of the instance using 'replace()'"""
        return attrs.evolve(self, **kwargs)

    def new_key_bounds(self, min_key: Vector, max_key: Vector, *, key_types: Optional[Sequence[IKey]] = None) -> Self:
        if self.min_key is not None:
            assert self.min_key <= min_key, (self.min_key, min_key)
            assert self.min_key < max_key

        if self.max_key is not None:
            assert min_key < self.max_key
            assert max_key <= self.max_key

        # If asked, enforce the PKs to proper types, mainly to meta-params of the relevant side,
        # so that we do not leak e.g. casing of UUIDs from side A to side B and vice versa.
        # If not asked, keep the meta-params of the keys as is (assume them already casted).
        if key_types is not None:
            min_key = Vector(type.make_value(val) for type, val in safezip(key_types, min_key))
            max_key = Vector(type.make_value(val) for type, val in safezip(key_types, max_key))

        return attrs.evolve(self, min_key=min_key, max_key=max_key)

    @property
    def relevant_columns(self) -> List[str]:
        extras = list(self.extra_columns)

        if self.update_column and self.update_column not in extras:
            extras = [self.update_column] + extras

        return list(self.key_columns) + extras

    @property
    def _relevant_columns_repr(self) -> List[Expr]:
        # return [NormalizeAsString(this[c]) for c in self.relevant_columns]
        expressions = []
        for c in self.relevant_columns:
            quoted_column_name = self.database.quote(s=c)
            schema = self._schema[c]
            if self.transform_columns and c in self.transform_columns:
                transform_expr = self.transform_columns[c]
                quoted_expr = transform_expr.format(column=quoted_column_name)
                expressions.append(NormalizeAsString(Code(quoted_expr), schema))
            else:
                expressions.append(NormalizeAsString(this[c], schema))
        return expressions

    def count(self) -> int:
        """Count how many rows are in the segment, in one pass."""
        start_time = time.monotonic()
        result = self.database.query(self.make_select().select(Count()), int)
        query_time_ms = (time.monotonic() - start_time) * 1000
        self._update_stats("count_queries_stats", query_time_ms)

        return result

    def count_and_checksum(self) -> Tuple[int, int]:
        """Count and checksum the rows in the segment, in one pass."""

        checked_columns = [c for c in self.relevant_columns if c not in self.ignored_columns]
        # cols = [NormalizeAsString(this[c]) for c in checked_columns]

        # q = self.make_select().select(Count(), Checksum(cols))
        q = self.make_select().select(Count(), Checksum(self._relevant_columns_repr))
        start_time = time.monotonic()
        count, checksum = self.database.query(q, tuple)
        query_time_ms = (time.monotonic() - start_time) * 1000

        self._update_stats("checksum_queries_stats", query_time_ms)

        duration = query_time_ms / 1000
        if duration > RECOMMENDED_CHECKSUM_DURATION:
            logger.warning(
                "Checksum is taking longer than expected (%.2f). "
                "We recommend increasing --bisection-factor or decreasing --threads.",
                duration,
            )

        if count:
            assert checksum, (count, checksum)
        return count or 0, int(checksum) if count else None

    def query_key_range(self) -> Tuple[tuple, tuple]:
        """Query database for minimum and maximum key. This is used for setting the initial bounds."""
        # Normalizes the result (needed for UUIDs) after the min/max computation
        select = self.make_select().select(
            ApplyFuncAndNormalizeAsString(this[k], f) for k in self.key_columns for f in (min_, max_)
        )
        result = tuple(self.database.query(select, tuple))

        if any(i is None for i in result):
            raise ValueError("Table appears to be empty")

        # Min/max keys are interleaved
        min_key, max_key = result[::2], result[1::2]
        assert len(min_key) == len(max_key)

        return min_key, max_key

    @property
    def is_bounded(self):
        return self.min_key is not None and self.max_key is not None

    # def approximate_size(self, row_count: Optional[int] = None):
    #     if not self.is_bounded:
    #         raise RuntimeError("Cannot approximate the size of an unbounded segment. Must have min_key and max_key.")
    #     diff = self.max_key - self.min_key
    #     assert all(d > 0 for d in diff)
    #     return int_product(diff)

    def approximate_size(self, row_count: Optional[int] = None) -> int:
        if not self.is_bounded:
            raise RuntimeError("Cannot approximate the size of an unbounded segment. Must have min_key and max_key.")

        schema = self.get_schema()
        key_types = [schema[col].__class__ for col in self.key_columns]

        if all(issubclass(t, NumericType) for t in key_types):
            try:
                diff = [mx - mn for mn, mx in zip(self.min_key, self.max_key)]
                if not all(d > 0 for d in diff):
                    return row_count if row_count is not None else self.count()
                return int_product(diff)
            except (ValueError, TypeError):
                return row_count if row_count is not None else self.count()
        else:
            return row_count if row_count is not None else self.count()
