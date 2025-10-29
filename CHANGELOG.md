# Changelog

All notable changes to the Universal Printer Wizard project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0][1.0.0] - 2025-10-29

### Added

- Initial release of Universal Printer Wizard
- Multi-stage printer discovery system
  - Passive discovery via mDNS/Zeroconf
  - Active discovery via IP address and port scanning
  - Intelligent model detection via IPP, SNMP, and PJL protocols
- Rich TUI (Terminal User Interface) for interactive printer configuration
- CUPS integration with support for both model names and PPD files
- Async architecture for fast, non-blocking operations
- Support for multiple printer protocols:
  - IPP (Internet Printing Protocol) on port 631
  - Raw Socket on port 9100
  - LPD (Line Printer Daemon) on port 515
- Comprehensive error handling and user feedback
- PPD file validation and custom driver support
- Option to set printer as system default
- Detailed logging for troubleshooting

### Documentation

- Comprehensive README with usage examples
- Contributing guidelines
- MIT License
- Installation and setup instructions
- Troubleshooting guide
- Architecture documentation

### Dependencies

- rich - Terminal UI framework
- pyipp - IPP protocol client
- pysnmp - SNMP protocol client
- zeroconf - mDNS/Zeroconf discovery
- aiohttp - Async HTTP client
- deepmerge - Dictionary merging utility
- yarl - URL parsing

[1.0.0]: https://github.com/yourusername/printer_wizard/releases/tag/v1.0.0
