## Description

( Summarise the changes introduced in this merge request )

### Added 
- ( new features )

### Changed
- ( changes in existing functionality )

### Deprecated 
- ( soon-to-be removed features )

### Removed
- ( now removed features )

### Fixed
- ( any bug fixes )

### Security
- ( in case of vulnerabilities )

## Checklist for every commit before merge

- [ ] `pytest` (existing tests must pass, try to cover most of new code)
- [ ] `flake8 pyCFS` (there shouldn't be any errors) 
  - if there are, run `black pyCFS/` and recheck with flake8
  - you might need to fix something manually
- [ ] `mypy pyCFS` (there shouldn't be any errors)
- [ ] Add changes to `Changelog.md`
- [ ] Extended tests passed (start manually)