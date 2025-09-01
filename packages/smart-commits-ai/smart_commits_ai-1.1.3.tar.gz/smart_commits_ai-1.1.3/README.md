# 🤖 Smart Commits AI - Universal Git Commit Generator

[![PyPI version](https://badge.fury.io/py/smart-commits-ai.svg)](https://badge.fury.io/py/smart-commits-ai)
[![NPM version](https://img.shields.io/npm/v/smart-commits-ai.svg)](https://www.npmjs.com/package/smart-commits-ai)
[![Docker](https://img.shields.io/docker/v/joshi/smart-commits-ai?label=docker)](https://hub.docker.com/r/joshi/smart-commits-ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/smart-commits-ai)](https://pepy.tech/project/smart-commits-ai)

**AI-powered commit messages for ANY project - React, Flutter, Go, Python, and more!**

> Transform your Git workflow with AI that understands your code changes and generates perfect conventional commit messages. Works with **any programming language** and **any project type**.

This tool works as a **Git pre-commit hook** that analyzes your staged changes and generates professional commit messages using AI APIs (Groq, OpenRouter, Cohere).

---

## 🚀 Quick Start (2 minutes)

## 🚀 Universal Installation (Works with ANY Project)

### **Method 1: One-Line Install (Recommended)**
```bash
# Universal installer - works on macOS, Linux, Windows
curl -fsSL https://raw.githubusercontent.com/Joshi-e8/ai-commit-generator/main/install.sh | bash
```

### **Method 2: NPM (Perfect for JavaScript/React/Next.js)**
```bash
# Install via NPM (no Python knowledge required)
npm install -g smart-commits-ai

# Or use without global install
npx smart-commits-ai install
```

### **Method 3: Docker (Zero Dependencies)**
```bash
# Works everywhere, no local setup needed
docker run --rm -v $(pwd):/workspace joshi/smart-commits-ai install
```

### **Method 4: Python Package (Traditional)**
```bash
# For Python developers
pip install smart-commits-ai
```

## 📊 Choose Your Installation Method

| Method | Best For | Setup Time | Dependencies |
|--------|----------|------------|--------------|
| **One-Line Script** | Any team | 30 seconds | Auto-detected |
| **NPM Package** | JS/React/Node teams | 15 seconds | Node.js |
| **Docker** | DevOps/Containerized | 20 seconds | Docker only |
| **Python Package** | Python developers | 10 seconds | Python 3.8+ |

## ⚡ Quick Setup (2 Minutes)

### **Step 1: Get Free API Key**
Choose your preferred AI provider:

- **🚀 Groq** (Recommended - Free): https://console.groq.com/keys
- **🎯 OpenRouter** (Premium models): https://openrouter.ai/keys
- **🏢 Cohere** (Enterprise): https://dashboard.cohere.ai/api-keys

### **Step 2: Setup in Your Project**
```bash
# Navigate to ANY Git repository (React, Flutter, Go, Python, etc.)
cd your-awesome-project

# Install Git hook
smart-commits-ai install

# Add your API key
echo "GROQ_API_KEY=your_key_here" >> .env
```

### **Step 3: Start Using AI Commits**
```bash
# Normal Git workflow - AI handles the message!
git add src/components/Button.js
git commit  # ✨ AI generates: "feat(ui): add Button component with hover effects"
```

**That's it! Every `git commit` now uses AI.** 🎉

## 🌍 Works with ANY Project Type

### **React/Next.js Projects**
```bash
# Install via NPM (feels native to JS developers)
npm install smart-commits-ai
npx smart-commits-ai install

# Example AI-generated commits:
# feat(components): add responsive navigation bar with mobile menu
# fix(api): resolve authentication token refresh issue
# style(ui): update button hover animations and color scheme
```

### **Flutter/Mobile Projects**
```bash
# One-line install
curl -fsSL https://raw.githubusercontent.com/Joshi-e8/ai-commit-generator/main/install.sh | bash

# Example AI-generated commits:
# feat(widgets): implement custom date picker with theme support
# fix(navigation): resolve back button behavior on Android
# perf(images): optimize asset loading and caching strategy
```

### **Backend Projects (Go, Rust, Java, etc.)**
```bash
# Docker approach (no dependencies)
docker run --rm -v $(pwd):/workspace joshi/smart-commits-ai install

# Example AI-generated commits:
# feat(api): add user authentication middleware with JWT
# fix(db): resolve connection pool timeout issues
# refactor(handlers): improve error handling and logging
```

### **Any Git Repository**
```bash
# Universal installer
bash <(curl -fsSL https://raw.githubusercontent.com/Joshi-e8/ai-commit-generator/main/install.sh)

# Works with: Python, C++, C#, PHP, Ruby, Swift, Kotlin, and more!
```

---

---

## ✨ Features

- **🌍 Universal**: Works with ANY programming language and project type
- **🤖 AI-Powered**: Uses Groq, OpenRouter, or Cohere APIs
- **📝 Conventional Commits**: Automatic `type(scope): description` format
- **⚡ Fast**: < 2 second response time with Groq
- **📦 Multiple Install Methods**: NPM, Docker, Python, or standalone
- **🔧 Configurable**: Customize prompts, models, and scopes
- **🛡️ Secure**: Only staged changes sent to AI, no data storage
- **🔄 Fallback**: Works even if AI fails
- **🎯 Team-Friendly**: No Python knowledge required for team adoption
- **🧪 Testable**: Comprehensive test suite and type hints
- **🎨 Rich CLI**: Beautiful command-line interface with colors

---

## 🎯 Real-World Examples

### **React Component Changes**
```bash
# Your changes: Added a new Button component with TypeScript
git add src/components/Button.tsx
git commit
# 🤖 AI generates: "feat(components): add Button component with TypeScript and hover animations"
```

### **Flutter Widget Updates**
```bash
# Your changes: Fixed navigation issue on Android
git add lib/screens/home_screen.dart
git commit
# 🤖 AI generates: "fix(navigation): resolve back button behavior on Android devices"
```

### **API Endpoint Development**
```bash
# Your changes: Added user authentication middleware
git add src/middleware/auth.go
git commit
# 🤖 AI generates: "feat(auth): implement JWT middleware with role-based access control"
```

### **Database Schema Updates**
```bash
# Your changes: Added indexes for better performance
git add migrations/add_user_indexes.sql
git commit
# 🤖 AI generates: "perf(db): add indexes on user table for faster queries"
```

## 🏢 Team Adoption

### **For JavaScript/TypeScript Teams**
```json
{
  "devDependencies": {
    "smart-commits-ai": "^1.0.4"
  },
  "scripts": {
    "postinstall": "smart-commits-ai install",
    "commit": "git commit"
  }
}
```

### **For Any Team (Docker)**
```bash
# Add to team setup docs
echo 'alias smart-commits="docker run --rm -v $(pwd):/workspace joshi/smart-commits-ai"' >> ~/.bashrc
```

### **For CI/CD Pipelines**
```yaml
# .github/workflows/commits.yml
- uses: joshi-e8/smart-commits-ai-action@v1
  with:
    api_key: ${{ secrets.GROQ_API_KEY }}
```

---

## 📁 Project Structure

```
ai-commit-generator/
├── README.md                           # This file
├── TEAM_SETUP_GUIDE.md                # Detailed team documentation
├── pyproject.toml                     # Python package configuration
├── src/
│   └── ai_commit_generator/
│       ├── __init__.py                # Package initialization
│       ├── cli.py                     # Command-line interface
│       ├── core.py                    # Main commit generation logic
│       ├── config.py                  # Configuration management
│       ├── api_clients.py             # AI API clients
│       └── git_hook.py                # Git hook management
├── templates/
│   ├── .commitgen.yml                 # Configuration template
│   └── .env.example                   # Environment template
├── tests/                             # Test suite
├── examples/                          # Usage examples
└── legacy/                            # Original bash scripts
    ├── install_hook.sh                # Legacy installer
    └── hooks/
        └── prepare-commit-msg         # Legacy hook script
```

---

## 🖥️ CLI Commands

### Install Hook
```bash
# Install Git hook in current repository
smart-commits-ai install

# Install with configuration files
smart-commits-ai install --config

# Force overwrite existing hook
smart-commits-ai install --force
```

### Manage Installation
```bash
# Check installation status
smart-commits-ai status

# Test with current staged changes
smart-commits-ai test

# Uninstall hook
smart-commits-ai uninstall
```

### Generate Messages
```bash
# Generate message for staged changes
smart-commits-ai generate

# Generate without writing to file (dry run)
smart-commits-ai generate --dry-run

# Generate and save to specific file
smart-commits-ai generate --output commit-msg.txt
```

### Configuration
```bash
# Show current configuration
smart-commits-ai config --show

# Validate configuration
smart-commits-ai config --validate
```

---

## 🔧 Configuration

### Basic Setup (`.env`)
```bash
# Choose one provider
GROQ_API_KEY=gsk_your_key_here
# OPENROUTER_API_KEY=sk-or-your_key_here
# COHERE_API_KEY=your_cohere_key_here
```

### Advanced Setup (`.commitgen.yml`)
```yaml
api:
  provider: groq
  
commit:
  max_chars: 72
  types: [feat, fix, docs, style, refactor, test, chore]
  scopes: [api, ui, auth, db, config]
  
prompt:
  template: |
    Generate a conventional commit message for:
    {{diff}}
```

---

## 🏢 Team Deployment

### Option 1: Shared Network Drive
```bash
# Copy to shared location
cp -r ai-commit-generator /shared/tools/

# Team members install from shared location
/shared/tools/ai-commit-generator/install_hook.sh
```

### Option 2: Internal Git Repository
```bash
# Create internal repo
git init ai-commit-generator
git add .
git commit -m "feat: add AI commit message generator"
git remote add origin https://github.com/your-org/ai-commit-generator.git
git push -u origin main

# Team members clone and install
git clone https://github.com/your-org/ai-commit-generator.git
cd your-project
../ai-commit-generator/install_hook.sh
```

### Option 3: Package Distribution
```bash
# Create distributable package
tar -czf ai-commit-generator.tar.gz ai-commit-generator/

# Team members download and extract
curl -sSL https://your-server/ai-commit-generator.tar.gz | tar -xz
./ai-commit-generator/install_hook.sh
```

---

## 🛠️ Advanced Usage

### Custom Prompts
```yaml
prompt:
  template: |
    You are a senior developer. Generate a commit message for:
    
    {{diff}}
    
    Requirements:
    - Use conventional commits
    - Be specific about business impact
    - Maximum {{max_chars}} characters
```

### Multiple Models
```bash
# Fast and efficient
GROQ_MODEL=llama-3.1-8b-instant

# More detailed
GROQ_MODEL=llama-3.3-70b-versatile

# Creative (if available)
GROQ_MODEL=gemma2-9b-it
```

### Debug Mode
```bash
DEBUG_ENABLED=true
tail -f .commitgen.log
```

---

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not found" | Check `.env` file, ensure correct variable is set |
| "jq: command not found" | Install jq: `brew install jq` or `apt install jq` |
| "Rate limit exceeded" | Wait 1 minute or switch to different provider |
| "Hook not working" | Reinstall: `./install_hook.sh` |
| **"ImportError: dlopen... incompatible architecture"** | **Apple Silicon Fix**: `pip3 uninstall -y charset-normalizer requests && pip3 install --no-cache-dir --force-reinstall charset-normalizer requests` |
| **"ModuleNotFoundError: No module named 'chardet'"** | **Architecture mismatch**: Run the Apple Silicon fix above |

---

## 📊 Provider Comparison

| Provider | Speed | Cost | Models | Best For |
|----------|-------|------|--------|----------|
| **Groq** | ⚡ Very Fast | 🆓 Free | Llama 3, Mixtral | Teams, Daily Use |
| **OpenRouter** | 🐌 Medium | 💰 Paid | Claude, GPT-4 | Premium Quality |
| **Cohere** | ⚖️ Fast | 🆓 Free Tier | Command-R | Enterprise |

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'feat: add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Conventional Commits](https://www.conventionalcommits.org/) specification
- [Groq](https://groq.com/) for fast AI inference
- [OpenRouter](https://openrouter.ai/) for model diversity
- [Cohere](https://cohere.ai/) for enterprise AI

## 🎉 Success Stories

> **"We migrated our entire React team (12 developers) to Smart Commits AI in one day. Now our commit history is consistent and descriptive!"**
> — Frontend Team Lead

> **"Works perfectly with our Flutter CI/CD pipeline. No Python knowledge required for the mobile team."**
> — Mobile Developer

> **"The Docker approach was perfect for our polyglot microservices architecture."**
> — DevOps Engineer

## 📊 Why Teams Choose Smart Commits AI

| Team Type | Traditional Approach | With Smart Commits AI |
|-----------|---------------------|----------------------|
| **React/Next.js** | Inconsistent messages | Professional conventional commits |
| **Flutter/Mobile** | "fix", "update" messages | Descriptive widget/feature commits |
| **Backend APIs** | Generic descriptions | Specific endpoint/middleware commits |
| **Full-Stack** | Mixed commit styles | Unified team standards |

## 🔗 Links

- **📦 PyPI Package**: https://pypi.org/project/smart-commits-ai/
- **📦 NPM Package**: https://www.npmjs.com/package/smart-commits-ai
- **🐳 Docker Hub**: https://hub.docker.com/r/joshi/smart-commits-ai
- **📖 Universal Installation Guide**: [UNIVERSAL_INSTALLATION.md](UNIVERSAL_INSTALLATION.md)
- **🏢 Team Setup Guide**: [TEAM_SETUP_GUIDE.md](TEAM_SETUP_GUIDE.md)

---

**Transform ANY team's commit messages today! 🚀**

*Works with React, Flutter, Go, Python, Java, C++, and every other language.*
