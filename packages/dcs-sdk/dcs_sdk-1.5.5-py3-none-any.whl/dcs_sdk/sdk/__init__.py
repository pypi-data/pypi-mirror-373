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

from typing import Any, Dict, List, Optional

from dcs_sdk.sdk.config.config_loader import Comparison, data_diff_config_loader
from dcs_sdk.sdk.data_diff.data_differ import diff_db_tables


class DcsSdk:
    def __init__(
        self,
        comparison_name: str,
        config_path: Optional[str] = None,
        config_yaml: Optional[str] = None,
        config_json: Optional[Dict] = None,
        api_key: str = "ABC",
    ):
        self.default_api_key = "ABC"
        self.comparison_name = comparison_name
        self.config_path = config_path
        self.config_yaml = config_yaml
        self.config_json = config_json
        self.api_key = api_key
        self.__validate_api_key()

    def __validate_api_key(self):
        if not self.api_key or self.api_key != self.default_api_key:
            raise ValueError("Invalid API key provided.")

    def run(self):
        data_diff = self.__run_data_diff()
        return data_diff

    def __run_data_diff(self) -> Any:
        """
        Run Data Diff
        """
        comparisons: List[Comparison] = data_diff_config_loader(
            config_path=self.config_path, config_yaml=self.config_yaml, config_json=self.config_json
        )
        for comparison in comparisons:
            if comparison.comparison_name == self.comparison_name:
                result = diff_db_tables(comparison)
                return result

        raise ValueError(f"Comparison name {self.comparison_name} not found in the config file")
