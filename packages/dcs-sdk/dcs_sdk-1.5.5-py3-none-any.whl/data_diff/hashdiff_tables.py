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
import os
import time
from collections import defaultdict
from numbers import Number
from threading import Lock
from typing import Any, Collection, Dict, Iterator, List, Sequence, Set, Tuple

import attrs
from loguru import logger
from typing_extensions import Literal

from data_diff.abcs.database_types import (
    JSON,
    Boolean,
    ColType_UUID,
    NumericType,
    PrecisionType,
    StringType,
)
from data_diff.diff_tables import TableDiffer
from data_diff.info_tree import InfoTree
from data_diff.table_segment import TableSegment
from data_diff.thread_utils import ThreadedYielder
from data_diff.utils import diffs_are_equiv_jsons, safezip

BENCHMARK = os.environ.get("BENCHMARK", False)

DEFAULT_BISECTION_THRESHOLD = 1024 * 16
DEFAULT_BISECTION_FACTOR = 32
DEFAULT_PER_COLUMN_DIFF_LIMIT = 100
DEFAULT_ENGRESS_LIMIT = 5_00_000
DEAFULT_TIMEOUT = 60 * 5  # minutes

# logger = logging.getLogger("hashdiff_tables")

# Just for local readability: TODO: later switch to real type declarations of these.
_Op = Literal["+", "-"]
_PK = Sequence[Any]
_Row = Tuple[Any]


class PerColumnDiffTracker:
    """Thread-safe tracker for differences per column and enforces limits"""

    def __init__(
        self,
        per_column_diff_limit: int,
        columns1: Sequence[str],
        columns2: Sequence[str],
        ignored_columns1: Collection[str],
        ignored_columns2: Collection[str],
    ):
        self.per_column_diff_limit = per_column_diff_limit
        self.column_diff_counts = defaultdict(int)
        self.stopped_columns = set()
        self.exclusive_pk_count = 0
        self.duplicate_pk_count = 0
        self._lock = Lock()

        # Store original column mappings
        self.original_columns1 = list(columns1)
        self.original_columns2 = list(columns2)
        self.original_ignored_columns1 = set(ignored_columns1)
        self.original_ignored_columns2 = set(ignored_columns2)

        # Create column name to index mapping for non-ignored columns
        self.active_columns1 = [col for col in columns1 if col not in ignored_columns1]
        self.active_columns2 = [col for col in columns2 if col not in ignored_columns2]
        self.column1_to_index = {col: idx for idx, col in enumerate(self.active_columns1)}
        self.column2_to_index = {col: idx for idx, col in enumerate(self.active_columns2)}

    def should_process_column_diff(self, column_index: int) -> bool:
        """Check if we should continue processing diffs for this column"""
        with self._lock:
            return column_index not in self.stopped_columns

    def record_column_diff(self, column_index: int) -> bool:
        """Record a diff for a column and return True if we should continue processing this column"""
        with self._lock:
            if column_index in self.stopped_columns:
                return False

            if self.column_diff_counts[column_index] >= self.per_column_diff_limit:
                self.stopped_columns.add(column_index)
                column_name = (
                    self.active_columns1[column_index]
                    if column_index < len(self.active_columns1)
                    else f"column_{column_index}"
                )
                logger.info(
                    f"Column '{column_name}' reached diff limit of {self.per_column_diff_limit}, stopping further diff tracking for this column"
                )
                return False
            self.column_diff_counts[column_index] += 1
            return True

    def record_exclusive_pk(self) -> bool:
        """Record an exclusive PK and return True if we should continue processing"""
        with self._lock:
            self.exclusive_pk_count += 1
            return self.exclusive_pk_count < self.per_column_diff_limit

    def record_duplicate_pk(self) -> bool:
        """Record a duplicate PK and return True if we should continue processing"""
        with self._lock:
            self.duplicate_pk_count += 1
            return self.duplicate_pk_count < self.per_column_diff_limit

    def has_active_targets(self, total_columns: int) -> bool:
        """Check if there are still columns being actively tracked"""
        with self._lock:
            return (
                len(self.stopped_columns) < total_columns
                or self.exclusive_pk_count < self.per_column_diff_limit
                or self.duplicate_pk_count < self.per_column_diff_limit
            )

    def get_updated_ignored_columns(self) -> Tuple[Set[str], Set[str]]:
        """Get updated ignored columns including stopped columns"""
        with self._lock:
            updated_ignored1 = set(self.original_ignored_columns1)
            updated_ignored2 = set(self.original_ignored_columns2)

            # Add stopped columns to ignored columns
            for col_idx in self.stopped_columns:
                if col_idx < len(self.active_columns1):
                    updated_ignored1.add(self.active_columns1[col_idx])
                if col_idx < len(self.active_columns2):
                    updated_ignored2.add(self.active_columns2[col_idx])

            return updated_ignored1, updated_ignored2

    def get_active_columns_for_checksum(self) -> Tuple[List[str], List[str]]:
        """Get columns that should be included in checksum (excluding stopped columns)"""
        with self._lock:
            active_checksum_columns1 = []
            active_checksum_columns2 = []

            for idx, col in enumerate(self.active_columns1):
                if idx not in self.stopped_columns:
                    active_checksum_columns1.append(col)

            for idx, col in enumerate(self.active_columns2):
                if idx not in self.stopped_columns:
                    active_checksum_columns2.append(col)

            return active_checksum_columns1, active_checksum_columns2

    def get_stopped_columns(self) -> Set[int]:
        with self._lock:
            return self.stopped_columns.copy()


