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
import uuid
from typing import List, Optional, Union

import duckdb
import requests

from dcs_sdk.sdk.config.config_loader import Comparison
from dcs_sdk.sdk.rules.rules_repository import RulesRepository


def generate_table_name(file_path, is_table: bool = True):
    base_name = os.path.basename(file_path)
    if is_table:
        table_name = os.path.splitext(base_name)[0]
    else:
        table_name = base_name
    return table_name


def calculate_column_differences(source_columns, target_columns, columns_mappings):
    rules_repo = RulesRepository.get_instance()
    columns_with_unmatched_data_type = []
    columns_not_compared = []
    processed_cols = set()

    source_column_dict = {col["column_name"]: col for col in source_columns}
    target_column_dict = {col["column_name"]: col for col in target_columns}

    mapped_source_columns = {mapping["source_column"] for mapping in columns_mappings}
    mapped_target_columns = {mapping["target_column"] for mapping in columns_mappings}

    for mapping in columns_mappings:
        source_col_name = mapping["source_column"]
        target_col_name = mapping["target_column"]

        processed_cols.add(source_col_name)
        processed_cols.add(target_col_name)

        source_col = source_column_dict[source_col_name]
        target_col = target_column_dict[target_col_name]
        match, reason = rules_repo.apply_schema_rules(src_col=source_col, tgt_col=target_col)
        if not match:
            columns_with_unmatched_data_type.append(
                {
                    "source": {
                        "column_name": source_col_name,
                        "data_type": source_col["data_type"],
                        "character_maximum_length": source_col.get("character_maximum_length"),
                        "mismatch_reason": reason,
                    },
                    "target": {
                        "column_name": target_col_name,
                        "data_type": target_col["data_type"],
                        "character_maximum_length": target_col.get("character_maximum_length"),
                        "mismatch_reason": reason,
                    },
                }
            )

    # Check auto-matched common columns not in mapping
    common_column_names = set(source_column_dict.keys()) & set(target_column_dict.keys())

    for col_name in common_column_names:
        if col_name in mapped_source_columns or col_name in mapped_target_columns:
            continue

        source_col = source_column_dict[col_name]
        target_col = target_column_dict[col_name]
        processed_cols.add(col_name)

        match, reason = rules_repo.apply_schema_rules(src_col=source_col, tgt_col=target_col)
        if not match:
            columns_with_unmatched_data_type.append(
                {
                    "source": {
                        "column_name": col_name,
                        "data_type": source_col["data_type"],
                        "character_maximum_length": source_col.get("character_maximum_length"),
                        "mismatch_reason": reason,
                    },
                    "target": {
                        "column_name": col_name,
                        "data_type": target_col["data_type"],
                        "character_maximum_length": target_col.get("character_maximum_length"),
                        "mismatch_reason": reason,
                    },
                }
            )

    for source_col_name in source_column_dict:
        if source_col_name not in mapped_source_columns:
            columns_not_compared.append(
                {
                    "column_name": source_col_name,
                    "data_type": source_column_dict[source_col_name]["data_type"],
                    "origin": "source",
                }
            )

    for target_col_name in target_column_dict:
        if target_col_name not in mapped_target_columns:
            columns_not_compared.append(
                {
                    "column_name": target_col_name,
                    "data_type": target_column_dict[target_col_name]["data_type"],
                    "origin": "target",
                }
            )

    source_col_names = set(source_column_dict.keys())
    target_col_names = set(target_column_dict.keys())

    exclusive_to_source = source_col_names - processed_cols
    exclusive_to_target = target_col_names - processed_cols

    return (
        columns_with_unmatched_data_type,
        columns_not_compared,
        exclusive_to_source,
        exclusive_to_target,
    )


def duck_db_load_csv_to_table(config: Comparison, path, is_source: bool = False) -> bool:
    dir_name = "tmp"
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    csv_files = glob.glob(path)

    if is_source:
        pk_cols = config.primary_keys_source
    else:
        pk_cols = config.primary_keys_target

    duck_db_file_name = f"{dir_name}/{uuid.uuid4()}.duckdb"
    create_view = False
    query = None
    table_name = None
    if is_source and config.source_query:
        create_view = True
        query = config.source_query
    elif not is_source and config.target_query:
        create_view = True
        query = config.target_query

    for csv_file in csv_files:
        try:
            table_name = generate_table_name(csv_file)
            conn = duckdb.connect(database=duck_db_file_name, read_only=False)
            conn.execute(
                """
                    CREATE OR REPLACE TABLE {} AS SELECT * FROM read_csv('{}',HEADER=True, UNION_BY_NAME=True, nullstr='NULL', all_varchar=True, IGNORE_ERRORS=TRUE);
                    """.format(
                    table_name, csv_file
                )
            )

            if pk_cols and len(pk_cols) > 0:
                pk_cols_str = ", ".join(pk_cols)
                conn.execute(
                    """
                    CREATE INDEX idx_{} ON {} ({});
                    """.format(
                        table_name,
                        table_name,
                        pk_cols_str,
                    )
                )

            if create_view:
                table_name = f"{table_name}_query"
                conn.execute(
                    """
                    CREATE VIEW {} AS {};
                    """.format(
                        table_name, query
                    )
                )
            conn.close()
        except Exception as e:
            print(f"Error in loading CSV to DuckDB: {e}")
            return False

    if is_source:
        config.source.filepath = duck_db_file_name
        config.source.table = table_name
    else:
        config.target.filepath = duck_db_file_name
        config.target.table = table_name
    return True


