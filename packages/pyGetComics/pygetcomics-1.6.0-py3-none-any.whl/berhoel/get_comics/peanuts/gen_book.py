"""Generate Book of all Peanuts comics from images."""

from __future__ import annotations

import datetime
from enum import IntEnum
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Callable
    from io import TextIOWrapper


START_YEAR = 1950
START_MONTH = 10
START_DAY = 2

START_DATE = datetime.datetime(
    START_YEAR,
    START_MONTH,
    START_DAY,
    tzinfo=datetime.UTC,
)
TODAY = datetime.datetime.now(tz=datetime.UTC).date()

DELTA = datetime.timedelta(days=1)

PATH_FMT = f"{(Path('%Y') / '%m' / '%d')}"


class DayOfWeek(IntEnum):
    """Day of week."""

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    STATURDAY = 6
    SUNDAY = 7


class PrintPageSide(IntEnum):
    """Side on output."""

    LEFT = 1
    RIGHT = 2


class Pos(NamedTuple):
    """Position information."""

    x: PrintPageSide
    y: int


class PeanutsBook:
    """Generate LaTeX file for Peanuts comic book."""

    def __init__(self, fname: Path) -> None:
        self.cur_date = START_DATE
        self.fname = fname
        self.grpath: Path | None = None
        self.outp_done = False
        self.side_weekd = PrintPageSide.LEFT
        self.side_sund = PrintPageSide.RIGHT
        self.with_sund = False
        self.days: list[tuple[Callable, Path, datetime.datetime]] = []

    def run(self) -> None:
        """Do the actual processing."""
        with self.fname.open("w") as out:
            self.write_prologue(out)

            while self.cur_date <= TODAY:
                self.wr_image(self.cur_date)
                if self.cur_date.isoweekday() == DayOfWeek.SUNDAY and self.outp_done:
                    side_weekd = self.side_weekd
                    if self.side_weekd == PrintPageSide.RIGHT and self.with_sund:
                        out.write("\\clearpage\n")
                        self.side_weekd = PrintPageSide.LEFT
                    for func, path, date in self.days:
                        self.graphicspath(out, path)
                        func(out, path.name, date)
                    if self.with_sund or side_weekd == PrintPageSide.RIGHT:
                        out.write("\\clearpage\n")
                        self.side_weekd = PrintPageSide.LEFT
                    else:
                        self.side_weekd = PrintPageSide.RIGHT
                    self.outp_done = False
                    self.with_sund = False
                    self.days = []

                self.cur_date += DELTA

            self.write_epilog(out)

    def write_prologue(self, out: TextIOWrapper) -> None:
        """Write LaTeX prologue."""
        out.write(
            r"""\documentclass[a4paper,landscape]{book}
\usepackage{graphicx}
\usepackage{textpos}
\usepackage{multicol}
\usepackage[textwidth=277.0mm,textheight=189.9mm,headsep=1mm]{geometry}
\makeatletter
\TPGrid[12mm,12mm]{2}{6}
\setlength{\parindent}{0pt}
\usepackage{fontspec}
%\setmainfont[Ligatures={Common,Rare,Historic}, Numbers=OldStyle]{Linux Libertine O}
\usepackage{libertine}[Ligatures={Common,Rare,Historic}, Numbers=OldStyle]
\begin{document}
\begin{multicols}{2}
""",
        )

    def wr_image(self, date: datetime.datetime) -> None:
        """Write information for including image."""
        path = Path(f"{date:{PATH_FMT}}")
        if (path := path.with_suffix(".png")).is_file():
            weekday = date.isoweekday()
            self.days.append(
                (
                    {
                        DayOfWeek.MONDAY: self.do_mo,
                        DayOfWeek.TUESDAY: self.do_di,
                        DayOfWeek.WEDNESDAY: self.do_mi,
                        DayOfWeek.THURSDAY: self.do_do,
                        DayOfWeek.FRIDAY: self.do_fr,
                        DayOfWeek.STATURDAY: self.do_sa,
                        DayOfWeek.SUNDAY: self.do_so,
                    }[DayOfWeek(weekday)],
                    path,
                    date,
                ),
            )
            self.outp_done = True

    def graphicspath(self, out: TextIOWrapper, path: Path) -> None:
        """Write appropriate Graphicspath information."""
        grpath = path.parent
        if grpath != self.grpath:
            out.write(f"\\graphicspath{{{{{grpath}}}}}\n")
            self.grpath = grpath

    def do_mo(self, out: TextIOWrapper, fname: str, date: datetime.date) -> None:
        """Place Monday figure."""
        self.place_img(out, Pos(self.side_weekd, 1), fname, date)

    def do_di(self, out: TextIOWrapper, fname: str, date: datetime.date) -> None:
        """Place Tuesday figure."""
        self.place_img(out, Pos(self.side_weekd, 2), fname, date)

    def do_mi(self, out: TextIOWrapper, fname: str, date: datetime.date) -> None:
        """Place Wednesday figure."""
        self.place_img(out, Pos(self.side_weekd, 3), fname, date)

    def do_do(self, out: TextIOWrapper, fname: str, date: datetime.date) -> None:
        """Place Thursday figure."""
        self.place_img(out, Pos(self.side_weekd, 4), fname, date)

    def do_fr(self, out: TextIOWrapper, fname: str, date: datetime.date) -> None:
        """Place Friday figure."""
        self.place_img(out, Pos(self.side_weekd, 5), fname, date)

    def do_sa(self, out: TextIOWrapper, fname: str, date: datetime.date) -> None:
        """Place Saturday figure."""
        self.place_img(out, Pos(self.side_weekd, 6), fname, date)

    def do_so(self, out: TextIOWrapper, fname: str, date: datetime.date) -> None:
        """Place Sunday figure."""
        self.place_img(out, Pos(self.side_sund, 1), fname, date)
        self.with_sund = True

    def place_img(
        self,
        out: TextIOWrapper,
        pos: Pos,
        fname: str,
        date: datetime.date,
    ) -> None:
        """Place image in grid."""
        fac = "" if (date.isoweekday() == DayOfWeek.SUNDAY) else 1.0 / 7.0
        out.write(
            f"""\
\\begin{{textblock}}{{1}}({pos.x - 1:d},{pos.y - 1:d})
  {date:%a %d. %B %Y}\\par
  \\centering%
    \\includegraphics[width=.95\\linewidth,height={fac}\\textheight,%
         keepaspectratio]{{{fname}}}
\\end{{textblock}}
""",
        )

    def write_epilog(self, out: TextIOWrapper) -> None:
        """Write LaTeX epilogue."""
        out.write(
            r"""\end{multicols}
\end{document}
""",
        )


def main() -> None:
    """Execute main processing."""
    book = PeanutsBook(fname=Path("Peanuts_book.tex"))
    book.run()


if __name__ == "__main__":
    main()
