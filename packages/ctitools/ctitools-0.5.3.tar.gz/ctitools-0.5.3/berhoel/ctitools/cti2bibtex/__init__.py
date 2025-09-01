"""Export cti as BiBTeX for Zotero."""

from __future__ import annotations

import argparse
from importlib import metadata
from pathlib import Path
import re
from typing import TYPE_CHECKING

from berhoel.ctitools.ctientry import CTIEntry

if TYPE_CHECKING:
    from berhoel.ctitools.ct import Ct
    from berhoel.ctitools.ix import Ix

__date__ = "2024/08/13 18:52:55 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


class BiBTeXEntry:
    """Represent BiBTeX entry."""

    def __init__(self, entry: Ct | Ix | CTIEntry):
        """Intitalize.

        :param entry: Entry das from CTI file
        """
        self.entry = entry if isinstance(entry, CTIEntry) else entry()

    @staticmethod
    def fix_title(inp: str) -> str:
        """Prepare string for BiBTeX file.

        :param inp: BiBTeX entry sting to modify.

        :return: BiBTeX entry string wich escaped upper characters
        """
        upper = re.compile(r"([A-Z])")
        return upper.sub(r"{\1}", inp)

    def __str__(self) -> str:
        """Return string for entry."""
        if self.entry.author is None:
            authors = ""
        else:
            authors = " and ".join(
                ", ".join(j[::-1] for j in i[::-1].split(maxsplit=1))
                for ii in self.entry.author
                if (i := (ii if ii is not None else " "))
            )
        papershort = {"c't magazin für computertechnik": "c't"}.get(
            self.entry.journaltitle,
            self.entry.journaltitle,
        )
        keywords = ",".join(
            s for i in self.entry.keywords.split(",") if (s := i.strip())
        )
        res = f"""\
@article{{{self.entry.pages}:{papershort}_{self.entry.issue.replace(" ", "_")},
  title = {{{self.fix_title(self.entry.title)}}},"""
        if self.entry.shorttitle is not None:
            res = f"""{res}
  shorttitle = {{{self.fix_title(self.entry.shorttitle)}}},"""
        return f"""{res}
  author = {{{authors}}},
  date = {{{self.entry.date}}},
  journaltitle = {{{self.entry.journaltitle}}},
  pages = {{{self.entry.pages}}},
  issue = {{{self.entry.issue}}},
  keywords = {{{keywords}}},
}}
"""


def build_parser() -> argparse.ArgumentParser:
    """Build cli parser."""
    parser = argparse.ArgumentParser(
        prog="cti2bibtex",
        description="Read a cti file and generate a BiBTeX file.",
    )
    parser.add_argument(
        "cti",
        type=Path,
        help="""input file, cti, frm, or zip file containing one of the  previous
(required)""",
    )
    parser.add_argument(
        "bibtex",
        type=Path,
        nargs="?",
        default=None,
        help="output file (name will be derived from input file, if not given)",
    )
    parser.add_argument(
        "--limit-year",
        type=int,
        default=None,
        help="limit output to given year (default: all years in input file)",
    )
    parser.add_argument(
        "--limit-issue",
        type=int,
        default=None,
        help="limit output to given issue (default: all issues in input file)",
    )
    parser.add_argument(
        "--limit-journal",
        type=str,
        default=None,
        help="limit output to given magazine ('i' for iX, or 'c'  for c't) "
        "(default: both magazines)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {metadata.version('ctitools')}",
    )
    return parser
