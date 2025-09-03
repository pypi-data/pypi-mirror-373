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

from nltk.metrics import edit_distance

from dcs_sdk.sdk.utils.similarity_score.base_provider import SimilarityScoreProvider


class LevenshteinDistanceProvider(SimilarityScoreProvider):
    def fuzzy_match(self, tokens1: set, tokens2: set) -> float:
        """Computes similarity score using Levenshtein distance."""
        str1 = " ".join(tokens1)
        str2 = " ".join(tokens2)

        max_len = max(len(str1), len(str2))
        if max_len == 0:
            return 1.0

        distance = edit_distance(str1, str2)
        return round(1 - (distance / max_len), 4)
