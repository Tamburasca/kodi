# Changelog
## unreleased (xxxx-xx-xx)
### Added
### Changed
### Fixed
### Deprecated
### Removed
### Security
## 0.4.0 (2025-09-15)
### Added
- a new method to read the original EPG as downloaded from the site 
via http://localhost:3003/original/guide.xml for debugging purposes
### Changed
### Fixed
### Deprecated
### Removed
### Security## 0.3.0 (2925-09-12)
### Added
### Changed
- upgraded for NodeJS 24
### Fixed
- EPG is read from local file, http://localhost:3000/guide.xml seems not to work
### Deprecated
### Removed
- option epg_cached
### Security
## 0.2.1 (2024-07-17)
### Added
### Changed
- update json
- TV channel may be dsiabled from list - by station:{"disable": True}
### Fixed
### Deprecated
### Removed
### Security
## 0.2.0 (2023-mm-dd)
### Added
### Changed
- debug and epg_cached options are bool now and can be modified in .env
### Fixed
### Deprecated
### Removed
### Security
## 0.1.1 (2023-12-10)
### Added
- iptv_corrected.json updated by 3rd German local channels 
### Changed
- python script option epg_cached may be empty
### Fixed
### Deprecated
### Removed
### Security
## 0.1.0 (2023-12-08)
### Added
- guide.xml is cached in local file
### Changed
### Fixed
### Deprecated
### Removed
### Security
## 0.0.4 (2023-12-07)
### Added
- redefine openapi for application/xml response type
### Changed
- Logging to ipytv extended
- update README.md
### Fixed
### Deprecated
### Removed
### Security
## 0.0.3 (2023-12-01)
### Added
- logging
### Changed
### Fixed
- Dockerfile (deprecated download of nodejs)
### Deprecated
### Removed
### Security
## 0.0.2 (2023-11-26)
### Added
- merge EPG and IPTV app
## 0.0.1 (2023-11-15)
### Initial release