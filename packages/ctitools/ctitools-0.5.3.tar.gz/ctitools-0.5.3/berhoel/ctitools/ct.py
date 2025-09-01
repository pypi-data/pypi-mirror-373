"""Manage entries for c't."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from functools import partial
from types import MappingProxyType
from typing import TYPE_CHECKING, Final

from .ctientry import CTIEntry

if TYPE_CHECKING:
    from collections.abc import Callable

    from . import IssueData

__date__ = "2025/02/01 18:17:50 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


class IssueMap:
    """Class for determinig issue date for c't issues."""

    SPECIAL_ISSUE: Final[int] = 27
    YEAR_FOR_MONTLY_TO_2WEEK_FREQUENCY: Final[int] = 1997
    LAST_MONTHLY_ISSUE_IN_1997: Final[int] = 11
    YEAR_FOR_RETRO_STARTING_AS_SPECIAL_ISSUE: Final[int] = 2016
    DATETIME: Final[Callable] = partial(datetime, tzinfo=UTC)

    def __init__(self) -> None:
        """Intitalize."""
        self._issue_max: tuple[int, int] = (2022, 16)
        self._issue_min: tuple[int, int] = self._issue_max
        self._date_max: datetime = IssueMap.DATETIME(year=2022, month=7, day=16)
        self._date_min: datetime = self._date_max
        self._cache: dict[tuple[int, int], datetime] = {
            self._issue_max: self._date_max,
            (2018, 27): IssueMap.DATETIME(2018, 10, 23),
            (2019, 27): IssueMap.DATETIME(2019, 10, 21),
            (2020, 27): IssueMap.DATETIME(2020, 10, 20),
            (2021, 27): IssueMap.DATETIME(2021, 10, 19),
            (2022, 27): IssueMap.DATETIME(2022, 11, 26),
            (2023, 1): IssueMap.DATETIME(2022, 12, 17),
            (2023, 11): IssueMap.DATETIME(2023, 5, 6),
            (2023, 12): IssueMap.DATETIME(2023, 5, 13),
            (2023, 13): IssueMap.DATETIME(2023, 5, 20),
            (2023, 26): IssueMap.DATETIME(2023, 11, 11),
            (2023, 27): IssueMap.DATETIME(2023, 11, 18),
            (2023, 28): IssueMap.DATETIME(2023, 12, 2),
            (2023, 29): IssueMap.DATETIME(2023, 12, 16),
            (2024, 2): IssueMap.DATETIME(2024, 1, 12),
            (2024, 11): IssueMap.DATETIME(2024, 5, 10),
            (2024, 12): IssueMap.DATETIME(2024, 5, 17),
            (2024, 25): IssueMap.DATETIME(2024, 11, 6),
            (2024, 26): IssueMap.DATETIME(2024, 11, 15),
            (2024, 27): IssueMap.DATETIME(2024, 11, 29),
            (2024, 28): IssueMap.DATETIME(2024, 12, 13),
        }

    def __add_issues_up(self, diff: timedelta, key: tuple[int, int]) -> tuple[int, int]:
        """Add issues later then last known issue.

        :param diff: difference between issues
        :param key: requested issue

        :raises: `AssertionError` if inconsisten data detected
        """
        step_year, step_issue = self._issue_max
        step_issue += 1
        self._issue_max = (step_year, step_issue)
        if self._issue_max not in self._cache:
            if step_issue >= IssueMap.SPECIAL_ISSUE:
                step_issue = 1
                step_year += 1
                self._issue_max = (step_year, step_issue)
            self._date_max += diff
            self._cache[self._issue_max] = self._date_max
        elif self._date_max < self._cache[self._issue_max]:
            self._date_max = self._cache[self._issue_max]
        if self._date_max >= datetime.now(tz=UTC) + timedelta(
            days=16,
        ):
            msg = (
                f"{self._date_max=} < "
                f"{datetime.now(tz=UTC) + timedelta(days=14)=}, "
                f"{key=}\n{self._cache=}"
            )
            raise AssertionError(msg)
        return (step_year, step_issue)

    def __add_issues_down(
        self,
        diff: timedelta,
        key: tuple[int, int],
    ) -> None:
        step_year, step_issue = self._issue_min
        if self._date_min <= IssueMap.DATETIME(
            IssueMap.YEAR_FOR_MONTLY_TO_2WEEK_FREQUENCY,
            10,
            13,
        ):
            step_issue -= 1
            if step_issue < 1:
                step_issue = 12
                step_year -= 1
            self._date_min = IssueMap.DATETIME(step_year, step_issue, 1)
            self._issue_min = (step_year, step_issue)
        else:
            self._date_min -= diff
            step_year, step_issue = self._issue_min
            step_issue -= 1
            if self._date_min == IssueMap.DATETIME(2014, 6, 28):
                self._date_min += timedelta(days=2)
            if step_issue < 1:
                step_year -= 1
                if step_year in {2015}:
                    step_issue = 27
                elif self._date_min < IssueMap.DATETIME(
                    IssueMap.YEAR_FOR_MONTLY_TO_2WEEK_FREQUENCY,
                    1,
                    1,
                ):
                    step_issue = 12
                elif self._date_min < IssueMap.DATETIME(1998, 1, 5):
                    step_issue = 16
                else:
                    step_issue = 26
            self._issue_min = (step_year, step_issue)
        self._cache[self._issue_min] = self._date_min
        if self._date_min <= IssueMap.DATETIME(1983, 1, 1):
            msg = f"{self._date_min=} > {IssueMap.DATETIME(1983, 1, 1)=}, {key=}"
            raise AssertionError(msg)

    def __call__(self, year: int, issue: int) -> datetime:
        """Generate release dates for c't."""
        key = (year, issue)
        diff = timedelta(days=14)
        if key in self._cache:
            return self._cache[key]
        while key > self._issue_max:
            step_year, step_issue = self.__add_issues_up(diff, key)
        while key < self._issue_min:
            self.__add_issues_down(diff, key)

        return self._cache[key]


