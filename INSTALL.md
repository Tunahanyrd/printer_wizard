# Installation Guide

This guide will walk you through installing and setting up the Universal Printer Wizard on your Linux system.

## Prerequisites

### System Requirements

- **Operating System**: Linux (any distribution with CUPS support)
- **Python**: Version 3.8 or higher
- **CUPS**: Common UNIX Printing System (usually pre-installed)
- **Permissions**: Root/sudo access for printer installation

### Check Python Version

```bash
python3 --version
```

You should see Python 3.8 or higher.

### Check CUPS Installation

```bash
# Check if CUPS is installed
which cupsd

# Check if CUPS is running
sudo systemctl status cups

# If not running, start it
sudo systemctl start cups
sudo systemctl enable cups
```

## Installation Methods

### Method 1: Direct Installation (Recommended)

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/printer_wizard.git
cd printer_wizard
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

Or install with user permissions:
```bash
pip install --user -r requirements.txt
```

3. **Verify installation**:
```bash
python3 --version
python3 -c "import rich, pyipp, pysnmp, zeroconf; print('All dependencies OK')"
```

### Method 2: Using Virtual Environment (Recommended for Development)

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/printer_wizard.git
cd printer_wizard
```

2. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the wizard** (requires sudo):
```bash
sudo ./venv/bin/python3 tui.py
```

### Method 3: System-wide Installation with Poetry

1. **Install Poetry** (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. **Clone and install**:
```bash
git clone https://github.com/yourusername/printer_wizard.git
cd printer_wizard
poetry install
```

3. **Run with Poetry**:
```bash
sudo poetry run python3 tui.py
```

## Quick Start

After installation, run the wizard:

```bash
sudo python3 tui.py
```

Follow the interactive prompts to discover and install your printer.

## Verifying Installation

### Test Core Module

```bash
python3 core.py
```

This will run a test discovery scan.

### Test Config Module

```bash
python3 config.py
```

This will test the CUPS configuration (may require sudo).

### Check Installed Dependencies

```bash
pip list | grep -E "rich|pyipp|pysnmp|zeroconf|aiohttp|deepmerge|yarl"
```

## Troubleshooting Installation

### Issue: Permission Denied

**Solution**: Ensure you run the TUI with sudo:
```bash
sudo python3 tui.py
```

### Issue: Module Not Found

**Solution**: Reinstall dependencies:
```bash
pip install --force-reinstall -r requirements.txt
```

### Issue: CUPS Not Found

**Solution**: Install CUPS for your distribution:

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install cups cups-client
```

**Fedora/RHEL/CentOS**:
```bash
sudo dnf install cups
```

**Arch Linux**:
```bash
sudo pacman -S cups
```

### Issue: Network Discovery Not Working

**Solution**: Check firewall settings:
```bash
# Allow mDNS
sudo ufw allow 5353/udp

# Allow IPP
sudo ufw allow 631/tcp
```

### Issue: Python Version Too Old

**Solution**: Install a newer Python version or use a distribution with Python 3.8+.

## Uninstallation

To remove the Universal Printer Wizard:

1. **Remove the directory**:
```bash
rm -rf /path/to/printer_wizard
```

2. **Uninstall Python packages** (if installed globally):
```bash
pip uninstall rich pyipp pysnmp zeroconf aiohttp deepmerge yarl
```

3. **Remove installed printers** (optional):
```bash
# List printers
lpstat -p

# Remove a specific printer
sudo lpadmin -x PrinterName
```

## Next Steps

- Read the [README.md](README.md) for usage examples
- Check [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

## Getting Help

If you encounter issues during installation:
1. Check the troubleshooting section above
2. Review the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide
3. Open an issue on GitHub with your system details and error messages

---

Happy printing! 🖨️
