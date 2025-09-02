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

import math
from collections import Counter

from dcs_sdk.sdk.utils.similarity_score.base_provider import SimilarityScoreProvider


class CosineSimilarityProvider(SimilarityScoreProvider):
    def fuzzy_match(self, tokens1: set, tokens2: set) -> float:
        """Computes cosine similarity between two sets of tokens."""
        if not tokens1 or not tokens2:
            return 0.0

        freq1 = Counter(tokens1)
        freq2 = Counter(tokens2)

        all_words = set(freq1.keys()).union(set(freq2.keys()))

        dot_product = sum(freq1[word] * freq2[word] for word in all_words)
        magnitude1 = math.sqrt(sum(freq1[word] ** 2 for word in all_words))
        magnitude2 = math.sqrt(sum(freq2[word] ** 2 for word in all_words))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return round(dot_product / (magnitude1 * magnitude2), 4)
