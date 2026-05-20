# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- (Add new features here)

### Changed
- (Add changes here)

### Fixed
- (Add bug fixes here)

### Deprecated
- (Add deprecated features here)

### Removed
- (Add removed features here)

### Security
- (Add security fixes here)

---

## [0.1.0] - 2024-05-20

### Added
- Initial release of ThreatIntel Daily
- NVD (CVE) feed integration
- HaveIBeenPwned (credential breach) feed
- AbuseIPDB (malicious IP) feed
- URLhaus (malware URL) feed
- Email alert delivery (SMTP)
- Slack webhook alerts
- Microsoft Teams webhook alerts
- Discord webhook alerts
- SQLite local database storage
- CLI with 50+ commands
- Docker & Docker Compose support
- Comprehensive documentation
- MIT License

### Features
- Multi-source threat aggregation
- Local-first privacy (no cloud)
- Scheduled threat fetching (hourly)
- Full-text search on threats
- Export to JSON/CSV
- Statistics & trend analysis
- Extensible architecture for custom feeds

---

## How to Update This Changelog

1. **Before release:** Update Unreleased section
2. **On release:** Move changes to new version header with date
3. **Version format:** [VERSION] - YYYY-MM-DD
4. **Categories:** Added, Changed, Fixed, Deprecated, Removed, Security

Example:
```markdown
## [0.2.0] - 2024-06-15

### Added
- Shodan feed integration
- Wazuh lab connector
- Web dashboard (beta)

### Fixed
- Email alert HTML formatting
- SQLite connection pooling

### Changed
- Improved threat correlation algorithm
```
