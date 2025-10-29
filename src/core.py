#!/usr/bin/env python3

"""
core.py: Universal Printer Wizard - Backend Logic
(All-Async Architecture - Corrected Imports)

This script implements a multi-stage, universal discovery logic to find a
printer's CUPS URI and Model Name, abstracting away network complexity.

Required Libraries:
- pysnmp
- pyipp
- zeroconf
- aiohttp
- deepmerge
- yarl
"""

import socket
import sys
import asyncio
import time
from typing import Tuple, List, Optional, Dict, Any

# --- Dependency Checks & Imports ---

try:
    # Use the v3 architecture path
    from pysnmp.hlapi.v3arch.asyncio import (
        SnmpEngine, CommunityData, UdpTransportTarget,
        ContextData, ObjectType, ObjectIdentity, get_cmd
    )
    PYSNMP_AVAILABLE = True
except ImportError:
    print("Warning: 'pysnmp' library not found or import path incorrect. SNMP discovery (Stage 3B) will be skipped.", file=sys.stderr)
    PYSNMP_AVAILABLE = False

try:
    # 'pyipp' is the new 'python-ipp'
    from pyipp import IPP, Printer
    from pyipp.exceptions import IPPConnectionError
    PYIPP_AVAILABLE = True
except ImportError:
    print("Warning: 'pyipp' library not found. IPP discovery (Stage 3A) will be skipped.", file=sys.stderr)
    PYIPP_AVAILABLE = False

try:
    from zeroconf import ServiceBrowser, Zeroconf, ServiceListener
    ZEROCONF_AVAILABLE = True
except ImportError:
    print("Warning: 'zeroconf' library not found. Passive discovery (Stage 1) will be skipped.", file=sys.stderr)
    ZEROCONF_AVAILABLE = False

# --- Stage 1: Passive Discovery (The "Easy Button") ---

class _ZeroconfPrinterListener(ServiceListener):
    """Internal listener class for Zeroconf announcements."""
    def __init__(self):
        self.found_printers: Dict[str, Dict[str, Any]] = {}

    def _parse_service_info(self, zc: Zeroconf, type: str, name: str) -> Optional[Dict[str, Any]]:
        """Utility to get and parse info for a found service."""
        info = zc.get_service_info(type, name)
        if not info or not info.addresses: return None
        try:
            ip_address = socket.inet_ntoa(info.addresses[0])
            port = info.port
        except (OSError, IndexError):
            print(f"\n[Stage 1] Error parsing service info for {name}", file=sys.stderr)
            return None
        model = info.properties.get(b'product', b'').decode('utf-8').strip('()')
        if not model: model = info.properties.get(b'ty', b'').decode('utf-8')
        if not model: model = name.split('.')[0].replace('-', ' ').replace('_', ' ')
        return {"model": model, "uri": f"ipp://{ip_address}:{port}/ipp/print", "ip": ip_address}

    def update_service(self, zc: Zeroconf, type: str, name: str) -> None:
        printer_info = self._parse_service_info(zc, type, name)
        if printer_info and printer_info['uri'] not in self.found_printers:
            print(f"\n[Stage 1] Found service: {name}", end="", flush=True)
            self.found_printers[printer_info['uri']] = printer_info

    def remove_service(self, zc: Zeroconf, type: str, name: str) -> None: pass
    def add_service(self, zc: Zeroconf, type: str, name: str) -> None: pass

async def async_discover_printers_passive(scan_duration: int = 3) -> List[Dict[str, Any]]:
    """STAGE 1: Asynchronously listens on the network via mDNS/Zeroconf."""
    if not ZEROCONF_AVAILABLE:
        print("[Stage 1] Skipped. 'zeroconf' library not found.")
        return []
    print(f"[Stage 1] Passive mDNS discovery starting (scanning for {scan_duration} seconds)...")
    listener = _ZeroconfPrinterListener()
    zconf = Zeroconf()
    services = ["_ipp._tcp.local.", "_printer._tcp.local."]
    browser = ServiceBrowser(zconf, services, listener)
    for _ in range(scan_duration):
        print("...", end="", flush=True)
        await asyncio.sleep(1)
    browser.cancel()
    zconf.close()
    print("\n[Stage 1] Passive discovery complete.")
    return list(listener.found_printers.values())

