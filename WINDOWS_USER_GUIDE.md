# 🪟 ThreatIntel Daily for Windows - User Guide

**For Windows users who want to just run the application.**

---

## 📥 Installation (Choose One)

### Option 1: Installer (Easiest) ⭐

1. Download `ThreatIntel-Daily-Setup.exe` from Releases
2. Double-click to run installer
3. Click "Next" through the installation
4. Done! A shortcut appears on your desktop

**First run may take 30 seconds to initialize the database.**

### Option 2: Portable Executable

1. Download `ThreatIntel Daily.exe` from Releases
2. Save it anywhere (Desktop, Downloads, USB drive, etc.)
3. Double-click to run
4. Done!

**No installation needed. Can run from USB drive.**

### Option 3: From Python (For Developers)

```bash
# Install Python 3.9+ from https://www.python.org
# Run installer, CHECK "Add Python to PATH"

# Open Command Prompt and run:
git clone https://github.com/YOUR_USERNAME/threatintel-daily.git
cd threatintel-daily
pip install -r requirements-gui.txt
python -m threatintel_daily.gui
```

---

## ⚙️ First Setup (2 minutes)

When you first launch the app:

1. **Click Settings** (⚙️ button)
2. **Add API Keys:**
   - Get NVD key: https://nvd.nist.gov/developers/request-an-api-key
   - (Optional) HaveIBeenPwned key: https://haveibeenpwned.com/API/v3
   - (Optional) AbuseIPDB key: https://www.abuseipdb.com/api
3. **Add your email:**
   - Under "Emails to monitor"
   - Enter your email address (to check if it's in breaches)
4. **Add your domain:**
   - Under "Domains to monitor"
   - Enter your domain (if you own one)
5. **Click Save**

That's it! Your app is configured.

---

## 🚀 Using the Application

### Dashboard Tab
- See total threats at a glance
- View threat counts by severity (Critical, High, etc.)
- See recent threats from all sources

### Threats Tab
- View all detected threats
- Filter by:
  - Type (CVE, Breach, Malicious IP, etc.)
  - Severity (Critical, High, Medium, Low)
  - Time period (Last 7 days, 30 days, etc.)
- Double-click a threat to see full details

### Statistics Tab
- Threats by type (CVE, Breach, etc.)
- Threats by severity
- Which threat sources are most active

### Settings
- Update API keys
- Add/remove emails to monitor
- Configure alert severity level

---

## 🔄 Fetching Threats

### Automatic (Recommended)
- The app fetches threats **every hour automatically**
- Checks all threat feeds in background
- You get alerts when new threats are found

### Manual
1. Click **"🔄 Fetch Now"** button
2. Wait for it to complete (30 seconds to 2 minutes)
3. New threats appear in the Threats tab

---

## 📧 Email Alerts (Optional)

To get email notifications when threats are found:

1. **Click Settings**
2. **Check "Enable email alerts"**
3. **Enter your email address**
4. **Select alert severity** (recommended: MEDIUM or higher)
5. **Click Save**

You'll get daily email digest of threats found.

---

## 🔍 Checking Your Email

Concerned your email might be in a breach?

1. Go to **Threats tab**
2. Set Type filter to "CREDENTIAL_BREACH"
3. Your emails appear if found in known breaches
4. Double-click to see breach details

---

## 💾 Exporting Data

To back up or analyze threats:

1. Open Command Prompt
2. Navigate to app folder
3. Run:
   ```bash
   python -m threatintel_daily.cli export-threats --format json --output threats.json
   ```
4. File `threats.json` contains all threats in JSON format

---

## 🔒 Security Notes

### Protecting API Keys
- Never share your API keys
- If someone gets them, regenerate them immediately
- They're stored in `config.yml` (don't commit to GitHub)

### Data Privacy
- All threat data stays on **your machine**
- Nothing is sent to the cloud
- Database is stored in `data/` folder

### Backups
- Back up `data/` folder regularly
- Contains all your threat intelligence history

---

## 🆘 Troubleshooting

### "Application won't start"
- Try again - sometimes takes 30 seconds first time
- Check if antivirus is blocking it (it's safe!)
- Right-click → Run as Administrator

### "Database locked" error
- Close all instances of the app
- Delete `data/threatintel.db` file
- Restart the app

### "API key invalid" error
- Check you copied the API key correctly
- Visit https://nvd.nist.gov/developers to verify
- Try clicking "Fetch Now" again

### "No threats appearing"
- Make sure you have API keys configured
- Click "Fetch Now" button
- Wait 1-2 minutes for first fetch
- Check your email address is in the config

### "Can't find config.yml"
- The app creates it automatically
- Look in the installation folder
- Or in your user home folder

### Application crashes
- Check error message
- Try updating to latest version
- Report issue on GitHub Issues

---

## 🛠️ Advanced Usage

### CLI Commands (Command Prompt)

```bash
# List threats from last 7 days
python -m threatintel_daily.cli list-threats --since 7d

# Check if your email is in a breach
python -m threatintel_daily.cli check-email --email you@example.com

# Export threats as CSV
python -m threatintel_daily.cli export-threats --format csv --output threats.csv

# View statistics
python -m threatintel_daily.cli stats --days 30
```

### Logs
Logs are saved in `logs/` folder:
- `logs/threatintel-daily.log` contains all activity
- Useful for debugging issues

---

## 📊 Example Usage Scenarios

### Scenario 1: "Is my email in a breach?"
1. Open app
2. Go to Threats tab
3. Filter Type = "CREDENTIAL_BREACH"
4. Search for your email in the list
5. If found, double-click to see breach details and recommendations

### Scenario 2: "Monitor my company domain"
1. Click Settings
2. Add your company domain under "Domains to monitor"
3. Save
4. App will alert you if domain appears in CVEs or breaches
5. Get email alerts on new threats

### Scenario 3: "Track security trends"
1. Click Statistics tab
2. See which threat types are most common
3. Which threat feeds are most active
4. Track threats over time

---

## 🔄 Updating

When new versions are released:

### Option 1: Installer
- Download new `ThreatIntel-Daily-Setup.exe`
- Run it (will update installation)

### Option 2: Portable Executable
- Download new `ThreatIntel Daily.exe`
- Replace old one

### Option 3: From Python
```bash
git pull origin main
pip install -r requirements-gui.txt
```

---

## 💬 Getting Help

- **GitHub Issues:** https://github.com/YOUR_USERNAME/threatintel-daily/issues
- **GitHub Discussions:** https://github.com/YOUR_USERNAME/threatintel-daily/discussions
- **README:** Detailed technical documentation
- **QUICKSTART.md:** Getting started guide

---

## 🎓 Learning More

- **Threat Intelligence:** https://en.wikipedia.org/wiki/Threat_intelligence
- **Cybersecurity:** r/cybersecurity on Reddit
- **Stay Updated:** Follow HackerNews for security news

---

## ❤️ Feedback

Help improve ThreatIntel Daily:
- Found a bug? Open an Issue
- Have an idea? Open a Discussion
- Want to help? Contribute on GitHub
- Like it? Leave a ⭐ on GitHub

---

**Happy threat hunting!** 🔒

For detailed technical docs, see:
- `README.md` - Full documentation
- `BUILD_WINDOWS_EXE.md` - For developers building from source
- `QUICKSTART.md` - Developer quick start
