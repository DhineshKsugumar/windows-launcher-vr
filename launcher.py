#!/usr/bin/env python3
"""
mbvr:// Custom Protocol Launcher
Opens local files with their default application via Start-Process.
Format: mbvr://<local file path>
Example: mbvr://C:/Users/Name/Documents/file.pdf
Windows only.
"""

import argparse
import sys
from typing import Optional

if sys.platform != "win32":
    sys.exit("This launcher is for Windows only.")

import os
import subprocess
import winreg
from pathlib import Path
from urllib.parse import unquote

# Protocol prefix to strip
PROTOCOL_PREFIX = "mbvr://"


def get_log_path() -> Path:
    """Return path to log file in %TEMP%."""
    temp = os.environ.get("TEMP", os.environ.get("TMP", "."))
    return Path(temp) / "mbvr_launcher.log"


def log(message: str) -> None:
    """Write message to log file."""
    try:
        log_path = get_log_path()
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")
    except OSError:
        pass


def parse_mbvr_uri(raw_arg: str) -> Optional[str]:
    """
    Parse mbvr:// URI from command-line argument.
    - Strip surrounding quotes
    - Strip mbvr:// prefix
    - URL-decode the remaining string (handles %20, %3A, etc.)
    Returns the local file path or None if invalid.
    """
    if not raw_arg:
        return None

    # Strip surrounding quotes (Windows may pass "mbvr://...")
    s = raw_arg.strip().strip('"').strip("'")

    # Strip mbvr:// prefix (case-insensitive)
    if s.lower().startswith(PROTOCOL_PREFIX):
        s = s[len(PROTOCOL_PREFIX):]
    else:
        log(f"Warning: URI does not start with {PROTOCOL_PREFIX}: {raw_arg[:80]}")
        return None

    # URL-decode (handles %20 for spaces, %3A for :, etc.)
    try:
        s = unquote(s)
    except Exception as e:
        log(f"URL decode error: {e}")
        return None

    s = s.strip()
    if not s:
        return None

    # Normalize path separators for Windows
    return s.replace("/", "\\")


def open_with_default_app(file_path: str) -> bool:
    """Open file with default application using Start-Process (PowerShell)."""
    try:
        # Escape single quotes for PowerShell
        escaped = file_path.replace("'", "''")
        cmd = ["powershell", "-NoProfile", "-Command", f"Start-Process -FilePath '{escaped}'"]
        # Hide PowerShell window (CREATE_NO_WINDOW = 0x08000000)
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        subprocess.Popen(cmd, creationflags=creationflags)
        log(f"Opened with default app: {file_path}")
        return True
    except OSError as e:
        log(f"Failed to open: {e}")
        return False


def install_protocol_handler() -> bool:
    """Register mbvr:// protocol in HKEY_CURRENT_USER."""
    try:
        exe_path = os.path.abspath(sys.executable)

        key_path = r"Software\Classes\mbvr"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "URL:mbvr Protocol")
            winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")

        cmd_key_path = r"Software\Classes\mbvr\shell\open\command"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_key_path) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, f'"{exe_path}" "%1"')

        log(f"Protocol installed: {exe_path}")
        return True
    except OSError as e:
        log(f"Install failed: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="mbvr:// File Launcher (opens with default app)")
    parser.add_argument("uri", nargs="?", help="mbvr:// URI with local file path (passed by Windows)")
    parser.add_argument("--install", action="store_true", help="Register protocol handler")
    args = parser.parse_args()

    if args.install:
        if install_protocol_handler():
            return 0
        return 1

    if not args.uri:
        log("No URI provided")
        return 1

    file_path = parse_mbvr_uri(args.uri)
    if not file_path:
        log(f"Failed to parse URI: {args.uri[:100]}")
        return 1

    log(f"Parsed target: {file_path}")

    if open_with_default_app(file_path):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
