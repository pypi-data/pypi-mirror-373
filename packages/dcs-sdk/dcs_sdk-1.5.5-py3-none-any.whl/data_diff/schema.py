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
from typing import Any, Collection, Iterator, Optional

import attrs

from data_diff.abcs.database_types import DbPath
from data_diff.utils import CaseAwareMapping, CaseInsensitiveDict, CaseSensitiveDict

logger = logging.getLogger("schema")

Schema = CaseAwareMapping


@attrs.frozen(kw_only=True)
class RawColumnInfo(Collection[Any]):
    """
    A raw row representing the schema info about a column.

    Do not rely on this class too much, it will be removed soon when the schema
    selecting & parsing methods are united into one overrideable method.
    """

    column_name: str
    data_type: str
    datetime_precision: Optional[int] = None
    numeric_precision: Optional[int] = None
    numeric_scale: Optional[int] = None
    collation_name: Optional[str] = None
    character_maximum_length: Optional[int] = None

    # It was a tuple once, so we keep it backward compatible temporarily, until remade to classes.
    def __iter__(self) -> Iterator[Any]:
        return iter(
            (self.column_name, self.data_type, self.datetime_precision, self.numeric_precision, self.numeric_scale)
        )

    def __len__(self) -> int:
        return 5

    def __contains__(self, item: Any) -> bool:
        return False  # that was not used


def create_schema(db_name: str, table_path: DbPath, schema: dict, case_sensitive: bool) -> CaseAwareMapping:
    logger.info(f"[{db_name}] Schema = {schema}")

    if case_sensitive:
        return CaseSensitiveDict(schema)

    if len({k.lower() for k in schema}) < len(schema):
        logger.warning(f'Ambiguous schema for {db_name}:{".".join(table_path)} | Columns = {", ".join(list(schema))}')
        logger.warning("We recommend to disable case-insensitivity (set --case-sensitive).")
    return CaseInsensitiveDict(schema)
