"""Manage entries for iX."""

from __future__ import annotations

from datetime import datetime
from functools import partial
from typing import TYPE_CHECKING, ClassVar

from .ctientry import CTIEntry

if TYPE_CHECKING:
    from . import IssueData

__date__ = "2024/11/27 21:30:44 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"

DATETIME = partial(datetime, tzinfo=None)


class Ix:
    """Prepare iX issue information."""

    MONTH_ISSUE_MAP: ClassVar = {
        1: "Januar",
        2: "Februar",
        3: "März",
        4: "April",
        5: "Mai",
        6: "Juni",
        7: "Juli",
        8: "August",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Dezember",
    }

    last_issue_of_year: int = 12

    def __init__(
        self,
        arg: IssueData,
    ):
        """Add information for a iX issue.

        :param arg:
        """
        self.shorttitle: str | None
        if arg.shorttitle is not None:
            self.shorttitle, self.title = arg.shorttitle, arg.title
        else:
            self.shorttitle, self.title = None, arg.title
        self.date: datetime
        self.issue: str
        self.issue, self.date = (
            {
                2016: ("iX Special 2016", DATETIME(2016, 6, 3)),
                2017: ("iX Special 2017", DATETIME(2017, 6, 9)),
                2018: ("iX Special 2018", DATETIME(2018, 5, 25)),
                2019: ("iX Special 2019", DATETIME(2019, 6, 3)),
                2020: ("iX Special 2020", DATETIME(2020, 6, 12)),
                2021: ("iX Special 2021", DATETIME(2021, 6, 9)),
                2022: ("iX Special Green IT", DATETIME(2022, 6, 8)),
                2023: ("iX Special 2023 Künstliche Intelligenz", DATETIME(2023, 6, 13)),
                2024: ("iX Special 2024 Notfallguid", DATETIME(2024, 6, 14)),
            }[arg.year]
            if arg.issue > Ix.last_issue_of_year
            else (Ix.MONTH_ISSUE_MAP[arg.issue], DATETIME(arg.year, arg.issue, 1))
        )
        self.full_issue = f"{arg.year} / {arg.issue}"
        self.author = arg.author
        self.pages = arg.pages
        self.info = arg.info
        self.references = arg.references
        self.keywords = arg.keywords

    def __call__(self) -> CTIEntry:
        """Return CTIEntry from data.

        :return: CTIEntry
        """
        return CTIEntry(
            self.shorttitle,
            self.title,
            self.author,
            self.pages,
            self.full_issue,
            self.info,
            "iX",
            self.date.strftime("%Y-%m-%d"),
            self.references,
            self.keywords,
        )
