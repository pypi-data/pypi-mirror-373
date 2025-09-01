"""Work with cti index files for the Heise papers c't and iX."""

from __future__ import annotations

import argparse
import asyncio
from collections import defaultdict
from collections.abc import Iterable
from contextlib import suppress
from importlib import metadata
from pathlib import Path
import re
from typing import IO, TYPE_CHECKING, Final, NamedTuple
import zipfile

from rich.console import Console
from rich.table import Table

from .ct import Ct
from .ctientry import CTIEntry
from .ix import Ix

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Iterator


__date__ = "2024/12/24 13:38:45 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


class IssueData(NamedTuple):
    """Data for preparing issue instances."""

    shorttitle: str | None
    title: str
    author: tuple[str, ...] | None
    pages: int
    issue: int
    info: dict[str, str]
    year: int
    references: str
    keywords: str


class CTI(Iterable[CTIEntry]):
    """Read entries from cti files.

    .. code:: asc

      Bürokratie: Mit analoger Wucht

      Tim Gerber
      tig
        3
      16
      c22

      Standpunkt,Immer in c't,Gesellschaft,Ukraine-Krieg,Ukraine-Hilfe,Digitalisierung
    """

    PAPER_YEAR_RE: Final = re.compile(r"(?P<paper>[ci])(?P<year>[0-9]{2})")
    PAPER_MAP: Final[dict[str, str]] = {
        "i": "iX",
        "c": "c't magazin für computertechnik",
    }
    LAST_OF_20TH_CENTURY: Final[int] = 80
    NUM_OF_ENTRY_LINES: Final[int] = 9

    def __init__(
        self,
        infile: Path | str,
        limit_year: int | None = None,
        limit_issue: int | None = None,
        limit_journal: str | None = None,
    ) -> None:
        """Read input file.

        :param infile: Input file
        :param limit_year: Limit output to given year
        :param limit_issue: Limit output to given issue
        :param limit_journal: Limit output to given journal

        """
        self.__entries = []
        self.limit_year = limit_year
        self.limit_issue = limit_issue
        self.limit_journal = limit_journal
        if zipfile.is_zipfile(infile):
            with zipfile.ZipFile(infile) as thiszip:
                infolist = thiszip.infolist()
                for info in infolist:
                    extension = info.filename.split(".")[-1]
                    if extension in {"frm", "cti"}:
                        with thiszip.open(info, "r") as inp:
                            self.__entries.extend(asyncio.run(self._gen_data(inp)))
        else:
            if isinstance(infile, str):
                infile = Path(infile)
            with infile.open("rb") as inp:
                self.__entries.extend(asyncio.run(self._gen_data(inp)))

    async def _gen_data(self, inp: IO[bytes]) -> list[CTIEntry]:
        return [
            entry
            async for data in self._read_lines(inp)
            if (entry := await self._parse_input(data)) is not None
        ]

    async def _read_lines(
        self,
        inp: IO[bytes],
    ) -> AsyncGenerator[list[bytes], None]:
        while True:
            res = [
                line
                for _, line in zip(range(CTI.NUM_OF_ENTRY_LINES), inp, strict=False)
            ]
            if len(res) != CTI.NUM_OF_ENTRY_LINES:
                return
            yield res

    async def _parse_input(self, data: list[bytes]) -> CTIEntry | None:
        shorttitle = (
            self.fix_chars(data[0]).decode(encoding="cp858", errors="ignore").strip()
        )
        title = (
            self.fix_chars(data[1]).decode(encoding="cp858", errors="ignore").strip()
        )
        if not title:
            title = shorttitle
            shorttitle = ""
        author = self.fix_author(
            self.fix_chars(data[2])
            .decode(encoding="cp858", errors="ignore")
            .strip()
            .strip(","),
        )
        data[3].decode(encoding="cp858", errors="ignore").strip()  # author shortsign
        pages = int(data[4].decode(encoding="cp858", errors="ignore").strip())
        issue = int(data[5].decode(encoding="cp858", errors="ignore").strip())
        match = self.PAPER_YEAR_RE.match(
            data[6].decode(encoding="cp858", errors="ignore").strip(),
        )
        info = {"paper": "", "year": "-1"}
        if match is not None:
            info = match.groupdict()
        journal = info["paper"]
        year = int(info["year"])
        year += 1900 if year > CTI.LAST_OF_20TH_CENTURY else 2000
        references = data[7].decode(encoding="cp858", errors="ignore").strip()
        keywords = (
            self.fix_chars(data[8])
            .decode(encoding="cp858", errors="ignore")
            .strip()
            .strip(",")
        )
        if (
            (self.limit_issue is not None and issue != self.limit_issue)
            or (self.limit_journal is not None and journal != self.limit_journal)
            or (self.limit_year is not None and year != self.limit_year)
        ):
            return None
        ret_class: type[Ct | Ix] = Ct if journal == "c" else Ix
        item = ret_class(
            IssueData(
                shorttitle=shorttitle,
                title=title,
                author=author,
                pages=pages,
                issue=issue,
                info=info,
                year=year,
                references=references,
                keywords=keywords,
            ),
        )
        return item()

    @staticmethod
    def fix_chars(inp: bytes) -> bytes:
        """Fix characters in input string.

        :param: input string

        :return: string with characters fixed
        """
        table = bytes.maketrans(
            b"\334\344\374\366\337\351",
            b"\232\204\201\224\341\202",
        )
        return inp.translate(table).replace(b"\307\317", b"\204")

    dusan_replace_re = re.compile("Duzan|Dusan")
    zivadinovic_replace_re = re.compile(
        "Zivadinovic|Zivadinovi∩c|Zivadinovi'c|Zivadanovic|Zivadinivic",
    )

    @staticmethod
    def fix_author(author: str) -> tuple[str, ...]:
        """Fix author information.

        :param author: list of authors

        :return: list of autors
        """
        if author.count(",") > 0 and author.count(",") == author.count(" "):
            res = [
                " ".join(j.strip() for j in i.split(",")[::-1])
                for i in author.split("/")
            ]
            author = ",".join(res)
        author = author.replace(" und ", ", ")
        author = author.replace("Von ", "")
        author = "Dušan".join(CTI.dusan_replace_re.split(author))
        author = "Živadinović".join(CTI.zivadinovic_replace_re.split(author))
        author = author.replace('M"cker', "Möcker")

        return tuple([i.strip() for i in author.split(",")])

    def __iter__(self) -> Iterator[CTIEntry]:
        """Prepare interator."""
        return iter(self.__entries)


