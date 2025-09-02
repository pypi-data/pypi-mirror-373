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

import multiprocessing
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Union

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from dcs_sdk.sdk.rules.rules_repository import RulesRepository
from dcs_sdk.sdk.utils.utils import apply_custom_masking, apply_masking


def create_legend():
    legend = Table(show_header=False, box=None)
    legend.add_column(style="bold")
    legend.add_column()
    legend.add_row("Red", "Mismatch", style="red")
    legend.add_row("Cyan", "Match", style="cyan")
    legend.add_row("Yellow", "Duplicate", style="yellow")
    return Panel(legend, title="Info", border_style="cyan bold", width=80)


def create_schema_table(response, console, is_source=True):
    key = "source_dataset" if is_source else "target_dataset"
    columns = response[key]["columns"]
    title = f"Schema: {response[key]['database']}.{response[key]['schema']}.{response[key]['table_name']}"
    mapped_columns = response["columns_mappings"]
    other_columns = response["target_dataset"]["columns"] if is_source else response["source_dataset"]["columns"]
    rules_repo = RulesRepository.get_instance()

    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("#")
    table.add_column("Column Name", style="cyan")
    table.add_column("Data Type", style="magenta")
    table.add_column("Reason", style="red")

    for index, col in enumerate(columns, start=1):
        name = col["column_name"]
        data_type = col["data_type"]
        max_length = col.get("character_maximum_length", None)

        mapped_col = next(
            (
                m["target_column"] if is_source else m["source_column"]
                for m in mapped_columns
                if m["source_column" if is_source else "target_column"] == name
            ),
            None,
        )

        other_col = next((c for c in other_columns if c["column_name"] == (mapped_col or name)), None)

        mismatch_reason = ""
        if other_col:
            match, reason = rules_repo.apply_schema_rules(
                src_col=col,
                tgt_col=other_col,
            )

            if not match:
                mismatch_reason = reason or ("Exclusive to source" if is_source else "Exclusive to target")
        else:
            mismatch_reason = "Exclusive to source" if is_source else "Exclusive to target"

        data_type_with_max_len = f"{data_type} {('('+ str(max_length) + ')') if max_length is not None else ''}"
        if mismatch_reason:
            table.add_row(
                str(index),
                Text(name, style="red"),
                Text(data_type_with_max_len, style="red"),
                mismatch_reason,
            )
        else:
            table.add_row(str(index), name, data_type_with_max_len, Text("-", style="green", justify="left"))
        col["mismatch_reason"] = mismatch_reason
    console.print(table)


def create_table_schema_row_count(response, row_diff_table, console):
    source_dataset = response["source_dataset"]
    target_dataset = response["target_dataset"]

    console.print(create_legend())
    table_row_counts = Table(title="Row Counts", show_header=True, header_style="bold magenta")
    table_row_counts.add_column("")
    table_row_counts.add_column(
        f"{source_dataset['database']}.{source_dataset['schema']}.{source_dataset['table_name']}",
        style="cyan",
    )
    table_row_counts.add_column(
        f"{target_dataset['database']}.{target_dataset['schema']}.{target_dataset['table_name']}",
        style="yellow",
    )
    table_row_counts.add_row(
        "Row Count",
        str(source_dataset["row_count"]),
        str(target_dataset["row_count"]),
    )
    console.print(table_row_counts)

    create_schema_table(response, console, is_source=True)
    create_schema_table(response, console, is_source=False)

    if row_diff_table is not None:
        console.print(row_diff_table)


def process_batch(
    batch: List[Dict[str, Any]],
    provider_class,
    primary_keys,
    fields,
    similarity,
    src_masking_cols: List[str],
    tgt_masking_cols: List[str],
    masking_character: str,
) -> List[Dict[str, Any]]:
    if not provider_class or len(batch) < 2:
        return batch

    provider = provider_class()
    batch_size = len(batch)
    i = 0
    while i < batch_size - 1:
        provider.add_text_similarity(
            data=batch[i : i + 2],
            key=primary_keys,
            fields=fields,
            similarity=similarity,
            source_masking_cols=src_masking_cols,
            target_masking_cols=tgt_masking_cols,
            mask_char=masking_character,
        )
        i += 2

    return batch


