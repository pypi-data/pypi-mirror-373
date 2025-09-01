"""Download comics from gocomic."""

from __future__ import annotations

import atexit
import datetime as dtm
from datetime import date, datetime
import fcntl
import hashlib
import os
from pathlib import Path
import pickle
import shutil
import stat
import sys
from typing import IO, TYPE_CHECKING, ClassVar
from urllib.request import urlopen

from PIL import Image

if TYPE_CHECKING:
    from playwright.sync_api import Playwright

FILE_MODE = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
TOUCH_FMT = "%Y%m%d0300"


class SaveState:
    """Save state information on already downloaded files and dates tried."""

    def __init__(self) -> None:
        self.loaded: dict[tuple[str, str, str] | str, tuple[str, str, str] | str] = {}
        self.tried: dict[tuple[str, str, str], int] = {}
        self.downloaded = [0, 0, 0, 0]


def savestate(state: SaveState, statfile: IO[bytes]) -> None:
    """Save state dictionary."""
    pickle.dump(state, statfile, pickle.HIGHEST_PROTOCOL)
    fcntl.fcntl(statfile, fcntl.LOCK_UN)


def mk_dir_tree(path: Path) -> None:
    """Generate directory including missing upper directories."""
    if not path.is_dir():
        mode = (
            stat.S_ISGID
            | stat.S_IRWXU
            | stat.S_IRGRP
            | stat.S_IXGRP
            | stat.S_IROTH
            | stat.S_IXOTH
        )
        path.mkdir(mode=mode, parents=True)
        path.chmod(mode)


class GoComics:
    """Download comics from GoComics."""

    start_year = -1
    start_month = -1
    start_day = -1

    skip: ClassVar = {}

    max_num = 100

    gif_path_fmt = ""
    png_path_fmt = ""
    url_fmt = ""

    statefile_name = Path()

    def __init__(self, playwright: Playwright) -> None:
        self.start_date = date(
            self.start_year,
            self.start_month,
            self.start_day,
        )

        self.delta = dtm.timedelta(days=1)
        self.browser = playwright.chromium.launch(headless=True)

    @staticmethod
    def _progres_cur_date(
        cur_year: int,
        cur_month: int,
        cur_date: date,
    ) -> tuple[int, int]:
        if cur_year != cur_date.year:
            if cur_year != 0:
                sys.stdout.write("\r" + " " * 40)
            cur_year = cur_date.year
            sys.stdout.write(f"\rprocessing year: {cur_date:%Y}\n")
        if cur_month != cur_date.month:
            cur_month = cur_date.month
            sys.stdout.write("\r" + " " * 40)
            sys.stdout.write(f"\r{cur_date:%m} ")
        sys.stdout.flush()
        return cur_year, cur_month

    def _open_statefile(self) -> tuple[SaveState, object]:
        if self.statefile_name.is_file():
            state = pickle.load(self.statefile_name.open("rb"))  # noqa:S301
            shutil.copy2(self.statefile_name, f"{self.statefile_name}_BAK")
        else:
            state = SaveState()
        statfile = self.statefile_name.open("wb")
        fcntl.fcntl(statfile, fcntl.LOCK_EX)
        atexit.register(savestate, state, statfile)
        state.downloaded = [0, 0, 0, 0]

        root = self.statefile_name.parent

        for pic in root.glob("**/*.png"):
            key = pic.with_suffix("").parts[-3:]

            if key not in state.loaded:
                sys.stdout.write(f"\rhashing {pic}.")
                with pic.open("rb") as content:
                    hash_ = hashlib.sha256(content.read()).hexdigest()
                    if hash_ in state.loaded:
                        msg = f"image for {key} same as {state.loaded[hash_]}"
                        raise ValueError(msg)
                    state.loaded[hash_] = key
                    state.loaded[key] = hash_

        return state, statfile

    def _get_img(self, cur_date: date, png_path: Path) -> str | None:
        url = f"{cur_date:{self.url_fmt}}"

        context = self.browser.new_context()
        page = context.new_page()
        page.goto(url)
        page.get_by_role("button", name="Alle akzeptieren").click()

        page.locator("section").get_by_label("Expand comic").first.click()

        img = page.locator(".yarl__slide_image").get_attribute("src")

        if img is None or len(img) == 0:
            sys.stdout.write(f"***\nno download {png_path}\nURL: {url:s}\n")
            return None
        return img

    def _postprocess_image(self, gif_path: Path, png_path: Path) -> None:
        Image.open(gif_path).save(png_path)

        gif_path.unlink()
        png_path.chmod(FILE_MODE)

        sys.stdout.write(f"\r                    \r{png_path}\n")

    def _retrieve_image(self, data_norm: str, gif_path: Path) -> None:
        with (
            urlopen(data_norm) as response,  # noqa: S310
            Path(gif_path).open("wb") as outp,
        ):
            outp.write(response.read())

    def __call__(self) -> None:  # noqa: PLR0915, C901
        """Control program flow."""
        state, statfile = self._open_statefile()

        cur_date = datetime.now(tz=dtm.UTC).date()

        count = self.max_num

        cur_year = 0
        cur_month = 0

        devidor = 7

        while (cur_date := cur_date - self.delta) >= self.start_date:
            if cur_date in self.skip:
                continue
            if count <= 0:
                break
            cur_year, cur_month = self._progres_cur_date(cur_year, cur_month, cur_date)

            png_path = Path(f"{cur_date:{self.png_path_fmt}}")
            pic_id = None
            if not png_path.is_file():
                key = png_path.with_suffix("").parts[-3:]
                state.tried[key] = (state.tried.get(key, -1) + 1) % devidor  # type:ignore[index,arg-type]
                if state.tried[key] != 0:  # type:ignore[index]
                    sys.stdout.write("+")
                    state.downloaded[2] += 1
                    continue

                sys.stdout.flush()

                gif_path = Path(f"{cur_date:{self.gif_path_fmt}}")
                if not gif_path.is_file():
                    data_norm = None
                    img = self._get_img(cur_date, png_path)
                    if img is None:
                        state.downloaded[3] += 1
                        continue

                    pic_id = gif_path.with_suffix("").parts[-3:]

                    if state.loaded.get(pic_id) is not None:  # type:ignore[arg-type]
                        sys.stdout.write(".")
                        sys.stdout.flush()
                        sys.stdout.write(
                            f"\r{png_path} is same as of {state.loaded.get(pic_id)}\n",  # type:ignore[arg-type]
                        )
                        state.downloaded[3] += 1
                        count -= 1
                        continue

                    mk_dir_tree(png_path.parent)

                    with urlopen(img) as response:  # noqa: S310
                        if response.headers.get_default_type() == "text/html":
                            if not isinstance(data_norm, str):
                                raise TypeError
                            self._retrieve_image(data_norm, gif_path)
                        else:
                            with Path(gif_path).open("wb") as outp:
                                outp.write(response.read())

                self._postprocess_image(gif_path, png_path)

                state.downloaded[0] += 1

                cur_datetime = datetime.combine(cur_date, datetime.min.time())

                os.utime(
                    f"{png_path}", (cur_datetime.timestamp(), cur_datetime.timestamp())
                )
            else:
                state.downloaded[1] += 1
                sys.stdout.write("*")

            sys.stdout.flush()

        sys.stdout.write(
            f"\ndownloaded {state.downloaded[0]:d} strips, "
            f"kept {state.downloaded[1]:d}, "
            f"skipped {state.downloaded[2]:d}, "
            f"failed {state.downloaded[3]:d}\n",
        )
