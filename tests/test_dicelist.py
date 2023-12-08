from pathlib import Path

import pytest

import dl


@pytest.mark.parametrize(("value", "dice", "expected"), [(0, 1, "1"), (5, 1, "6")])
def test_valid_dice_str(value: int, dice: int, expected: str) -> None:
    assert dl.dice_str(value, dice) == expected


@pytest.mark.parametrize(("value", "dice"), [(6, 1), (7, 1), (100, 2)])
def test_invalid_dice_str(value: int, dice: int) -> None:
    with pytest.raises(dl.Error, match=rf"^Value {value} out of range for {dice} dice$"):
        dl.dice_str(value, dice)


@pytest.mark.parametrize(
    ("len_min", "error"),
    [(100, r"^No words found$"), (8, r"^Expected at least 6 words, found 3$")],
)
def test_invalid_words(len_min: int, error: str) -> None:
    with pytest.raises(dl.Error, match=error):
        dl.Words(
            Path("tests/data/words.txt"),
            num_dice=1,
            count_thresh=1,
            len_min=len_min,
            len_max=1000,
            stale_thresh=0,
            step_thresh=None,
        )


def test_valid_words(tmpdir: Path) -> None:
    output = tmpdir / "dicelist.txt"
    dl.Words(
        Path("tests/data/words.txt"),
        num_dice=1,
        count_thresh=1,
        len_min=1,
        len_max=100,
        stale_thresh=1,
        step_thresh=None,
    ).optimize(output)
