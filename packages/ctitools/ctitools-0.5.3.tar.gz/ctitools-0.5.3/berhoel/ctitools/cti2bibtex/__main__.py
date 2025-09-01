"""Main code for module."""

from __future__ import annotations

from berhoel.ctitools import CTI

from . import BiBTeXEntry, build_parser

__date__ = "2024/08/13 19:10:55 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


def main() -> None:
    """Run the conversion for CLI file."""
    parser = build_parser()
    args = parser.parse_args()

    cti = CTI(
        args.cti,
        args.limit_year,
        args.limit_issue,
        args.limit_journal,
    )

    out = args.cti.with_suffix(".bib") if args.bibtex is None else args.bibtex

    with out.open("w") as outp:
        for entry in cti:
            outp.write(str(BiBTeXEntry(entry)))


if __name__ == "__main__":
    main()
