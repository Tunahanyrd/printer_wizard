#!/usr/bin/env python3

"""
tui.py: Universal Printer Wizard - TUI Application

This is the main entry point for the user.
It uses 'rich' to create a TUI, calls 'core.py' to discover,
and calls 'config.py' to install.

Requires: 'rich'
"""

import asyncio
import sys
import os # Necessary for os.path.exists if PPD option is used
from rich.console import Console
from rich.prompt import Prompt, Confirm, InvalidResponse
from rich.status import Status
from rich.panel import Panel
from rich.table import Table
from rich.text import Text # CRITICAL: Import Text for explicit construction
from rich.markup import escape # CRITICAL: Ensure this import is present
from typing import Optional

# Import the main functions from our other files
try:
    # Try relative import first (when used as module)
    from .core import async_discover_printers_passive, async_discover_printer_by_ip
    from .config import configure_cups_printer
except ImportError:
    try:
        # Fall back to absolute import (when run directly)
        from core import async_discover_printers_passive, async_discover_printer_by_ip
        from config import configure_cups_printer
    except ImportError as e:
        print(f"Error: Failed to import required modules (core.py, config.py). {e}")
        print("Please ensure core.py and config.py are in the same directory.")
        sys.exit(1)

console = Console()

async def main():
    """Runs the main TUI application flow."""
    
    console.print(Panel("[bold cyan]Universal Printer Wizard[/bold cyan]", title="Welcome", expand=False))
    
    cups_uri: Optional[str] = None
    model_name_or_path: Optional[str] = None # Will store either name or path

    # --- STAGE 1: PASSIVE DISCOVERY ---
    console.print("\n[bold]Stage 1: Passive Network Scan[/bold]")
    if Confirm.ask("Search network for automatically discoverable printers? (Recommended)", default=True):
        with console.status("[bold green]Listening to network... (5 seconds)", spinner="dots"):
            found_printers = await async_discover_printers_passive(scan_duration=5)
        if found_printers:
            console.print(f"[bold green]✅ Found {len(found_printers)} printer(s) automatically![/bold green]")
            table = Table(title="Discovered Printers")
            table.add_column("No", style="cyan"); table.add_column("Model", style="magenta"); table.add_column("URI", style="green")
            for i, p in enumerate(found_printers): table.add_row(str(i + 1), p['model'], p['uri'])
            console.print(table)
            choice = Prompt.ask("Enter number to install (or 'm' for manual IP)", default="1")
            if choice.lower() != 'm':
                try:
                    chosen = found_printers[int(choice) - 1]
                    cups_uri = chosen['uri']
                    model_name_or_path = chosen['model'] # Use model name found
                except (ValueError, IndexError): console.print("[red]Invalid selection. Switching to manual mode.[/red]")
        else: console.print("[yellow]No printers found via passive discovery.[/yellow]")

    # --- STAGE 2: ACTIVE DISCOVERY (MANUAL IP) ---
    if not cups_uri:
        console.print("\n[bold]Stage 2: Active Scan via IP Address[/bold]")
        console.print("Enter printer IP. Default [cyan]192.168.1.1[/cyan] is often the router/gateway (for USB-connected printers).")
        ip_address = Prompt.ask("Printer IP Address", default="192.168.1.1")
        with console.status(f"[bold green]Scanning {ip_address}... (This may take 6-10 seconds)", spinner="earth"):
            cups_uri, discovered_model = await async_discover_printer_by_ip(ip_address)
        if not cups_uri:
            console.print(f"[bold red]❌ ERROR: No known ports found at {ip_address}. Exiting.[/bold red]")
            return
        model_name_or_path = discovered_model # Store the potentially 'Unknown' model

    # --- STAGE 3: CONFIRMATION & MANUAL MODEL ENTRY ---
    console.print("\n[bold]Stage 3: Installation Details[/bold]")
    console.print(Panel(f"[bold]Discovered URI:[/bold] [green]{cups_uri}[/green]\n[bold]Discovered Model/Path:[/bold] [magenta]{model_name_or_path}[/magenta]", title="Discovery Result"))
    printer_alias = Prompt.ask("Enter a descriptive name for this printer (e.g., Office_Laser)", default="MyPrinter")

    # Ask HOW to specify the model if needed
    if model_name_or_path == "Unknown" or Confirm.ask("Manually specify the driver model/PPD?", default=(model_name_or_path == "Unknown")):
        console.print(Panel( "[bold red]⚠️ DRIVER REQUIRED[/bold red]: Model could not be auto-detected.", title="Model Missing", border_style="red"))
        
        use_ppd_file = Confirm.ask("Do you have a local PPD file for this printer?", default=False)

        if use_ppd_file:
            # PPD File Path option
            console.print("\n[yellow]Provide the full path to your PPD file.[/yellow]")
            while True:
                ppd_path = Prompt.ask("[bold yellow]Enter PPD file path[/bold yellow]")
                # Check existence and extension rigorously
                if os.path.exists(ppd_path) and os.path.isfile(ppd_path) and ppd_path.lower().endswith(('.ppd', '.ppd.gz')):
                    model_name_or_path = ppd_path # Store the file path
                    break
                else:
                    console.print("[red]Error: File not found, is not a file, or not a valid .ppd/.ppd.gz file. Please try again.[/red]")
        else:
            # CUPS Model Name option
            console.print("\n[yellow]Provide the exact CUPS driver name (model) from the system list.[/yellow]")
            try: grep_suggestion = printer_alias.split('_')[0].split('-')[0]
            except IndexError: grep_suggestion = 'printer'
            console.print(Panel(f"1. RUN: [green]lpinfo -m | grep -i '{grep_suggestion}'[/green]\n"
                                  "2. COPY the driver name (e.g., [yellow]drv:///...[/yellow])\n"
                                  "3. PASTE below.", title="Action Required", border_style="cyan"))
            model_name_input = Prompt.ask("[bold yellow]Paste the exact CUPS driver model name here[/bold yellow]")
            model_name_or_path = model_name_input # Store the model name

    # --- Final Confirmation (with MarkupError fix using explicit Text object) ---
    
    # Escape user inputs just to be safe, though Text() should handle plain text correctly
    safe_model_info = escape(model_name_or_path or "Unknown") # Ensure not None
    safe_alias = escape(printer_alias or "Printer") # Ensure not None
    
    # --- FINAL FIX 3: Construct prompt using explicit Text objects ---
    confirmation_text = Text("\nInstall printer ")
    confirmation_text.append(safe_alias, style="bold cyan")
    confirmation_text.append(" using driver/PPD ")
    confirmation_text.append(safe_model_info, style="bold magenta")
    confirmation_text.append("?")
    # --- End of explicit Text construction ---

    # Final confirmation using the constructed Text object
    if not Confirm.ask(confirmation_text, default=True):
        console.print("Installation cancelled. Exiting.")
        return
        
    # --- STAGE 4: INSTALLATION ---
    with console.status(f"[bold green]Adding '{printer_alias}' to CUPS...", spinner="monkey"):
        success, error_msg = await configure_cups_printer(
            printer_name=printer_alias,
            cups_uri=cups_uri,
            model_info=model_name_or_path # Pass the raw input to config.py
        )

    if success:
        console.print(Panel(f"✅ [bold green]Success![/bold green]\nPrinter '{printer_alias}' has been installed.", title="Installation Complete"))
        # Ask if user wants to set as default
        if Confirm.ask("Set this printer as the system default?", default=False):
             with console.status(f"Setting {printer_alias} as default..."):
                 # Note: Setting default might also require sudo
                 proc = await asyncio.create_subprocess_exec('lpadmin', '-d', printer_alias)
                 await proc.wait()
                 if proc.returncode == 0:
                     console.print(f"[green]'{printer_alias}' is now the default printer.[/green]")
                 else:
                     console.print(f"[red]Failed to set default printer (check permissions?).[/red]")
    else:
        console.print(Panel(f"❌ [bold red]ERROR![/bold red]\n{error_msg}", title="Installation Failed"))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[red]Cancelled by user. Exiting.[/red]")