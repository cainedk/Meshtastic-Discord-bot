# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-07

### Added
- Initial release
- Discord bot integration with Meshtastic mesh network
- Bidirectional messaging between Discord and Meshtastic
- Device telemetry monitoring (battery, voltage, uptime, signal strength)
- Discord commands for mesh network control:
  - `!mesh info` - Get connected node information
  - `!mesh send <message>` - Send messages to mesh (240 char limit)
  - `!mesh nodes` - List all visible nodes
  - `!mesh help` - Show command help
- Auto-reconnect functionality for both Discord and Meshtastic
- Docker and Docker Compose support
- Comprehensive logging system
- Node name resolution (shows friendly names instead of IDs)
- Message timestamping and formatting
- Signal strength (SNR/RSSI) monitoring
- GPS position support (logged but not displayed)

### Technical Features
- Async/await architecture for Discord
- Threaded Meshtastic client for blocking serial I/O
- Thread-safe message passing between components
- Environment-based configuration
- Graceful shutdown handling
- Health checks and restart policies in Docker
- Automatic USB device permission handling

### Documentation
- Comprehensive README with quick start guide
- Detailed installation instructions (INSTALL.md)
- Contributing guidelines (CONTRIBUTING.md)
- MIT License
- Example environment configuration
- Troubleshooting guide

### Security
- Environment variable-based configuration
- No hardcoded credentials
- Docker security best practices


---

For upgrade instructions between versions, see [INSTALL.md](INSTALL.md#updating).
