"""Generate PDF from several comic PDFs."""

from __future__ import annotations

import datetime
from enum import Enum
from pathlib import Path
import sys
from typing import TYPE_CHECKING

import jinja2

if TYPE_CHECKING:
    from collections.abc import Generator


class Keep:
    """Helper class."""

    def __init__(self) -> None:
        """Keep values."""
        self.cur_month: int | None = None

    def set_cur_month(self, inp: int) -> None:
        """Set current month."""
        self.cur_month = inp


class PaperOrientation(Enum):
    """Choose paper orientation."""

    PORTRAIT = 1
    LANDSCAPE = 2


class GenPDF:
    """Create pdf for comic collection."""

    latex_jinja_env = jinja2.Environment(
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        line_statement_prefix="%%",
        line_comment_prefix="%#",
        trim_blocks=True,
        autoescape=False,  # noqa:S701
        loader=jinja2.FileSystemLoader(Path(__file__).with_name("template")),
    )

    def __init__(
        self,
        *,
        title: str,
        base_path: Path,
        start_date: datetime.date,
        paper_orientation: PaperOrientation = PaperOrientation.PORTRAIT,
    ) -> None:
        """Generate PDF in comics path."""
        self.title = title
        self.base_path = base_path
        self.start_date = start_date
        self.paper_orientation = paper_orientation

    def _gen_dates(
        self,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> Generator:
        one_day = datetime.timedelta(days=1)
        now = start_date
        if now is None:
            now = self.start_date
        if end_date is None:
            end_date = datetime.datetime.now(tz=datetime.UTC).date()
        while now <= end_date:
            yield now
            now += one_day

    def __call__(
        self,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> str:
        """Control program."""
        template = self.latex_jinja_env.get_template("book.tex")
        gen_dates = self._gen_dates(start_date, end_date)
        return template.render(
            paper_orientation=self.paper_orientation == PaperOrientation.PORTRAIT,
            dates=gen_dates,
            base_path=self.base_path,
            keep=Keep(),
        )


if __name__ == "__main__":
    base_path = Path.home() / "Bilder" / "Dilbert"
    prog = GenPDF(
        title="Dilbert",
        base_path=base_path,
        start_date=datetime.date(2016, 12, 20),
    )
    sys.stdout.write(f"{prog()}")
