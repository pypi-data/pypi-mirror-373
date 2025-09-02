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

import uuid
from typing import Any, ClassVar, Type

import attrs

from data_diff.abcs.database_types import ColType_UUID, String_UUID, TemporalType
from data_diff.databases import presto
from data_diff.databases.base import TIMESTAMP_PRECISION_POS, BaseDialect, import_helper


@import_helper("trino")
def import_trino():
    import trino

    return trino


class Dialect(presto.Dialect):
    name = "Trino"

    def normalize_timestamp(self, value: str, coltype: TemporalType) -> str:
        if coltype.rounds:
            s = f"date_format(cast({value} as timestamp({coltype.precision})), '%Y-%m-%d %H:%i:%S.%f')"
        else:
            s = f"date_format(cast({value} as timestamp(6)), '%Y-%m-%d %H:%i:%S.%f')"

        return (
            f"RPAD(RPAD({s}, {TIMESTAMP_PRECISION_POS + coltype.precision}, '.'), {TIMESTAMP_PRECISION_POS + 6}, '0')"
        )

    def normalize_uuid(self, value: str, coltype: ColType_UUID) -> str:
        if isinstance(coltype, String_UUID):
            return f"TRIM({value})"
        return f"CAST({value} AS VARCHAR)"

    def set_timezone_to_utc(self) -> str:
        return "SET TIME ZONE '+00:00'"


@attrs.define(frozen=False, init=False, kw_only=True)
class Trino(presto.Presto):
    DIALECT_CLASS: ClassVar[Type[BaseDialect]] = Dialect
    CONNECT_URI_HELP = "trino://<user>@<host>/<catalog>/<schema>"
    CONNECT_URI_PARAMS = ["catalog", "schema"]

    _conn: Any

    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        trino = import_trino()

        if kw.get("schema"):
            self.default_schema = kw.get("schema")

        self._conn = trino.dbapi.connect(**kw)

    @property
    def is_autocommit(self) -> bool:
        return True
