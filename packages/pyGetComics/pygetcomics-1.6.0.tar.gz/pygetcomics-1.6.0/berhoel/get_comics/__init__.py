"""Download various daily comics."""

from __future__ import annotations

import argparse
from importlib import metadata
import sys

from . import garfield, peanuts


def get_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="get_comics",
        description="Download various periodic comics.",
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"%(prog)s {metadata.version('pyGetComics')}",
    )
    return parser


def main(args: None | argparse.Namespace = None) -> None:
    """Get all supported comics."""
    args = get_parser().parse_args()

    sys.stdout.write("Get Peanuts.\n")
    peanuts.main(args)
    sys.stdout.write("Get Garfield.\n")
    garfield.main(args)


if __name__ == "__main__":
    main()