def __build_cti_statistics_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cti_statistics",
        description="List number of articles for each issue found in input file.",
    )
    parser.add_argument(
        "cti",
        type=Path,
        help="""input file, cti, frm, or zip file containing one of the  previous
(required)""",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {metadata.version('ctitools')}",
    )
    return parser


def issue_key(key: str | int) -> int:
    """Return sort key for c't issues.

    :param: issue key
    """
    month_sort = {
        "Januar": 1,
        "Februar": 2,
        "März": 3,
        "April": 4,
        "Mai": 5,
        "Juni": 6,
        "Juli": 7,
        "August": 8,
        "September": 9,
        "Oktober": 10,
        "November": 11,
        "Dezember": 12,
        "retro": 27,
        "ausblick": 27,
        "c't Jahresrückblick": 27,
    }
    if isinstance(key, str):
        if match := re.match(r"(?P<num>\d{1,2})", key):
            return int(match.group("num"))
        return month_sort[key]
    return key


def cti_statistics() -> None:
    """Print statistics to CTI File."""
    args = __build_cti_statistics_parser().parse_args()
    cti = CTI(args.cti)

    data: defaultdict = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    console = Console()

    for entry in cti:
        paper = "c't" if entry.info["paper"] == "c" else "iX"
        year, issue = entry.issue.split("/")  # type: str, str | int
        with suppress(ValueError):
            if isinstance(issue, str):
                issue = issue.strip()
                issue = int(issue)
        data[paper][int(year)][issue] += 1

    for paper in ("iX", "c't"):
        table = Table(title=paper)
        years = sorted(data[paper].keys())
        for year in years:
            table.add_row(f"{year}")
            issues = sorted(data[paper][year].keys(), key=issue_key)
            s_issues = [f"{i}" for i in issues]
            s_issues = [f"{i:>{max(len(i), 3)}}" for i in s_issues]
            table.add_row(*s_issues)
            table.add_row(
                *(
                    f"{data[paper][year][i]:>{len(s)}}"
                    for i, s in zip(issues, s_issues, strict=False)
                ),
            )
        console.print(table)
