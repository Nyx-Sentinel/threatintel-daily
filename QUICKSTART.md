# ThreatIntel Daily - Quick Start 🚀

Get up and running in 5 minutes.

## Option 1: Docker (Easiest)

**Requirements:** Docker and Docker Compose

```bash
# Clone the repo
git clone https://github.com/Nyx-Sentinel/threatintel-daily.git
cd threatintel-daily

# Copy config template
cp config.example.yml config.yml

# Edit config with your API keys
nano config.yml
# (Required: NVD API key, optional: others)

# Start it
docker-compose up -d

# Check logs
docker-compose logs -f threatintel-daily
```

**Done!** Your threats are being monitored. Check alerts at your configured channels (email, Slack, etc.).

---

## Option 2: Local Install (Linux/macOS)

**Requirements:** Python 3.9+

```bash
# Clone
git clone https://github.com/Nyx-Sentinel/threatintel-daily.git
cd threatintel-daily

# Virtual env
python -m venv venv
source venv/bin/activate

# Install
pip install -r requirements.txt

# Configure
cp config.example.yml config.yml
nano config.yml

# Run
python -m threatintel_daily.main
```

---

## Quick Configuration

### 1. Get API Keys (5 min)

| Service | Steps | Cost |
|---------|-------|------|
| **NVD** | Visit https://nvd.nist.gov/developers/request-an-api-key → Request key → Copy | Free |
| **HaveIBeenPwned** | Visit https://haveibeenpwned.com/API/v3 → Subscribe | $3.50/month |
| **AbuseIPDB** | Visit https://www.abuseipdb.com/api → Sign up → Get key | Free (15k/day) |

### 2. Edit `config.yml`

```yaml
monitored:
  emails:
    - your-email@example.com
  domains:
    - your-domain.com

feeds:
  nvd:
    enabled: true
    api_key: "YOUR_NVD_KEY_HERE"
  
  haveibeenpwned:
    enabled: true
    api_key: "YOUR_HIBP_KEY_HERE"

alerts:
  email:
    enabled: true
    from: "your-email@gmail.com"
    to:
      - your-email@example.com
    smtp:
      username: "your-email@gmail.com"
      password: "YOUR_GMAIL_APP_PASSWORD"
      # See: https://support.google.com/accounts/answer/185833
```

### 3. Run a Test

```bash
# Check threats immediately (don't wait for scheduler)
python -m threatintel_daily.cli check-all

# View threats collected
python -m threatintel_daily.cli list-threats

# Check if your email is in a breach
python -m threatintel_daily.cli check-email --email your-email@example.com
```

---

## Command Cheat Sheet

```bash
# Run the continuous monitor
python -m threatintel_daily.main

# One-off threat check
python -m threatintel_daily.cli check-all

# List all threats (last 7 days)
python -m threatintel_daily.cli list-threats --since 7d

# Show threat details
python -m threatintel_daily.cli show-threat --threat-id CVE-2024-1234

# Check if email in breach
python -m threatintel_daily.cli check-email --email you@example.com

# Check IP reputation
python -m threatintel_daily.cli check-ip --ip 192.168.1.1

# Export threats as JSON
python -m threatintel_daily.cli export-threats --format json --output threats.json

# View statistics
python -m threatintel_daily.cli stats --days 7

# Clean old data
python -m threatintel_daily.cli cleanup --days 90
```

---

## Add Slack Alerts (1 min)

1. Go to https://api.slack.com/apps → Create New App
2. Enable "Incoming Webhooks"
3. Add New Webhook to your channel
4. Copy webhook URL
5. In `config.yml`:

```yaml
alerts:
  webhook:
    enabled: true
    slack:
      enabled: true
      webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

**Done!** Now you'll get Slack notifications for new threats.

---

## Next Steps

- ✅ **Monitor it**: Leave it running, get alerts
- 📊 **Analyze**: Use `list-threats` to see patterns
- 🔗 **Integrate**: Add Wazuh, FortiGate, or T-Pot (see README)
- 🚀 **Deploy**: Run on a Raspberry Pi, cloud VM, or NAS
- 📖 **Extend**: Add custom threat feeds or lab integrations

---

## Troubleshooting

**"API key invalid"**
- Check NVD key at https://nvd.nist.gov/developers/request-an-api-key
- Restart container: `docker-compose restart`

**"No email alerts"**
- Gmail: Use an [App Password](https://support.google.com/accounts/answer/185833), NOT your real password
- Check logs: `docker-compose logs -f`

**"Database error"**
- Clear data: `rm -rf ./data/threatintel.db`
- Restart: `docker-compose down && docker-compose up -d`

**"Still stuck?"**
- Check the [Full README](README.md)
- Open a GitHub issue

---

**You're all set!** 🎉 Your personal threat intelligence is now running. Monitor from the comfort of your inbox, Slack, or terminal.

*Questions?* See the [README](README.md) or open an issue.
