# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
Types of changes:
    Added for new features.
    Changed for changes in existing functionality.
    Deprecated for soon-to-be removed features.
    Removed for now removed features.
    Fixed for any bug fixes.
    Security in case of vulnerabilities.
    -- custom --
    Internal for changes not effecting package users (e.g. CI, dev tools, etc).
-->

## [Unreleased]

## [0.2.1] - 2024-12-20

## Fixed
* Fix typo in end-of-life status message (#6)

## Internal
* Restructure and reformat README (#6)
* Add mypy to test suite (#7)

## [0.2.0] - 2024-12-15

### Added
* Add new subcommand `check` that prints a short info about your active Python version (#4)
* Use rich for logging and add option to configure verbosity via `-v, --verbose` (#3)
* Add CHANGELOG file (#3)

### Changed
* Move previous root command to subcommand `list` (#4)
  * To support backwards compatibility, invoking `pirel` will default to `pirel list`

## [0.1.1] - 2024-11-03

### Added
* More content to README including a GIF with demo
* MIT license

### Changed
* Refactor Python version parsing
* Brighten color of "Released" column

### Fixed
* Fix Python version regex (allow alpha, beta, etc. versions)

## [0.1.0] - 2024-11-02

### Added
* Basic CLI app that shows all Python releases with the active Python interpeter being highlighted


[unreleased]: https://github.com/RafaelWO/pirel/compare/0.2.1...HEAD
[0.2.1]: https://github.com/RafaelWO/pirel/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/RafaelWO/pirel/compare/0.1.1...0.2.0
[0.1.1]: https://github.com/RafaelWO/pirel/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/RafaelWO/pirel/releases/tag/0.1.0
