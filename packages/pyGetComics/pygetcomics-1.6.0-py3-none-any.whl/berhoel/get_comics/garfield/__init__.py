"""Download Garfield comic strips."""

from __future__ import annotations

import argparse
from importlib import metadata
from pathlib import Path

from playwright.sync_api import sync_playwright

from berhoel.get_comics.gocomics import GoComics


class Garfield(GoComics):
    """Download daily Garfield comcs fromGoComics."""

    # June 19, 1978
    start_year = 1978
    start_month = 6
    start_day = 19

    garfield_path = Path.home() / "Bilder" / "Garfield"

    gif_path_fmt = f"{garfield_path / '%Y' / '%m' / '%d.gif'}"
    png_path_fmt = f"{garfield_path / '%Y' / '%m' / '%d.png'}"
    url_fmt = "http://www.gocomics.com/garfield/%Y/%m/%d"

    statefile_name = garfield_path / "garfield.statfile"


def get_parser() -> argparse.ArgumentParser:
    """Define argument parser."""
    parser = argparse.ArgumentParser(
        prog="get_garfield",
        description="Download daily Garfield comics.",
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
        Garfield(playwright)()


if __name__ == "__main__":
    main()
