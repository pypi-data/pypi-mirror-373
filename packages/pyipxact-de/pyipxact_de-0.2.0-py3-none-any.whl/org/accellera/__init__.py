"""Accellera standards utilities package.

Provides transformation metadata and exposes ``TRANSFORMATIONS`` for XSL based
version upgrading. Version enumeration symbols were removed in favor of the
``Standard`` registry inside ``standard``.
"""

from pathlib import Path
from typing import Final

from .standard import (
    STANDARDS,
    Standard,
    VersionError,
)

FILE_PATH: Final[Path] = Path(__file__).parent


# Transformation recipe type: (from_version, to_version, xsl_paths)
TRANSFORMATIONS: Final[list[tuple[str, str, tuple[str, ...]]]] = [
    ("1.0", "1.1", (f"{FILE_PATH}/xsl/from1.0_to_1.1.xsl",)),
    ("1.1", "1.2", (f"{FILE_PATH}/xsl/from1.1_to_1.2.xsl",)),
    ("1.2", "1.4",
        (
            f"{FILE_PATH}/xsl/from1.2_to_1.4.xsl",
            f"{FILE_PATH}/xsl/from1.2_to_1.4_abstractionDef.xsl",
        ),
    ),
    ("1.4", "1.5", (f"{FILE_PATH}/xsl/from1.4_to_1.5.xsl",)),
    ("1.4", "1685-2009", (f"{FILE_PATH}/xsl/from1.4_to_1685_2009.xsl",)),
    ("1.5", "1685-2009", (f"{FILE_PATH}/xsl/from1.5_to_1685_2009.xsl",)),
    ("1685-2009", "1685-2014", (f"{FILE_PATH}/xsl/from1685_2009_to_1685_2014.xsl",)),
    ("1685-2014", "1685-2022", (f"{FILE_PATH}/xsl/from1685_2014_to_1685_2022.xsl",)),
]

__all__ = [
    "Standard",
    "STANDARDS",
    "TRANSFORMATIONS",
    "VersionError",
]
