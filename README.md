# mbvr:// Zoho WorkDrive Launcher for Windows

A Windows custom URL protocol launcher that opens **Zoho WorkDrive True Sync** desktop app from `mbvr://` links. Designed for use with Zoho CRM custom buttons via `openUrl("mbvr://<workdrive-link>")`.

## Quick Start

1. **Build the EXE** (on Windows with Python):
   ```bash
   pip install pyinstaller
   pyinstaller --noconsole --onefile --name mbvr_launcher launcher.py
   ```

2. **Install the protocol handler**:
   ```bash
   dist\mbvr_launcher.exe --install
   ```

3. **Test**: Click a link like `mbvr://https://workdrive.zoho.com/folder/abc123` — Zoho WorkDrive True Sync should open with that folder.

---

## Build Instructions (PyInstaller)

### Prerequisites
- Windows 10/11
- Python 3.8+
- Zoho WorkDrive True Sync installed

### Build Command
```bash
pyinstaller --noconsole --onefile --name mbvr_launcher launcher.py
```

**Output**: `dist/mbvr_launcher.exe`

### Alternative: Use build.bat
```bash
build.bat
```

---

## Installation

### Method 1: Using the launcher (recommended)
```bash
mbvr_launcher.exe --install
```

### Method 2: Manual registry (.reg file)
1. Edit `install_mbvr_protocol.reg`
2. Replace `C:\path\to\mbvr_launcher.exe` with your actual EXE path (use `\\` for backslashes)
3. Double-click the .reg file → Yes to merge

---

## Accepted Link Formats

| Format | Example |
|--------|---------|
| WorkDrive folder | `mbvr://https://workdrive.zoho.com/folder/<folder_id>` |
| Team folder | `mbvr://https://workdrive.zoho.com/home/teams/<team_id>/privatespace/folders/<folder_id>` |
| Private space | `mbvr://https://workdrive.zoho.com/teams/<team_id>/privatespace/folders/<folder_id>` |

Any `https://workdrive.zoho.com/...` URL is accepted.

---

## ZohoWorkDriveTS.exe Search Locations

The launcher looks for **ZohoWorkDriveTS.exe** (Zoho WorkDrive True Sync) in this order:

1. **Registry** – Windows Uninstall entries for "Zoho WorkDrive TrueSync"
2. `C:\Program Files\Zoho\ZohoWorkDriveTS\bin\ZohoWorkDriveTS.exe` *(verified)*
3. `C:\Program Files (x86)\Zoho\ZohoWorkDriveTS\bin\ZohoWorkDriveTS.exe`
4. `%LOCALAPPDATA%\Zoho WorkDrive TrueSync\ZohoWorkDriveTS.exe`
5. `%APPDATA%\Zoho WorkDrive TrueSync\ZohoWorkDriveTS.exe`
6. Additional fallback paths

If not found, errors are logged to `%TEMP%\mbvr_launcher.log`.

---

## Testing Instructions

### 1. Install the protocol
```bash
dist\mbvr_launcher.exe --install
```

### 2. Test from Run dialog
- Press `Win+R`
- Paste: `mbvr://https://workdrive.zoho.com/folder/YOUR_FOLDER_ID`
- Press Enter

### 3. Test from Zoho CRM
In a custom button:
```javascript
openUrl("mbvr://https://workdrive.zoho.com/folder/YOUR_FOLDER_ID");
```

### 4. Check logs
If something fails, check: `%TEMP%\mbvr_launcher.log`

---

## Success Criteria

- [x] `mbvr://<workdrive-link>` triggers the EXE
- [x] EXE launches Zoho WorkDrive True Sync desktop app
- [x] WorkDrive opens the given folder/link
- [x] Works from Zoho CRM `openUrl("mbvr://<workdrive-link>")`

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "ZohoWorkDriveTS.exe not found" | Install Zoho WorkDrive True Sync; check log for paths searched |
| Link does nothing | Re-run `mbvr_launcher.exe --install` |
| Wrong app path | Edit registry: `HKEY_CURRENT_USER\Software\Classes\mbvr\shell\open\command` |
| Log location | `%TEMP%\mbvr_launcher.log` (e.g. `C:\Users\<you>\AppData\Local\Temp\`) |
