# Universal Printer Wizard

A universal, intelligent printer discovery and configuration tool for Linux systems using CUPS. This TUI application automatically detects network printers and configures them with minimal user intervention.

## Features

- **🔍 Passive Network Discovery**: Automatically finds printers on your network using mDNS/Zeroconf
- **🎯 Active IP Scanning**: Manual printer discovery by IP address with port detection (IPP, Raw Socket, LPD)
- **🧠 Intelligent Model Detection**: Multi-protocol model identification (IPP, SNMP, PJL)
- **⚡ Async Architecture**: Fast, non-blocking operations for efficient scanning
- **🎨 Rich TUI**: Beautiful terminal interface with interactive prompts
- **📦 PPD Support**: Use either CUPS model names or custom PPD files
- **🔧 CUPS Integration**: Seamless printer installation and configuration

## Requirements

- Linux OS with CUPS installed
- Python 3.8+
- Root/sudo access (required for printer installation)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/printer_wizard.git
cd printer_wizard
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure CUPS is installed and running:

```bash
sudo systemctl status cups
```

## Usage

Run the wizard with sudo privileges:

```bash
sudo python3 printer_wizard.py
```

Or directly from src:

```bash
sudo python3 src/tui.py
```

### Discovery Modes

**1. Passive Discovery (Recommended)**

- Automatically scans the network for 5 seconds
- Discovers printers announcing themselves via mDNS
- Zero configuration required

**2. Active Discovery (Manual IP)**

- Enter the printer's IP address manually
- Scans common printer ports (631, 9100, 515)
- Useful for printers without mDNS support

### Driver Configuration

The wizard supports two methods for specifying the printer driver:

**Option 1: CUPS Model Name**

```bash
# Find available drivers
lpinfo -m | grep -i "your_printer_brand"

# Example output:
# drv:///sample.drv/laserjet.ppd
```

**Option 2: PPD File**

- Provide the full path to a local PPD file
- Supports both `.ppd` and `.ppd.gz` formats

## Architecture

The project consists of three main modules:

### `core.py` - Discovery Engine

- **Stage 1**: Passive mDNS/Zeroconf discovery
- **Stage 2**: Active port scanning (631/IPP, 9100/Raw, 515/LPD)
- **Stage 3**: Model identification via IPP, SNMP, and PJL protocols
- **Stage 4**: Orchestration and result aggregation

### `config.py` - CUPS Integration

- Executes `lpadmin` commands
- Handles both model names (`-m`) and PPD files (`-P`)
- Manages printer enablement and default printer settings

### `tui.py` - User Interface

- Interactive terminal UI using Rich library
- Guides users through discovery and installation
- Handles user input and error messages

## Protocol Support

| Protocol      | Port | Purpose              | Library         |
| ------------- | ---- | -------------------- | --------------- |
| mDNS/Zeroconf | 5353 | Passive discovery    | `zeroconf`    |
| IPP           | 631  | Model identification | `pyipp`       |
| SNMP          | 161  | Model identification | `pysnmp`      |
| PJL           | 9100 | Model identification | Built-in socket |
| Raw Socket    | 9100 | Print protocol       | CUPS native     |
| LPD           | 515  | Print protocol       | CUPS native     |

## Examples

### Example 1: Automatic Discovery

```bash
sudo python3 tui.py

# The wizard will:
# 1. Scan the network automatically
# 2. List discovered printers
# 3. Install your selection with detected drivers
```

### Example 2: Manual IP with Custom PPD

```bash
sudo python3 tui.py

# When prompted:
# 1. Skip passive discovery or proceed
# 2. Enter IP: 192.168.1.100
# 3. Choose "Use PPD file"
# 4. Provide path: /path/to/printer.ppd
```

## Testing

Each module can be tested independently:

```bash
# Test core discovery engine
python3 core.py

# Test CUPS configuration
python3 config.py
```

## Troubleshooting

### Permission Denied

The `lpadmin` command requires root privileges:

```bash
python3 tui.py
```

### No Printers Found

- Ensure the printer is powered on and connected to the network
- Check firewall settings (allow ports 631, 9100, 515, 5353)
- Try manual IP discovery mode

### CUPS Service Not Running

```bash
sudo systemctl start cups
sudo systemctl enable cups
```

### Missing Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Or install individually
pip install rich pyipp pysnmp zeroconf aiohttp deepmerge yarl
```

## Dependencies

Core libraries:

- `rich` - Terminal UI framework
- `pyipp` - IPP protocol client
- `pysnmp` - SNMP protocol client
- `zeroconf` - mDNS/Zeroconf discovery
- `aiohttp` - Async HTTP client
- `deepmerge` - Dictionary merging utility
- `yarl` - URL parsing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](#license) file for details.

## Acknowledgments

- CUPS (Common UNIX Printing System) for the printing infrastructure
- The Rich library for the beautiful terminal interface
- All the open-source protocol libraries that make this possible

## Project Status

✅ **Complete and Production Ready**

The Universal Printer Wizard is fully functional and ready for end-to-end printer discovery and configuration on Linux systems.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Made with ❤️ for the Linux community**
