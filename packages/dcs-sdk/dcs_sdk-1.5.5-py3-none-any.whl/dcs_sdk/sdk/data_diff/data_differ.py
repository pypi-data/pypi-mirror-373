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

import glob
import os
import time
from collections import defaultdict
from contextlib import suppress
from datetime import datetime, timezone
from typing import Dict, Optional

from loguru import logger
from rich.console import Console

from data_diff import TableSegment, connect, connect_to_table, diff_tables
from data_diff.databases import Database
from dcs_sdk.sdk.config.config_loader import Comparison, SourceTargetConnection
from dcs_sdk.sdk.rules.rules_repository import RulesRepository
from dcs_sdk.sdk.utils.serializer import serialize_table_schema
from dcs_sdk.sdk.utils.table import create_table_schema_row_count, differ_rows
from dcs_sdk.sdk.utils.themes import theme_1
from dcs_sdk.sdk.utils.utils import (
    calculate_column_differences,
    convert_to_masked_if_required,
    duck_db_load_csv_to_table,
    find_identical_columns,
    generate_table_name,
    obfuscate_sensitive_data,
)

DYNAMIC_BISECTION_THRESHOLD_MAX_LIMIT = 5_00_000
DEFAULT_BISECTION_THRESHOLD = 50_000
ROW_COUNT_PER_SEGMENT = 1_00_000
MAX_EGRESS_LIMIT = 5_00_000
MIN_EGRESS_LIMIT = 50_000