def differ_rows(
    diff_iter,
    response,
    src_masking_cols: List[str],
    tgt_masking_cols: List[str],
    masking_character: str,
    limit: int | None = None,
    table_limit: int = 100,
    display_table: bool = False,
    similarity=None,
    similarity_providers=None,
    fields=None,
    batch_size: int = 2_000,
    max_workers: int = max(1, multiprocessing.cpu_count() - 2),
    quick_comparison: bool = False,
):
    if quick_comparison:
        try:
            next(iter(diff_iter))
            return {
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
                    "has_differences": True,
                },
                "exclusive_pk_values_target": [],
                "exclusive_pk_values_source": [],
                "duplicate_pk_values_source": [],
                "duplicate_pk_values_target": [],
                "records_with_differences": [],
                "table": None,
            }
        except StopIteration:
            return {
                "stats": {"has_differences": False},
                "exclusive_pk_values_target": [],
                "exclusive_pk_values_source": [],
                "duplicate_pk_values_source": [],
                "duplicate_pk_values_target": [],
                "records_with_differences": [],
                "table": None,
            }
    stats = diff_iter.get_stats_dict()
    exclusive_source_set = set(stats["exclusive_source_ids"])
    exclusive_target_set = set(stats["exclusive_target_ids"])
    diff_values_set = set(stats["diff_values_ids"])
    source_duplicates = set(stats["duplicate_source_ids"])
    target_duplicates = set(stats["duplicate_target_ids"])
    pk_key_cols = response["source_dataset"]["primary_keys"]

    exclusive_to_source = []
    exclusive_to_target = []
    duplicates_in_source = []
    duplicates_in_target = []

    seen_ex_source = set()
    seen_ex_target = set()

    diff_pks_to_collect = set(diff_values_set) if limit is None else set(list(diff_values_set)[:limit])
    diff_records_dict = {}

    total_source_duplicates = 0
    total_target_duplicates = 0
    table_data = []
    table = None

    for diff in diff_iter:
        sign, rows = diff
        obj = {"meta": {"origin": "source" if sign == "-" else "target", "sign": sign}}
        column_values = {}

        for idx, col_ in enumerate(rows):
            column_name = response["columns_mappings"][idx]["source_column"]
            obj[column_name] = col_
            column_values[column_name] = col_

        if len(table_data) < table_limit:
            table_data.append(obj)
        pk_value = tuple(column_values[col] for col in pk_key_cols)

        if sign == "-" and pk_value in exclusive_source_set:
            if pk_value not in seen_ex_source and (limit is None or len(exclusive_to_source) < limit):
                masked_obj = apply_masking(obj, src_masking_cols, masking_character)
                exclusive_to_source.append(masked_obj)
                seen_ex_source.add(pk_value)

        if sign == "+" and pk_value in exclusive_target_set:
            if pk_value not in seen_ex_target and (limit is None or len(exclusive_to_target) < limit):
                masked_obj = apply_masking(obj, tgt_masking_cols, masking_character)
                exclusive_to_target.append(masked_obj)
                seen_ex_target.add(pk_value)

        if sign == "-" and pk_value in source_duplicates:
            total_source_duplicates += 1
            if limit is None or len(duplicates_in_source) < limit:
                masked_obj = apply_masking(obj, src_masking_cols, masking_character)
                duplicates_in_source.append(masked_obj)

        if sign == "+" and pk_value in target_duplicates:
            total_target_duplicates += 1
            if limit is None or len(duplicates_in_target) < limit:
                masked_obj = apply_masking(obj, tgt_masking_cols, masking_character)
                duplicates_in_target.append(masked_obj)

        if pk_value in diff_pks_to_collect:
            if pk_value not in diff_records_dict:
                diff_records_dict[pk_value] = []
            if limit is None or len(diff_records_dict[pk_value]) < 2:
                diff_records_dict[pk_value].append(obj.copy())

    def sort_by_pk(obj):
        sort_key = []
        for col in pk_key_cols:
            pk_value = obj[col]
            try:
                sort_key.append((0, int(pk_value)))
            except (ValueError, TypeError):
                sort_key.append((1, str(pk_value)))
        return tuple(sort_key)

    try:
        exclusive_to_source.sort(key=sort_by_pk)
        exclusive_to_target.sort(key=sort_by_pk)
        duplicates_in_source.sort(key=sort_by_pk)
        duplicates_in_target.sort(key=sort_by_pk)
    except:
        pass

    records_with_differences = []
    masked_records = []

    for pk_value, records in diff_records_dict.items():
        records.sort(key=lambda x: x["meta"]["sign"], reverse=True)
        if not similarity:
            if len(records) == 2:
                source = records[0]
                target = records[1]

                masked_src, masked_tgt = apply_custom_masking(
                    source=source,
                    target=target,
                    source_masking_cols=src_masking_cols,
                    target_masking_cols=tgt_masking_cols,
                    mask_char=masking_character,
                )

                masked_record = [masked_src, masked_tgt]
                masked_records.extend(masked_record)
        else:
            masked_records.extend(records)

    records_with_differences.extend(masked_records)

    provider_class = None
    primary_keys = response["source_dataset"]["primary_keys"]
    if similarity and similarity_providers and fields and primary_keys:
        provider_class = similarity_providers.get(similarity.similarity_method.lower())
        if not provider_class:
            print(f"Unknown similarity method: {similarity.similarity_method}")

    if provider_class:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            effective_batch_size = min(batch_size, len(records_with_differences))
            effective_batch_size = effective_batch_size if effective_batch_size % 2 == 0 else effective_batch_size - 1
            if effective_batch_size < 2:
                effective_batch_size = 2
            batches = [
                records_with_differences[i : i + effective_batch_size]
                for i in range(0, len(records_with_differences), effective_batch_size)
            ]
            futures = [
                executor.submit(
                    process_batch,
                    batch,
                    provider_class,
                    primary_keys,
                    fields,
                    similarity,
                    src_masking_cols,
                    tgt_masking_cols,
                    masking_character,
                )
                for batch in batches
            ]
            i = 0
            for future in as_completed(futures):
                try:
                    result = future.result()
                    records_with_differences[i : i + len(result)] = result
                    i += len(result)
                except Exception as e:
                    print(f"Error in batch processing: {str(e)}")

        try:
            records_with_differences.sort(key=sort_by_pk)
        except:
            pass

    stats["total_diff_count"] = len(diff_values_set) + len(exclusive_source_set) + len(exclusive_target_set)
    stats["diff_rows_count"] = len(diff_values_set)
    stats.pop("exclusive_source_ids", None)
    stats.pop("exclusive_target_ids", None)
    stats.pop("diff_values_ids", None)
    stats.pop("duplicate_source_ids", None)
    stats.pop("duplicate_target_ids", None)
    stats["total_duplicate_count_source"] = total_source_duplicates
    stats["total_duplicate_count_target"] = total_target_duplicates
    try:
        diff_rows_percent = stats.get("diff_rows_count", 0) / (
            stats.get("diff_rows_count", 0) + stats.get("unchanged", 0)
        )
        diff_rows_percent = abs(diff_rows_percent)
    except ZeroDivisionError:
        diff_rows_percent = 0.0
    stats["diff_pk_percent"] = min(stats.get("diff_pk_percent", 0), 1)
    stats["diff_rows_percent"] = diff_rows_percent
    has_differences = diff_rows_percent != 0 or stats["diff_pk_percent"] != 0
    stats["has_differences"] = has_differences
    stats["source_masked_columns"] = src_masking_cols
    stats["target_masked_columns"] = tgt_masking_cols

    if display_table:
        table = create_table_diff_rows(table_data, primary_keys, response["columns_mappings"], 100)

    return {
        "exclusive_pk_values_target": exclusive_to_target,
        "exclusive_pk_values_source": exclusive_to_source,
        "duplicate_pk_values_source": duplicates_in_source,
        "duplicate_pk_values_target": duplicates_in_target,
        "records_with_differences": records_with_differences,
        "stats": stats,
        "table": table,
    }


