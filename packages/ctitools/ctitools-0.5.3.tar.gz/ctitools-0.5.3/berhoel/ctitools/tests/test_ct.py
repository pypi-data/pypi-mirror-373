"""Tests for processing c't entries."""

from __future__ import annotations

from datetime import datetime
from functools import partial

import pytest

from berhoel.ctitools import ct

try:
    from datetime import UTC, datetime
except ImportError:
    from datetime import datetime, timezone

    UTC = timezone.utc

__date__ = "2024/06/23 20:36:33 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


@pytest.fixture(scope="session")
def issue_map() -> ct.IssueMap:
    """Return map from issue to corresponding data.

    :return: map
    """
    return ct.IssueMap()


DATETIME = partial(datetime, tzinfo=UTC)


@pytest.mark.parametrize(
    ("issue", "date"),
    [
        ((2024, 3), DATETIME(2024, 1, 26)),
        ((2024, 2), DATETIME(2024, 1, 12)),
        ((2024, 1), DATETIME(2023, 12, 30)),
        ((2023, 29), DATETIME(2023, 12, 16)),
        ((2023, 28), DATETIME(2023, 12, 2)),
        ((2023, 27), DATETIME(2023, 11, 18)),
        ((2023, 26), DATETIME(2023, 11, 11)),
        ((2023, 13), DATETIME(2023, 5, 20)),
        ((2023, 12), DATETIME(2023, 5, 13)),
        ((2023, 11), DATETIME(2023, 5, 6)),
        ((2023, 10), DATETIME(2023, 4, 22)),
        ((2023, 9), DATETIME(2023, 4, 8)),
        ((2023, 1), DATETIME(2022, 12, 17)),
        ((2022, 27), DATETIME(2022, 11, 26)),
        ((2022, 26), DATETIME(2022, 12, 3)),
        ((2022, 25), DATETIME(2022, 11, 19)),
        ((2022, 17), DATETIME(2022, 7, 30)),
        ((2022, 16), DATETIME(2022, 7, 16)),
        ((2007, 10), DATETIME(2007, 4, 30)),
        ((2018, 27), DATETIME(2018, 10, 23)),
        ((2019, 27), DATETIME(2019, 10, 21)),
        ((2020, 27), DATETIME(2020, 10, 20)),
        ((2021, 27), DATETIME(2021, 10, 19)),
        ((2014, 15), DATETIME(2014, 6, 30)),
        ((1997, 10), DATETIME(1997, 10, 1)),
    ],
)
def test_ct_dategen(
    issue: tuple,
    date: datetime,
    issue_map: ct.IssueMap,
) -> None:
    """Check for correct mappiong from issue to issue data.

    :param issue:
    """
    if issue_map(*issue) != date:
        msg = f"{issue_map(*issue)=} != {date}"
        raise AssertionError(msg)
