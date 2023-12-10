import getpass
from pathlib import Path

import pytest

from tools.trainphrase import Error, main


def test_invalid_check_and_store() -> None:
    with pytest.raises(Error, match="^Options --check and --store are mutually exclusive$"):
        main(["-c", "-s", "/dev/zero"])
    with pytest.raises(Error, match="^Either --check or --store are required$"):
        main(["/dev/zero"])


def test_invalid_missing_db() -> None:
    with pytest.raises(Error, match="^Database file /missing/db not found$"):
        main(["-c", "/missing/db"])


@pytest.mark.parametrize(
    ("initial", "repetition", "check", "result"),
    [
        ("pass", "pass", "invalid_pass", "Password mismatch."),
        ("pass", "mismatch", "pass", "Passwords differ - nothing stored."),
    ],
)
def test_invalid(
    initial: str,
    repetition: str,
    check: str,
    result: str,
    monkeypatch: pytest.MonkeyPatch,
    tmpdir: Path,
) -> None:
    def mock_getpass(prompt: str) -> str:
        if prompt == "Passphrase to store: ":
            return initial
        if prompt == "Reenter passphrase to store: ":
            return repetition
        if prompt == "Passphrase to check: ":
            return check
        assert False, f"Unexpected prompt: {prompt}"

    monkeypatch.setattr(getpass, "getpass", mock_getpass)

    with pytest.raises(Error, match=rf"^{result}$"):  # noqa: PT012
        main(["-s", str(tmpdir / "pass.json")])
        main(["-c", str(tmpdir / "pass.json")])


def test_valid_store_and_check(monkeypatch: pytest.MonkeyPatch, tmpdir: Path) -> None:
    def mock_getpass(prompt: str) -> str:  # noqa: ARG001
        return "deadbeef"

    monkeypatch.setattr(getpass, "getpass", mock_getpass)
    main(["-s", str(tmpdir / "pass.json")])
    main(["-c", str(tmpdir / "pass.json")])