class Ct:
    """Prepare c't issue information."""

    issue_map = IssueMap()
    month_issue_map = MappingProxyType(
        {
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
        },
    )

    def __init__(
        self,
        data: IssueData,
    ) -> None:
        """Add information for a c't issue.

        :param data: data describing c't issue
        """
        full_issue = self.year_issue2full_issue(data.year, data.issue)
        self.date = self.issue_map(data.year, data.issue)
        self.shorttitle: str | None
        self.title: str
        if data.title is None:
            self.shorttitle, self.title = None, data.shorttitle
        else:
            self.shorttitle, self.title = (
                data.shorttitle,
                data.title,
            )
        self.author = data.author
        self.pages = data.pages
        self.full_issue = full_issue
        self.info = data.info
        self.references = data.references
        self.keywords = data.keywords

    def __call__(self) -> CTIEntry:
        """Return `CTIEntry` for content.

        :return: `CTIEntry` instance
        """
        return CTIEntry(
            self.shorttitle,
            self.title,
            self.author,
            self.pages,
            self.full_issue,
            self.info,
            "c't magazin für computertechnik",
            self.date.strftime("%Y-%m-%d"),
            self.references,
            self.keywords,
        )

    @staticmethod
    def year_issue2full_issue(year: int, issue: int) -> str:
        """Retrieve full issue for c't from year and issue number.

        :param year: issue year
        :param issue: issue number in year

        :return: correctly formatted issue number string
        """
        tmp_issue: int | str = issue
        if tmp_issue == IssueMap.SPECIAL_ISSUE:
            if year in {2022}:
                tmp_issue = "c't Jahresrückblick"
            elif year in {2023, 2024}:
                pass
            elif year >= IssueMap.YEAR_FOR_RETRO_STARTING_AS_SPECIAL_ISSUE:
                tmp_issue = "retro"
        if year < IssueMap.YEAR_FOR_MONTLY_TO_2WEEK_FREQUENCY or (
            year == IssueMap.YEAR_FOR_MONTLY_TO_2WEEK_FREQUENCY
            and issue < IssueMap.LAST_MONTHLY_ISSUE_IN_1997
        ):
            return f"{year:04d} / {Ct.month_issue_map[issue]}"
        if year == 2024 and issue == 25:  # noqa: PLR2004
            return f"{year:04d} / {issue}: Das c't-Bastel-Kompendium"
        return f"{year:04d} / {tmp_issue}"
