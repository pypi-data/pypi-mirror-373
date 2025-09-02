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
import string
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Dict, List

import nltk
from dotenv import load_dotenv
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from dcs_sdk.sdk.config.config_loader import SimilarityConfig


def ensure_nltk_data():
    load_dotenv()
    nltk_data_dir = os.getenv("NLTK_DATA_DIR")

    if not nltk_data_dir:
        default_root = os.path.dirname(os.path.abspath(__file__))
        nltk_data_dir = os.path.join(default_root, "nltk_data")
        print(f"NLTK_DATA_DIR ENV variable not set. Using default path: {nltk_data_dir}")

    punkt_path = os.path.join(nltk_data_dir, "tokenizers", "punkt")
    stopwords_path = os.path.join(nltk_data_dir, "corpora", "stopwords")
    punkt_tab_path = os.path.join(nltk_data_dir, "tokenizers", "punkt_tab")

    if not os.path.exists(punkt_path):
        nltk.download(
            "punkt",
            download_dir=nltk_data_dir,
            halt_on_error=True,
            raise_on_error=True,
        )
    if not os.path.exists(stopwords_path):
        nltk.download(
            "stopwords",
            download_dir=nltk_data_dir,
            halt_on_error=True,
            raise_on_error=True,
        )
    if not os.path.exists(punkt_tab_path):
        nltk.download(
            "punkt_tab",
            download_dir=nltk_data_dir,
            halt_on_error=True,
            raise_on_error=True,
        )

    nltk.data.path.append(nltk_data_dir)


class SimilarityScoreProvider(ABC):
    def preprocess_text(self, text: str, methods: list[str]) -> set:
        """Applies preprocessing steps dynamically before tokenization."""
        if "lower_case" in methods:
            text = text.lower()
        if "remove_punctuation" in methods:
            text = text.translate(str.maketrans("", "", string.punctuation))
        if "remove_stop_words" in methods:
            stop_words = set(stopwords.words("english"))
            text = " ".join(word for word in text.split() if word not in stop_words)
        if "remove_extra_whitespaces" in methods:
            text = " ".join(text.split())

        tokens = set(word_tokenize(text))
        return tokens

    @abstractmethod
    def fuzzy_match(self, str1: set, str2: set) -> float:
        """Computes a similarity score between two sets of tokens."""
        pass

    def add_text_similarity(
        self,
        key: List[str],
        data: List[Dict[str, Any]],
        fields: List[str],
        similarity: SimilarityConfig,
        source_masking_cols: List[str],
        target_masking_cols: List[str],
        mask_char: str,
    ) -> List[Dict[str, Any]]:
        """Adds text similarity scores for the given fields inside the meta dictionary
        and determines if they are a match based on the threshold.

        Args:
            key (List[str]): List of primary key column names to form a composite key.
            data (List[Dict[str, Any]]): List of records to process.
            fields (List[str]): List of fields to compute similarity scores for.
            similarity (SimilarityConfig): Configuration object with pre_processing and threshold.
            source_masking_cols (List[str]): List of cols from the source to be masked
            target_masking_cols (List[str]): List of cols from the target to be masked
            mask_char (str): Character to be used for masking (Default = "*")

        Returns:
            List[Dict[str, Any]]: Processed records with similarity scores added.
        """
        grouped_data = defaultdict(list)
        for item in data:
            composite_key = "_".join(str(item[k]) for k in key)
            grouped_data[composite_key].append(item)

        for _, items in grouped_data.items():
            if len(items) == 2:
                source, target = items

                source.setdefault("meta", {}).setdefault("scores", {})
                target.setdefault("meta", {}).setdefault("scores", {})

                for field in fields:
                    source_text = self.preprocess_text(source.get(field, ""), similarity.pre_processing)
                    target_text = self.preprocess_text(target.get(field, ""), similarity.pre_processing)
                    similarity_score = self.fuzzy_match(source_text, target_text)

                    match_status = "match" if similarity_score >= similarity.threshold else "not matched"

                    score_key = f"{field}"
                    source["meta"]["scores"][score_key] = {"score": similarity_score, "status": match_status}
                    target["meta"]["scores"][score_key] = {"score": similarity_score, "status": match_status}

                    source_val = str(source.get(field, ""))
                    target_val = str(target.get(field, ""))

                    if field in source_masking_cols and field in target_masking_cols:
                        if len(source_val) == len(target_val) and match_status == "not matched":
                            source[field] = mask_char * (len(source_val) + 1)
                            target[field] = mask_char * (len(target_val))
                        else:
                            source[field] = mask_char * (len(source_val))
                            target[field] = mask_char * (len(target_val))

                    if field in source_masking_cols:
                        source[field] = mask_char * len(source_val)

                    if field in target_masking_cols:
                        target[field] = mask_char * len(target_val)

        return data
