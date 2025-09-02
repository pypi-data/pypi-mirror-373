# tarka

## 0.20.0
- generalized aio-compatible thread-worker utility

## 0.19.1
- Python 3.13 compatibility
- Some improvements to asqla module
- Modernized packaging a little bit

## 0.19.0
- relaxed recursive forward import utility to pass on unconventional modules

## 0.18.0
- added an isolated module loader utility from arbitrary absolute path

## 0.17.0
- added some module loading utilities
- added a package data accessor utility

## 0.15.0
- added serializable transaction executor utilities for SQLA
- added some postgres advisory lock utilities
- testing extended to be able to run with postgresql (requires envvar config)
- tested with Python 3.12

## 0.14.0
- added Alembic+SQLAlchemy database utility

## 0.13.0
- added formatter option to logging setup utility

## 0.12.0
- convenient and improved logging setup

## 0.11.0
- new utf8 utilities in `tarka.utltity.utf8`

## 0.10.2
- improved `tarka.utltity.file.reserve` to use platform specific length encoding

## 0.10.1
- added try_as_is option to `tarka.utltity.file.reserve`

## 0.10.0
- improved customization options of `tarka.utltity.file.reserve`

## 0.9.0
- improved retry logic of `tarka.utltity.aio_sqlite`
- moved SafePath utility to `tarka.utltity.file.safe` the `tarka.utltity.file` import path has been deprecated
- new filename-extension splitting utility in `tarka.utltity.file.name`
- new fire creation utility that reserves the given filename on best effort basis
- fixed some utc-datetime compatibility issues for Windows

## 0.8.0
- key argument added to iterator merge utilities
- iterator merge utilities can handle descending order as well

## 0.7.0
- NamedObject utility (elegant singleton objects)
- merge-zip utility with iterators

## 0.6.1
- Packaging bugfix

## 0.6.0
- Initial release