# --- Stage 2: Active Port Scan (The "Manual" Path) ---

def _sync_scan_ports(ip: str, timeout: int = 1) -> Tuple[Optional[str], List[int]]:
    """Synchronous function to scan ports. Must be run in a thread."""
    PRINTER_PORTS = { 631: "IPP", 9100: "Raw Socket", 515: "LPD" }
    open_ports = []
    cups_uri: Optional[str] = None
    for port, protocol_name in PRINTER_PORTS.items():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    print(f"[{ip}] ✅ Port {port} open ({protocol_name})")
                    open_ports.append(port)
        except socket.error as e:
            print(f"[{ip}] ❌ Socket error on port {port}: {e}", file=sys.stderr)
    if 631 in open_ports: cups_uri = f"ipp://{ip}:631/ipp/print"
    elif 9100 in open_ports: cups_uri = f"socket://{ip}:9100"
    elif 515 in open_ports: cups_uri = f"lpd://{ip}/lp"
    return cups_uri, open_ports

async def _async_scan_ports_and_get_uri(ip: str, timeout: int = 1) -> Tuple[Optional[str], List[int]]:
    """STAGE 2: Async wrapper for the synchronous port scan."""
    print(f"[{ip}] Starting Stage 2: Port Scan (Async)...")
    try:
        cups_uri, open_ports = await asyncio.to_thread(_sync_scan_ports, ip, timeout)
        if cups_uri: print(f"[{ip}] ✨ URI selected: {cups_uri}")
        else: print(f"[{ip}] ❌ No known printer ports found.")
        return cups_uri, open_ports
    except Exception as e:
        print(f"[{ip}] ❌ Stage 2 failed: {e}", file=sys.stderr)
        return None, []

# --- Stage 3: Model Identification (The "Intelligence" Layer) ---

async def _get_model_name_ipp(ip: str) -> Optional[str]:
    """STAGE 3A: Asynchronously queries the printer using IPP (pyipp)."""
    if not PYIPP_AVAILABLE: return None
    print(f"[{ip}] Starting Stage 3A: IPP Model Query...")
    try:
        async with IPP(host=ip, port=631, base_path="/ipp/print") as ipp_client:
            printer: Printer = await ipp_client.printer()
            model_name = printer.name_make_and_model
            if model_name:
                print(f"[{ip}] ✅ IPP Success! Found model: {model_name}")
                return model_name.strip()
            print(f"[{ip}] ❌ IPP query successful, but model name was empty.")
    except (IPPConnectionError, asyncio.TimeoutError, socket.gaierror) as e:
        print(f"[{ip}] ❌ IPP query failed: {e}", file=sys.stderr)
    except Exception as e: # Catch other potential pyipp errors
        print(f"[{ip}] ❌ IPP query critical error: {e}", file=sys.stderr)
    return None

async def _get_model_name_snmp(ip: str) -> Optional[str]:
    """STAGE 3B: Asynchronously queries the printer using SNMP."""
    if not PYSNMP_AVAILABLE: return None
    print(f"[{ip}] Starting Stage 3B: SNMP Model Query...")
    SNMP_OID_SYS_DESCR = '1.3.6.1.2.1.1.1.0'
    model_name = None
    try:
        transport_target = await UdpTransportTarget.create((ip, 161))
        iterator = get_cmd(
            SnmpEngine(), CommunityData("public", mpModel=0), transport_target,
            ContextData(), ObjectType(ObjectIdentity(SNMP_OID_SYS_DESCR))
        )
        error_indication, error_status, error_index, var_binds = await iterator
        if error_indication: print(f"[{ip}] ❌ SNMP Network error: {error_indication}", file=sys.stderr)
        elif error_status: print(f"[{ip}] ❌ SNMP Protocol error: {str(error_status)}", file=sys.stderr)
        else:
            for var_bind in var_binds:
                if var_bind[0].prettyPrint() == SNMP_OID_SYS_DESCR:
                    model_name = str(var_bind[1]).strip()
                    print(f"[{ip}] ✅ SNMP Success! Found model: {model_name}")
                    return model_name
    except Exception as e:
        print(f"[{ip}] ❌ SNMP critical error: {e}", file=sys.stderr)
    return None

