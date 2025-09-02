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

from typing import Dict, Optional


def ignore_column_length_difference(
    src_col: Dict,
    tgt_col: Dict,
    params: Optional[Dict] = None,
) -> bool:
    if not params:
        # IN THIS CASE ALWAYS RETURN TRUE
        return True

    # IF PARAMS THEN PROCESS
    # FOR EG: MAX_LENGTH_DIFF = 30 SO IN THIS CASE WE CAN CACL THE DIFF AND RETURN APPROPRIATE RESPONSE

    return False


def allow_equivalent_data_types(src_col: Dict, tgt_col: Dict, params: Optional[Dict] = None) -> bool:

    src_type = src_col["data_type"].lower()
    tgt_type = tgt_col["data_type"].lower()

    if params and "equivalent_groups" in params:
        for group in params["equivalent_groups"]:
            group_set = {t.lower() for t in group}
            if src_type in group_set and tgt_type in group_set:
                return True

    return False


def ignore_numeric_precision_difference(src_col: Dict, tgt_col: Dict, params: Optional[Dict] = None) -> bool:
    if not params:
        return True

    return False


def ignore_numeric_scale_difference(src_col: Dict, tgt_col: Dict, params: Optional[Dict] = None) -> bool:
    if not params:
        return True

    return False


def ignore_datetime_precision_difference(src_col: Dict, tgt_col: Dict, params: Optional[Dict] = None) -> bool:
    if not params:
        return True

    return False
