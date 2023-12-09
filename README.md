# Generate memorable Diceware word list from text corpora

[Diceware](https://theworld.com/~reinhold/diceware.html) is a method to creating secure, yet easy to remember passphrases.

Text corpora are datasets consisting of language resources used in linguistics and natural language processing.

This tool uses the word list of the [Leipzig Corpora Collection](https://wortschatz.uni-leipzig.de/en/download).
The format is described [here](https://wortschatz.uni-leipzig.de/public/documents/Format_Download_File-eng.pdf).

## Installation

Install the dependencies:

```console
pip install -r requirements.txt
```

## Usage

```console
$ ./dicelist -h
usage: dicelist [-h] -i INFILE -o OUTFILE [-n NUM_DICE] [-c COUNT_THRESH]
                [-l LEN_MIN] [-u LEN_MAX] [-s STALE_THRESH] [-S STEP_THRESH]

options:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        Corpora file
  -o OUTFILE, --outfile OUTFILE
                        Output word list file
  -n NUM_DICE, --num-dice NUM_DICE
                        Number of dice (default: 5)
  -c COUNT_THRESH, --count-thresh COUNT_THRESH
                        Disregard words with fewer occurrences (default: 50)
  -l LEN_MIN, --len-min LEN_MIN
                        Minimum word length (default: 3)
  -u LEN_MAX, --len-max LEN_MAX
                        Maximum word length (default: 15)
  -s STALE_THRESH, --stale-thresh STALE_THRESH
                        Number of optimizations after which solution is
                        considered stale (default: 100)
  -S STEP_THRESH, --step-thresh STEP_THRESH
                        Maximum number of optimizations steps to perform
                        (default: 100000)
```

## Approach

To make passphrases more memorable, this tool maximizes the overall [Damerau–Levenshtein distance](https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance) between word pairs.

A symmetric matrix of distance values is created from all word pairs extracted from the corpus.
That matrix is sorted in descending order by the word frequency in the input corpus.
The most frequent 2^(*number of dice*) words in that matrix constitute the initial word list.
The objective function is the sum of all distance values in that sub-matrix of initial words.

The brute-force algorithm implemented in this tool picks a column from the initial words sub-matrix at random.
This column and the corresponding row of the symmetric matrix is swapped with the first column and row outside the initial word sub-matrix.
If the resulting objective value is smaller than the previous one, the previous operation is reverted and the subsequent outside column is tried.
Otherwise, a new random column inside the word list is picked.

The algorithm terminates once a configurable number of steps or unsuccessful swap operations has been performed.

## Limitations

- The number of sides per die is currently hardcoded to 6.
- The brute force approach may result in performance issues on large word list.
- The algorithm is inefficient.
- The algorithm is not parallelized.

## License

Copyright 2023 Alexander Senier

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   <http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
