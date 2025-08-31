# Changelog

This document lists notable changes for each release and follows:
- Keep a Changelog: https://keepachangelog.com
- Semantic Versioning: https://semver.org

<!-- Template Release
## [Unreleased]
### Added:
### Changed:
### Deprecated:
### Removed:
### Fixed:
### Security:
### Docs:
### Build/CI:
- No changes recorded since the last release.
-->

## [Unreleased]

### Changed
- Commented out "illegal" signal directions in XML files to avoid schema violations.

## [0.1.0] - 2024-12-01

- Migration to xsData and repository restructure.
  - Moved to xsData[^1] instead of PyXB[^2] that provides a cleaner Pythong interface using dataclasses.
  - Old PyXB version has been moved to `PyXB` directory.

### Added
- IP-XACT/SPIRIT bindings generated with xsData.
- Missing bindings based on xsData PR tefra/xsdata#1100.
- XSL files for transformations/translations.
- Accellera XML tests.

### Changed
- Regenerated bindings after xsData bugfix tefra/xsdata#1106.
- Fixed Makefile to update binding generation.
- Repository layout updates and file moves.
- Minor updates and root file refresh.

### Docs
- Updated text. (95ae72c)

## [0.0.0] - 2016-11-15

### Added
- Initial commit and Accellera schemas submodule.
- Generated bindings snapshot.


[Unreleased]: https://github.com/amal-khailtash/pyipxact-de/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/amal-khailtash/pyipxact-de/releases/tag/v0.1.0
[0.0.0]: https://github.com/amal-khailtash/pyipxact-de/tree/b55e147

[^1]: [xsData - Naive XML & JSON Bindings for python](https://github.com/tefra/xsdata)
[^2]: [PyXB: Python XML Schema Bindings](https://pyxb.sourceforge.net/)
