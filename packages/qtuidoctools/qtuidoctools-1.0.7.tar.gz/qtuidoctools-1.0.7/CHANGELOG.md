# Changelog

All notable changes to qtuidoctools will be documented in this file.

## [Unreleased]

### Added
- Modern Python packaging with pyproject.toml and hatch build backend
- Git-tag based semantic versioning using hatch-vcs
- Src layout project structure for better organization
- Comprehensive ruff configuration for linting and formatting
- Type hints for improved code quality
- Pytest testing infrastructure setup
- Modernized development workflow

### Changed
- **BREAKING**: Migrated from setup.py to pyproject.toml
- **BREAKING**: Moved package from `qtuidoctools/` to `src/qtuidoctools/`
- Replaced external textutils.py and keymap_db.py with proper functioning versions
- Updated all file paths and this_file references for src layout
- Enhanced Python 3.11+ compatibility throughout codebase
- Fixed f-string syntax issues for Python 3.11 compliance
- Modernized string formatting from % style to f-strings
- Fixed star imports replaced with explicit imports
- Removed deprecated `from __future__ import unicode_literals`
- Updated dependencies to support Python 3.11+

### Fixed
- F403/F405 linting errors from star imports
- F811 duplicate function definition error
- Python 3.11 f-string backslash syntax compatibility
- All import paths updated for src layout structure

### Removed
- Legacy setup.py packaging configuration
- Python 2 compatibility constructs
- Star imports throughout codebase

### Technical Details
- **COMPLETED**: Migrated from Click to Fire CLI framework 
  - Converted all CLI commands (update, build, cleanup, version) to Fire-based interface
  - Updated CLI tests from Click's CliRunner to subprocess calls for Fire compatibility  
  - All 6 CLI tests now pass with Fire framework
  - Commands work identically to previous Click implementation
- Configured hatch-vcs for automatic version management from git tags
- Set up comprehensive testing infrastructure with pytest (in progress)
- Added mypy configuration for type checking
- Configured development environments and scripts with hatch

## Previous Versions

### [0.8.3] - Historical
- Last version using legacy setup.py packaging
- Original Click-based CLI interface
- Original project structure and dependencies