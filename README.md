# mbvr:// Zoom Launcher for Windows

A Windows custom URL protocol launcher that opens Zoom desktop app from `mbvr://` links. Designed for use with Zoho CRM custom buttons via `openUrl("mbvr://<zoom-meeting-link>")`.

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

3. **Test**: Click a link like `mbvr://https://zoom.us/j/123456789` — Zoom should open and join the meeting.

---

## Build Instructions (PyInstaller)

### Prerequisites
- Windows 10/11
- Python 3.8+
- Zoom desktop app installed

### Build Command
```bash
pyinstaller --noconsole --onefile --name mbvr_launcher launcher.py
```

**Output**: `dist/mbvr_launcher.exe`

### Build Options Explained
| Option | Purpose |
|--------|---------|
| `--noconsole` | No black console window when launching Zoom |
| `--onefile` | Single EXE, no extra files |
| `--name mbvr_launcher` | Output filename |

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
| Zoom HTTPS | `mbvr://https://zoom.us/j/9345839485?pwd=xyz` |
| Zoom deep link | `mbvr://zoommtg://zoomus?confno=123456789&pwd=abcd` |

---

## Zoom.exe Search Locations

The launcher looks for Zoom in this order:
1. `%APPDATA%\Zoom\bin\Zoom.exe`
2. `C:\Users\<user>\AppData\Roaming\Zoom\bin\Zoom.exe`
3. `C:\Program Files (x86)\Zoom\bin\Zoom.exe`
4. `C:\Program Files\Zoom\bin\Zoom.exe`

If not found, errors are logged to `%TEMP%\mbvr_launcher.log`.

---

## Testing Instructions

### 1. Install the protocol
```bash
dist\mbvr_launcher.exe --install
```

### 2. Test from Run dialog
- Press `Win+R`
- Paste: `mbvr://https://zoom.us/j/123456789`
- Press Enter

### 3. Test from browser
- Create an HTML file:
  ```html
  <a href="mbvr://https://zoom.us/j/123456789">Join Zoom</a>
  ```
- Open in browser and click the link

### 4. Test from Zoho CRM
In a custom button:
```javascript
openUrl("mbvr://https://zoom.us/j/9345839485?pwd=xyz");
```

### 5. Check logs
If something fails, check: `%TEMP%\mbvr_launcher.log`

---

## Success Criteria

- [x] `mbvr://<zoom-link>` triggers the EXE
- [x] EXE launches Zoom desktop
- [x] Zoom joins the meeting directly
- [x] No Chrome extension needed
- [x] Works from Zoho CRM `openUrl("mbvr://<zoom-meeting-link>")`

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Zoom.exe not found" | Install Zoom desktop app; check log for paths searched |
| Link does nothing | Re-run `mbvr_launcher.exe --install` |
| Wrong Zoom path | Edit registry: `HKEY_CURRENT_USER\Software\Classes\mbvr\shell\open\command` |
| Log location | `%TEMP%\mbvr_launcher.log` (e.g. `C:\Users\<you>\AppData\Local\Temp\`) |