def diff_sets(
    a: Sequence[_Row],
    b: Sequence[_Row],
    *,
    json_cols: dict = None,
    columns1: Sequence[str],
    columns2: Sequence[str],
    key_columns1: Sequence[str],
    key_columns2: Sequence[str],
    ignored_columns1: Collection[str],
    ignored_columns2: Collection[str],
    diff_tracker: PerColumnDiffTracker = None,
) -> Iterator:
    # Initialize per-column diff tracker if not provided
    if diff_tracker is None:
        diff_tracker = PerColumnDiffTracker(
            DEFAULT_PER_COLUMN_DIFF_LIMIT, columns1, columns2, ignored_columns1, ignored_columns2
        )

    # Get updated ignored columns (including stopped columns)
    updated_ignored1, updated_ignored2 = diff_tracker.get_updated_ignored_columns()

    # Group full rows by PKs on each side. The first items are the PK: TableSegment.relevant_columns
    rows_by_pks1: Dict[_PK, List[_Row]] = defaultdict(list)
    rows_by_pks2: Dict[_PK, List[_Row]] = defaultdict(list)
    for row in a:
        pk: _PK = tuple(val for col, val in zip(key_columns1, row))
        rows_by_pks1[pk].append(row)
    for row in b:
        pk: _PK = tuple(val for col, val in zip(key_columns2, row))
        rows_by_pks2[pk].append(row)

    # Calculate total active columns for tracking
    total_columns = len([col for col in columns1 if col not in updated_ignored1])

    # Mind that the same pk MUST go in full with all the -/+ rows all at once, for grouping.
    diffs_by_pks: Dict[_PK, List[Tuple[_Op, _Row]]] = defaultdict(list)

    warned_diff_cols = set()

    for pk in sorted(set(rows_by_pks1) | set(rows_by_pks2)):
        if not diff_tracker.has_active_targets(total_columns):
            logger.info(
                "Diffing stopped because columns with potential differences have reached their configured diff limits."
            )
            break

        cutrows1: List[_Row] = [tuple(row1) for row1 in rows_by_pks1[pk]]

        cutrows2: List[_Row] = [tuple(row2) for row2 in rows_by_pks2[pk]]

        # Handle exclusive rows (present in only one side)
        if len(rows_by_pks1[pk]) == 0 or len(rows_by_pks2[pk]) == 0:
            if not diff_tracker.record_exclusive_pk():
                continue

            for row1 in rows_by_pks1[pk]:
                diffs_by_pks[pk].append(("-", row1))
            for row2 in rows_by_pks2[pk]:
                diffs_by_pks[pk].append(("+", row2))
            continue

        # Handle duplicate PKs (2+ rows on either side)
        if len(cutrows1) > 1 or len(cutrows2) > 1:
            if not diff_tracker.record_duplicate_pk():
                continue

            for row1 in rows_by_pks1[pk]:
                diffs_by_pks[pk].append(("-", row1))
            for row2 in rows_by_pks2[pk]:
                diffs_by_pks[pk].append(("+", row2))
            continue

        if len(cutrows1) == 1 and len(cutrows2) == 1:
            row1, row2 = cutrows1[0], cutrows2[0]

            # Find all differing columns and attempt to record them
            has_recordable_diff = False

            for col_idx, (val1, val2) in enumerate(zip(row1, row2)):
                if val1 != val2:  # This column has a difference
                    # Try to record it if the column is still being tracked
                    if diff_tracker.should_process_column_diff(col_idx):
                        if diff_tracker.record_column_diff(col_idx):
                            has_recordable_diff = True
                        # Continue checking other columns even if this one just got exhausted

            # Include the row pair if we successfully recorded at least one difference
            if has_recordable_diff:
                for row1 in rows_by_pks1[pk]:
                    diffs_by_pks[pk].append(("-", row1))
                for row2 in rows_by_pks2[pk]:
                    diffs_by_pks[pk].append(("+", row2))

    # Process and yield the collected diffs
    for diffs in (diffs_by_pks[pk] for pk in sorted(diffs_by_pks)):
        if json_cols:
            parsed_match, overriden_diff_cols = diffs_are_equiv_jsons(diffs, json_cols)
            if parsed_match:
                to_warn = overriden_diff_cols - warned_diff_cols
                for w in to_warn:
                    logger.warning(
                        f"Equivalent JSON objects with different string representations detected "
                        f"in column '{w}'. These cases are NOT reported as differences."
                    )
                    warned_diff_cols.add(w)
                continue
        yield from diffs


