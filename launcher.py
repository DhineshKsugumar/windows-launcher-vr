#!/usr/bin/env python3
"""
mbvr:// Custom Protocol Launcher for Zoho WorkDrive True Sync
Launches Zoho WorkDrive True Sync desktop app from mbvr:// links (e.g., from Zoho CRM custom buttons).
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

# Zoho WorkDrive URL patterns
# Examples: https://workdrive.zoho.com/home/teams/.../folders/...
#           https://workdrive.zoho.com/folder/<folder_id>
#           https://workdrive.zoho.com/teams/.../privatespace/folders/...
WORKDRIVE_URL_PATTERN = re.compile(
    r"^https?://(?:[a-z0-9-]+\.)?workdrive\.zoho\.com/[^\s]+",
    re.IGNORECASE
)

# Executable name for Zoho WorkDrive True Sync
WORKDRIVE_EXE = "ZohoWorkDriveTS.exe"


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


def _find_via_registry() -> Optional[str]:
    """Try to find Zoho WorkDrive True Sync via Windows Uninstall registry."""
    base_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]
    for base in base_paths:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base, 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name, 0, winreg.KEY_READ)
                    try:
                        display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                        if display_name and "Zoho WorkDrive TrueSync" in display_name:
                            install_loc, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                            if install_loc:
                                exe = Path(install_loc.rstrip("\\")) / WORKDRIVE_EXE
                                if exe.exists():
                                    return str(exe)
                    except OSError:
                        pass
                    finally:
                        winreg.CloseKey(subkey)
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except OSError:
            pass
    return None


def find_workdrive_exe() -> Optional[str]:
    """Find ZohoWorkDriveTS.exe in common install locations."""
    # Try registry first (most reliable if app is installed)
    reg_path = _find_via_registry()
    if reg_path:
        return reg_path

    local_appdata = os.environ.get("LOCALAPPDATA", "")
    appdata = os.environ.get("APPDATA", "")
    userprofile = os.environ.get("USERPROFILE", "")

    locations = [
        # Verified path: C:\Program Files\Zoho\ZohoWorkDriveTS\bin\ZohoWorkDriveTS.exe
        Path("C:\\Program Files") / "Zoho" / "ZohoWorkDriveTS" / "bin" / WORKDRIVE_EXE,
        Path("C:\\Program Files (x86)") / "Zoho" / "ZohoWorkDriveTS" / "bin" / WORKDRIVE_EXE,
        # User AppData (fallbacks)
        Path(local_appdata) / "Zoho WorkDrive TrueSync" / WORKDRIVE_EXE,
        Path(local_appdata) / "Zoho" / "ZohoWorkDriveTS" / "bin" / WORKDRIVE_EXE,
        Path(appdata) / "Zoho WorkDrive TrueSync" / WORKDRIVE_EXE,
        Path(appdata) / "Zoho" / "ZohoWorkDriveTS" / "bin" / WORKDRIVE_EXE,
        Path(userprofile) / "AppData" / "Local" / "Zoho WorkDrive TrueSync" / WORKDRIVE_EXE,
        Path(userprofile) / "AppData" / "Roaming" / "Zoho WorkDrive TrueSync" / WORKDRIVE_EXE,
        Path("C:\\Program Files") / "Zoho WorkDrive TrueSync" / WORKDRIVE_EXE,
        Path("C:\\Program Files (x86)") / "Zoho WorkDrive TrueSync" / WORKDRIVE_EXE,
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
    Returns the WorkDrive URL or None if invalid.
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


def is_valid_workdrive_url(url: str) -> bool:
    """Check if the URL is a valid Zoho WorkDrive link."""
    return bool(WORKDRIVE_URL_PATTERN.match(url))


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


def launch_workdrive(workdrive_url: str) -> bool:
    """Launch Zoho WorkDrive True Sync with the WorkDrive URL."""
    exe_path = find_workdrive_exe()
    if not exe_path:
        log(f"{WORKDRIVE_EXE} not found in any known location")
        return False

    try:
        subprocess.Popen([exe_path, workdrive_url])
        log(f"Launched WorkDrive: {exe_path} with URL: {workdrive_url[:80]}...")
        return True
    except OSError as e:
        log(f"Failed to launch WorkDrive: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="mbvr:// Zoho WorkDrive Launcher")
    parser.add_argument("uri", nargs="?", help="mbvr:// URI (passed by Windows)")
    parser.add_argument("--install", action="store_true", help="Register protocol handler")
    args = parser.parse_args()

    if args.install:
        if install_protocol_handler():
            return 0
        return 1

    if not args.uri:
        log("No URI provided")
        return 1

    workdrive_url = parse_mbvr_uri(args.uri)
    if not workdrive_url:
        log(f"Failed to parse URI: {args.uri[:100]}")
        return 1

    log(f"Parsed target: {workdrive_url}")

    if not is_valid_workdrive_url(workdrive_url):
        log(f"Invalid WorkDrive URL: {workdrive_url[:100]}")
        return 1

    if launch_workdrive(workdrive_url):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
