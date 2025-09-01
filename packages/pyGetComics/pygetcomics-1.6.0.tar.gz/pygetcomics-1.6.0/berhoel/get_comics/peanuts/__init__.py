"""Download Peanuts comics since Oct 2, 1950."""

from __future__ import annotations

import argparse
import datetime
from importlib import metadata
from pathlib import Path
import typing

from playwright.sync_api import sync_playwright

from berhoel.get_comics.gocomics import GoComics


class Peanuts(GoComics):
    """Download daily Peanuts comics from GoComics."""

    # October 2, 1950
    start_year = 1950
    start_month = 10
    start_day = 2

    skip: typing.ClassVar = {
        datetime.date(*d)
        for d in (
            (1951, 12, 30),
            (1951, 12, 23),
            (1951, 12, 16),
            (1951, 12, 9),
            (1951, 12, 2),
            (1951, 11, 25),
            (1951, 11, 18),
            (1951, 11, 11),
            (1951, 11, 4),
            (1951, 10, 28),
            (1951, 10, 21),
            (1951, 10, 14),
            (1951, 10, 7),
            (1951, 9, 30),
            (1951, 9, 23),
            (1951, 9, 16),
            (1951, 9, 9),
            (1951, 9, 2),
            (1951, 8, 26),
            (1951, 8, 19),
            (1951, 8, 12),
            (1951, 8, 5),
            (1951, 7, 29),
            (1951, 7, 22),
            (1951, 7, 15),
            (1951, 7, 8),
            (1951, 7, 1),
            (1951, 6, 24),
            (1951, 6, 17),
            (1951, 6, 10),
            (1951, 6, 3),
            (1951, 5, 27),
            (1951, 5, 20),
            (1951, 5, 13),
            (1951, 5, 6),
            (1951, 4, 29),
            (1951, 4, 22),
            (1951, 4, 15),
            (1951, 4, 8),
            (1951, 4, 1),
            (1951, 3, 25),
            (1951, 3, 18),
            (1951, 3, 11),
            (1951, 3, 4),
            (1951, 2, 25),
            (1951, 2, 18),
            (1951, 2, 11),
            (1951, 2, 4),
            (1951, 1, 28),
            (1951, 1, 21),
            (1951, 1, 14),
            (1951, 1, 7),
            (1950, 12, 31),
            (1950, 12, 24),
            (1950, 12, 17),
            (1950, 12, 10),
            (1950, 12, 3),
            (1950, 11, 26),
            (1950, 11, 19),
            (1950, 11, 12),
            (1950, 11, 5),
            (1950, 10, 29),
            (1950, 10, 22),
            (1950, 10, 15),
            (1950, 10, 8),
        )
    }

    peanuts_path = Path.home() / "Bilder" / "Peanuts"

    gif_path_fmt = f"{peanuts_path / '%Y' / '%m' / '%d.gif'}"
    png_path_fmt = f"{peanuts_path / '%Y' / '%m' / '%d.png'}"
    url_fmt = "https://www.gocomics.com/peanuts/%Y/%m/%d"

    statefile_name = peanuts_path / "peanuts.statfile"


def get_parser() -> argparse.ArgumentParser:
    """Create command line parser."""
    parser = argparse.ArgumentParser(
        prog="get_peanuts",
        description="Download daily Peanuts comics.",
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"%(prog)s {metadata.version('pyGetComics')}",
    )
    return parser


def main(args: None | argparse.Namespace = None) -> None:
    """Execute main Program."""
    if args is None:
        args = get_parser().parse_args()

    with sync_playwright() as playwright:
        Peanuts(playwright)()


if __name__ == "__main__":
    main()
