# Universal Printer Wizard
> note: this repo is a project for our blog. [read](https://funeralcs.com/posts/vibe-coding/)

A smart printer discovery and configuration tool for Linux systems using CUPS. Automatically detects network printers with minimal user intervention.

## Features

- 🔍 **Automatic Discovery**: mDNS/Zeroconf passive scanning
- 🎯 **Manual Discovery**: IP-based active scanning (IPP, Raw Socket, LPD)
- 🧠 **Smart Detection**: Multi-protocol model identification (IPP, SNMP, PJL)
- 🎨 **Beautiful TUI**: Rich terminal interface with interactive prompts
- ⚡ **Fast**: Async architecture for quick scanning
- 📦 **Flexible**: Supports PPD files or CUPS model names

## Requirements

- Linux with CUPS installed
- Python 3.9+
- Root/sudo access

## Quick Start

**Option 1: Using setup script (Recommended)**
```bash
git clone https://github.com/Tunahanyrd/printer_wizard.git
cd printer_wizard
./setup.sh
```

**Option 2: Manual installation with virtual environment**
```bash
git clone https://github.com/Tunahanyrd/printer_wizard.git
cd printer_wizard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the wizard
sudo ./venv/bin/python3 printer_wizard.py
```

**Option 3: System-wide installation**
```bash
git clone https://github.com/Tunahanyrd/printer_wizard.git
cd printer_wizard
pip install -r requirements.txt
sudo python3 printer_wizard.py
```

## Usage

### Automatic Discovery (Recommended)

The wizard will scan your network for 5 seconds and list all discovered printers:

```bash
# With virtual environment
sudo ./venv/bin/python3 printer_wizard.py

# Or without virtual environment
sudo python3 printer_wizard.py
```

### Manual Discovery

If automatic discovery doesn't find your printer:

1. Enter the printer's IP address when prompted
2. The wizard will scan ports and detect the model
3. Confirm or manually specify the driver

### Driver Options

**Option 1: Let the wizard detect automatically** (works most of the time)

**Option 2: CUPS model name**
```bash
lpinfo -m | grep -i "hp"  # Find available drivers
# Use the exact driver name shown
```

**Option 3: PPD file**
- Download from manufacturer's website
- Provide the full path to the `.ppd` or `.ppd.gz` file

## Project Structure

```
printer_wizard/
├── src/
│   ├── tui.py          # Terminal user interface
│   ├── core.py         # Discovery engine
│   └── config.py       # CUPS integration
├── printer_wizard.py   # Main entry point
├── requirements.txt    # Dependencies
└── setup.sh           # Quick setup script
```

## How It Works

1. **Stage 1**: Passive mDNS/Zeroconf discovery (5 seconds)
2. **Stage 2**: Active port scanning if needed (631, 9100, 515)
3. **Stage 3**: Model detection via IPP, SNMP, or PJL
4. **Stage 4**: CUPS configuration with `lpadmin`

## Troubleshooting

**No printers found?**
- Check if printer is on and connected to network
- Allow ports 631, 9100, 515, 5353 in firewall
- Try manual IP entry

**Permission denied?**
- Always run with `sudo`

**CUPS not running?**
```bash
sudo systemctl start cups
```

**Need more help?**
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions
- Check [INSTALL.md](INSTALL.md) for installation issues

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE)

## Acknowledgments

Built with Rich, pyipp, pysnmp, zeroconf, and CUPS.  
Made with ❤️ for the Linux community.

---

⭐ If this tool helped you, please star the repo!
