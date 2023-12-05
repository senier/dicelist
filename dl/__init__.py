from __future__ import annotations

import logging
import random
import re
from pathlib import Path
from typing import Optional

import jellyfish
import numpy as np


def dice(value: int, num: int, pos: int = 0) -> str:
    if value == 0:
        return (num - pos) * "1"
    return dice(value // 6, num, pos + 1) + f"{value % 6 + 1}"


class Words:
    def __init__(  # noqa: PLR0913
        self,
        filename: Path,
        num_dice: int,
        count_thresh: int,
        len_min: int,
        len_max: int,
        stale_thresh: int,
    ):
        self._num_dice: int = num_dice
        self._stale_thresh = stale_thresh

        with filename.open() as infile:
            self._all_words = sorted(
                [
                    (word, count)
                    for line in infile.readlines()
                    for _, word, count_str in [line.strip().split("\t")]
                    if (
                        (count := int(count_str)) > count_thresh
                        and len(word) >= len_min
                        and len(word) <= len_max
                        and re.match(r"^[^\W\d_]+$", word)
                    )
                ],
                key=lambda e: e[1],
                reverse=True,
            )

    @property
    def _word_len(self) -> int:
        return len(self._all_words)

    @property
    def _num_words(self) -> int:
        result = 6**self._num_dice
        assert isinstance(result, int)
        return result

    def _optimize(self) -> list[str]:
        stale = 0
        score: Optional[int] = None

        similarity = np.empty((self._word_len + 1) ** 2).reshape(
            self._word_len + 1,
            self._word_len + 1,
        )
        for i in range(1, self._word_len):
            similarity[0, i] = i
            similarity[i, 0] = i

        for li in range(0, self._word_len):
            for ri in range(0, self._word_len):
                if li < ri:
                    similarity[li + 1, ri + 1] = jellyfish.jaro_winkler_similarity(
                        self._all_words[li][0],
                        self._all_words[ri][0],
                    )
            if li % 100 == 99:
                logging.log(
                    logging.INFO,
                    "Calculating similarity: %2.2f%%",
                    100 * li / len(self._all_words),
                )

        while stale < self._stale_thresh:
            inner = random.randint(1, self._num_words)  # noqa: S311
            outer = self._num_words
            while outer <= len(self._all_words):
                similarity[:, [inner, outer]] = similarity[:, [outer, inner]]
                similarity[[inner, outer], :] = similarity[[outer, inner], :]
                temp = np.sum(
                    similarity[1 : self._num_words + 1, 1 : self._num_words + 1],
                )

                if score is None or temp < score - 0.0001:
                    stale = 0
                    score = temp
                    logging.log(logging.INFO, "Optimizing: %.1f", score)
                    break

                similarity[[outer, inner], :] = similarity[[inner, outer], :]
                similarity[:, [outer, inner]] = similarity[:, [inner, outer]]
                stale += 1
                outer += 1

        return sorted(
            self._all_words[int(index)][0] for index in similarity[0, 1 : self._num_words + 1]
        )

    def write(self, filename: Path) -> None:
        words = self._optimize()
        with filename.open("w+") as outfile:
            for i in range(0, self._num_words):
                print(f"{dice(i, self._num_dice)} {words[i]}", file=outfile)
