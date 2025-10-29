# Troubleshooting Guide

This guide addresses common issues you may encounter while using the Universal Printer Wizard.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Discovery Issues](#discovery-issues)
- [Configuration Issues](#configuration-issues)
- [Printing Issues](#printing-issues)
- [Network Issues](#network-issues)
- [Advanced Debugging](#advanced-debugging)

---

## Installation Issues

### Python Dependencies Won't Install

**Problem**: `pip install -r requirements.txt` fails

**Solutions**:

1. **Update pip**:
```bash
python3 -m pip install --upgrade pip
```

2. **Install build dependencies**:
```bash
# Ubuntu/Debian
sudo apt install python3-dev python3-pip build-essential

# Fedora/RHEL
sudo dnf install python3-devel gcc

# Arch Linux
sudo pacman -S python python-pip base-devel
```

3. **Use a virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### CUPS Not Installed

**Problem**: `cupsd: command not found`

**Solutions**:

```bash
# Ubuntu/Debian
sudo apt install cups cups-client

# Fedora/RHEL
sudo dnf install cups

# Arch Linux
sudo pacman -S cups

# Start and enable CUPS
sudo systemctl start cups
sudo systemctl enable cups
```

---

## Discovery Issues

### No Printers Found in Passive Discovery

**Problem**: Stage 1 doesn't find any printers

**Possible Causes**:
- Printer doesn't support mDNS/Bonjour
- Firewall blocking mDNS traffic
- Printer on different subnet

**Solutions**:

1. **Check firewall** (allow mDNS port):
```bash
sudo ufw allow 5353/udp
```

2. **Verify printer supports mDNS**:
   - Check printer manual
   - Look for "AirPrint" or "Bonjour" in specs

3. **Use manual IP discovery instead**:
   - Skip passive discovery
   - Enter printer IP manually in Stage 2

### Active Discovery Fails (Manual IP)

**Problem**: "No known ports found" after entering IP

**Possible Causes**:
- Wrong IP address
- Printer turned off
- Network connectivity issues
- Firewall blocking printer ports

**Solutions**:

1. **Verify printer IP address**:
```bash
# Print test page from printer to see IP
# Or check router's connected devices

# Ping the printer
ping 192.168.1.100
```

2. **Check printer ports manually**:
```bash
# Scan printer ports
nmap -p 631,9100,515 192.168.1.100

# Or use netcat
nc -zv 192.168.1.100 631
nc -zv 192.168.1.100 9100
```

3. **Check firewall rules**:
```bash
# Temporarily disable firewall for testing
sudo ufw disable

# After testing, re-enable with proper rules
sudo ufw enable
sudo ufw allow 631/tcp
sudo ufw allow 9100/tcp
sudo ufw allow 515/tcp
```

### Model Detection Returns "Unknown"

**Problem**: Wizard can't detect printer model

**This is normal for**:
- Some older printers
- Printers with limited protocol support
- USB printers accessed through network gateway

**Solutions**:

1. **Provide CUPS model name**:
```bash
# Search for your printer brand
lpinfo -m | grep -i "hp"
lpinfo -m | grep -i "epson"
lpinfo -m | grep -i "brother"
lpinfo -m | grep -i "canon"

# Use the exact driver name shown
```

2. **Download PPD file**:
   - Visit printer manufacturer's website
   - Download Linux/CUPS driver
   - Extract .ppd file
   - Provide full path to wizard

3. **Use generic driver** (last resort):
```bash
lpinfo -m | grep -i "generic"
```

---

## Configuration Issues

### Permission Denied / Forbidden Error

**Problem**: `lpadmin` fails with permission error

**Cause**: CUPS commands require root privileges

**Solution**:
```bash
# Always run the wizard with sudo
sudo python3 tui.py
```

### "lpadmin: command not found"

**Problem**: CUPS client tools not in PATH

**Solution**:
```bash
# Check if CUPS is installed
which lpadmin

# If not found, install CUPS
sudo apt install cups cups-client  # Ubuntu/Debian
sudo dnf install cups              # Fedora/RHEL
sudo pacman -S cups                # Arch Linux
```

### PPD File Validation Fails

**Problem**: "File not found or not a valid .ppd file"

**Solutions**:

1. **Check file exists**:
```bash
ls -l /path/to/printer.ppd
```

2. **Verify file extension**:
   - Must end with `.ppd` or `.ppd.gz`
   - Case-sensitive on Linux

3. **Check file permissions**:
```bash
sudo chmod 644 /path/to/printer.ppd
```

4. **Validate PPD syntax**:
```bash
cupstestppd /path/to/printer.ppd
```

---

## Printing Issues

### Printer Installed but Won't Print

**Problem**: Printer shows in system but jobs fail

**Solutions**:

1. **Check printer status**:
```bash
lpstat -p
lpstat -t
```

2. **Enable printer** (if paused):
```bash
sudo cupsenable PrinterName
sudo cupsaccept PrinterName
```

3. **Test print**:
```bash
echo "Test Page" | lp -d PrinterName
```

4. **Check CUPS error log**:
```bash
sudo tail -f /var/log/cups/error_log
```

### Print Jobs Stuck in Queue

**Problem**: Jobs queued but not printing

**Solutions**:

1. **Check printer state**:
```bash
lpstat -p PrinterName
```

2. **Cancel stuck jobs**:
```bash
cancel -a PrinterName
```

3. **Restart CUPS**:
```bash
sudo systemctl restart cups
```

4. **Check printer connection**:
```bash
# Verify printer is reachable
ping printer_ip_address
```

---

## Network Issues

### Firewall Blocking Discovery

**Problem**: Can't discover or connect to network printer

**Solution - Configure firewall**:

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 5353/udp   # mDNS
sudo ufw allow 631/tcp    # IPP
sudo ufw allow 9100/tcp   # Raw socket
sudo ufw allow 515/tcp    # LPD
sudo ufw allow 161/udp    # SNMP

# Fedora/RHEL (firewalld)
sudo firewall-cmd --add-service=mdns --permanent
sudo firewall-cmd --add-service=ipp --permanent
sudo firewall-cmd --add-port=9100/tcp --permanent
sudo firewall-cmd --reload
```

### Printer on Different Subnet

**Problem**: Can't discover printer in different network segment

**Solution**:
- Use manual IP discovery
- Add static route if needed:
```bash
sudo ip route add 192.168.2.0/24 via 192.168.1.1
```

### DNS/Hostname Issues

**Problem**: Printer hostname doesn't resolve

**Solution**:
```bash
# Use IP address instead of hostname
# Or add entry to /etc/hosts
echo "192.168.1.100 myprinter.local" | sudo tee -a /etc/hosts
```

---

## Advanced Debugging

### Enable Verbose Logging

Modify the scripts to see more details:

**For core.py**:
```python
# Add at the start of main_test()
import logging
logging.basicConfig(level=logging.DEBUG)
```

**For CUPS debugging**:
```bash
# Edit /etc/cups/cupsd.conf
sudo nano /etc/cups/cupsd.conf

# Set LogLevel to debug
LogLevel debug

# Restart CUPS
sudo systemctl restart cups

# Watch logs
sudo tail -f /var/log/cups/error_log
```

### Check Network Traffic

**Use tcpdump to see printer communication**:
```bash
# Monitor IPP traffic
sudo tcpdump -i any port 631 -A

# Monitor SNMP traffic
sudo tcpdump -i any port 161 -A

# Monitor mDNS traffic
sudo tcpdump -i any port 5353 -A
```

### Test Modules Independently

**Test discovery engine**:
```bash
python3 core.py
```

**Test CUPS config**:
```bash
python3 config.py
```

### Manual CUPS Commands

**Manually add printer for testing**:
```bash
# Using IPP
sudo lpadmin -p TestPrinter -v ipp://192.168.1.100/ipp/print -m everywhere -E

# Using socket
sudo lpadmin -p TestPrinter -v socket://192.168.1.100:9100 -m drv:///sample.drv/generic.ppd -E

# List printers
lpstat -p -d

# Remove printer
sudo lpadmin -x TestPrinter
```

### Check System Resources

**If discovery is slow**:
```bash
# Check CPU and memory
top

# Check network interfaces
ip addr show

# Check DNS resolution
nslookup printer-hostname
```

---

## Common Error Messages

### "Error: Failed to import required modules"

**Cause**: Missing Python dependencies

**Solution**:
```bash
pip install -r requirements.txt
```

### "SNMP Network error: Request timeout"

**Cause**: Printer doesn't support SNMP or port 161 is blocked

**Impact**: Not critical - IPP or PJL will still work

**Solution**: Ignore if printer is discovered successfully

### "IPP query failed: Connection refused"

**Cause**: Printer doesn't support IPP on port 631

**Impact**: Not critical - Socket or LPD might still work

**Solution**: Continue with manual model entry

### "lpadmin failed (Code 1): Unsupported format"

**Cause**: Invalid PPD file or wrong model name

**Solution**:
1. Validate PPD: `cupstestppd file.ppd`
2. Or search for correct model: `lpinfo -m | grep -i "brand"`

---

## Getting More Help

If you're still experiencing issues:

1. **Check the logs**:
```bash
sudo journalctl -u cups -n 100
sudo tail -100 /var/log/cups/error_log
```

2. **Gather system information**:
```bash
python3 --version
lpstat -t
lpinfo -v
lpinfo -m | head -20
uname -a
```

3. **Open a GitHub issue** with:
   - Your OS and version
   - Python version
   - CUPS version
   - Complete error message
   - Steps to reproduce
   - Relevant logs

---

## Additional Resources

- [CUPS Documentation](https://www.cups.org/documentation.html)
- [CUPS Command Reference](https://www.cups.org/doc/man-lpadmin.html)
- [IPP Standard](https://www.pwg.org/ipp/)
- [Project README](README.md)

---

**Need immediate help?** Open an issue on GitHub with your problem details!
