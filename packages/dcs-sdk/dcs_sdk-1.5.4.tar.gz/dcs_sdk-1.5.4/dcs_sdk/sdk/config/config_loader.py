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

import os
import uuid
from typing import Dict, List, Literal, Optional, Union

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel

from dcs_sdk.sdk.rules import RulesRepository


class InvalidUUIDError(ValueError):
    pass


class MissingRequiredFieldError(ValueError):
    pass


class InvalidConnectionTypeError(ValueError):
    pass


class InvalidSimilarityMethodError(ValueError):
    pass


class SourceTargetConnection(BaseModel):
    id: Optional[Union[str, None]] = None
    name: str
    workspace: Optional[str] = "default"
    host: Optional[str] = None
    port: Optional[Union[int, str]] = None
    driver: str
    table: Optional[str] = None
    database: Optional[str] = None
    filepath: Optional[str] = None
    catalog: Optional[str] = None
    schema_name: Optional[str] = None
    warehouse: Optional[str] = None
    role: Optional[str] = None
    account: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    http_path: Optional[str] = None
    access_token: Optional[str] = None
    odbc_driver: Optional[str] = None
    server: Optional[str] = None
    project: Optional[str] = None  # bigquery specific
    dataset: Optional[str] = None  # bigquery specific
    keyfile: Optional[str] = None  # bigquery specific
    impersonate_service_account: Optional[str] = None  # bigquery specific
    bigquery_credentials: Optional[str] = None  # bigquery specific
    transform_columns: Dict[str, str] | None = None


class SimilarityConfig(BaseModel):
    pre_processing: List[str]
    similarity_method: str
    threshold: float


class DiffAdvancedConfig(BaseModel):
    bisection_factor: int = 10
    bisection_threshold: int = 50_000
    max_threadpool_size: int = 2
    egress_limit: int = 5_00_000
    per_column_diff_limit: int = 100
    timeout_limit: int = 60 * 5  # minutes


class Comparison(BaseModel):
    comparison_name: str
    source: SourceTargetConnection
    target: SourceTargetConnection
    source_columns: Optional[List[str]] = None
    target_columns: Optional[List[str]] = None
    primary_keys_source: List[str] = []
    primary_keys_target: List[str] = []
    source_filter: Optional[str] = None
    target_filter: Optional[str] = None
    source_query: Optional[str] = None
    target_query: Optional[str] = None
    temporary_schema_source: Optional[str] = None
    temporary_schema_target: Optional[str] = None
    similarity: Optional[SimilarityConfig] = None
    view_name_source: Optional[str] = None
    view_name_target: Optional[str] = None
    advanced_configuration: DiffAdvancedConfig
    limit: Union[int, None, str] = "10%"
    strict: bool = True  # Used for strict comparison with matching column data types
    quick_comparison: bool = False  # Used for quick overview of the comparison
    source_masking_columns: Optional[List[str]] = None
    target_masking_columns: Optional[List[str]] = None
    masking_character: str = "*"
    schema_diff: bool = False  # Used for schema diff


class EnvYamlLoader(yaml.SafeLoader):
    """YAML Loader with `!ENV` constructor."""

    def __init__(self, stream):
        super(EnvYamlLoader, self).__init__(stream)
        self.add_constructor("!ENV", self.env_constructor)

    @classmethod
    def env_constructor(cls, loader, node):
        value = loader.construct_scalar(node)
        env_var = value.strip("${} ")
        return os.environ.get(env_var, "")