def _sync_get_model_name_pjl(ip: str, port: int = 9100, timeout: int = 2) -> Optional[str]:
    """Synchronous function for PJL query. Must be run in a thread."""
    PJL_COMMAND = b"\x1B%-12345X@PJL INFO ID\r\n\x1B%-12345X\r\n"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((ip, port))
            sock.sendall(PJL_COMMAND)
            response_bytes = sock.recv(1024)
            response_str = response_bytes.decode('utf-8', errors='ignore')
            if "@PJL" in response_str and ("ID" in response_str or "MODEL" in response_str):
                for line in response_str.splitlines():
                    if "ID" in line or "MODEL" in line:
                         model_name = line.split(":")[-1].split("=")[-1].strip().strip('"')
                         if model_name: return model_name
    except (socket.timeout, socket.error): pass
    return None

async def _get_model_name_pjl(ip: str, port: int = 9100, timeout: int = 2) -> Optional[str]:
    """STAGE 3C: Async wrapper for the synchronous PJL query."""
    print(f"[{ip}] Starting Stage 3C: PJL Model Query...")
    try:
        model_name = await asyncio.to_thread(_sync_get_model_name_pjl, ip, port, timeout)
        if model_name:
            print(f"[{ip}] ✅ PJL Success! Found model: {model_name}")
            return model_name
        else: print(f"[{ip}] ❌ PJL query failed or returned no data.")
    except Exception as e:
        print(f"[{ip}] ❌ PJL query critical error: {e}", file=sys.stderr)
    return None

# --- Stage 4: The Orchestrator (Main Wizard Logic) ---

async def async_discover_printer_by_ip(ip: str) -> Tuple[Optional[str], Optional[str]]:
    """Runs the full discovery logic for a single IP address."""
    cups_uri, open_ports = await _async_scan_ports_and_get_uri(ip)
    if not cups_uri: return None, None

    tasks = {"ipp": None, "snmp": None, "pjl": None}
    if 631 in open_ports and PYIPP_AVAILABLE: tasks["ipp"] = asyncio.create_task(_get_model_name_ipp(ip))
    if PYSNMP_AVAILABLE: tasks["snmp"] = asyncio.create_task(_get_model_name_snmp(ip))
    if 9100 in open_ports: tasks["pjl"] = asyncio.create_task(_get_model_name_pjl(ip))

    await asyncio.gather(*[task for task in tasks.values() if task], return_exceptions=True)

    model_name: Optional[str] = None
    if tasks["ipp"] and tasks["ipp"].done() and not tasks["ipp"].exception() and tasks["ipp"].result(): model_name = tasks["ipp"].result()
    if not model_name and tasks["snmp"] and tasks["snmp"].done() and not tasks["snmp"].exception() and tasks["snmp"].result(): model_name = tasks["snmp"].result()
    if not model_name and tasks["pjl"] and tasks["pjl"].done() and not tasks["pjl"].exception() and tasks["pjl"].result(): model_name = tasks["pjl"].result()

    if not model_name:
        print(f"[{ip}] ⚠️ All model discovery methods failed.")
        model_name = "Unknown"
    return cups_uri, model_name

# --- Main Test Block (To run core.py directly) ---
async def main_test():
    print("--- Universal Printer Wizard (Core Test Run) ---")
    printers_found = await async_discover_printers_passive(scan_duration=3)
    print(f"\n[Stage 1] Passively found: {len(printers_found)} printer(s)")
    for p in printers_found: print(f"  -> Model: {p['model']}, URI: {p['uri']}")
    TARGET_IP = "192.168.1.1"
    print(f"\n--- Running Active Discovery for {TARGET_IP} ---")
    start_time = time.time()
    final_uri, final_model = await async_discover_printer_by_ip(TARGET_IP)
    end_time = time.time()
    print(f"\n--- Wizard Result (Completed in {end_time - start_time:.2f}s) ---")
    if final_uri:
        print(f"  Recommended CUPS URI: {final_uri}")
        print(f"  Discovered Model:     {final_model}")
        if final_model == "Unknown": print("\n  ACTION: TUI should now ask user for the model name.")
        else: print("\n  ACTION: TUI can now proceed with automatic setup.")
    else: print(f"  No printer found at {TARGET_IP}.")

if __name__ == "__main__":
    try: asyncio.run(main_test())
    except KeyboardInterrupt: print("\nWizard test stopped by user.")