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

"Useful AST classes that don't quite fall within the scope of regular SQL"

from typing import Callable, Optional, Sequence

import attrs

from data_diff.abcs.database_types import ColType
from data_diff.queries.ast_classes import Expr, ExprNode


@attrs.define(frozen=True)
class NormalizeAsString(ExprNode):
    expr: ExprNode
    expr_type: Optional[ColType] = None

    @property
    def type(self) -> Optional[type]:
        return str


@attrs.define(frozen=True)
class ApplyFuncAndNormalizeAsString(ExprNode):
    expr: ExprNode
    apply_func: Optional[Callable] = None


@attrs.define(frozen=True)
class Checksum(ExprNode):
    exprs: Sequence[Expr]
