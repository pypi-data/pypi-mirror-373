"""Base class for cti (c't iX) entries."""

from __future__ import annotations

from dataclasses import dataclass

__date__ = "2024/06/23 19:28:19 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


@dataclass
class CTIEntry:
    """Store information from input file."""

    shorttitle: str | None
    title: str
    author: tuple[str, ...] | None
    pages: int
    issue: str
    info: dict[str, str]
    journaltitle: str
    date: str
    references: str
    keywords: str

    def __hash__(self) -> int:
        """Calculate hash value for instance.

        :return: hash value
        """
        return hash(
            (
                self.shorttitle,
                self.title,
                self.author,
                self.pages,
                self.issue,
                "".join(f"{i}{j}" for i, j in self.info.items()),
                self.journaltitle,
                self.date,
                self.references,
                self.keywords,
            ),
        )
