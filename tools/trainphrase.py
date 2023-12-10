#!/usr/bin/env python3

"""Tool to train a passphrase."""

from __future__ import annotations

import argparse
import base64
import getpass
import hashlib
import json
import os
import sys
from pathlib import Path


class Error(Exception):
    pass


def main(arglist: list[str]) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--check", action="store_true")
    parser.add_argument("-s", "--store", action="store_true")
    parser.add_argument("file", nargs=1, type=Path)
    arguments = parser.parse_args(arglist)

    if arguments.check and arguments.store:
        raise Error("Options --check and --store are mutually exclusive")

    if not arguments.check and not arguments.store:
        raise Error("Either --check or --store are required")

    file = arguments.file[0]
    assert isinstance(file, Path)

    if arguments.check:
        if not file.exists():
            raise Error(f"Database file {file} not found")

        with file.open() as f:
            data = json.load(f)

        password = getpass.getpass(prompt="Passphrase to check: ")

        salt = base64.b64decode(data["salt"])
        expected = data["hash"]
        h = hashlib.sha3_512()
        h.update(salt + b"#" + password.encode(encoding="utf-8"))

        if expected != h.hexdigest():
            raise Error("Password mismatch.")
    else:
        salt = os.urandom(8)
        password = getpass.getpass(prompt="Passphrase to store: ")
        verification = getpass.getpass(prompt="Reenter passphrase to store: ")
        if password != verification:
            raise Error("Passwords differ - nothing stored.")

        h = hashlib.sha3_512()
        h.update(salt + b"#" + password.encode(encoding="utf-8"))
        pass_hash = h.hexdigest()

        with file.open("w") as f:
            json.dump({"salt": base64.b64encode(salt).decode("utf-8"), "hash": pass_hash}, f)

        print("Passphrase stored.")  # noqa: T201


if __name__ == "__main__":  # pragma: no cover
    try:
        main(sys.argv[1:])
    except Error as e:
        sys.exit(str(e))