def create_table_diff_rows(data, primary_keys: Union[str, list[str]], columns_mappings, limit: int = 100):
    table = Table(title="Diff Rows", show_header=True, header_style="bold magenta")
    column_mapping_dict = {mapping["source_column"]: mapping["target_column"] for mapping in columns_mappings}

    table.add_column("#")
    table.add_column("Origin")
    for mapping in columns_mappings:
        source_col = mapping["source_column"]
        target_col = mapping["target_column"]
        if source_col == target_col:
            table.add_column(source_col, style="cyan")
        else:
            table.add_column(f"{target_col}/{source_col}", style="cyan")

    if isinstance(primary_keys, str):
        primary_keys = [primary_keys]

    def get_composite_key(row):
        return tuple(row[key] for key in primary_keys)

    records = defaultdict(lambda: defaultdict(list))
    for row in data:
        composite_key = get_composite_key(row)
        origin = row["meta"]["origin"]
        records[composite_key][origin].append(row)

    previous_composite_key = None
    serial_number = 0
    unique_keys_processed = set()
    for row in data:
        composite_key = get_composite_key(row)
        if composite_key not in unique_keys_processed:
            if len(unique_keys_processed) >= limit:
                break
            serial_number += 1
        meta_values = row["meta"]
        row_values = {key: row[key] for key in column_mapping_dict.keys()}
        origin = meta_values["origin"]
        has_duplicates = any(len(records[composite_key][orig]) > 1 for orig in records[composite_key])

        mismatched_columns = set()
        if not has_duplicates:
            source_count = len(records[composite_key]["source"])
            target_count = len(records[composite_key]["target"])
            if source_count == 1 and target_count == 1:
                source_row = records[composite_key]["source"][0]
                target_row = records[composite_key]["target"][0]
                if origin == "target":
                    for col in column_mapping_dict.keys():
                        if source_row[col] != target_row[col]:
                            mismatched_columns.add(col)

        formatted_cells = [Text(str(serial_number))]
        for col in meta_values:
            if col != "sign":
                formatted_cells.append(
                    Text(
                        str(meta_values[col]),
                        style=f"{'chartreuse2' if meta_values['origin'] == 'source' else 'cyan3'}",
                    )
                )

        for col in column_mapping_dict.keys():
            cell_value = row_values[col]
            if has_duplicates:
                formatted_cells.append(Text(str(cell_value), style="yellow bold"))
            elif col in mismatched_columns:
                formatted_cells.append(Text(str(cell_value), style="red bold"))
            else:
                formatted_cells.append(Text(str(cell_value)))

        if previous_composite_key is not None and previous_composite_key != composite_key:
            table.add_section()

        table.add_row(*formatted_cells)
        previous_composite_key = composite_key
        unique_keys_processed.add(composite_key)
    return table