class DataDiffConfig:
    DRIVER_MAP = {
        "file": "duckdb",
        "duckdb": "duckdb",
        "postgres": "postgres",
        "postgresql": "postgres",
        "snowflake": "snowflake",
        "trino": "trino",
        "databricks": "databricks",
        "oracle": "oracle",
        "mssql": "mssql",
        "mysql": "mysql",
        "sybase": "sybase",
        "bigquery": "bigquery",
    }

    def __init__(
        self,
        yaml_file_path: Optional[str] = None,
        yaml_string: Optional[str] = None,
        config_json: Optional[dict] = None,
    ):
        load_dotenv()
        if yaml_file_path:
            self.data = self.read_yaml_file(yaml_file_path)
        elif yaml_string:
            self.data = self.read_yaml_string(yaml_string)
        elif config_json:
            self.data = config_json
        else:
            raise ValueError("No configuration provided")
        self.rules_repo = RulesRepository.get_instance()

    @staticmethod
    def read_yaml_file(file_path: str) -> dict:
        with open(file_path, "r") as file:
            return yaml.load(file, Loader=EnvYamlLoader)

    @staticmethod
    def read_yaml_string(yaml_string: str) -> dict:
        return yaml.load(yaml_string, Loader=EnvYamlLoader)

    @staticmethod
    def is_valid_uuid(val: str) -> bool:
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False

    def validate_uuid(self, uuid_str: str | None, field_name: str) -> None:
        if uuid_str is not None and not self.is_valid_uuid(uuid_str):
            raise InvalidUUIDError(f"{field_name} is not a valid UUID")

    @staticmethod
    def validate_required_field(value: Union[str, None], field_name: str, source_name: str) -> None:
        if value is None:
            raise MissingRequiredFieldError(f"{field_name} is required for datasource {source_name}")

    @staticmethod
    def validate_file_connection(connection: dict) -> None:
        if connection.get("type") == "file" and connection.get("filepath") is None:
            raise MissingRequiredFieldError("file path is required for file connection")

    @staticmethod
    def validate_databricks_connection(connection: dict) -> None:
        if connection.get("type") == "databricks":
            if connection.get("connection", {}).get("http_path") is None:
                raise MissingRequiredFieldError("http_path is required for databricks connection")
            if connection.get("connection", {}).get("access_token") is None:
                raise MissingRequiredFieldError("access_token is required for databricks connection")

    @staticmethod
    def validate_host_or_server(connection: dict) -> None:
        if connection.get("type") == "sybase":
            if not connection.get("connection", {}).get("host") and not connection.get("connection", {}).get("server"):
                raise MissingRequiredFieldError("host or server is required for connection")

    @staticmethod
    def validate_comparison_by_query(
        comparison_data: dict,
        field_name: Literal["source", "target"],
        temporary_schema: str | None,
        database_type: str,
        view_name: str | None,
    ) -> None:
        if comparison_data.get(field_name, {}).get("query") is not None:
            if comparison_data.get(field_name, {}).get("table") is not None:
                raise ValueError(f"table and query cannot be used together in {field_name} connection")
            if comparison_data.get(field_name, {}).get("filter") is not None:
                raise ValueError(f"filter and query cannot be used together in {field_name} connection")
            if database_type in ["file", "oracle"]:
                return
            if temporary_schema is None:
                raise ValueError("temporary_schema is required for query based comparison")
            if view_name is not None and len(view_name.split(".")) > 1:
                raise ValueError("view_name should not contain schema name")

    @staticmethod
    def validate_similarity_threshold(threshold: float) -> None:
        if threshold is None:
            raise MissingRequiredFieldError("threshold is required for similarity")
        if not 0 <= threshold <= 1:
            raise ValueError("Similarity threshold must be between 0 and 1")
        return threshold

    def get_driver(self, connection: dict) -> str:
        connection_type = connection.get("type")
        if connection_type not in self.DRIVER_MAP:
            raise InvalidConnectionTypeError(f"Invalid connection type: {connection_type}")
        return self.DRIVER_MAP[connection_type]

    def get_similarity_method(self, similarity_method: str) -> str:
        if similarity_method is None:
            raise MissingRequiredFieldError("similarity_method is required for similarity")
        similarity_methods = ["jaccard", "cosine", "levenshtein"]
        if similarity_method not in similarity_methods:
            raise InvalidSimilarityMethodError(f"Invalid similarity method: {similarity_method}")
        return similarity_method

    def get_pre_processing_methods(self, pre_processing: List[str]) -> List[str]:
        if pre_processing is None:
            raise MissingRequiredFieldError("pre_processing is required for similarity")
        pre_processing_methods = ["lower_case", "remove_punctuation", "remove_stop_words", "remove_extra_whitespaces"]
        for method in pre_processing:
            if method not in pre_processing_methods:
                raise ValueError(f"Invalid pre_processing method: {method}")
        return pre_processing

    def create_connection_config(
        self,
        connection: dict,
        comparison_data: dict,
        is_source: bool,
        temporary_schema: str | None,
        view_name: str | None,
        transform_columns: Dict[str, str] | None = None,
    ) -> dict:
        self.validate_uuid(connection.get("id", None), "Datasource id")
        self.validate_required_field(connection.get("name"), "connection name", source_name=connection.get("name"))
        self.validate_required_field(connection.get("type"), "connection type", source_name=connection.get("name"))
        self.validate_file_connection(connection)
        self.validate_databricks_connection(connection)
        self.validate_host_or_server(connection)
        self.validate_comparison_by_query(
            comparison_data,
            "source" if is_source else "target",
            temporary_schema,
            connection.get("type"),
            view_name,
        )

        driver = self.get_driver(connection)

        return {
            "id": connection.get("id", None),
            "name": connection.get("name"),
            "workspace": connection.get("workspace", "default"),
            "host": connection.get("connection", {}).get("host", ""),
            "port": connection.get("connection", {}).get("port", None),
            "account": connection.get("connection", {}).get("account"),
            "warehouse": connection.get("connection", {}).get("warehouse"),
            "role": connection.get("connection", {}).get("role"),
            "driver": driver,
            "table": comparison_data.get("source" if is_source else "target", {}).get("table"),
            "database": connection.get("connection", {}).get("database"),
            "catalog": connection.get("connection", {}).get("catalog"),
            "schema_name": connection.get("connection", {}).get("schema"),
            "username": connection.get("connection", {}).get("username"),
            "password": connection.get("connection", {}).get("password"),
            "http_path": connection.get("connection", {}).get("http_path"),
            "access_token": connection.get("connection", {}).get("access_token"),
            "filepath": connection.get("filepath"),
            "odbc_driver": connection.get("connection", {}).get("odbc_driver"),
            "server": connection.get("connection", {}).get("server"),
            "project": connection.get("connection", {}).get("project"),
            "dataset": connection.get("connection", {}).get("dataset"),
            "keyfile": connection.get("connection", {}).get("keyfile"),
            "impersonate_service_account": connection.get("connection", {}).get("impersonate_service_account"),
            "bigquery_credentials": connection.get("connection", {}).get("bigquery_credentials"),
            "transform_columns": transform_columns,
        }

    def get_data_diff_configs(self) -> List[Comparison]:
        data_sources = {
            ds["name"]: {
                "name": ds.get("name"),
                "id": ds.get("id", None),
                "type": ds.get("type"),
                "workspace": ds.get("workspace", "default"),
                "connection": ds.get("connection", {}),
                "filepath": ds.get("file_path"),
                "temporary_schema": ds.get("temporary_schema"),
                "view_name": ds.get("view_name"),
            }
            for ds in self.data["data_sources"]
        }

        rules = self.data.get("rules", []) or []

        for rule in rules:
            rule_id = rule.get("id")
            if rule_id:
                self.rules_repo.register(rule_id, rule)

        new_structure = []

        for comparison_name, comparison_data in self.data["comparisons"].items():
            source_connection = data_sources[comparison_data["source"]["data_source"]]
            target_connection = data_sources[comparison_data["target"]["data_source"]]

            source_masking_cols = comparison_data.get("source", {}).get("masking_columns")
            target_masking_cols = comparison_data.get("target", {}).get("masking_columns")

            masking_character = comparison_data.get("masking_configuration", {}).get("mask_character", "*") or "*"

            schema_overrides = comparison_data.get("schema_overrides", []) or []
            self.rules_repo.register_schema_rules(schema_rules=schema_overrides)

            transform_columns = comparison_data.get("transform_columns", {}) or {}
            self.rules_repo.register_value_rules(value_rules=transform_columns)

            source_transform_columns = {}
            target_transform_columns = {}

            source_transform_configs = transform_columns.get("source", []) or []
            if source_transform_configs:
                for source_transform_config in source_transform_configs:
                    column = source_transform_config.get("name")
                    rule_id = source_transform_config.get("rule")
                    rule = self.rules_repo.get(rule_id)

                    if not rule:
                        raise ValueError(f"Rule with '{rule_id}' not found in rules repository")

                    transformation_template = rule["transformation"]
                    transformation_query = self._build_query(column, transformation_template)
                    source_transform_columns[column] = transformation_template

            target_transform_configs = transform_columns.get("target", []) or []
            if target_transform_configs:
                for target_transform_config in target_transform_configs:
                    column = target_transform_config.get("name")
                    rule_id = target_transform_config.get("rule")
                    rule = self.rules_repo.get(rule_id)

                    if not rule:
                        raise ValueError(f"Rule with '{rule_id}' not found in rules repository")

                    transformation_template = rule["transformation"]
                    transformation_query = self._build_query(column, transformation_template)
                    target_transform_columns[column] = transformation_template

            temporary_schema_source = source_connection.get("temporary_schema")
            temporary_schema_target = target_connection.get("temporary_schema")

            view_name_source = comparison_data.get("source", {}).get("view_name", None)
            view_name_target = comparison_data.get("target", {}).get("view_name", None)

            source_to_target = {
                item["source_column"]: item["target_column"] for item in comparison_data.get("columns_mappings", {})
            }

            source_columns = comparison_data.get("columns", [])
            limit = comparison_data.get("limit", None)
            strict = comparison_data.get("strict", True)
            quick_comparison = comparison_data.get("quick_comparison", False)
            target_columns = [source_to_target.get(col, col) for col in source_columns]
            schema_diff = comparison_data.get("schema_diff", False)
            if quick_comparison and schema_diff:
                raise ValueError("quick_comparison and schema_diff cannot be used together")
            assert len(source_columns) == len(
                target_columns
            ), "source_columns and target_columns must have the same length"
            if not schema_diff and not (source_columns or target_columns):
                raise MissingRequiredFieldError("source_columns and target_columns are required for comparison")

            primary_keys_source = comparison_data.get("key_columns", [])
            if not primary_keys_source and not schema_diff:
                raise MissingRequiredFieldError("key_columns are required for comparison")
            primary_keys_target = [source_to_target.get(pk, pk) for pk in primary_keys_source]

            similarity_data = comparison_data.get("similarity")
            similarity = (
                SimilarityConfig(
                    pre_processing=self.get_pre_processing_methods(similarity_data.get("pre_processing", None)),
                    similarity_method=self.get_similarity_method(similarity_data.get("similarity_method", None)),
                    threshold=self.validate_similarity_threshold(similarity_data.get("threshold", None)),
                )
                if similarity_data
                else None
            )
            advanced_diff_config = comparison_data.get("advanced_configuration", {})
            advanced_configuration = DiffAdvancedConfig(
                bisection_factor=advanced_diff_config.get("bisection_factor", 10),
                bisection_threshold=advanced_diff_config.get("bisection_threshold", 50_000),
                max_threadpool_size=advanced_diff_config.get("max_threadpool_size", 2),
                egress_limit=advanced_diff_config.get("egress_limit", 5_00_000),
                per_column_diff_limit=advanced_diff_config.get("per_column_diff_limit", 100),
                timeout_limit=advanced_diff_config.get("timeout_limit", 60 * 5),
            )
            new_comparison = {
                "comparison_name": comparison_name,
                "source": self.create_connection_config(
                    source_connection,
                    comparison_data,
                    True,
                    temporary_schema_source,
                    view_name_source,
                    transform_columns=source_transform_columns,
                ),
                "target": self.create_connection_config(
                    target_connection,
                    comparison_data,
                    False,
                    temporary_schema_target,
                    view_name_target,
                    transform_columns=target_transform_columns,
                ),
                "source_columns": source_columns,
                "target_columns": target_columns,
                "primary_keys_source": primary_keys_source,
                "primary_keys_target": primary_keys_target,
                "source_filter": comparison_data.get("source", {}).get("filter", None),
                "target_filter": comparison_data.get("target", {}).get("filter", None),
                "source_query": comparison_data.get("source", {}).get("query", None),
                "target_query": comparison_data.get("target", {}).get("query", None),
                "temporary_schema_source": temporary_schema_source,
                "temporary_schema_target": temporary_schema_target,
                "similarity": similarity,
                "view_name_source": view_name_source,
                "view_name_target": view_name_target,
                "advanced_configuration": advanced_configuration,
                "limit": limit,
                "strict": strict,
                "quick_comparison": quick_comparison,
                "source_masking_columns": source_masking_cols,
                "target_masking_columns": target_masking_cols,
                "masking_character": masking_character,
                "schema_diff": schema_diff,
            }
            new_structure.append(Comparison(**new_comparison))

        return new_structure

    def _build_query(self, column, transformation_template):
        transformation_query = transformation_template.format(column=column)
        return transformation_query


def data_diff_config_loader(
    config_path: Optional[str] = None,
    config_yaml: Optional[str] = None,
    config_json: Optional[dict] = None,
) -> List[Comparison]:
    config = DataDiffConfig(
        yaml_file_path=config_path,
        yaml_string=config_yaml,
        config_json=config_json,
    )
    return config.get_data_diff_configs()
