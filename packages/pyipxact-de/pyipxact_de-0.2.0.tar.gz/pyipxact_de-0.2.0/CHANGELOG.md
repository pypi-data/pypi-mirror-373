# Changelog

This document lists notable changes for each release and follows:
- Keep a Changelog: https://keepachangelog.com
- Semantic Versioning: https://semver.org

## [Unreleased]


## [0.2.0] - 2025-09-01

### Added
- enhance documentation configuration and update project classifiers (bfb3f16)

### Changed
- commented out "illegal" signal directions in XML files to avoid schema violations.

### Build/CI:
- validation for `CHANGELOG.md` Unreleased section in manual release workflows (fba4a99)
- update workflow names for consistency and remove obsolete workflows (99f193d)
- update CI workflow name for consistency, enhance README with project badges, and improve documentation styling (0e7abfc)


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


[Unreleased]: https://github.com/amal-khailtash/pyipxact-de/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/amal-khailtash/pyipxact-de/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/amal-khailtash/pyipxact-de/releases/tag/v0.1.0
[0.0.0]: https://github.com/amal-khailtash/pyipxact-de/tree/b55e147

[^1]: [xsData - Naive XML & JSON Bindings for python](https://github.com/tefra/xsdata)
[^2]: [PyXB: Python XML Schema Bindings](https://pyxb.sourceforge.net/)
