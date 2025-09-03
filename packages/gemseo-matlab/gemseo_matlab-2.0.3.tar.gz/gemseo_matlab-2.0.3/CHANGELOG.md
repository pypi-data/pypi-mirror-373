<!--
Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->

<!--
Changelog titles are:
- Added: for new features.
- Changed: for changes in existing functionality.
- Deprecated: for soon-to-be removed features.
- Removed: for now removed features.
- Fixed: for any bug fixes.
- Security: in case of vulnerabilities.
-->

# Changelog

All notable changes of this project will be documented here.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0)
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Version 2.0.3 (September 2025)

### Fixed

- Compatibility with `gemseo.configure`.

## Version 2.0.2 (August 2025)

### Added

- Support GEMSEO v6.2.0.

## Version 2.0.1 (April 2025)

### Added

- Support GEMSEO v6.1.0.
- Support for Python 3.12.
- Support for matlab r2023b, r2024a.

## Version 2.0.0 (November 2024)

### Added

- Support GEMSEO v6.

### Changed

- The following arguments of `MatlabDiscipline` constructor were changed:
  - `matlab_fct` to `matlab_function_path`
  - `search_file` to `root_search_path`
  - `matlab_data_file` to `matlab_data_path`
  - `clean_cache_each_n` to `cleaning_interval`

## Version 1.0.3 (December 2023)

### Added

- Support for Python 3.11.

### Removed

- Support for Python 3.8.

## Version 1.0.2 (December 2023)

### Fixed

- Compatibility with GEMSEO version 5.2.

## Version 1.0.1 (September 2023)

### Fixed

- Memory leaks are fixed in the Matlab discipline,
for matlabengine >= 9.12.
Linked issue:
<https://gitlab.com/gemseo/dev/gemseo-matlab/-/issues/4>

- The MatLab discipline can now be instantiated using input and output
grammar files. Linked issue:
<https://gitlab.com/gemseo/dev/gemseo-matlab/-/issues/3>

- The Matlab discipline can now be serialized. Linked issue:
<https://gitlab.com/gemseo/dev/gemseo/-/issues/674>

## Version 1.0.0 (June 2023)

First release.
