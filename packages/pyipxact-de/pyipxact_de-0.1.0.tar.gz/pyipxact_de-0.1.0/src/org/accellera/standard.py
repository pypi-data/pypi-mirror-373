"""Utilities for representing supported SPIRIT / IP-XACT standard versions.

This module provides a single source of truth for supported standards via the
``Standard`` dataclass and the ``STANDARDS`` registry plus a few helper
functions for validation and namespace / schema URL construction.
"""

from dataclasses import dataclass
from typing import Final


class VersionError(ValueError):
    """Raised when an unknown standard or version is referenced."""


@dataclass(slots=True, frozen=True)
class Standard:
    """Metadata for a standards family and its supported versions.

    Attributes
    ----------
    name:
        Canonical lowercase name (``"spirit"`` or ``"ipxact"``).
    prefix:
        XML namespace prefix to be used (often identical to ``name``).
    schema_root:
        Base root URL for schemas of this standard family.
    token:
        Upper-case token inserted inside the namespace URL path.
    versions:
        Ordered collection (tuple) of all supported version strings.
    """

    name: str
    prefix: str
    schema_root: str
    token: str
    versions: tuple[str, ...]

    # ---- Static convenience helpers (single validation path) ----
    @staticmethod
    def get(name: str, version: str | None = None) -> "Standard":
        """Retrieve standard metadata, optionally validating a version.

        Args:
            name: Standard family name (case-insensitive).
            version: Optional version identifier to validate against the standard.
        Returns:
            Standard: Corresponding metadata object.
        Raises:
            VersionError: If the standard is unknown or the version is unsupported.
        """

        key = name.lower()
        try:
            meta = STANDARDS[key]
        except KeyError as exc:  # pragma: no cover - defensive
            raise VersionError(f"Unknown standard: {name}") from exc

        if version is not None and version not in meta.versions:
            raise VersionError(f"Unknown version for {name}: {version}")
        return meta

    @staticmethod
    def validate(standard: str, version: str) -> None:
        """Validate a standard/version pair.

        Args:
            standard: Standard family name.
            version: Version identifier.

        Raises:
            VersionError: If the standard or version is unsupported.
        """
        Standard.get(standard, version)

    @staticmethod
    def ns_url_for(standard: str, version: str) -> str:
        """Return the namespace URL for the given standard/version.

        Args:
            standard: Standard family name.
            version: Version identifier.

        Returns:
            str: The full namespace URL (without trailing index.xsd).
        """
        meta = Standard.get(standard, version)
        return f"{meta.schema_root}/{meta.token}/{version}"

    @staticmethod
    def namespace_map_for(standard: str, version: str) -> dict[str, str]:
        """Return the XML namespace prefix→URI map for a standard/version.

        Args:
            standard: Standard family name.
            version: Version identifier.
        Returns:
            dict[str, str]: Namespace mapping including ``xsi`` and standard prefix.
        """
        meta = Standard.get(standard, version)
        url = f"{meta.schema_root}/{meta.token}/{version}"
        return {
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            meta.prefix: url,
        }

    @staticmethod
    def schema_location_for(standard: str, version: str) -> str:
        """Return the value for ``xsi:schemaLocation`` for a standard/version.

        Args:
            standard: Standard family name.
            version: Version identifier.

        Returns:
            str: Concatenated namespace URL and its ``index.xsd`` path.
        """
        meta = Standard.get(standard, version)
        url = f"{meta.schema_root}/{meta.token}/{version}"
        return f"{url} {url}/index.xsd"


# Declarative registry (single source of truth)
STANDARDS: Final[dict[str, Standard]] = {
    "spirit": Standard(
        name="spirit",
        prefix="spirit",
        schema_root="http://www.spiritconsortium.org/XMLSchema",
        token="SPIRIT",
        versions=("1.0", "1.1", "1.2", "1.4", "1.5", "1685-2009"),
    ),
    "ipxact": Standard(
        name="ipxact",
        prefix="ipxact",
        schema_root="http://www.accellera.org/XMLSchema",
        token="IPXACT",
        versions=("1685-2014", "1685-2022"),
    ),
}
