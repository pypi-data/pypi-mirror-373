"""Main code for module."""

from __future__ import annotations

import argparse
from pathlib import Path

from . import CTI

__date__ = "2024/08/13 19:12:23 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2022 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"


def main() -> None:
    """Execute reading of CTI file."""
    parser = argparse.ArgumentParser("Read cti file.")
    parser.add_argument("cti", type=Path, help="input file (required)")
    args = parser.parse_args()

    CTI(args.cti)


if __name__ == "__main__":
    main()
