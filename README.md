# ThreatIntel Daily 🛡️

A **personal threat intelligence aggregator** that monitors your digital footprint and alerts you to threats that matter. Self-hosted, privacy-first, extensible.

## What It Does

ThreatIntel Daily automatically:
- **Monitors CVEs** that affect your software/services
- **Tracks compromised credentials** against your email addresses and domains
- **Flags malicious IPs/domains** hitting your infrastructure (via logs or custom feeds)
- **Correlates threats** across multiple public threat feeds
- **Alerts you** via email, webhook, or CLI when relevant threats emerge
- **Integrates with your lab** (T-Pot honeypots, FortiGate logs, Wazuh, etc.)

## Why It's Different

Most threat intelligence tools are **enterprise-scale**, expensive, and overkill for individuals. ThreatIntel Daily is:

- ✅ **Lightweight** — runs on a Raspberry Pi, Docker container, or local machine
- ✅ **Privacy-first** — all data stored locally, no cloud vendor lock-in
- ✅ **Multi-source** — aggregates NVD, OSV, HaveIBeenPwned, AbuseIPDB, URLhaus, custom feeds
- ✅ **Lab-aware** — pulls alerts from Wazuh, parses FortiGate firewall logs, T-Pot honeypot events
- ✅ **Simple to extend** — clean Python API for custom integrations
- ✅ **No subscription** — fully open-source, MIT licensed

## Features

### 🔍 Threat Monitoring
- **CVE monitoring** — Watch for vulns in your stack (Python packages, OS, services)
- **Credential exposure** — Know instantly if your email/domain appears in breaches
- **IP reputation** — Track malicious IPs + domains from AbuseIPDB, Shodan, URLhaus
- **STIX/TAXII feeds** — Ingest custom threat feeds from your organization

### 🚨 Alerts
- Email notifications (immediate, digest, or hourly)
- Webhook POST to Slack, Microsoft Teams, Discord, or custom endpoints
- Web dashboard to review threats at your pace
- CLI for headless/lab environments

### 🏠 Lab Integration
- Ingest **Wazuh** alerts and correlate with external threats
- Parse **FortiGate** firewall logs (NetFlow, IPS events)
- Monitor **T-Pot** honeypot interactions
- Custom log parsers for your own tools

### 📊 Analytics
- Trend charts: Which threat types hit you most?
- Top sources: Where are attacks originating?
- False positive learning: Mark alerts as false positives, system learns
- Export reports (JSON, CSV) for your own analysis

## Installation

### Option 1: Docker (Recommended)

```bash
git clone https://github.com/Nyx-Sentinel/threatintel-daily.git
cd threatintel-daily
cp config.example.yml config.yml
# Edit config.yml with your API keys and monitored domains
docker-compose up -d
```

Browse to `http://localhost:8080` for the dashboard.

### Option 2: Local Install (Linux/macOS)

**Requirements:** Python 3.9+

```bash
git clone https://github.com/Nyx-Sentinel/threatintel-daily.git
cd threatintel-daily
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp config.example.yml config.yml
```

Edit `config.yml` with your settings, then:

```bash
# Run the aggregator (pulls threats every hour)
python -m threatintel_daily.main

# Or use CLI commands
python -m threatintel_daily.cli check-cves
python -m threatintel_daily.cli check-breaches
python -m threatintel_daily.cli monitor --interval 3600
```

### Option 3: Raspberry Pi / Low-Power

```bash
# Same as Option 2, but:
pip install -r requirements-minimal.txt  # Lighter dependencies
# Edit config.yml to disable unused features (e.g., Shodan) to save API quota
```

## Quick Start

### 1. Configure Your Threats

```yaml
# config.yml
monitored:
  emails:
    - your-email@example.com
    - work-email@company.com
  domains:
    - example.com
    - company.com
  subdomains:  # Monitor all *.example.com
    - example.com
  services:
    - software: "python"
      version: "3.11.x"
    - software: "nginx"
      version: "1.24.x"

feeds:
  nvd:
    enabled: true
    api_key: ""  # Get free key at https://nvd.nist.gov/developers/request-an-api-key
  
  haveibeenpwned:
    enabled: true
    api_key: "YOUR_HIBP_API_KEY"  # https://haveibeenpwned.com/API/v3
  
  abuseipdb:
    enabled: true
    api_key: "YOUR_ABUSEIPDB_KEY"  # https://www.abuseipdb.com/api
  
  custom_feeds:
    - url: "https://your-org.com/threat-feed.json"
      format: "stix2"
      frequency: "daily"

alerts:
  email:
    enabled: true
    from: "threatintel-daily@example.com"
    to:
      - "your-email@example.com"
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your-email@gmail.com"
    password: "YOUR_APP_PASSWORD"  # NOT your real password
    digest: "daily"  # or "immediate", "hourly"

  webhook:
    enabled: true
    url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    service: "slack"  # or "teams", "discord", "custom"
  
  dashboard:
    enabled: true
    port: 8080
    username: "admin"
    password: "CHANGE_ME"

lab_integration:
  wazuh:
    enabled: false
    api_url: "https://wazuh-manager.local:55000"
    api_user: "wazuh_user"
    api_pass: "wazuh_pass"
  
  fortigate:
    enabled: false
    device_ip: "192.168.1.1"
    api_token: "YOUR_FORTIGATE_TOKEN"
  
  tpot:
    enabled: false
    api_url: "http://tpot.local:64297"
    api_key: "YOUR_TPOT_KEY"
```