class DBTableDiffer:
    def __init__(self, config: Comparison):
        self.config = config
        self.console = Console(record=True)
        self.created_at = datetime.now(tz=timezone.utc)
        self.start_time = time.monotonic()
        self.algorithm = "hashdiff"
        self.table1 = None
        self.table2 = None
        self.diff_iter = None
        self.response = {}
        self.source_file_path = self.config.source.filepath
        self.target_file_path = self.config.target.filepath
        self.limit = config.limit
        self.default_limit = 1000
        self.table_limit = 100
        self.source_db: Database = None
        self.target_db: Database = None
        self.similarity = self.config.similarity
        self.similarity_providers = None
        if self.similarity:
            from dcs_sdk.sdk.utils.similarity_score.base_provider import (
                ensure_nltk_data,
            )
            from dcs_sdk.sdk.utils.similarity_score.cosine_similarity_provider import (
                CosineSimilarityProvider,
            )
            from dcs_sdk.sdk.utils.similarity_score.jaccard_provider import (
                JaccardSimilarityProvider,
            )
            from dcs_sdk.sdk.utils.similarity_score.levenshtein_distance_provider import (
                LevenshteinDistanceProvider,
            )

            ensure_nltk_data()

            self.similarity_providers = {
                "jaccard": JaccardSimilarityProvider,
                "levenshtein": LevenshteinDistanceProvider,
                "cosine": CosineSimilarityProvider,
            }

    def create_dataset_dict(
        self,
        config: SourceTargetConnection,
        table: TableSegment,
        db_name: str,
        file_path: str,
        database_type: str,
    ) -> Dict:
        schema_list = [serialize_table_schema(v) for v in table.get_schema().values()]
        schema_list.sort(key=lambda x: x["column_name"].upper())

        return {
            "id": config.id,
            "name": config.name,
            "workspace": config.workspace,
            "database_type": database_type,
            "table_name": table.table_path[0],
            "schema": table.database.default_schema,
            "database": db_name,
            "primary_keys": list(table.key_columns),
            "file_path": file_path,
            "files": [] if file_path is None else [generate_table_name(csv, False) for csv in glob.glob(file_path)],
            "row_count": table.count(),
            "columns": schema_list,
            "exclusive_pk_cnt": 0,
            "duplicate_pk_cnt": 0,
            "null_pk_cnt": 0,
        }

    def connect_to_db_table(
        self,
        config: SourceTargetConnection,
        is_source: bool,
    ) -> TableSegment:
        if is_source:
            primary_keys = self.config.primary_keys_source
            columns = self.config.source_columns
            where = self.config.source_filter
        else:
            primary_keys = self.config.primary_keys_target
            columns = self.config.target_columns
            where = self.config.target_filter

        return connect_to_table(
            {
                "driver": config.driver,
                "host": config.host,
                "port": config.port,
                "http_path": config.http_path,
                "access_token": config.access_token,
                "user": config.username,
                "password": config.password,
                "database": config.database,
                "schema": config.schema_name,
                "filepath": config.filepath,
                "warehouse": config.warehouse,
                "role": config.role,
                "catalog": config.catalog,
                "account": config.account,
                "odbc_driver": config.odbc_driver,
                "server": config.server,
                "project": config.project,
                "dataset": config.dataset,
                "keyfile": config.keyfile,
                "impersonate_service_account": config.impersonate_service_account,
                "bigquery_credentials": config.bigquery_credentials,
            },
            config.table,
            tuple(primary_keys),
            extra_columns=tuple(columns),
            where=where,
            transform_columns=config.transform_columns,
        )

    def connect_to_db(self, config: SourceTargetConnection, is_source: bool):
        if is_source:
            self.source_db: Database = connect(
                {
                    "driver": config.driver,
                    "host": config.host,
                    "port": config.port,
                    "http_path": config.http_path,
                    "access_token": config.access_token,
                    "user": config.username,
                    "password": config.password,
                    "database": config.database,
                    "warehouse": config.warehouse,
                    "schema": config.schema_name,
                    "role": config.role,
                    "catalog": config.catalog,
                    "account": config.account,
                    "odbc_driver": config.odbc_driver,
                    "server": config.server,
                    "project": config.project,
                    "keyfile": config.keyfile,
                    "impersonate_service_account": config.impersonate_service_account,
                    "bigquery_credentials": config.bigquery_credentials,
                    "dataset": config.dataset,
                }
            )
        else:
            self.target_db: Database = connect(
                {
                    "driver": config.driver,
                    "host": config.host,
                    "port": config.port,
                    "http_path": config.http_path,
                    "access_token": config.access_token,
                    "user": config.username,
                    "password": config.password,
                    "database": config.database,
                    "warehouse": config.warehouse,
                    "schema": config.schema_name,
                    "role": config.role,
                    "catalog": config.catalog,
                    "account": config.account,
                    "odbc_driver": config.odbc_driver,
                    "server": config.server,
                    "project": config.project,
                    "keyfile": config.keyfile,
                    "impersonate_service_account": config.impersonate_service_account,
                    "bigquery_credentials": config.bigquery_credentials,
                    "dataset": config.dataset,
                }
            )

    def process_duckdb(self, is_source: bool):
        if is_source:
            filepath = self.config.source.filepath
        else:
            filepath = self.config.target.filepath
        if filepath is None:
            raise ValueError("File path is required for file")
        if filepath.endswith(".csv"):
            if not duck_db_load_csv_to_table(self.config, filepath, is_source):
                raise ValueError(f"Error in loading CSV, for the {'source' if is_source else 'target'}")

    def _prepare_source_table(self) -> Optional[str]:
        view_name = None
        if self.config.source.driver == "duckdb":
            return view_name
        if self.config.source_query is not None:
            self._process_database_as_schema(
                driver=self.config.source.driver,
                is_source=True,
            )
            self.connect_to_db(
                self.config.source,
                is_source=True,
            )
            view_name = self.source_db.create_view_from_query(
                query=self.config.source_query,
                schema=self.config.temporary_schema_source,
                view_name=self.config.view_name_source,
            )
            self.config.source.schema_name = self.config.temporary_schema_source
            self.config.source.table = view_name
        return view_name

    def _prepare_target_table(self) -> Optional[str]:
        view_name = None
        if self.config.target.driver == "duckdb":
            return view_name
        if self.config.target_query is not None:
            self._process_database_as_schema(
                driver=self.config.target.driver,
                is_source=False,
            )
            self.connect_to_db(
                self.config.target,
                is_source=False,
            )
            view_name = self.target_db.create_view_from_query(
                query=self.config.target_query,
                schema=self.config.temporary_schema_target,
                view_name=self.config.view_name_target,
            )
            self.config.target.schema_name = self.config.temporary_schema_target
            self.config.target.table = view_name

        return view_name

    def _process_database_as_schema(self, driver: str, is_source: bool):
        if driver in ["mysql"]:
            if is_source:
                self.config.source.database = self.config.temporary_schema_source
            else:
                self.config.target.database = self.config.temporary_schema_target

    def _process_duckdb_connections(self):
        if self.config.source.driver == "duckdb":
            self.process_duckdb(is_source=True)
        if self.config.target.driver == "duckdb":
            self.process_duckdb(is_source=False)

    def _get_automatic_bisection_threshold(self, max_row_count: int) -> int:
        val = max_row_count // 10

        if val > DYNAMIC_BISECTION_THRESHOLD_MAX_LIMIT:
            return DYNAMIC_BISECTION_THRESHOLD_MAX_LIMIT

        return val

    def _get_automatic_bisection_factor(self, max_row_count) -> int:
        return max_row_count // ROW_COUNT_PER_SEGMENT

    def _get_automatic_egress_limit(self, max_row_count: int) -> int:
        val = max_row_count // 10

        if val > MAX_EGRESS_LIMIT:
            return MAX_EGRESS_LIMIT

        return val

    def diff_tables(
        self,
        is_cli: bool = False,
        show_stats: bool = False,
        save_html: bool = False,
        html_path: str = "dcs_report.html",
        display_table: bool = False,
    ) -> Dict:
        view_name_source = None
        view_name_target = None
        duckb_file_location_source = None
        duckb_file_location_target = None

        try:
            self._process_duckdb_connections()
            view_name_source = self._prepare_source_table()
            view_name_target = self._prepare_target_table()

            self.table1 = self.connect_to_db_table(self.config.source, is_source=True)
            self.table2 = self.connect_to_db_table(self.config.target, is_source=False)

            table_1_sample_data = []
            table_2_sample_data = []
            db1_name = (
                self.config.source.database or self.config.source.catalog or self.config.source.project or "source"
            )
            db2_name = (
                self.config.target.database or self.config.target.catalog or self.config.target.project or "target"
            )

            columns_order_wise_src = self.config.primary_keys_source + self.config.source_columns
            columns_order_wise_target = self.config.primary_keys_target + self.config.target_columns

            src_masking_cols = self.config.source_masking_columns
            tgt_masking_cols = self.config.target_masking_columns
            masking_character = self.config.masking_character

            source_dataset = self.create_dataset_dict(
                self.config.source,
                self.table1,
                db1_name,
                self.source_file_path,
                "file" if self.config.source.driver == "duckdb" else self.config.source.driver,
            )
            target_dataset = self.create_dataset_dict(
                self.config.target,
                self.table2,
                db2_name,
                self.target_file_path,
                "file" if self.config.target.driver == "duckdb" else self.config.target.driver,
            )
            table_1_row_count = source_dataset.get("row_count", 0)
            table_2_row_count = target_dataset.get("row_count", 0)
            max_row_count = max(table_1_row_count, table_2_row_count)

            is_bisection_threshold_automatic = self.config.advanced_configuration.bisection_threshold == -1
            is_bisection_factor_automatic = self.config.advanced_configuration.bisection_factor == -1
            is_egress_limit_automatic = self.config.advanced_configuration.egress_limit == -1

            threshold = (
                self.config.advanced_configuration.bisection_threshold
                if not is_bisection_threshold_automatic
                else self._get_automatic_bisection_threshold(max_row_count)
            )

            factor = (
                self.config.advanced_configuration.bisection_factor
                if not is_bisection_factor_automatic
                else self._get_automatic_bisection_factor(max_row_count)
            )

            egress_limit = (
                self.config.advanced_configuration.egress_limit
                if not is_egress_limit_automatic
                else self._get_automatic_egress_limit(max_row_count)
            )

            self.config.advanced_configuration.bisection_threshold = max(threshold, 1000)
            self.config.advanced_configuration.bisection_factor = max(factor, 10)
            self.config.advanced_configuration.egress_limit = max(egress_limit, MIN_EGRESS_LIMIT)

            error_message = None
            is_table_empty = False
            if table_1_row_count == 0:
                error_message = f"Source table '{source_dataset.get('table_name')}' is empty"
                is_table_empty = True
            if table_2_row_count == 0:
                if error_message:
                    error_message += f" and target table '{target_dataset.get('table_name')}' is empty"
                else:
                    error_message = f"Target table '{target_dataset.get('table_name')}' is empty"
                is_table_empty = True
            if not is_table_empty and not self.config.schema_diff:
                pks_len = len(self.table1.key_columns)
                table_1_sample_data = self.table1.with_schema().get_sample_data(limit=100)
                sample_keys = [list(row[:pks_len]) for row in table_1_sample_data]
                table_2_sample_data = self.table2.with_schema().get_sample_data(limit=100, sample_keys=sample_keys)
                self.diff_iter = diff_tables(
                    self.table1,
                    self.table2,
                    algorithm=self.algorithm,
                    bisection_factor=self.config.advanced_configuration.bisection_factor,
                    bisection_threshold=self.config.advanced_configuration.bisection_threshold,
                    max_threadpool_size=self.config.advanced_configuration.max_threadpool_size,
                    strict=self.config.strict,
                    per_column_diff_limit=self.config.advanced_configuration.per_column_diff_limit,
                    egress_limit=self.config.advanced_configuration.egress_limit,
                    timeout_limit=self.config.advanced_configuration.timeout_limit,
                )

            columns_mappings = [
                {"source_column": src, "target_column": trg}
                for src, trg in zip(columns_order_wise_src, columns_order_wise_target)
            ]

            self.response = {
                "source_dataset": source_dataset,
                "target_dataset": target_dataset,
                "columns_mappings": columns_mappings,
            }

            self.process_limit(max_row_count)
            if not is_table_empty and not self.config.schema_diff:
                diff_res = differ_rows(
                    diff_iter=self.diff_iter,
                    response=self.response,
                    limit=self.limit,
                    table_limit=self.table_limit,
                    display_table=display_table,
                    similarity=self.similarity,
                    similarity_providers=self.similarity_providers,
                    fields=self.config.source_columns,
                    quick_comparison=self.config.quick_comparison,
                    src_masking_cols=src_masking_cols if src_masking_cols else [],
                    tgt_masking_cols=tgt_masking_cols if tgt_masking_cols else [],
                    masking_character=masking_character,
                )
            else:
                diff_res = {
                    "stats": {
                        "rows_A": 0,
                        "rows_B": 0,
                        "exclusive_A": 0,
                        "exclusive_B": 0,
                        "diff_pk_percent": 0,
                        "unchanged": 0,
                        "total_diff_count": 0,
                        "diff_rows_count": 0,
                        "total_duplicate_count_source": 0,
                        "total_duplicate_count_target": 0,
                        "diff_rows_percent": 0,
                        "has_differences": False,
                        "error": {},
                    },
                    "exclusive_pk_values_target": [],
                    "exclusive_pk_values_source": [],
                    "duplicate_pk_values_source": [],
                    "duplicate_pk_values_target": [],
                    "records_with_differences": [],
                    "table": None,
                }
                if is_table_empty:
                    diff_res["stats"]["has_differences"] = table_1_row_count != table_2_row_count
                    try:
                        diff_res["stats"]["diff_pk_percent"] = abs(
                            (table_1_row_count - table_2_row_count) / max(table_1_row_count, table_2_row_count)
                        )
                    except ZeroDivisionError:
                        diff_res["stats"]["diff_pk_percent"] = 0
                    diff_res["stats"]["error"] = {
                        "code": "empty_table",
                        "message": error_message,
                        "level": "WARNING",
                    }

            diff_res.setdefault("stats", {})["rows_A"] = table_1_row_count
            diff_res.setdefault("stats", {})["rows_B"] = table_2_row_count
            columns_with_unmatched_data_type, columns_not_compared, exc_to_src, exc_to_tgt = (
                calculate_column_differences(
                    source_columns=source_dataset["columns"],
                    target_columns=target_dataset["columns"],
                    columns_mappings=columns_mappings,
                )
            )

            diff_res.get("stats", {}).update(
                {
                    "identical_columns": find_identical_columns(
                        source_dataset["columns"],
                        target_dataset["columns"],
                    ),
                    "columns_with_unmatched_data_type": columns_with_unmatched_data_type,
                    "columns_not_compared": columns_not_compared,
                }
            )
            if self.config.schema_diff:
                if error_message:
                    diff_res["stats"]["error"]["level"] = "WARNING"

            source_dataset["exclusive_pk_cnt"] = diff_res.get("stats", {}).get("exclusive_A", 0)
            target_dataset["exclusive_pk_cnt"] = diff_res.get("stats", {}).get("exclusive_B", 0)
            table = diff_res.pop("table", None)
            if is_cli and display_table:
                create_table_schema_row_count(self.response, table, self.console)
                if save_html:
                    self.console.save_html(html_path, theme=theme_1, clear=True)

            duckb_file_location_source = self.config.source.filepath
            duckb_file_location_target = self.config.target.filepath
            self.config.source.filepath = self.source_file_path
            self.config.target.filepath = self.target_file_path
            if self.config.source.driver == "duckdb":
                self.config.source.driver = "file"
            if self.config.target.driver == "duckdb":
                self.config.target.driver = "file"

            self.response["source_dataset"]["duplicate_pk_cnt"] = diff_res.get("stats", {}).get(
                "total_duplicate_count_source", 0
            )
            self.response["target_dataset"]["duplicate_pk_cnt"] = diff_res.get("stats", {}).get(
                "total_duplicate_count_target", 0
            )
            self.response["source_dataset"]["null_pk_cnt"] = diff_res.get("stats", {}).get("null_pk_count_source", 0)
            self.response["target_dataset"]["null_pk_cnt"] = diff_res.get("stats", {}).get("null_pk_count_target", 0)

            self.response["source_dataset"]["pk_cnt"] = (
                self.response["source_dataset"]["row_count"]
                - self.response["source_dataset"]["duplicate_pk_cnt"]
                - self.response["source_dataset"]["null_pk_cnt"]
            )
            self.response["target_dataset"]["pk_cnt"] = (
                self.response["target_dataset"]["row_count"]
                - self.response["target_dataset"]["duplicate_pk_cnt"]
                - self.response["target_dataset"]["null_pk_cnt"]
            )
            self.response.update(diff_res)
            if show_stats:
                self.print_stats()
            table_1_stats = self.table1.query_stats
            table_2_stats = self.table2.query_stats
            for stats in [table_1_stats, table_2_stats]:
                for _, stats_dict in stats.items():
                    if isinstance(stats_dict, dict):
                        stats_dict.pop("_query_times", None)

            self.response.get("stats", {}).update(
                {
                    "source_query_stats": table_1_stats,
                    "target_query_stats": table_2_stats,
                    "comparison_tracker": diff_res.get("stats", {}).get("comparison_tracker", []),
                }
            )
            finished_at = datetime.now(tz=timezone.utc)
            end_time = time.monotonic()
            duration = end_time - self.start_time
            meta = {
                "meta": {
                    "created_at": self.created_at.isoformat(),
                    "seconds": round(duration, 2),
                    "finished_at": finished_at.isoformat(),
                    "status": "done",
                }
            }
            self.response.update(meta)
            rules_repo = RulesRepository.get_instance()
            column_transforms = rules_repo.value_rules
            schema_overrides = rules_repo.schema_rules

            # diff_res["stats"]["has_differences"] = (table_1_row_count != table_2_row_count) or diff_res["stats"].get(
            #     "total_diff_count", 0
            # ) > 0

            is_row_mismatch = table_1_row_count != table_2_row_count

            is_value_mismatch = diff_res["stats"].get("total_diff_count", 0) > 0

            is_schema_mismatch = any([len(exc_to_src) != 0, len(exc_to_tgt) != 0, columns_with_unmatched_data_type])

            diff_res["stats"]["has_differences"] = is_row_mismatch or is_value_mismatch or is_schema_mismatch
            diff_res["stats"]["is_row_count_mismatch"] = is_row_mismatch
            diff_res["stats"]["is_value_mismatch"] = is_value_mismatch
            diff_res["stats"]["is_schema_mismatch"] = is_schema_mismatch

            if not is_value_mismatch:
                table_1_sample_data = convert_to_masked_if_required(
                    table_sample_data=table_1_sample_data if table_1_sample_data else [],
                    masking_character=masking_character,
                    masking_columns=src_masking_cols if src_masking_cols else [],
                    columns_order_wise=columns_order_wise_src if columns_order_wise_src else [],
                )

                table_2_sample_data = convert_to_masked_if_required(
                    table_sample_data=table_2_sample_data if table_2_sample_data else [],
                    masking_character=masking_character,
                    masking_columns=tgt_masking_cols if tgt_masking_cols else [],
                    columns_order_wise=columns_order_wise_target if columns_order_wise_target else [],
                )

                sample_value_column_names_src = list(self.table1.key_columns) + list(self.table1.extra_columns)
                sample_value_column_names_tgt = list(self.table2.key_columns) + list(self.table2.extra_columns)
                sample_value_source_dicts = [
                    dict(zip(sample_value_column_names_src, row)) for row in table_1_sample_data
                ]
                sample_value_target_dicts = [
                    dict(zip(sample_value_column_names_tgt, row)) for row in table_2_sample_data
                ]

                def get_pk(row, key_columns):
                    return tuple(row[k] for k in key_columns)

                grouped_source = defaultdict(list)
                grouped_target = defaultdict(list)

                for row in sample_value_source_dicts:
                    grouped_source[get_pk(row, self.table1.key_columns)].append(row)

                for row in sample_value_target_dicts:
                    grouped_target[get_pk(row, self.table2.key_columns)].append(row)

                sample_values_record_list = []

                def safe_numeric_sort(keys: list[tuple[str]]) -> list[tuple[str]]:
                    def sort_key(tup):
                        key = []
                        for val in tup:
                            if isinstance(val, str) and val.isdigit():
                                key.append((0, int(val)))
                            else:
                                key.append((1, str(val)))
                        return tuple(key)

                    return sorted(keys, key=sort_key)

                sorted_pks = safe_numeric_sort(list(grouped_source.keys() | grouped_target.keys()))

                for pk in sorted_pks:
                    source_rows = grouped_source.get(pk, [])
                    target_rows = grouped_target.get(pk, [])
                    used_targets = set()
                    used_sources = set()

                    for i, src_row in enumerate(source_rows):
                        for j, tgt_row in enumerate(target_rows):
                            if j in used_targets:
                                continue
                            if src_row.values() == tgt_row.values():
                                sample_values_record_list.append(src_row)
                                sample_values_record_list.append(tgt_row)
                                used_sources.add(i)
                                used_targets.add(j)
                                break

                    def sort_key(row, key_columns, extra_columns):
                        return tuple(row[k] for k in key_columns + extra_columns if k in row)

                    remaining_sources = [row for i, row in enumerate(source_rows) if i not in used_sources]
                    remaining_targets = [row for j, row in enumerate(target_rows) if j not in used_targets]

                    remaining_sources_sorted = sorted(
                        remaining_sources,
                        key=lambda row: sort_key(row, self.table1.key_columns, self.table1.extra_columns),
                    )

                    remaining_targets_sorted = sorted(
                        remaining_targets,
                        key=lambda row: sort_key(row, self.table2.key_columns, self.table2.extra_columns),
                    )

                    for src_row, tgt_row in zip(remaining_sources_sorted, remaining_targets_sorted):
                        sample_values_record_list.append(src_row)
                        sample_values_record_list.append(tgt_row)

                self.response["sample_data_values"] = sample_values_record_list

            self.response.update({"column_transforms": column_transforms})
            self.response.update({"schema_overrides": schema_overrides})

            return self.response
        except Exception as e:
            logger.exception(f"Error during diff_tables: {e}")
            raise
        finally:
            self.drop_view_and_close_connection(view_name_source, view_name_target)
            self.cleanup_duckdb(
                src=duckb_file_location_source,
                target=duckb_file_location_target,
            )
            logger.info("Dropped views and closed database connections")

    def process_limit(self, max_row_count):
        if isinstance(self.limit, int):
            if self.limit > max_row_count:
                self.limit = max_row_count
                logger.info(f"Limit exceeds max row count, adjusted to {max_row_count}")
            return

        if isinstance(self.limit, str):
            if "%" in self.limit:
                cleaned_limit = self.limit.replace("%", "").strip()
                if cleaned_limit.isdigit():
                    percentage = float(cleaned_limit)
                    if percentage > 100:
                        self.limit = max_row_count
                        logger.info("Percentage exceeds 100%, set limit to maximum row count")
                    else:
                        calc_limit = int((percentage / 100) * max_row_count)
                        self.limit = max(1, int(calc_limit))
                        logger.info(f"Limit set to {self.limit} ({percentage}% of {max_row_count})")
                else:
                    self.limit = self.default_limit
                    logger.warning(
                        f"Invalid percentage format '{self.limit}', using default limit: {self.default_limit}"
                    )
            else:
                self.limit = self.default_limit
                logger.warning(f"Invalid limit format '{self.limit}', using default limit: {self.default_limit}")

    def drop_view_and_close_connection(self, view_name_source, view_name_target):

        def safe_close(db_connection):
            if db_connection:
                with suppress(Exception):
                    db_connection.close()

        safe_close(self.table1.database)
        safe_close(self.table2.database)

        if self.source_db:
            self.source_db.drop_view_from_db(
                view_name=view_name_source,
                schema=self.config.temporary_schema_source,
            )
        if self.target_db:
            self.target_db.drop_view_from_db(
                view_name=view_name_target,
                schema=self.config.temporary_schema_target,
            )

        safe_close(self.source_db)
        safe_close(self.target_db)

    def cleanup_duckdb(self, src: str, target: str):
        if src and src.endswith("duckdb"):
            with suppress(Exception):
                os.remove(src)
        if target and target.endswith("duckdb"):
            with suppress(Exception):
                os.remove(target)

    def print_stats(self):
        try:
            stats = self.response.get("stats", {})
            output = ""
            if stats:
                if self.config.quick_comparison:
                    output += f"Quick comparison: {self.config.quick_comparison}\n"
                    output += f"Has differences {stats.get('has_differences', False)}\n"
                else:
                    output += f"{stats.get('exclusive_A', 0)} rows are exclusive to source\n"
                    output += f"{stats.get('exclusive_B', 0)} rows are exclusive to target\n"
                    output += f"{stats.get('total_duplicate_count_source', 0)} duplicate rows in source\n"
                    output += f"{stats.get('total_duplicate_count_target', 0)} duplicate rows in target\n"
                    # output += f"{stats.get('total_diff_count', 0)} rows are different\n"
                    # output += f"{stats.get('diff_rows_count', 0)} rows are different\n"
                    for k, v in stats.get("values", {}).items():
                        output += f"{v} rows with different values in column: {k}\n"
                    # output += f"{round((stats.get('diff_pk_percent', 0) * 100),3)}% of primary keys are different\n"
                    # output += f"{round((stats.get('diff_rows_percent', 0) * 100),3)}% of rows are different\n"
                print(output)
        except Exception as e:
            logger.exception(f"Error in printing stats: {e}")

    def slice_rows(self, rows, start, end):
        return rows[start:end]


def diff_db_tables(
    config: Comparison,
    is_cli: bool = False,
    show_stats: bool = False,
    save_html: bool = False,
    html_path: str = "dcs_report.html",
    display_table: bool = False,
) -> Dict:
    differ = DBTableDiffer(config)
    response = differ.diff_tables(
        is_cli=is_cli,
        show_stats=show_stats,
        save_html=save_html,
        html_path=html_path,
        display_table=display_table,
    )
    response["comparison_name"] = config.comparison_name
    configuration = config.model_dump()
    del configuration["source"]["id"]
    del configuration["target"]["id"]
    configuration["source"]["schema_name"] = response["source_dataset"]["schema"]
    configuration["target"]["schema_name"] = response["target_dataset"]["schema"]
    response["configuration"] = configuration
    if is_cli:
        response["configuration"]["source"] = obfuscate_sensitive_data(response["configuration"]["source"])
        response["configuration"]["target"] = obfuscate_sensitive_data(response["configuration"]["target"])
    return response
