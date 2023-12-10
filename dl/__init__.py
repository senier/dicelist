#
# Copyright 2023 Alexander Senier
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import annotations

import logging
import random
import re
from pathlib import Path
from typing import Optional

import jellyfish
import numpy as np


class Error(Exception):
    pass


def dice_str(value: int, num_dice: int, pos: int = 0) -> str:
    """Return the string representation of a value as a number of dice."""
    if value > 6**num_dice - 1:
        raise Error(f"Value {value} out of range for {num_dice} dice")
    if value == 0:
        return (num_dice - pos) * "1"
    return dice_str(value // 6, num_dice, pos + 1) + f"{value % 6 + 1}"


class Words:
    def __init__(  # noqa: PLR0913
        self,
        filename: Path,
        num_dice: int,
        count_thresh: int,
        len_min: int,
        len_max: int,
        stale_thresh: int,
        step_thresh: Optional[int],
    ):
        self._num_dice: int = num_dice
        self._stale_thresh = stale_thresh
        self._step_thresh = step_thresh

        with filename.open() as infile:
            lines = list(infile.readlines())
            self._all_words = sorted(
                [
                    (word, count)
                    for line in lines
                    for _, word, count_str in [line.strip().split("\t")]
                    if (
                        (count := int(count_str)) > count_thresh
                        and len(word) >= len_min
                        and len(word) <= len_max
                        and re.match(r"^[A-ZÄÖÜa-zßäöü][a-zßäöü]*$", word)
                    )
                ],
                key=lambda e: e[1],
                reverse=True,
            )

        if not self._all_words:
            raise Error("No words found")

        if len(self._all_words) < self._num_words:
            raise Error(f"Expected at least {self._num_words} words, found {len(self._all_words)}")

        self._similarity = np.empty((self._word_len + 1) ** 2, dtype=np.float32).reshape(
            self._word_len + 1,
            self._word_len + 1,
        )
        for i in range(1, self._word_len):
            self._similarity[0, i] = i
            self._similarity[i, 0] = i

    @property
    def _word_len(self) -> int:
        return len(self._all_words)

    @property
    def _num_words(self) -> int:
        result = 6**self._num_dice
        assert isinstance(result, int)
        return result

    def optimize(self, filename: Path) -> None:
        stale = 0
        score: Optional[int] = None

        for li in range(0, self._word_len):
            for ri in range(0, self._word_len):
                if li < ri:
                    self._similarity[li + 1, ri + 1] = 10.0 ** -float(
                        jellyfish.damerau_levenshtein_distance(
                            self._all_words[li][0],
                            self._all_words[ri][0],
                        ),
                    )
            if li % 100 == 0:
                logging.log(
                    logging.INFO,
                    "Calculating similarity: %2.2f%%",
                    100 * li / len(self._all_words),
                )

        steps = 0
        while stale < self._stale_thresh and (not self._step_thresh or steps < self._step_thresh):
            inner = random.randint(1, self._num_words)  # noqa: S311
            outer = self._num_words
            while outer <= len(self._all_words):
                self._similarity[:, [inner, outer]] = self._similarity[:, [outer, inner]]
                self._similarity[[inner, outer], :] = self._similarity[[outer, inner], :]
                temp = np.sum(
                    self._similarity[1 : self._num_words + 1, 1 : self._num_words + 1],
                )

                steps += 1
                if score is None or temp < score:
                    stale = 0
                    score = temp
                    logging.log(
                        logging.INFO,
                        "Optimizing: %.3f [%d/%d]",
                        score,
                        steps,
                        self._step_thresh,
                    )
                    self.write(filename)
                    break

                self._similarity[[outer, inner], :] = self._similarity[[inner, outer], :]
                self._similarity[:, [outer, inner]] = self._similarity[:, [inner, outer]]
                stale += 1
                outer += 1

    def write(self, filename: Path) -> None:
        words = sorted(
            self._all_words[int(index)][0] for index in self._similarity[0, 1 : self._num_words + 1]
        )
        with filename.open("w+") as outfile:
            for i in range(0, self._num_words):
                print(f"{dice_str(i, self._num_dice)} {words[i]}", file=outfile)
