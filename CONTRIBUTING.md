# Contributing to Universal Printer Wizard

Thank you for considering contributing to the Universal Printer Wizard! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with:
- A clear and descriptive title
- Steps to reproduce the problem
- Expected behavior vs actual behavior
- Your environment (OS, Python version, CUPS version)
- Any relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please open an issue with:
- A clear description of the feature
- Why this feature would be useful
- Any examples or mockups if applicable

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style guidelines
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Submit a pull request** with a clear description of the changes

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/printer_wizard.git
cd printer_wizard

# Install dependencies
pip install -r requirements.txt

# Test the modules independently
python3 core.py
python3 config.py
sudo python3 tui.py
```

## Code Style Guidelines

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular
- Use type hints where appropriate

## Testing

Before submitting a pull request:

1. Test all three modules independently
2. Test the full workflow with both discovery modes
3. Test with different printer types if possible
4. Ensure no new warnings or errors are introduced

## Module Structure

- **core.py**: Discovery engine (add new protocols here)
- **config.py**: CUPS integration (modify CUPS commands here)
- **tui.py**: User interface (improve UX here)

## Adding New Features

### Adding a New Discovery Protocol

1. Add the protocol implementation to `core.py`
2. Create an async function following the pattern: `async def _get_model_name_<protocol>(ip: str) -> Optional[str]`
3. Add it to the task orchestration in `async_discover_printer_by_ip()`
4. Update the README.md with protocol information

### Improving the TUI

1. Modify `tui.py`
2. Use Rich library components for consistency
3. Ensure error handling and user feedback
4. Test with various terminal sizes

## Commit Message Guidelines

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests when relevant

Examples:
```
Add support for AirPrint discovery
Fix IPP timeout on slow networks
Improve error messages for CUPS failures
```

## Code Review Process

All submissions require review before merging. We'll:
- Check code quality and style
- Verify functionality
- Ensure documentation is updated
- Test on different systems if possible

## Community

- Be respectful and constructive
- Help others when you can
- Focus on what's best for the project

## Questions?

Feel free to open an issue for any questions about contributing!

---

Thank you for helping make Universal Printer Wizard better! 🎉