def find_identical_columns(source, target):
    identical_columns = []
    rules_repo = RulesRepository.get_instance()

    for s_col in source:
        for t_col in target:
            if s_col["column_name"] != t_col["column_name"]:
                continue

            match, reason = rules_repo.apply_schema_rules(src_col=s_col, tgt_col=t_col)
            if match:
                identical_columns.append(
                    {
                        "column_name": s_col["column_name"],
                        "data_type": s_col["data_type"],
                        "character_maximum_length": s_col.get("character_maximum_length"),
                    }
                )

    return identical_columns


def post_comparison_results(comparison_data, url, is_cli=True):
    try:
        comparison_data["is_cli"] = is_cli
        response = requests.post(url, json=comparison_data)
        try:
            print(response.json())
        except Exception as e:
            print(f"Error in parsing response: {e}")
        if response.ok:
            print(f"Comparison results posted successfully")
    except Exception as e:
        print(f"Error in posting comparison results: {e}")


def _obfuscate_value(value: Optional[Union[str, int]]) -> Optional[str]:
    if not value or not isinstance(value, (str, int)):
        return value

    str_value = str(value)[:10]
    if len(str_value) > 2:
        return str_value[0] + "*" * (len(str_value) - 2) + str_value[-1]
    return "*" * len(str_value)


def obfuscate_sensitive_data(configuration: dict) -> dict:
    sensitive_keys = {
        "role",
        "account",
        "username",
        "password",
        "http_path",
        "access_token",
        "host",
        "port",
        "server",
        "keyfile",
        "bigquery_credentials",
    }
    return {key: _obfuscate_value(value) if key in sensitive_keys else value for key, value in configuration.items()}


def apply_masking(obj: dict, masking_columns: List[str], mask_char: str = "*") -> dict:
    masked_obj = obj.copy()
    for col in masking_columns:
        if col in masked_obj and masked_obj[col] is not None:
            masked_obj[col] = mask_char * len(str(masked_obj[col]))
    return masked_obj


def safe_str(value) -> str:
    """Safely convert value to string, handling None and exceptions"""
    if value is None:
        return None
    try:
        return str(value)
    except Exception:
        return "[unconvertible_value]"


def apply_custom_masking(
    source: Optional[dict],
    target: Optional[dict],
    source_masking_cols: List[str],
    target_masking_cols: List[str],
    mask_char: str = "*",
):
    source = source or {}
    target = target or {}
    masked_source = source.copy()
    masked_target = target.copy()

    common_masking_cols = set(source_masking_cols).intersection(set(target_masking_cols))

    # common masking columns
    for col in common_masking_cols:
        src_val = str(source.get(col, ""))
        tgt_val = str(target.get(col, ""))

        src_len, tgt_len = len(src_val), len(tgt_val)
        if src_len == tgt_len and src_val != tgt_val:
            masked_source[col] = mask_char * (src_len + 1)
            masked_target[col] = mask_char * tgt_len
        else:
            masked_source[col] = mask_char * src_len
            masked_target[col] = mask_char * tgt_len

    # Non-common columns
    for col in source_masking_cols:
        if col not in common_masking_cols:
            val = source.get(col, "")
            masked_source[col] = mask_char * len(val)

    for col in target_masking_cols:
        if col not in common_masking_cols:
            val = target.get(col, "")
            masked_target[col] = mask_char * len(val)

    return masked_source, masked_target


def convert_to_masked_if_required(
    table_sample_data: list, masking_character: str, masking_columns: list, columns_order_wise: list
):
    idxs_to_mask = []
    for i, val in enumerate(columns_order_wise):
        if val in masking_columns:
            idxs_to_mask.append(i)

    new_table_sample_data = []
    for row in table_sample_data:
        curr_sample_row = []
        for i, val in enumerate(row):
            if i in idxs_to_mask:
                curr_sample_row.append(masking_character * len(str(val)))
            else:
                curr_sample_row.append(val)
        new_table_sample_data.append(tuple(curr_sample_row))

    return new_table_sample_data
