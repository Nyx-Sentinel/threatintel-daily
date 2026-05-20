# Contributing to ThreatIntel Daily

Thank you for your interest in contributing! We welcome all contributions, from bug reports to new feature implementations.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/threatintel-daily.git
   cd threatintel-daily
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install in development mode**:
   ```bash
   pip install -e .
   pip install -r requirements.txt
   ```

5. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Style
- Follow PEP 8
- Use type hints where possible
- Document functions and classes with docstrings

### Testing
Run tests before submitting a PR:
```bash
pytest tests/
```

### Commit Messages
- Use clear, descriptive commit messages
- Reference issues when relevant: `Fix #123`
- Example: `Add Shodan feed integration`

## Areas for Contribution

### New Threat Feed Integrations
Want to add a new threat feed? Here's the template:

```python
# In threatintel_daily/feeds.py
class MyThreatFeed(ThreatFeed):
    """My threat feed description"""
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key)
    
    def fetch(self) -> List[Threat]:
        """Fetch threats from this feed"""
        threats = []
        # Implementation here
        return threats
```

### Lab Integrations
Add integrations with Wazuh, Suricata, Zeek, or other security tools:

```python
# In threatintel_daily/labs/
class MyLabIntegration:
    """Integrate with my security tool"""
    
    def __init__(self, config: dict):
        self.config = config
    
    def fetch_alerts(self) -> List[Threat]:
        """Fetch alerts from the tool"""
        pass
```

### Dashboard Improvements
The web dashboard (in `threatintel_daily/dashboard/`) is a React app. Areas to improve:

- Add threat visualization charts
- Implement real-time alert streaming
- Build threat trend analysis
- Add MITRE ATT&CK mapping visualizations

### Documentation
- Improve README or API docs
- Add more examples
- Create deployment guides for specific platforms (K8s, VPS, etc.)

### Bug Fixes
Found a bug? Great! Submit a PR with:
- A clear description of the bug
- Steps to reproduce
- Expected vs. actual behavior
- Any error logs

## Pull Request Process

1. **Update your branch**:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Open a PR** on GitHub with:
   - Clear title (e.g., "Add Censys feed integration")
   - Description of changes
   - Reference to any related issues
   - Screenshots if UI changes

4. **Respond to review feedback** promptly

## Code Review Guidelines

When reviewing PRs, we look for:
- ✅ Code quality and style
- ✅ Test coverage
- ✅ Documentation
- ✅ Backwards compatibility
- ✅ Security considerations

## Reporting Issues

Found a security vulnerability? **Please don't open a public issue.** Instead, email [nyxsentinel.se@gmail.com] with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Questions?** Open a discussion on GitHub or reach out to the maintainers.

Happy coding! 🔒
