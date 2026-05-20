# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in ThreatIntel Daily, please **do not** open a public GitHub issue.

Instead, please report it responsibly by emailing us at:
**nyxsentinel.se@gmail.com** (replace with your actual security email)

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond within 48 hours and work with you to verify and fix the issue before public disclosure.

## Security Considerations

### What We Take Seriously
- Authentication bypass
- Unauthorized data access
- API key exposure
- Code injection vulnerabilities
- Insecure cryptography

### What We Don't Consider Severe
- Missing documentation
- Minor UI/UX issues
- Duplicate reports
- Spam or false reports

## Responsible Disclosure Timeline

1. **Day 1:** You report the vulnerability
2. **Day 2:** We confirm receipt and begin investigation
3. **Day 3-7:** We develop and test a fix
4. **Day 8:** We release a patch
5. **Day 14:** Public disclosure (if needed)

We ask that you:
- ✅ Give us reasonable time to patch before public disclosure
- ✅ Not exploit the vulnerability beyond what's needed to demonstrate it
- ✅ Keep the vulnerability details confidential during the embargo period
- ✅ Not demand payment or publicity for reporting

## Security Best Practices for Users

If you use ThreatIntel Daily in production:

1. **Protect your API keys**
   - Never commit `config.yml` with real keys
   - Use environment variables in production
   - Rotate keys periodically

2. **Keep it updated**
   ```bash
   git pull origin main
   pip install -r requirements.txt
   ```

3. **Backup your data**
   - Backup `./data/` directory regularly
   - Store backups securely

4. **Monitor access**
   - Track who has access to the system
   - Review logs regularly
   - Use strong authentication for access

5. **Network security**
   - Don't expose the application to the internet without authentication
   - Use firewall rules to restrict access
   - If using webhooks, verify webhook signatures

## Known Limitations

- This is an **open-source security tool** for individuals and small teams
- It is **not** a substitute for professional security software
- Always validate and test in your own environment
- Use at your own risk

## Security Advisories

We will publish security advisories for:
- Remote code execution vulnerabilities
- Authentication bypass
- Arbitrary code execution
- Data exfiltration

Visit the [Security Advisories](https://github.com/YOUR_USERNAME/threatintel-daily/security/advisories) page for disclosed vulnerabilities.

## Support

For security-related questions (not vulnerability reports), please open a discussion or issue.

Thank you for helping keep ThreatIntel Daily secure! 🔒
