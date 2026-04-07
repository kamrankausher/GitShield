<h1 align="center">
  🛡️ GitShield
</h1>

<p align="center">
  <strong>AI-powered Git Guardian that prevents secret leaks, enforces best practices, and coaches developers in real-time</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.9+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/cost-100%25%20FREE-brightgreen.svg" alt="Free">
  <img src="https://img.shields.io/badge/dependencies-lightweight-orange.svg" alt="Lightweight">
</p>

<p align="center">
  Catch secrets before they leak &bull; Block bad commits &bull; Guide Git workflows &bull; Track developer habits
</p>

---

## 🔥 Why GitShield?

| Problem | GitShield Solution |
|---------|-------------------|
| Accidentally pushing `.env` files | 🔒 **Security Scanner** blocks it before push |
| Vague commit messages like "fix" | 📝 **Commit Analyzer** suggests better messages |
| Committing directly to `main` | 🌿 **Branch Guardian** warns and guides you |
| Leaked API keys in code | 🚨 **40+ secret patterns** detect them instantly |
| Large, unfocused commits | 📊 **File Analyzer** suggests splitting |
| Merge conflict markers in code | ⚠️ **Conflict Detector** blocks the commit |
| No idea how to fix Git mistakes | 🔧 **Recovery Wizard** provides step-by-step guides |
| Bad developer habits | 🧠 **Behavior Intelligence** tracks and improves habits |

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+** installed
- **Git** installed
- **pip** (Python package manager)

### Step-by-Step Installation

```bash
# Step 1: Clone the repository
git clone https://github.com/your-username/gitshield.git
cd gitshield

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Install GitShield as a CLI tool
pip install -e .

# Step 4: Verify installation
gitshield --version
# Output: GitShield, version 1.0.0
```

### First Run (in any Git project)

```bash
# Navigate to YOUR project
cd /path/to/your/project

# Step 5: Initialize GitShield (installs git hooks)
gitshield init

# Step 6: Run a full system check
gitshield doctor

# Step 7: Scan for secrets
gitshield scan .

# Step 8: Check repository health
gitshield health .
```

> **💡 Tip:** If `gitshield` command is not found, use `python -m devflow.cli` instead, or add your Python Scripts directory to PATH.

---

## 📋 All Commands

| Command | Description | Example |
|---------|-------------|---------|
| `gitshield scan .` | 🔒 Security scan for secrets | `gitshield scan . --strict` |
| `gitshield check` | 📋 Pre-commit quality analysis | `gitshield check --hook` |
| `gitshield health .` | 🏥 Repository health score (0-100) | `gitshield health .` |
| `gitshield fix` | 🔧 Interactive recovery wizard | `gitshield fix` |
| `gitshield init` | ⚡ Install git hooks | `gitshield init` |
| `gitshield uninstall` | 🗑️ Remove hooks | `gitshield uninstall` |
| `gitshield gitignore` | 📝 Smart .gitignore generator | `gitshield gitignore --write` |
| `gitshield guide <topic>` | 📚 Workflow tutorials | `gitshield guide pr` |
| `gitshield stats` | 📊 Developer statistics | `gitshield stats` |
| `gitshield doctor` | 🩺 Full system diagnostic | `gitshield doctor` |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│              GitShield CLI                    │
│         (10 commands, Rich UI)               │
├──────────┬──────────┬──────────┬─────────────┤
│ Security │  Rules   │   AI     │  Recovery   │
│ Scanner  │  Engine  │  Mentor  │  Engine     │
│ (40+     │ (Commit, │ (50+     │ (Undo,      │
│ patterns)│  Branch, │ suggest- │  Fix,       │
│          │  Files)  │  ions)   │  Guide)     │
├──────────┴──────────┴──────────┴─────────────┤
│         Git Hooks (pre-commit/push)          │
├──────────────────────────────────────────────┤
│       Behavior Intelligence Engine           │
│   (Memory, Stats, Skill Tracking)            │
└──────────────────────────────────────────────┘
```

---

## 🔒 Security Scanner — 40+ Secret Patterns

| Provider | What It Detects |
|----------|----------------|
| **AWS** | Access Keys, Secret Keys, MWS Keys |
| **Google/GCP** | API Keys, OAuth, Service Accounts |
| **GitHub** | Personal Access Tokens, OAuth, App Tokens |
| **Azure** | Storage Keys, Connection Strings |
| **Stripe** | Secret Keys, Publishable Keys |
| **Database** | MongoDB, PostgreSQL, MySQL, Redis URIs |
| **Auth** | JWT Tokens, Bearer Tokens |
| **SSH/Crypto** | RSA, DSA, EC, OpenSSH, PGP Private Keys |
| **Generic** | API keys, Passwords, Secrets in any format |
| + 20 more | Twilio, SendGrid, Slack, Firebase, Heroku... |

Each finding includes **severity level** (🔴 Critical → 🔵 Low), **file + line number**, and **remediation advice**.

---

## 📝 Rule Engine

- ✅ Conventional commit format (`feat:`, `fix:`, `docs:`, etc.)
- ✅ Message quality & vague word detection
- ✅ Dangerous file type blocking (`.exe`, `.zip`, `.db`)
- ✅ Large commit detection
- ✅ Merge conflict marker detection
- ✅ Direct-to-main commit warnings
- ✅ Branch naming convention checks

---

## 🔧 Recovery Wizard

Interactive guided recovery for:
- ↩️ Undo commits (soft/mixed/hard)
- 📝 Amend last commit
- 🗑️ Remove files from Git history
- 🔀 Fix detached HEAD
- 🌿 Fix diverged branches
- 🚨 **Emergency secret leak recovery**

---

## 📁 Project Structure

```
gitshield/
├── devflow/                    # Core Python package
│   ├── __init__.py             # Package metadata + banner
│   ├── cli.py                  # CLI with 10 commands
│   ├── scanner.py              # Security scanner (40+ patterns)
│   ├── rules.py                # Rule engine
│   ├── git_analyzer.py         # Git workflow analysis
│   ├── mentor.py               # AI mentor system
│   ├── memory.py               # Behavior intelligence
│   ├── ai_engine.py            # AI suggestion engine
│   ├── recovery.py             # Mistake recovery wizard
│   ├── health.py               # Repository health analyzer
│   ├── gitignore_gen.py        # .gitignore generator
│   ├── github_assistant.py     # GitHub workflow guides
│   └── hooks_manager.py        # Git hooks installer
├── tests/                      # Test suite (65 tests)
│   ├── test_scanner.py
│   ├── test_rules.py
│   └── test_modules.py
├── vscode-extension/           # VS Code extension
├── pyproject.toml              # Build config
├── setup.py                    # Package installer
├── requirements.txt            # Dependencies
├── LICENSE                     # MIT License
└── README.md                   # This file
```

---

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_scanner.py -v
```

---

## 💰 100% Free & Lightweight

- ✅ No API keys needed
- ✅ No paid services
- ✅ No heavy ML models (no PyTorch/TensorFlow)
- ✅ Only 3 dependencies: `click`, `rich`, `colorama`
- ✅ Works completely offline

---

## 🤝 Contributing

```bash
git checkout -b feature/your-feature
git commit -m 'feat: add your feature'
git push origin feature/your-feature
# Then open a Pull Request
```

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ❤️ | <strong>GitShield</strong> — Your code's last line of defense
</p>
