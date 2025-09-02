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
from typing import Any, ClassVar, Dict, Optional, Type

import attrs
from loguru import logger

from data_diff.abcs.database_types import (
    JSON,
    Boolean,
    Date,
    Datetime,
    DbPath,
    Decimal,
    Float,
    FractionalType,
    Integer,
    Native_UUID,
    String_UUID,
    TemporalType,
    Text,
    Time,
    Timestamp,
    TimestampTZ,
)
from data_diff.databases.base import (
    CHECKSUM_HEXDIGITS,
    CHECKSUM_OFFSET,
    BaseDialect,
    ConnectError,
    QueryError,
    ThreadedDatabase,
    import_helper,
)


@import_helper("mssql")
def import_mssql():
    import pyodbc

    return pyodbc


@attrs.define(frozen=False)
class Dialect(BaseDialect):
    name = "MsSQL"
    ROUNDS_ON_PREC_LOSS = True
    SUPPORTS_PRIMARY_KEY: ClassVar[bool] = True
    SUPPORTS_INDEXES = True
    TYPE_CLASSES = {
        # Timestamps
        "datetimeoffset": TimestampTZ,
        "datetime": Datetime,
        "datetime2": Timestamp,
        "smalldatetime": Datetime,
        "timestamp": Datetime,
        "date": Date,
        "time": Time,
        # Numbers
        "float": Float,
        "real": Float,
        "decimal": Decimal,
        "money": Decimal,
        "smallmoney": Decimal,
        "numeric": Decimal,
        # int
        "int": Integer,
        "bigint": Integer,
        "tinyint": Integer,
        "smallint": Integer,
        # Text
        "varchar": Text,
        "char": Text,
        "text": Text,
        "ntext": Text,
        "nvarchar": Text,
        "nchar": Text,
        "binary": Text,
        "varbinary": Text,
        "xml": Text,
        # UUID
        "uniqueidentifier": Native_UUID,
        # Bool
        "bit": Boolean,
        # JSON
        "json": JSON,
    }

    def quote(self, s: str, is_table: bool = False) -> str:
        if s in self.TABLE_NAMES and self.default_schema and is_table:
            return f"[{self.default_schema}].[{s}]"
        return f"[{s}]"

    def set_timezone_to_utc(self) -> str:
        raise NotImplementedError("MsSQL does not support a session timezone setting.")

    def current_timestamp(self) -> str:
        return "GETDATE()"

    def current_database(self) -> str:
        return "DB_NAME()"

    def current_schema(self) -> str:
        return """default_schema_name
        FROM sys.database_principals
        WHERE name = CURRENT_USER"""

    def to_string(self, s: str) -> str:
        s_temp = re.sub(r'["\[\]`]', "", s)
        col_info = self.get_column_raw_info(s_temp)
        ch_len = (col_info and col_info.character_maximum_length) or None
        if not ch_len:
            ch_len = 2500
        ch_len = max(ch_len, 2500)
        if col_info and col_info.data_type in ["nvarchar", "nchar", "ntext"]:
            return f"CONVERT(NVARCHAR({ch_len}), {s})"

        return f"CONVERT(VARCHAR({ch_len}), {s})"

    def type_repr(self, t) -> str:
        try:
            return {bool: "bit", str: "text"}[t]
        except KeyError:
            return super().type_repr(t)

    def random(self) -> str:
        return "rand()"

    def is_distinct_from(self, a: str, b: str) -> str:
        # IS (NOT) DISTINCT FROM is available only since SQLServer 2022.
        # See: https://stackoverflow.com/a/18684859/857383
        return f"(({a}<>{b} OR {a} IS NULL OR {b} IS NULL) AND NOT({a} IS NULL AND {b} IS NULL))"

    def limit_select(
        self,
        select_query: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        has_order_by: Optional[bool] = None,
    ) -> str:
        import re

        if offset:
            raise NotImplementedError("No support for OFFSET in query")

        result = ""
        if not has_order_by:
            result += "ORDER BY 1"

        if limit is not None:
            result += f" OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"

        # select_query = re.sub(r"TRIM\(\[([\w]+)\]\)", r"TRIM(CAST([\1] AS NVARCHAR(MAX)))", select_query)

        # select_query = re.sub(r"TRIM\(([\w]+)\)", r"TRIM(CAST(\1 AS NVARCHAR(MAX)))", select_query)

        # select_query = re.sub(r"TRIM\(\[([\w]+)\]\)", r"LTRIM(RTRIM(CAST([\1] AS VARCHAR(8000))))", select_query)

        # select_query = re.sub(r"TRIM\(([\w]+)\)", r"LTRIM(RTRIM(CAST(\1 AS VARCHAR(8000))))", select_query)

        return f"{select_query} {result}"

    def constant_values(self, rows) -> str:
        values = ", ".join("(%s)" % ", ".join(self._constant_value(v) for v in row) for row in rows)
        return f"VALUES {values}"

    def normalize_timestamp(self, value: str, coltype: TemporalType) -> str:
        # if coltype.precision > 0:
        #     formatted_value = (
        #         f"FORMAT({value}, 'yyyy-MM-dd HH:mm:ss') + '.' + "
        #         f"SUBSTRING(FORMAT({value}, 'fffffff'), 1, {coltype.precision})"
        #     )
        # else:
        #     formatted_value = f"FORMAT({value}, 'yyyy-MM-dd HH:mm:ss')"

        # return formatted_value
        if isinstance(coltype, Datetime):
            if coltype.precision > 0:
                return f"CASE WHEN {value} IS NULL THEN NULL ELSE FORMAT({value}, 'yyyy-MM-dd HH:mm:ss.fff') END"
            return f"CASE WHEN {value} IS NULL THEN NULL ELSE FORMAT({value}, 'yyyy-MM-dd HH:mm:ss') END"
        return f"CAST({value} AS VARCHAR)"

    def normalize_number(self, value: str, coltype: FractionalType) -> str:
        return self.to_string(f"CAST({value} AS DECIMAL(38, {coltype.precision}))")

    def md5_as_int(self, s: str) -> str:
        return f"convert(bigint, convert(varbinary, '0x' + RIGHT(CONVERT(NVARCHAR(32), HashBytes('MD5', {s}), 2), {CHECKSUM_HEXDIGITS}), 1)) - {CHECKSUM_OFFSET}"

    def md5_as_hex(self, s: str) -> str:
        return f"HashBytes('MD5', {s})"

    def parse_table_name(self, name: str) -> DbPath:
        "Parse the given table name into a DbPath"
        self.TABLE_NAMES.append(name.split(".")[-1])
        return tuple(name.split("."))

    def normalize_uuid(self, value, coltype):
        s_temp = re.sub(r'["\[\]`]', "", value)
        col_info = self.get_column_raw_info(s_temp)
        ch_len = (col_info and col_info.character_maximum_length) or None
        if not ch_len:
            ch_len = 2500
        ch_len = max(ch_len, 2500)
        if isinstance(coltype, String_UUID):
            return f"CAST({value} AS VARCHAR({ch_len}))"
        return f"CAST({value} AS VARCHAR(36))"


