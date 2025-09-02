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

from dcs_sdk.sdk.rules.schema_rules import (
    allow_equivalent_data_types,
    ignore_column_length_difference,
    ignore_datetime_precision_difference,
    ignore_numeric_precision_difference,
    ignore_numeric_scale_difference,
)


def get_rules_to_func_mapping():
    return {
        "ignore_column_length_difference": ignore_column_length_difference,
        "allow_equivalent_data_types": allow_equivalent_data_types,
        "ignore_numeric_precision_difference": ignore_numeric_precision_difference,
        "ignore_numeric_scale_difference": ignore_numeric_scale_difference,
        "ignore_datetime_precision_difference": ignore_datetime_precision_difference,
    }
