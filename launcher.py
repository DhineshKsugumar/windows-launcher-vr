#!/usr/bin/env python3
"""
mbvr:// Custom Protocol Launcher for Zoom
Launches Zoom desktop app from mbvr:// links (e.g., from Zoho CRM custom buttons).
Windows only.
"""

import argparse
import sys
from typing import Optional

if sys.platform != "win32":
    sys.exit("This launcher is for Windows only.")

import os
import re
import subprocess
import winreg
from pathlib import Path
from urllib.parse import unquote

# Protocol prefix to strip
PROTOCOL_PREFIX = "mbvr://"

# Zoom URL patterns
ZOOM_HTTPS_PATTERN = re.compile(
    r"^https?://(?:[a-z0-9-]+\.)?zoom\.us/(?:j|my|wc)/[^\s]+",
    re.IGNORECASE
)
ZOOM_DEEP_LINK_PATTERN = re.compile(
    r"^zoommtg://zoomus\?[^\s]+",
    re.IGNORECASE
)


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


def find_zoom_exe() -> Optional[str]:
    """Find Zoom.exe in common install locations."""
    locations = [
        Path(os.environ.get("APPDATA", "")) / "Zoom" / "bin" / "Zoom.exe",
        Path(os.environ.get("USERPROFILE", "")) / "AppData" / "Roaming" / "Zoom" / "bin" / "Zoom.exe",
        Path("C:\\Program Files (x86)") / "Zoom" / "bin" / "Zoom.exe",
        Path("C:\\Program Files") / "Zoom" / "bin" / "Zoom.exe",
    ]
    for path in locations:
        if path.exists():
            return str(path)
    return None


def parse_mbvr_uri(raw_arg: str) -> Optional[str]:
    """
    Parse mbvr:// URI from command-line argument.
    - Strip surrounding quotes
    - Strip mbvr:// prefix
    - URL-decode the remaining string
    Returns the meeting URL or None if invalid.
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

    # URL-decode
    try:
        s = unquote(s)
    except Exception as e:
        log(f"URL decode error: {e}")
        return None

    return s.strip() or None


def is_valid_zoom_url(url: str) -> bool:
    """Check if the URL is a valid Zoom meeting link."""
    return bool(
        ZOOM_HTTPS_PATTERN.match(url) or
        ZOOM_DEEP_LINK_PATTERN.match(url)
    )


def install_protocol_handler() -> bool:
    """Register mbvr:// protocol in HKEY_CURRENT_USER."""
    try:
        # sys.executable is the EXE path when packaged with PyInstaller
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


def launch_zoom(meeting_url: str) -> bool:
    """Launch Zoom desktop app with the meeting URL."""
    zoom_path = find_zoom_exe()
    if not zoom_path:
        log("Zoom.exe not found in any known location")
        return False

    try:
        subprocess.Popen([zoom_path, meeting_url])
        log(f"Launched Zoom: {zoom_path} with URL: {meeting_url[:80]}...")
        return True
    except OSError as e:
        log(f"Failed to launch Zoom: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="mbvr:// Zoom Launcher")
    parser.add_argument("uri", nargs="?", help="mbvr:// URI (passed by Windows)")
    parser.add_argument("--install", action="store_true", help="Register protocol handler")
    args = parser.parse_args()

    if args.install:
        if install_protocol_handler():
            # Show success (no console, so we could write to a temp file for GUI feedback)
            return 0
        return 1

    if not args.uri:
        log("No URI provided")
        return 1

    meeting_url = parse_mbvr_uri(args.uri)
    if not meeting_url:
        log(f"Failed to parse URI: {args.uri[:100]}")
        return 1

    log(f"Parsed target: {meeting_url}")

    if not is_valid_zoom_url(meeting_url):
        log(f"Invalid Zoom URL: {meeting_url[:100]}")
        return 1

    if launch_zoom(meeting_url):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
