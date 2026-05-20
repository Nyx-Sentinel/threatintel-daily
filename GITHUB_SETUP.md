# Setting Up ThreatIntel Daily on GitHub

Complete guide to publishing your project on GitHub.

## Step 1: Create Repository on GitHub

1. Go to **https://github.com/new**
2. Fill in:
   - **Repository name:** `threatintel-daily`
   - **Description:** "Personal threat intelligence aggregator for security professionals"
   - **Public** (open-source)
   - **Do NOT initialize with README** (we have one)
3. Click **Create repository**

## Step 2: Initialize Git Locally

In your `threatintel-daily/` folder:

```bash
# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: ThreatIntel Daily personal threat intelligence aggregator"

# Add GitHub as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/threatintel-daily.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

That's it! Your repo is now live on GitHub.

---

## Step 3: Verify on GitHub

Visit: `https://github.com/YOUR_USERNAME/threatintel-daily`

You should see:
- ✅ All source files
- ✅ README.md (auto-displayed)
- ✅ License badge
- ✅ File structure

---

## Step 4: GitHub Topics (Optional but Recommended)

Add topics to help people find your project:

1. Go to your repo Settings → General
2. Add these topics:
   - `threat-intelligence`
   - `cybersecurity`
   - `open-source`
   - `python`
   - `security-tools`
   - `osint`

---

## Step 5: Add GitHub Badge to README (Optional)

At the top of README.md, add:

```markdown
# ThreatIntel Daily 🛡️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/threatintel-daily.svg?style=social&label=Star&maxAge=2592000)](https://github.com/YOUR_USERNAME/threatintel-daily)
```

---

## Step 6: Enable Issues & Discussions

In GitHub repo Settings:

- ✅ Enable Issues (for bug reports)
- ✅ Enable Discussions (for feature requests)
- ✅ Enable Projects (optional, for tracking)

---

## Step 7: Create Issue Templates (Optional)

Create `.github/ISSUE_TEMPLATE/` folder with:

### `.github/ISSUE_TEMPLATE/bug_report.md`
```markdown
---
name: Bug report
about: Report a bug
title: '[BUG] '
labels: 'bug'
---

## Description
Describe the bug here.

## Steps to reproduce
1. 
2. 

## Expected behavior


## Actual behavior


## Environment
- OS: 
- Python version: 
- ThreatIntel Daily version: 
```

### `.github/ISSUE_TEMPLATE/feature_request.md`
```markdown
---
name: Feature request
about: Suggest an idea
title: '[FEATURE] '
labels: 'enhancement'
---

## Description
What feature would you like?

## Why?
Why is this useful?

## Implementation ideas
```

---

## Step 8: Create Pull Request Template (Optional)

Create `.github/pull_request_template.md`:

```markdown
## Description
Describe your changes here.

## Type of change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Integration (feed, lab, etc.)

## Related Issues
Closes #(issue number)

## Testing
How did you test this?

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No breaking changes
```

---

## Step 9: Add GitHub Actions (CI/CD) - Optional

Create `.github/workflows/python-test.yml`:

```yaml
name: Python Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 threatintel_daily --count --select=E9,F63,F7,F82 --show-source --statistics
    
    - name: Test with pytest
      run: |
        pip install pytest
        pytest tests/ || true
```

This auto-runs tests on every push/PR.

---

## Step 10: Keep It Updated

### Make Changes Locally
```bash
# Make edits to files
nano threatintel_daily/feeds.py

# Commit
git add .
git commit -m "Add Shodan feed integration"

# Push
git push origin main
```

### Update Version
In `setup.py`, update version number:
```python
version="0.2.0",  # Change from 0.1.0
```

Then commit and push.

---

## Step 11: Create Releases (When Ready)

```bash
# Tag the version
git tag -a v0.2.0 -m "Release version 0.2.0 - Add Shodan integration"

# Push tags
git push origin --tags
```

On GitHub, go to Releases → Auto-generate release notes.

---

## Step 12: Publicize It (Optional)

Share your project on:
- **Reddit:** r/cybersecurity, r/Python
- **HackerNews:** Show HN thread
- **Twitter/X:** #cybersecurity #opensourceSecurity
- **LinkedIn:** Share your work
- **GitHub Awesome List:** https://awesome.re/

---

## Git Workflow for Future Development

```bash
# Create feature branch
git checkout -b feature/new-feed

# Make changes
nano threatintel_daily/feeds.py

# Commit
git add .
git commit -m "Add Censys feed integration"

# Push feature branch
git push origin feature/new-feed

# On GitHub: Open Pull Request
# After review/approval: Merge to main
```

---

## Useful Git Commands

```bash
# Check status
git status

# See commit history
git log --oneline

# See changes
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Create new branch
git checkout -b branch-name

# Switch branches
git checkout main

# Delete local branch
git branch -d branch-name

# Pull latest from GitHub
git pull origin main
```

---

## Troubleshooting

### "fatal: not a git repository"
```bash
cd threatintel-daily
git init
```

### "permission denied (publickey)"
Set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### "Your branch is ahead of 'origin/main'"
```bash
git push origin main
```

### "Merge conflict"
```bash
# See conflicts
git status

# After fixing conflicts
git add .
git commit -m "Resolve merge conflict"
git push
```

---

## Next: Market Your Project

1. **Update GitHub profile** — Add link to this repo
2. **Add to portfolio** — Show it in your resume/CV
3. **Write a blog post** — "Building a Personal Threat Intelligence System"
4. **Share results** — "Found X threats in Y hours"
5. **Consider for thesis** — Use it as foundation for research

---

## Success! 🎉

Your project is now:
- ✅ Open-source on GitHub
- ✅ Discoverable by others
- ✅ Ready for contributions
- ✅ Perfect for your portfolio/thesis
- ✅ Can be forked and improved by the community

**Next steps:**
- Monitor issues & PRs
- Build features based on feedback
- Document everything
- Publish research findings
- Build community

---

**GitHub URL:** `https://github.com/YOUR_USERNAME/threatintel-daily`

Happy coding! 🔒
