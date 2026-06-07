#!/usr/bin/env python3
"""Detect available printer routes and suggest startup commands.

The helper checks CUPS, serial device nodes, and an optional TiMini-Print CLI.
It prints ready-to-copy commands for this project.
"""

from __future__ import annotations

import argparse
import glob
import os
import shlex
import shutil
import subprocess
import sys
from typing import Sequence


def _run(cmd: Sequence[str], timeout: int = 8) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            list(cmd),
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
        return result.returncode, (result.stdout or ""), (result.stderr or "")
    except Exception as exc:
        return 2, "", str(exc)


def _detect_cups() -> tuple[bool, str]:
    lpstat = shutil.which("lpstat")
    if lpstat is None:
        return False, "lpstat not found"
    code, out, err = _run([lpstat, "-p", "-d"])
    if code != 0:
        return False, (err or out).strip() or "lpstat failed"
    text = out.strip()
    # Locale-agnostic: successful lpstat output usually means CUPS is reachable.
    has_printer = bool(text)
    return has_printer, text


def _detect_serial_ports() -> list[str]:
    candidates = [
        *sorted(glob.glob("/dev/tty.usb*")),
        *sorted(glob.glob("/dev/cu.usb*")),
        *sorted(glob.glob("/dev/ttyUSB*")),
        *sorted(glob.glob("/dev/ttyACM*")),
        *sorted(glob.glob("/dev/rfcomm*")),
    ]
    seen: set[str] = set()
    unique: list[str] = []
    for item in candidates:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def _resolve_timiniprint_cmd(raw_cmd: str) -> list[str] | None:
    parts = shlex.split(raw_cmd)
    if not parts:
        return None

    if len(parts) == 1:
        binary = parts[0]
        if shutil.which(binary) is not None:
            return [binary]
        if os.path.exists(binary):
            if binary.endswith(".py"):
                return [sys.executable, binary]
            return [binary]
        return None

    first = parts[0]
    if shutil.which(first) is not None or os.path.exists(first):
        return parts
    return None


def _scan_timiniprint(cmd: list[str], timeout: int) -> tuple[bool, str]:
    code, out, err = _run([*cmd, "--scan"], timeout=timeout)
    if code != 0:
        return False, (err or out).strip() or "--scan failed"
    return True, out.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto-detect printer backends for techConferenceAgent")
    parser.add_argument(
        "--timiniprint-cmd",
        default=os.getenv("PRINTER_TIMINIPRINT_CMD", "timiniprint_command_line.py"),
        help="TiMini-Print CLI command (default: env PRINTER_TIMINIPRINT_CMD or timiniprint_command_line.py)",
    )
    parser.add_argument(
        "--scan-timeout",
        type=int,
        default=30,
        help="Timeout in seconds for TiMini-Print --scan (default: 30)",
    )
    args = parser.parse_args()

    print("== Printer auto-detect ==")

    has_cups, cups_detail = _detect_cups()
    print("\n[CUPS]")
    print(cups_detail or "No details")

    ports = _detect_serial_ports()
    print("\n[Serial Ports]")
    if ports:
        for p in ports:
            print(f"- {p}")
    else:
        print("- none found")

    timini_cmd = _resolve_timiniprint_cmd(args.timiniprint_cmd)
    print("\n[TiMini-Print]")
    if timini_cmd is None:
        print("command not found")
        timini_ok = False
        timini_detail = ""
    else:
        timini_ok, timini_detail = _scan_timiniprint(timini_cmd, timeout=max(5, args.scan_timeout))
        print("cmd:", " ".join(shlex.quote(x) for x in timini_cmd))
        if timini_ok:
            print(timini_detail or "scan completed")
        else:
            print(timini_detail)

    print("\n[Suggested Commands]")
    if has_cups:
        print("PRINTER_ENABLED=1 PRINTER_BACKEND=cups python main.py")

    if ports:
        first = ports[0]
        print(
            "PRINTER_ENABLED=1 PRINTER_BACKEND=serial "
            f"PRINTER_SERIAL_PORT=\"{first}\" PRINTER_SERIAL_BAUDRATE=9600 python main.py"
        )

    if timini_cmd is not None:
        base = (
            "PRINTER_ENABLED=1 PRINTER_BACKEND=timiniprint "
            f"PRINTER_TIMINIPRINT_CMD=\"{args.timiniprint_cmd}\""
        )
        if ports:
            print(f"{base} PRINTER_TIMINIPRINT_SERIAL=\"{ports[0]}\" python main.py")
        else:
            print(f"{base} PRINTER_TIMINIPRINT_BLUETOOTH=\"PRINTER_NAME\" python main.py")

    if not has_cups and not ports and timini_cmd is None:
        print("No backend detected. Check cable, USB-serial driver, and TiMini-Print installation.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
