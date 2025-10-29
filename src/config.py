#!/usr/bin/env python3

"""
config.py: Printer Configurator - CUPS Integration Layer

This module takes the URI and Model/PPD info and executes the
necessary lpadmin command to configure the printer in CUPS,
choosing between -m (model name) and -P (PPD file path).
"""

import asyncio
import sys
import os # Needed to check if the path exists
from typing import Tuple, Optional

async def configure_cups_printer(
    printer_name: str,
    cups_uri: str,
    model_info: str, # Can be a model name OR a file path
    default: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    Asynchronously executes lpadmin, using -m for model names
    or -P for PPD file paths.
    """
    print(f"\n[CUPS Config] Starting configuration for '{printer_name}'...")

    # Determine if model_info is a file path or a model name
    is_file_path = model_info.endswith('.ppd') or model_info.startswith('/')
    use_ppd_param = False

    if is_file_path:
        # Check if the PPD file actually exists
        if os.path.exists(model_info):
            print(f"[CUPS Config] Using PPD file path: {model_info}")
            use_ppd_param = True
        else:
            error_msg = f"Error: PPD file specified does not exist: {model_info}"
            print(f"[CUPS Config] ❌ {error_msg}")
            return False, error_msg
    else:
        print(f"[CUPS Config] Using model name: {model_info}")

    # Build the base lpadmin command
    command = ['lpadmin', '-p', printer_name, '-v', cups_uri]

    # Add the correct model/PPD parameter
    if use_ppd_param:
        command.extend(['-P', model_info]) # Use -P for PPD file path
    else:
        command.extend(['-m', model_info]) # Use -m for model name

    # Enable the printer
    command.append('-E')

    # Set as default if requested
    if default:
        command.extend(['-d', printer_name])

    print(f"[CUPS Config] Executing: {' '.join(command)}")

    # Execute the command
    try:
        # Note: Running lpadmin often requires root privileges.
        # This might fail if the script isn't run with sudo.
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return_code = process.returncode

        if return_code == 0:
            print(f"[CUPS Config] ✅ Printer '{printer_name}' installed successfully.")
            return True, None
        else:
            error_message = stderr.decode().strip()
            # Provide a hint if permission denied is likely
            if "Forbidden" in error_message or "permission denied" in error_message.lower():
                error_message += "\nHint: Try running the TUI script with 'sudo'."
            print(f"[CUPS Config] ❌ lpadmin failed (Code {return_code}): {error_message}")
            return False, error_message

    except FileNotFoundError:
        return False, "Error: 'lpadmin' command not found. Is CUPS installed and in PATH?"
    except PermissionError:
         return False, "Error: Permission denied running lpadmin. Try running the TUI script with 'sudo'."
    except Exception as e:
        return False, f"Critical error during process execution: {e}"

# --- Test Block ---
async def main_config_test():
    """Test function for the configurator."""
    # Test Scenario 1: Using a model name (like from lpinfo -m)
    URI_1 = "socket://127.0.0.1:9101" # Safe dummy URI
    MODEL_NAME_1 = "drv:///sample.drv/deskjet.ppd" # Example model name
    ALIAS_1 = "TestPrinter_Model"

    # Test Scenario 2: Using a local PPD file path
    URI_2 = "socket://127.0.0.1:9102" # Safe dummy URI
    # Create a dummy PPD file for testing
    PPD_PATH_2 = "./dummy_printer.ppd"
    with open(PPD_PATH_2, "w") as f:
        f.write("*PPD-Adobe: \"4.3\"\n*ModelName: \"Dummy Test Printer\"\n")
    ALIAS_2 = "TestPrinter_PPD"

    print("--- Configurator Test Run ---")
    print("Attempting to add two test printers (may require sudo)...")

    success1, error1 = await configure_cups_printer(ALIAS_1, URI_1, MODEL_NAME_1)
    if not success1: print(f"Test 1 Failed: {error1}")

    success2, error2 = await configure_cups_printer(ALIAS_2, URI_2, PPD_PATH_2, default=True)
    if not success2: print(f"Test 2 Failed: {error2}")

    # Cleanup dummy file
    if os.path.exists(PPD_PATH_2):
        os.remove(PPD_PATH_2)

    if success1 or success2:
        print("\nNOTE: Use 'lpstat -p' to see printers.")
        print("Use 'lpadmin -x <printer_name>' to remove test printers.")

if __name__ == "__main__":
    try: asyncio.run(main_config_test())
    except KeyboardInterrupt: print("\nTest cancelled.")