@attrs.define(frozen=False)
class HashDiffer(TableDiffer):
    """Finds the diff between two SQL tables

    The algorithm uses hashing to quickly check if the tables are different, and then applies a
    bisection search recursively to find the differences efficiently.

    Works best for comparing tables that are mostly the same, with minor discrepancies.

    Parameters:
        bisection_factor (int): Into how many segments to bisect per iteration.
        bisection_threshold (Number): When should we stop bisecting and compare locally (in row count).
        threaded (bool): Enable/disable threaded diffing. Needed to take advantage of database threads.
        max_threadpool_size (int): Maximum size of each threadpool. ``None`` means auto.
                                   Only relevant when `threaded` is ``True``.
                                   There may be many pools, so number of actual threads can be a lot higher.
        per_column_diff_limit (int): Stop targeting column after finding this many different values.
                                    Same applies to exclusive and duplicate PKs. If there are no targets left,
                                    diffing will stop.
        egress_limit (int): Maximum number of rows to download per segment.
        strict (bool): Enable strict type checking. If ``False``, will not raise errors on incompatible types,
    """

    bisection_factor: int = DEFAULT_BISECTION_FACTOR
    bisection_threshold: int = DEFAULT_BISECTION_THRESHOLD
    bisection_disabled: bool = False  # i.e. always download the rows (used in tests)
    strict: bool = True  # i.e. strict type check
    per_column_diff_limit: int = DEFAULT_PER_COLUMN_DIFF_LIMIT
    egress_limit: int = DEFAULT_ENGRESS_LIMIT  # Rows download limit
    stats: dict = attrs.field(factory=dict)
    t1_row_count: int = 0
    t2_row_count: int = 0
    start_time: float = attrs.Factory(lambda: time.monotonic())
    timeout_limit: int = DEAFULT_TIMEOUT

    # Thread-safe diff tracker instance
    _diff_tracker: PerColumnDiffTracker = attrs.field(default=None, init=False)

    def __attrs_post_init__(self) -> None:
        # Validate options
        if self.bisection_factor >= self.bisection_threshold:
            raise ValueError("Incorrect param values (bisection factor must be lower than threshold)")
        if self.bisection_factor < 2:
            raise ValueError("Must have at least two segments per iteration (i.e. bisection_factor >= 2)")
        if self.per_column_diff_limit <= 0:
            raise ValueError("per_column_diff_limit must be a positive integer")

    def _initialize_diff_tracker(self, table1: TableSegment, table2: TableSegment) -> None:
        """Initialize the diff tracker with table information"""
        if self._diff_tracker is None:
            self._diff_tracker = PerColumnDiffTracker(
                self.per_column_diff_limit,
                table1.relevant_columns,
                table2.relevant_columns,
                self.ignored_columns1,
                self.ignored_columns2,
            )

    def update_comparison_tracker(self, reason_type: str, segment: str) -> None:
        if "comparison_tracker" not in self.stats:
            self.stats["comparison_tracker"] = []

        if reason_type == "per_column_diff_limit":
            reason = (
                "Diffing stopped because columns with potential differences have reached their configured diff limits."
            )
        elif reason_type == "egress_limit":
            reason = f"Row download limit reached, {self.stats.get('rows_downloaded')}"
        elif reason_type == "timeout":
            reason = f"Timeout limit reached, {self.timeout_limit} min"

        tracker = self.stats["comparison_tracker"]
        reason_index_map = {
            entry.get("reason_type"): idx for idx, entry in enumerate(tracker) if "reason_type" in entry
        }

        new_entry = {"reason": reason, "segment": segment, "reason_type": reason_type}

        if reason_type in reason_index_map:
            tracker[reason_index_map[reason_type]] = new_entry
        else:
            tracker.append(new_entry)

        self.stats["comparison_tracker"] = tracker

    def _get_checksum_columns(self, table1: TableSegment, table2: TableSegment) -> Tuple[List[str], List[str]]:
        """Get columns to include in checksum, excluding stopped columns"""
        if self._diff_tracker is None:
            # If no diff tracker, use all relevant columns
            return list(table1.relevant_columns), list(table2.relevant_columns)

        # Get active columns for checksum (excluding stopped columns)
        active_cols1, active_cols2 = self._diff_tracker.get_active_columns_for_checksum()

        # If no active columns left, use key columns only
        if not active_cols1 or not active_cols2:
            return list(table1.key_columns), list(table2.key_columns)

        return active_cols1, active_cols2

    def _create_segment_with_updated_columns(
        self, original_segment: TableSegment, active_columns: List[str]
    ) -> TableSegment:
        """Create a new segment with updated relevant columns for checksum"""
        # Create a copy of the segment with updated relevant columns
        updated_segment = attrs.evolve(original_segment, extra_columns=active_columns)
        return updated_segment

    def _validate_and_adjust_columns(self, table1: TableSegment, table2: TableSegment) -> None:
        for c1, c2 in safezip(table1.relevant_columns, table2.relevant_columns):
            if c1 not in table1._schema:
                raise ValueError(f"Column '{c1}' not found in schema for table {table1}")
            if c2 not in table2._schema:
                raise ValueError(f"Column '{c2}' not found in schema for table {table2}")

            # Update schemas to minimal mutual precision
            col1 = table1._schema[c1]
            col2 = table2._schema[c2]
            if isinstance(col1, PrecisionType):
                if not isinstance(col2, PrecisionType):
                    if self.strict:
                        raise TypeError(f"Incompatible types for column '{c1}':  {col1} <-> {col2}")
                    else:
                        continue

                lowest = min(col1, col2, key=lambda col: col.precision)

                if col1.precision != col2.precision:
                    logger.warning(f"Using reduced precision {lowest} for column '{c1}'. Types={col1}, {col2}")

                table1._schema[c1] = attrs.evolve(col1, precision=lowest.precision, rounds=lowest.rounds)
                table2._schema[c2] = attrs.evolve(col2, precision=lowest.precision, rounds=lowest.rounds)

            elif isinstance(col1, (NumericType, Boolean)):
                if not isinstance(col2, (NumericType, Boolean)):
                    if self.strict:
                        raise TypeError(f"Incompatible types for column '{c1}':  {col1} <-> {col2}")
                    else:
                        continue

                lowest = min(col1, col2, key=lambda col: col.precision)

                if col1.precision != col2.precision:
                    logger.warning(f"Using reduced precision {lowest} for column '{c1}'. Types={col1}, {col2}")

                if lowest.precision != col1.precision:
                    table1._schema[c1] = attrs.evolve(col1, precision=lowest.precision)
                if lowest.precision != col2.precision:
                    table2._schema[c2] = attrs.evolve(col2, precision=lowest.precision)

        for t in [table1, table2]:
            for c in t.relevant_columns:
                ctype = t._schema[c]
                if not ctype.supported:
                    logger.warning(
                        f"[{t.database.name if t.database.name.lower() != 'duckdb' else 'File'}] Column '{c}' of type '{ctype}' has no compatibility handling. "
                        "If encoding/formatting differs between databases, it may result in false positives."
                    )

    def _diff_segments(
        self,
        ti: ThreadedYielder,
        table1: TableSegment,
        table2: TableSegment,
        info_tree: InfoTree,
        max_rows: int,
        level=0,
        segment_index=None,
        segment_count=None,
    ):
        # Check if level exceeds maximum allowed recursion depth
        if level > 15:
            raise RecursionError(f"Maximum recursion level exceeded: {level} > 15")

        # Initialize diff tracker if not already done
        self._initialize_diff_tracker(table1, table2)

        logger.info(
            ". " * level + f"Diffing segment {segment_index}/{segment_count}, "
            f"key-range: {table1.min_key}..{table2.max_key}, "
            f"size <= {max_rows}"
        )
        elapsed = time.monotonic() - self.start_time
        if (
            len(self._diff_tracker.get_stopped_columns()) > 0
            and not self.stats.get("rows_downloaded", 0) >= self.egress_limit
            and not elapsed > self.timeout_limit * 60
        ):
            self.update_comparison_tracker(
                reason_type="per_column_diff_limit",
                segment=f"{table1.min_key}..{table1.max_key}",
            )
        if not self._diff_tracker.has_active_targets(len(table1.relevant_columns)):
            logger.info(
                "Diffing stopped because columns with potential differences have reached their configured diff limits."
            )
            info_tree.info.is_diff = False
            self.update_comparison_tracker(
                reason_type="per_column_diff_limit",
                segment=f"{table1.min_key}..{table1.max_key}",
            )
            return
        if self.stats.get("rows_downloaded", 0) >= self.egress_limit:
            info_tree.info.is_diff = False
            logger.info(
                ". " * level
                + f"Row download limit reached {self.stats.get('rows_downloaded')}, stopping bisection for segment {table1.min_key}..{table1.max_key}"
            )
            self.update_comparison_tracker(
                reason_type="egress_limit",
                segment=f"{table1.min_key}..{table1.max_key}",
            )
            return

        elapsed = time.monotonic() - self.start_time
        if elapsed > self.timeout_limit * 60:
            info_tree.info.is_diff = False
            logger.info(
                ". " * level + f"Timeout limit reached ({self.timeout_limit} min); "
                f"stopping bisection for segment {table1.min_key}..{table1.max_key}"
            )
            self.update_comparison_tracker(
                reason_type="timeout",
                segment=f"{table1.min_key}..{table1.max_key}",
            )
            return
        # When benchmarking, we want the ability to skip checksumming. This
        # allows us to download all rows for comparison in performance. By
        # default, dcs-diff will checksum the section first (when it's below
        # the threshold) and _then_ download it.
        if BENCHMARK:
            if self.bisection_disabled or max_rows < self.bisection_threshold:
                return self._bisect_and_diff_segments(ti, table1, table2, info_tree, level=level, max_rows=max_rows)

        # Get active columns for checksum (excluding stopped columns)
        active_cols1, active_cols2 = self._get_checksum_columns(table1, table2)

        # Create segments with updated columns for checksum
        checksum_table1 = self._create_segment_with_updated_columns(table1, active_cols1)
        checksum_table2 = self._create_segment_with_updated_columns(table2, active_cols2)

        (count1, checksum1), (count2, checksum2) = self._threaded_call(
            "count_and_checksum", [checksum_table1, checksum_table2]
        )

        assert not info_tree.info.rowcounts
        info_tree.info.rowcounts = {1: count1, 2: count2}

        if count1 == 0 and count2 == 0:
            logger.debug(
                "Uneven distribution of keys detected in segment {}..{} (big gaps in the key column). "
                "For better performance, we recommend to increase the bisection-threshold.",
                table1.min_key,
                table1.max_key,
            )
            assert checksum1 is None and checksum2 is None
            info_tree.info.is_diff = False
            return

        if checksum1 == checksum2:
            info_tree.info.is_diff = False
            return

        info_tree.info.is_diff = True
        return self._bisect_and_diff_segments(ti, table1, table2, info_tree, level=level, max_rows=max(count1, count2))

    def _bisect_and_diff_segments(
        self,
        ti: ThreadedYielder,
        table1: TableSegment,
        table2: TableSegment,
        info_tree: InfoTree,
        level=0,
        max_rows=None,
    ):
        # Check if level exceeds maximum allowed recursion depth
        if level > 15:
            raise RecursionError(f"Maximum recursion level exceeded: {level} > 15")

        assert table1.is_bounded and table2.is_bounded

        # Initialize diff tracker if not already done
        self._initialize_diff_tracker(table1, table2)
        elapsed = time.monotonic() - self.start_time
        if (
            len(self._diff_tracker.get_stopped_columns()) > 0
            and not self.stats.get("rows_downloaded", 0) >= self.egress_limit
            and not elapsed > self.timeout_limit * 60
        ):
            self.update_comparison_tracker(
                reason_type="per_column_diff_limit",
                segment=f"{table1.min_key}..{table1.max_key}",
            )

        if not self._diff_tracker.has_active_targets(len(table1.relevant_columns)):
            logger.info(
                "Diffing stopped because columns with potential differences have reached their configured diff limits."
            )
            info_tree.info.is_diff = False
            self.update_comparison_tracker(
                reason_type="per_column_diff_limit",
                segment=f"{table1.min_key}..{table1.max_key}",
            )
            return
        if self.stats.get("rows_downloaded", 0) >= self.egress_limit:
            logger.info("Row download limit reached, stopping bisection")
            logger.info(
                ". " * level
                + f"Row download limit reached {self.stats.get('rows_downloaded')}, stopping bisection for segment {table1.min_key}..{table1.max_key}"
            )
            self.update_comparison_tracker(
                reason_type="egress_limit",
                segment=f"{table1.min_key}..{table1.max_key}",
            )
            info_tree.info.is_diff = False
            return

        elapsed = time.monotonic() - self.start_time
        if elapsed > self.timeout_limit * 60:
            info_tree.info.is_diff = False
            logger.info(
                ". " * level + f"Timeout limit reached ({self.timeout_limit} min); "
                f"stopping bisection for segment {table1.min_key}..{table1.max_key}"
            )
            self.update_comparison_tracker(
                reason_type="timeout",
                segment=f"{table1.min_key}..{table1.max_key}",
            )
            return

        max_space_size = max(table1.approximate_size(self.t1_row_count), table2.approximate_size(self.t2_row_count))
        if max_rows is None:
            # We can be sure that row_count <= max_rows iff the table key is unique
            max_rows = max_space_size
            info_tree.info.max_rows = max_rows

        # If count is below the threshold, just download and compare the columns locally
        # This saves time, as bisection speed is limited by ping and query performance.
        if self.bisection_disabled or max_rows < self.bisection_threshold or max_space_size < self.bisection_factor * 2:
            rows1, rows2 = self._threaded_call("get_values", [table1, table2])
            json_cols = {
                i: colname
                for i, colname in enumerate(table1.extra_columns)
                if isinstance(table1._schema[colname], JSON)
            }
            diff = list(
                diff_sets(
                    rows1,
                    rows2,
                    json_cols=json_cols,
                    columns1=table1.relevant_columns,
                    columns2=table2.relevant_columns,
                    key_columns1=table1.key_columns,
                    key_columns2=table2.key_columns,
                    ignored_columns1=self.ignored_columns1,
                    ignored_columns2=self.ignored_columns2,
                    diff_tracker=self._diff_tracker,
                )
            )

            info_tree.info.set_diff(diff)
            info_tree.info.rowcounts = {1: len(rows1), 2: len(rows2)}

            self.stats["rows_downloaded"] = self.stats.get("rows_downloaded", 0) + max(len(rows1), len(rows2))
            logger.info(
                ". " * level
                + f"Diff found {len(diff)} different rows, {self.stats['rows_downloaded']} total rows downloaded."
            )
            return diff

        return super()._bisect_and_diff_segments(ti, table1, table2, info_tree, level, max_rows)
