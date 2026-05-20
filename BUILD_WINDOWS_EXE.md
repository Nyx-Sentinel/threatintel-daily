# 🪟 Building ThreatIntel Daily for Windows

Complete guide to create a standalone .exe file and Windows installer.

---

## 📋 Prerequisites

You need:
1. **Windows 10/11**
2. **Python 3.9+** (download from https://www.python.org/downloads/)
   - ✅ Check "Add Python to PATH" during installation
3. **Visual C++ Build Tools** (for some Python packages)
   - Optional but recommended: https://visualstudio.microsoft.com/visual-cpp-build-tools/

---

## Step 1: Prepare Your Project

Extract `threatintel-daily.zip` and navigate to the folder:

```bash
cd threatintel-daily
```

---

## Step 2: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install GUI and build dependencies
pip install -r requirements-gui.txt

# Additional build tools
pip install pyinstaller wheel setuptools
```

---

## Step 3: Configure the Application

```bash
# Copy config template
copy config.example.yml config.yml

# Edit config.yml with your API keys
# (Use Notepad or your editor)
notepad config.yml
```

Set at minimum:
```yaml
feeds:
  nvd:
    enabled: true
    api_key: "YOUR_NVD_API_KEY"  # Get from https://nvd.nist.gov/developers
```

---

## Step 4: Test the GUI Locally

Before building the .exe, test that the GUI runs:

```bash
# From virtual environment
python -m threatintel_daily.gui
```

You should see the ThreatIntel Daily window open with:
- Dashboard tab showing threat stats
- Threats tab with filtering
- Statistics tab with threat analysis
- Settings button for configuration

If it works, close the window and continue.

---

## Step 5: Build the Executable

### Option A: Simple (Recommended for First Time)

```bash
# Activate virtual environment if not already
venv\Scripts\activate

# Build exe in a dist folder
pyinstaller threatintel-daily.spec

# The executable will be in: dist\ThreatIntel Daily\ThreatIntel Daily.exe
```

**First build takes 2-5 minutes.** This will create:
- `dist\ThreatIntel Daily\ThreatIntel Daily.exe` ← Your executable!

### Option B: Single File (Larger but Simpler)

```bash
pyinstaller --onefile --windowed threatintel_daily/gui.py --name "ThreatIntel Daily"
```

This creates `dist\ThreatIntel Daily.exe` (single ~150 MB file)

---

## Step 6: Create Application Icon (Optional)

For a professional look, add an icon:

1. Create or download an icon file (256x256 pixels, `.ico` format)
2. Save as `icon.ico` in the project root
3. Rebuild:
   ```bash
   pyinstaller threatintel-daily.spec
   ```

---

## Step 7: Test the Executable

Double-click `dist\ThreatIntel Daily\ThreatIntel Daily.exe`

You should see the GUI window. Test:
- [ ] Dashboard loads
- [ ] Settings opens
- [ ] Can view threats
- [ ] Filter works
- [ ] System tray icon appears

---

## Step 8: Create a Windows Installer (Optional)

For distribution, create an installer:

### Prerequisites
Download and install **NSIS** (free):
- https://nsis.sourceforge.io/Download
- Accept defaults during installation

### Build Installer

```bash
# Make sure you've built the exe first
# dist\ThreatIntel Daily\ folder must exist

# Copy installer script
copy installer.nsi .

# Right-click installer.nsi → Compile NSIS Script
# (Or from NSIS: File > Compile NSI Scripts)
```

This creates **`ThreatIntel-Daily-Setup.exe`** - a professional Windows installer!

---

## Step 9: Distribute Your Application

### Release Package Contents

Create a `Release` folder with:

```
ThreatIntel-Daily-Release/
├── ThreatIntel-Daily-Setup.exe      ← Installer (recommended for users)
├── README.txt                        ← Installation instructions
├── QUICKSTART.txt                    ← Getting started guide
└── config.example.yml                ← Example config
```

---

## Windows Installation Methods

### Method 1: Using the Installer (Best for Users)

Users run `ThreatIntel-Daily-Setup.exe`:
1. Clicks "Next"
2. Selects install location
3. Installation completes
4. Desktop shortcut created
5. Application ready to use

### Method 2: Portable .exe (No Installation)

Users can run `ThreatIntel Daily.exe` directly without installation:
- Single executable file
- No "installation" needed
- Can run from USB drive
- Store anywhere

### Method 3: Docker (For Advanced Users)

Users run:
```bash
docker-compose up -d
```

---

## Step 10: Create Release on GitHub

Once you've built the .exe:

1. Go to your GitHub repo
2. Click **Releases** tab
3. Click **Create a new release**
4. Fill in:
   - **Tag version:** `v0.1.0-windows`
   - **Release title:** `ThreatIntel Daily v0.1.0 - Windows Edition`
   - **Description:**
     ```
     Windows executable and installer for ThreatIntel Daily
     
     ## Download
     - ThreatIntel-Daily-Setup.exe (recommended) - Windows installer
     - ThreatIntel Daily.exe - Portable executable
     
     ## Installation
     Simply download and run the installer!
     
     ## Requirements
     - Windows 10/11
     - 200 MB free disk space
     - Internet connection for threat feeds
     ```
5. Upload files:
   - `ThreatIntel-Daily-Setup.exe` (installer)
   - `ThreatIntel Daily.exe` (portable)
6. Publish release

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'PyQt5'"
```bash
pip install PyQt5
```

### "PyInstaller: command not found"
```bash
pip install pyinstaller
```

### ".spec file missing"
Use the provided `threatintel-daily.spec` file, or create one:
```bash
pyi-makespec threatintel_daily/gui.py
```

### Executable is very large (>200 MB)
This is normal. PyInstaller bundles everything including Python. You can:
- Use `--onefile` flag to merge into single exe
- Use `--optimize=2` to reduce size
- Remove unused modules from `hiddenimports` in .spec file

### "Access denied" when running installer
Right-click installer → Run as Administrator

### Antivirus flags the .exe
This is common with compiled Python apps. You can:
- Submit to antivirus vendor for scanning
- Use code signing (costs ~$300/year)
- Tell users it's safe (it is!)

### GUI window won't open on startup
Check if config.yml exists. If not:
```bash
copy config.example.yml config.yml
```

---

## Performance Tips

### For Smaller File Size
```bash
pyinstaller --onefile --optimize=2 threatintel_daily/gui.py
```

### For Faster Startup
```bash
pyinstaller --onefile threatintel_daily/gui.py --distpath dist --buildpath build
```

### For Minimal Dependencies
Remove unused packages from `requirements-gui.txt` before building.

---

## Advanced: Code Signing

For professional releases, code-sign the executable:

```bash
# Requires a code signing certificate (~$300/year)
signtool sign /f "certificate.pfx" /p "password" /t http://timestamp.server "ThreatIntel Daily.exe"
```

Users will see verified publisher instead of "Unknown Publisher"

---

## Distribution Checklist

- [ ] .exe built and tested locally
- [ ] All dependencies included
- [ ] Config example included
- [ ] README with installation steps
- [ ] Installer (.nsi) created
- [ ] Released on GitHub Releases
- [ ] Tested on clean Windows machine
- [ ] Antivirus scanned (if distributing publicly)

---

## Next Steps

1. **Build locally** - Follow steps 1-7
2. **Test thoroughly** - Make sure everything works
3. **Create installer** - Follow step 8
4. **Release on GitHub** - Follow step 10
5. **Share with users** - Post on Reddit, HackerNews, etc.

---

## File Locations Reference

```
threatintel-daily/
├── threatintel_daily/
│   └── gui.py                    ← GUI application
├── requirements-gui.txt          ← Install dependencies
├── threatintel-daily.spec        ← PyInstaller config
├── installer.nsi                 ← Windows installer config
├── launch-gui.bat                ← Quick launch script
├── config.example.yml            ← Config template
└── dist/                          ← Output folder (created by PyInstaller)
    └── ThreatIntel Daily/
        └── ThreatIntel Daily.exe ← Your executable!
```

---

## Need Help?

- **PyInstaller Docs:** https://pyinstaller.org
- **NSIS Docs:** https://nsis.sourceforge.io/Docs
- **PyQt5 Docs:** https://www.riverbankcomputing.com/software/pyqt/intro

---

**Your Windows executable is ready!** 🎉

Share it on GitHub Releases and let Windows users enjoy ThreatIntel Daily. 🔒
