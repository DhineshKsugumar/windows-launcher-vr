# mbvr:// File Launcher for Windows

A Windows custom URL protocol launcher that opens **local files** with their default application using `Start-Process`. Designed for use with Zoho CRM custom buttons via `openUrl("mbvr://<local-file-path>")`.

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

3. **Test**: Click a link like `mbvr://C:/Users/Name/Documents/file.pdf` — the file opens in its default app.

---

## Build Instructions (PyInstaller)

### Prerequisites
- Windows 10/11
- Python 3.8+

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

## Accepted Link Format

| Format | Example |
|--------|---------|
| Local file path | `mbvr://C:/Users/Name/Documents/file.pdf` |
| With spaces | `mbvr://C:/Users/Name/My%20Documents/report.docx` |
| Folder | `mbvr://C:/Users/Name/Desktop/MyFolder` |

The path after `mbvr://` is URL-decoded and passed to `Start-Process`, which opens it with the default application for that file type (or Explorer for folders).

---

## How It Works

1. Windows invokes: `mbvr_launcher.exe "mbvr://C:/path/to/file.pdf"`
2. Launcher strips `mbvr://`, URL-decodes the path
3. Runs: `Start-Process -FilePath "C:\path\to\file.pdf"`
4. File opens in its default app (e.g. PDF reader, Word, etc.)

---

## Testing Instructions

### 1. Install the protocol
```bash
dist\mbvr_launcher.exe --install
```

### 2. Test from Run dialog
- Press `Win+R`
- Paste: `mbvr://C:/Users/YourName/Desktop/test.pdf` (use a real file path)
- Press Enter

### 3. Test from Zoho CRM
In a custom button:
```javascript
openUrl("mbvr://C:/path/to/your/file.pdf");
```

### 4. Check logs
If something fails, check: `%TEMP%\mbvr_launcher.log`

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| File doesn't open | Check path exists; ensure URL encoding for spaces (`%20`) |
| Link does nothing | Re-run `mbvr_launcher.exe --install` |
| Log location | `%TEMP%\mbvr_launcher.log` (e.g. `C:\Users\<you>\AppData\Local\Temp\`) |
