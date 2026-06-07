"""Printer controller for macOS and Raspberry Pi via CUPS ``lp``.

Printing is optional and resilient: if no printer is configured, the app keeps
running and logs what happened. This keeps development smooth on macOS while
using the same code path later on the Raspberry Pi.
"""

from __future__ import annotations

import glob
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable

import config


class PrinterController:
    def __init__(self):
        self._lock = threading.Lock()
        self._enabled = config.PRINTER_ENABLED
        self._backend = "none"
        self._lp_bin = shutil.which("lp")
        self._serial_port = None
        self._serial_baudrate = config.PRINTER_SERIAL_BAUDRATE
        self._raw_device = None
        self._timiniprint_cmd: list[str] | None = None

        if not self._enabled:
            print("[printer] disabled (PRINTER_ENABLED=0)")
            return

        requested = config.PRINTER_BACKEND
        if requested not in {"auto", "cups", "serial", "raw", "timiniprint"}:
            requested = "auto"

        if requested == "timiniprint" and self._configure_timiniprint():
            self._backend = "timiniprint"
            return

        if requested in {"auto", "cups"} and self._configure_cups():
            self._backend = "cups"
            return

        if requested in {"auto", "serial"} and self._configure_serial():
            self._backend = "serial"
            return

        if requested in {"auto", "raw"} and self._configure_raw():
            self._backend = "raw"
            return

        self._enabled = False
        print(
            "[printer] no usable backend found (cups/serial/raw/timiniprint). "
            "Set PRINTER_BACKEND and device settings."
        )

    def _configure_timiniprint(self) -> bool:
        cmd_parts = shlex.split(config.PRINTER_TIMINIPRINT_CMD)
        if not cmd_parts:
            return False

        if len(cmd_parts) == 1:
            candidate = cmd_parts[0]
            candidate_path = Path(candidate)
            if not candidate_path.is_absolute():
                repo_relative = Path(config.BASE_DIR) / candidate
                if repo_relative.exists():
                    candidate_path = repo_relative

            if candidate_path.suffix == ".py" and candidate_path.exists():
                cmd_parts = [sys.executable, str(candidate_path)]
            elif os.path.sep in candidate:
                if not candidate_path.exists():
                    return False
                cmd_parts = [str(candidate_path)]
            elif shutil.which(candidate) is None:
                return False
        self._timiniprint_cmd = cmd_parts
        print(f"[printer] ready via timiniprint cmd={' '.join(self._timiniprint_cmd)}")
        return True

    def _configure_cups(self) -> bool:
        if self._lp_bin is None:
            return False
        printer = config.PRINTER_NAME or "<system-default>"
        print(f"[printer] ready via cups lp, destination={printer}")
        return True

    def _configure_serial(self) -> bool:
        try:
            import serial  # noqa: F401
        except Exception:
            return False

        if config.PRINTER_SERIAL_PORT:
            self._serial_port = config.PRINTER_SERIAL_PORT
            print(
                "[printer] ready via serial, "
                f"port={self._serial_port} baud={self._serial_baudrate}"
            )
            return True

        candidates = [
            *sorted(glob.glob("/dev/tty.usb*")),
            *sorted(glob.glob("/dev/cu.usb*")),
            *sorted(glob.glob("/dev/ttyUSB*")),
            *sorted(glob.glob("/dev/ttyACM*")),
        ]
        if not candidates:
            return False

        self._serial_port = candidates[0]
        print(
            "[printer] ready via serial auto-detect, "
            f"port={self._serial_port} baud={self._serial_baudrate}"
        )
        return True

    def _configure_raw(self) -> bool:
        if config.PRINTER_RAW_DEVICE:
            self._raw_device = config.PRINTER_RAW_DEVICE
        elif Path("/dev/usb/lp0").exists():
            self._raw_device = "/dev/usb/lp0"

        if self._raw_device is None:
            return False

        print(f"[printer] ready via raw device, path={self._raw_device}")
        return True

    def start(self, _scene_config) -> None:
        """Compatibility with other controllers; printer has no loop to start."""

    def stop(self) -> None:
        """Compatibility with other controllers; no background thread to stop."""

    def close(self) -> None:
        self.stop()

    def print_scene_ticket(self, scene, index: int, total: int) -> None:
        if not self._enabled:
            return
        lines = [
            f"Scene: {scene.name}",
            f"Scene ID: {scene.id}",
            f"Position: {index}/{total}",
            "",
            f"LED: {scene.leds.animation_name}",
            f"Servo: {scene.servo.angle_profile}",
            f"Audio: {scene.audio.filename or 'none'}",
        ]
        self._submit_print_job(self._print_text, "Conference Robot Scene", lines)

    def print_test_ticket(self, scene, index: int, total: int) -> None:
        if not self._enabled:
            print("[printer] test skipped, printer integration is disabled")
            return
        lines = [
            "Printer integration test",
            "",
            f"Current scene: {scene.name}",
            f"Position: {index}/{total}",
            f"Host mode: {'mock' if config.IS_MOCK else 'real-hardware'}",
        ]
        self._submit_print_job(self._print_text, "Conference Robot Printer Test", lines)

    def print_pdf(self, pdf_path: str | None) -> None:
        if not self._enabled:
            print("[printer] scene print skipped, printer disabled")
            return
        if not pdf_path:
            print("[printer] scene has no pdf configured")
            return

        full_path = Path(pdf_path)
        if not full_path.is_absolute():
            full_path = Path(config.BASE_DIR) / full_path
        if not full_path.exists():
            print(f"[printer] pdf not found: {full_path}")
            return

        self._submit_print_job(self._print_pdf, full_path)

    def _print_pdf(self, full_path: Path) -> None:
        with self._lock:
            try:
                if self._backend == "timiniprint":
                    self._print_pdf_via_timiniprint(full_path)
                    return

                if self._backend == "cups":
                    self._print_file_via_cups(full_path)
                    return

                print(f"[printer] backend '{self._backend}' does not support PDF scene print")
            except Exception as exc:
                print(f"[printer] pdf print failed: {exc}")

    def _submit_print_job(self, fn, *args) -> None:
        thread = threading.Thread(
            target=self._run_print_job,
            args=(fn, *args),
            daemon=True,
        )
        thread.start()

    def _run_print_job(self, fn, *args) -> None:
        try:
            fn(*args)
        except Exception as exc:
            print(f"[printer] print job failed: {exc}")

    def _print_text(self, title: str, lines: Iterable[str]) -> None:
        with self._lock:
            try:
                text = self._compose_text(title, lines)
                if self._backend == "cups":
                    self._print_via_cups(text)
                elif self._backend == "serial":
                    self._print_via_serial(text)
                elif self._backend == "raw":
                    self._print_via_raw(text)
                elif self._backend == "timiniprint":
                    self._print_via_timiniprint(text)
                else:
                    print("[printer] print skipped, backend not configured")
            except Exception as exc:
                print(f"[printer] print failed: {exc}")

    def _compose_text(self, title: str, lines: Iterable[str]) -> str:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = [
            title,
            f"Generated: {stamp}",
            "=" * 42,
            *list(lines),
            "",
            "",
            "",
        ]
        return "\n".join(body)

    def _print_via_cups(self, text: str) -> None:
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False, encoding="utf-8"
            ) as temp_file:
                temp_path = Path(temp_file.name)
                temp_file.write(text)

            cmd = [self._lp_bin] if self._lp_bin is not None else ["lp"]
            if config.PRINTER_NAME:
                cmd.extend(["-d", config.PRINTER_NAME])
            cmd.append(str(temp_path))
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                error_text = (result.stderr or result.stdout).strip()
                print(f"[printer] cups print failed: {error_text}")
                return
            output = (result.stdout or "").strip()
            print(f"[printer] cups queued: {output or 'lp command succeeded'}")
        finally:
            if temp_path is not None:
                try:
                    temp_path.unlink(missing_ok=True)
                except Exception:
                    pass

    def _print_file_via_cups(self, path: Path) -> None:
        cmd = [self._lp_bin] if self._lp_bin is not None else ["lp"]
        if config.PRINTER_NAME:
            cmd.extend(["-d", config.PRINTER_NAME])
        cmd.append(str(path))
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            error_text = (result.stderr or result.stdout).strip()
            print(f"[printer] cups print failed: {error_text}")
            return
        output = (result.stdout or "").strip()
        print(f"[printer] cups queued: {output or 'lp command succeeded'}")

    def _print_via_serial(self, text: str) -> None:
        if self._serial_port is None:
            raise RuntimeError("serial port not configured")
        import serial

        payload = bytearray()
        payload.extend(b"\x1b@")  # ESC @ reset/init
        payload.extend(text.encode("ascii", errors="replace"))
        payload.extend(b"\n\n")
        if config.PRINTER_ESC_POS_CUT:
            payload.extend(b"\x1dV\x00")  # GS V 0 full cut

        with serial.Serial(self._serial_port, self._serial_baudrate, timeout=2) as ser:
            ser.write(payload)
            ser.flush()
        print(f"[printer] serial queued on {self._serial_port}")

    def _print_via_raw(self, text: str) -> None:
        if self._raw_device is None:
            raise RuntimeError("raw device path not configured")
        payload = bytearray()
        payload.extend(b"\x1b@")
        payload.extend(text.encode("ascii", errors="replace"))
        payload.extend(b"\n\n")
        if config.PRINTER_ESC_POS_CUT:
            payload.extend(b"\x1dV\x00")
        with open(self._raw_device, "wb") as raw_dev:
            raw_dev.write(payload)
            raw_dev.flush()
        print(f"[printer] raw queued on {self._raw_device}")

    def _print_via_timiniprint(self, text: str) -> None:
        if self._timiniprint_cmd is None:
            raise RuntimeError("timiniprint command not configured")

        cmd = [*self._timiniprint_cmd]
        if config.PRINTER_TIMINIPRINT_SERIAL:
            cmd.extend(["--serial", config.PRINTER_TIMINIPRINT_SERIAL])
        if config.PRINTER_TIMINIPRINT_BLUETOOTH:
            cmd.extend(["--bluetooth", config.PRINTER_TIMINIPRINT_BLUETOOTH])
        if config.PRINTER_TIMINIPRINT_CONFIG:
            cmd.extend(["--printer-config", config.PRINTER_TIMINIPRINT_CONFIG])
        cmd.extend(["--text", text])
        self._run_timiniprint_command(cmd, "timiniprint")

    def _print_pdf_via_timiniprint(self, path: Path) -> None:
        if self._timiniprint_cmd is None:
            print("[printer] timiniprint command not configured")
            return

        cmd = [*self._timiniprint_cmd]
        if config.PRINTER_TIMINIPRINT_SERIAL:
            cmd.extend(["--serial", config.PRINTER_TIMINIPRINT_SERIAL])
        if config.PRINTER_TIMINIPRINT_BLUETOOTH:
            cmd.extend(["--bluetooth", config.PRINTER_TIMINIPRINT_BLUETOOTH])
        if config.PRINTER_TIMINIPRINT_CONFIG:
            cmd.extend(["--printer-config", config.PRINTER_TIMINIPRINT_CONFIG])
        cmd.extend([
            "--darkness",
            str(max(1, min(5, config.PRINTER_TIMINIPRINT_DARKNESS))),
            "--pdf-page-gap",
            str(max(0, config.PRINTER_TIMINIPRINT_PDF_PAGE_GAP)),
            str(path),
        ])

        self._run_timiniprint_command(cmd, "timiniprint pdf")

    def _run_timiniprint_command(self, cmd: list[str], label: str) -> None:
        retries = 2
        for attempt in range(1, retries + 1):
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                output = (result.stdout or "").strip()
                print(f"[printer] {label} queued: {output or 'ok'}")
                return

            detail = (result.stderr or result.stdout).strip()
            if attempt < retries and self._is_transient_bt_error(detail):
                print(
                    f"[printer] {label} transient bluetooth issue, retrying "
                    f"({attempt}/{retries - 1})"
                )
                time.sleep(1.0)
                continue
            print(f"[printer] {label} failed: {detail}")
            return

    @staticmethod
    def _is_transient_bt_error(detail: str) -> bool:
        text = detail.lower()
        return (
            "bluetooth connection failed" in text
            or "service discovery" in text
            or "retrying over ble" in text
        )