@attrs.define(frozen=False, init=False, kw_only=True)
class MsSQL(ThreadedDatabase):
    DIALECT_CLASS: ClassVar[Type[BaseDialect]] = Dialect
    CONNECT_URI_HELP = "mssql://<user>:<password>@<host>/<database>/<schema>"
    CONNECT_URI_PARAMS = ["database", "schema"]

    default_database: str
    _args: Dict[str, Any]
    _mssql: Any
    _conn: Any

    def __init__(self, host, port, user, password, *, database, thread_count, **kw) -> None:
        super().__init__(thread_count=thread_count)

        port = port if port else 1433
        args = dict(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            **kw,
        )
        self._args = {k: v for k, v in args.items() if v is not None}
        if self._args.get("odbc_driver", None) is not None:
            self._args["driver"] = self._args.pop("odbc_driver")
        else:
            self._args["driver"] = "{ODBC Driver 18 for SQL Server}"
        try:
            self.default_database = self._args["database"]
            self.default_schema = self._args["schema"]
            self.dialect.default_schema = self.default_schema
        except KeyError:
            raise ValueError("Specify a default database and schema.")
        self._mssql = None
        self._conn = self.create_connection()

    def create_connection(self):
        self._mssql = import_mssql()
        try:
            server = self._args.get("server")
            port = self._args.get("port")
            host = self._args.get("host")
            driver = self._args.get("driver")
            user = self._args.get("user")
            password = self._args.get("password")
            database = self._args.get("database")
            connection_params = self._build_connection_params(
                driver=driver, database=database, username=user, password=password
            )
            self._conn = self._establish_connection(connection_params, host, server, port)
            return self._conn
        except self._mssql.Error as error:
            raise ConnectError(*error.args) from error

    def _prepare_driver_string(self, driver: str) -> str:
        return f"{{{driver}}}" if not driver.startswith("{") else driver

    def _build_connection_params(self, driver: str, database: str, username: str, password: str) -> dict:
        return {
            "DRIVER": self._prepare_driver_string(driver),
            "DATABASE": database,
            "UID": username,
            "PWD": password,
            "TrustServerCertificate": "yes",
        }

    def _establish_connection(self, conn_dict: dict, host: str, server: str, port: str) -> Any:
        connection_attempts = [
            (host, True),  # host with port
            (host, False),  # host without port
            (server, True),  # server with port
            (server, False),  # server without port
        ]

        for _, (server_value, use_port) in enumerate(connection_attempts, 1):
            if not server_value:
                continue
            try:
                conn_dict["SERVER"] = f"{server_value},{port}" if use_port and port else server_value
                connection = self._mssql.connect(**conn_dict)
                logger.info(f"Connected to MSSQL database using {conn_dict['SERVER']}")
                return connection
            except Exception:
                continue

    def select_table_schema(self, path: DbPath) -> str:
        """Provide SQL for selecting the table schema as (name, type, date_prec, num_prec)"""
        database, schema, name = self._normalize_table_path(path)
        info_schema_path = ["information_schema", "columns"]
        if database:
            info_schema_path.insert(0, self.dialect.quote(database))

        return (
            "SELECT column_name, data_type, ISNULL(datetime_precision, 0) AS datetime_precision, ISNULL(numeric_precision, 0) AS numeric_precision, ISNULL(numeric_scale, 0) AS numeric_scale, collation_name, ISNULL(character_maximum_length, 0) AS character_maximum_length "
            f"FROM {'.'.join(info_schema_path)} "
            f"WHERE table_name = '{name}' AND table_schema = '{schema}'"
        )

    def _normalize_table_path(self, path: DbPath) -> DbPath:
        if len(path) == 1:
            return self.default_database, self.default_schema, path[0]
        elif len(path) == 2:
            return self.default_database, path[0], path[1]
        elif len(path) == 3:
            return path

        raise ValueError(
            f"{self.name}: Bad table path for {self}: '{'.'.join(path)}'. Expected format: table, schema.table, or database.schema.table"
        )

    def _query_cursor(self, c, sql_code: str):
        try:
            return super()._query_cursor(c, sql_code)
        except self._mssql.DatabaseError as e:
            raise QueryError(e)

    def close(self):
        super().close()
        if self._conn is not None:
            self._conn.close()