### 2. Run It

```bash
# One-off check
python -m threatintel_daily.cli check-all

# Continuous monitoring (runs every hour by default)
python -m threatintel_daily.main
```

### 3. View Results

- **Dashboard:** `http://localhost:8080` (if enabled)
- **Email:** Digest or immediate alerts to your inbox
- **Slack/Teams:** Real-time webhook posts
- **CLI:** `python -m threatintel_daily.cli list-threats`

## API Keys Needed

| Service | What It Monitors | Cost | Link |
|---------|-----------------|------|------|
| **NVD** | CVE/vulnerabilities | Free | https://nvd.nist.gov/developers/request-an-api-key |
| **HaveIBeenPwned** | Breach databases | Free or paid tier | https://haveibeenpwned.com/API/v3 |
| **AbuseIPDB** | Malicious IPs | Free (15k/day) | https://www.abuseipdb.com/api |
| **URLhaus** | Malware URLs | Free (no key needed) | https://urlhaus-api.abuse.ch/docs/ |
| **Shodan** | Internet-wide scanning | Paid (optional) | https://www.shodan.io/ |
| **OSV** | Open-source vulns | Free | https://api.osv.dev/ |

## Lab Integration Examples

### Wazuh

Once configured, ThreatIntel Daily will:
1. Poll Wazuh for new alerts every 30 minutes
2. Cross-reference alert IPs/domains against AbuseIPDB + URLhaus
3. Flag if an internal alert matches a known malware IP

```bash
# Test the integration
python -m threatintel_daily.cli test-wazuh
```

### FortiGate

Parses IPS events, DDoS logs, and blocked connections:

```bash
# Fetch last 100 IPS events from FortiGate
python -m threatintel_daily.cli fortigate-logs --limit 100
```

### T-Pot

Monitors honeypot interactions (SSH, HTTP, Telnet attacks):

```bash
# Watch T-Pot in real-time
python -m threatintel_daily.cli tpot-monitor --live
```

## Examples

### "Alert me if my email appears in a breach"
```bash
python -m threatintel_daily.cli check-breaches --email your-email@example.com
```

### "Show me all threats in the last 24 hours"
```bash
python -m threatintel_daily.cli list-threats --since 24h
```

### "Export threats as JSON for further analysis"
```bash
python -m threatintel_daily.cli export-threats --format json --output threats.json
```

### "Silence false positives for a domain"
```bash
python -m threatintel_daily.cli silence-domain example-spam.com --reason "spam filter test"
```

### "Check if my Raspberry Pi's IP is blacklisted"
```bash
python -m threatintel_daily.cli check-ip 192.168.1.50
```

## Project Structure

```
threatintel-daily/
├── README.md
├── LICENSE (MIT)
├── requirements.txt
├── requirements-minimal.txt
├── config.example.yml
├── docker-compose.yml
├── Dockerfile
├── setup.py
├── threatintel_daily/
│   ├── __init__.py
│   ├── main.py                 # Scheduler + entry point
│   ├── cli.py                  # Command-line interface
│   ├── database.py             # SQLite local storage
│   ├── alerts.py               # Email, webhook, dashboard
│   ├── feeds/
│   │   ├── __init__.py
│   │   ├── nvd.py              # NVD CVE API
│   │   ├── hibp.py             # HaveIBeenPwned
│   │   ├── abuseipdb.py        # AbuseIPDB
│   │   ├── urlhaus.py          # URLhaus malware
│   │   ├── osv.py              # Open-source vulnerabilities
│   │   └── stix.py             # Custom STIX/TAXII feeds
│   ├── labs/
│   │   ├── __init__.py
│   │   ├── wazuh.py            # Wazuh integration
│   │   ├── fortigate.py        # FortiGate integration
│   │   └── tpot.py             # T-Pot honeypot
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # FastAPI routes for dashboard
│   │   └── auth.py             # Basic auth
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py           # Config parsing
│   │   ├── logger.py           # Logging setup
│   │   └── models.py           # Data models (Threat, Alert, etc.)
│   └── dashboard/              # React frontend (optional)
│       ├── public/
│       └── src/
└── tests/
    ├── test_feeds.py
    ├── test_alerts.py
    └── test_labs.py
```

## Contributing

We welcome contributions! Please:

1. Fork this repo
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -am 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open a PR with a clear description

**Ideas for PRs:**
- New threat feed integrations (MISP, Censys, etc.)
- Additional lab connectors (Suricata, Zeek, etc.)
- Dashboard improvements
- Mobile app
- Machine learning for false-positive reduction

## Roadmap

- [x] Core architecture + CLI
- [x] Multi-feed aggregation
- [x] Local SQLite storage
- [x] Email + webhook alerts
- [ ] Web dashboard (React)
- [ ] Wazuh integration
- [ ] FortiGate integration
- [ ] T-Pot integration
- [ ] Machine learning false-positive classifier
- [ ] MISP integration
- [ ] Mobile app (React Native)
- [ ] Kubernetes Helm chart
- [ ] Threat correlation engine (MITRE ATT&CK mapping)

## License

MIT License — See LICENSE file for details.

## Support

- **Issues:** GitHub Issues tab
- **Discussions:** GitHub Discussions
- **Security:** Please report vulns privately to [your-email@example.com](nyxsentinel.se@gmail.com)

---

**Built by cybersecurity enthusiasts, for cybersecurity enthusiasts.** 🔒
