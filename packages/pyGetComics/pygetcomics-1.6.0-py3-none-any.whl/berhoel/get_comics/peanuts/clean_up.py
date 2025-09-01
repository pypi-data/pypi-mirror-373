"""Prepare to delete Wrong Peanut downloads based on MD5."""

from __future__ import annotations

import collections
import hashlib
from pathlib import Path
import sys

FILES = Path().glob("*/*/*.png")

HASHES = collections.defaultdict(list)

YEAR = ""

for f_name in FILES:
    m = hashlib.md5()  # noqa:S324
    year = f_name.parents[1].name
    if year != YEAR:
        print("year:", year)  # noqa:T201
        YEAR = year
    with f_name.open("rb") as data:
        for i in data:
            m.update(i)
    HASHES[m.digest()].append(f_name)

for f_list in HASHES.values():
    if len(f_list) > 1:
        for name in f_list:
            sys.stdout.write(f"{name} ")
        sys.stdout.write("\n")
