# Security Policy

## Supported Versions

We currently support the following versions with security updates:

| Version | Supported |
| ------- | --------- |
| 1.0.x   | ✅        |

## Reporting a Vulnerability

We take the security of the Universal Printer Wizard seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. Email the maintainers directly at: [tunahanyrd@gmail.com]
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

### What to Expect

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: We aim to release security patches within 30 days

### Disclosure Policy

- We will work with you to understand and validate the vulnerability
- We will keep you informed about the progress toward a fix
- Once the fix is released, we will publicly acknowledge your responsible disclosure (unless you prefer to remain anonymous)

## Security Considerations

### Running with Root Privileges

The Universal Printer Wizard requires `sudo` privileges to configure CUPS printers. This is necessary for the `lpadmin` command. Be aware that:

- The tool executes system commands with elevated privileges
- Review the source code before running with sudo
- Only run trusted versions from official sources

### Network Security

The wizard performs network operations:

- Listens for mDNS broadcasts (port 5353)
- Connects to printers on ports 631 (IPP), 9100 (Raw), 515 (LPD)
- Sends SNMP queries on port 161

Ensure your firewall rules are appropriate for your security requirements.

### Input Validation

The wizard validates:

- PPD file paths and extensions
- IP address formats
- CUPS model names

However, always:

- Only use PPD files from trusted sources
- Verify printer IP addresses
- Use official manufacturer drivers when possible

### Dependencies

We use several third-party Python packages. Keep them updated:

```bash
pip install --upgrade -r requirements.txt
```

Check for known vulnerabilities:

```bash
pip install safety
safety check -r requirements.txt
```

## Best Practices

1. **Keep the tool updated**: Always use the latest version
2. **Review PPD files**: Only use PPD files from trusted sources
3. **Network security**: Use firewalls and network segmentation
4. **Audit logs**: Check `/var/log/cups/` for unusual activity
5. **Minimal permissions**: Only grant sudo when needed

## Known Limitations

- Requires root privileges for printer installation
- Network discovery can expose information about printers on your network
- SNMP uses cleartext "public" community string by default

## Security Fixes

Security fixes will be released as patch versions (e.g., 1.0.1) and documented in the [CHANGELOG.md](CHANGELOG.md).

---

Thank you for helping keep Universal Printer Wizard secure!
