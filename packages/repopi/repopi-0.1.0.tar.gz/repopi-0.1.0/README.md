<div align="center">

# 🚀 RepoPi

**An all-in-one developer assistant for Git workflows, hosting, and AI automation**

[![PyPI version](https://badge.fury.io/py/repopi.svg)](https://badge.fury.io/py/repopi)
[![Python Support](https://img.shields.io/pypi/pyversions/repopi.svg)](https://pypi.org/project/repopi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/saky-semicolon/repopi/workflows/CI/badge.svg)](https://github.com/saky-semicolon/repopi/actions)

</div>

RepoPi streamlines everyday Git workflows and integrates Git hosting features, AI automation, and team productivity tools—directly in the terminal. Replace multiple tools (Git CLI + GitHub/GitLab CLI + ad-hoc AI helpers) with a single, powerful, extensible CLI.

## 📖 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Commands Overview](#-commands-overview)
- [Configuration](#️-configuration)
- [AI Features](#-ai-features)
- [Platform Integration](#-platform-integration)
- [Examples](#-examples)
- [Development](#️-development)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

## ✨ Features

<div align="center">

| Feature | Description | Benefits |
|---------|-------------|----------|
| 🔧 **Git Automation** | Streamlined branch management, commits, pushes, and cleanup | Reduce repetitive Git commands by 80% |
| 🤖 **AI Integration** | AI-powered commit messages and code review assistance | Generate conventional commits automatically |
| 🌐 **Platform Support** | GitHub and GitLab integration for issues, PRs, and releases | Manage repositories without leaving terminal |
| 🎨 **Beautiful CLI** | Rich terminal interface with colors, tables, and progress bars | Enhanced developer experience |
| ⚙️ **Configurable** | Project-level and user-level configuration support | Customize workflows per project |
| 🔒 **Secure** | Encrypted token storage with minimal scope requirements | Enterprise-grade security |

</div>

### Core Capabilities

- **Intelligent Git Workflows**: Smart branch management with automatic cleanup
- **AI-Powered Development**: Generate commit messages, review code, analyze issues
- **Multi-Platform Integration**: Seamless GitHub and GitLab operations
- **Team Collaboration**: Streamlined PR/MR creation and review processes
- **Configuration Management**: Flexible project and user-level settings
- **Terminal-First Design**: Beautiful, fast, and keyboard-friendly interface

## 📦 Installation

### Recommended: pipx (Isolated Installation)

```bash
# Install pipx if you haven't already
python -m pip install --user pipx
python -m pipx ensurepath

# Install RepoPi
pipx install repopi
```

### Alternative: pip

```bash
# Global installation
pip install repopi

# User installation
pip install --user repopi
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/saky-semicolon/repopi.git
cd repopi

# Install in development mode
pip install -e .
```

### System Requirements

- **Python**: 3.9+ (3.11+ recommended)
- **Git**: 2.20+ installed and configured
- **Terminal**: Any modern terminal with Unicode support
- **APIs**: Optional OpenAI API key for AI features

## 🚀 Quick Start

### 1. Initialize RepoPi

```bash
# Navigate to your Git repository
cd your-project

# Initialize RepoPi (creates .repopi.yml)
repopi init
```

### 2. Configure Credentials

```bash
# Essential: Configure your platform tokens
repopi config set github-token YOUR_GITHUB_TOKEN
repopi config set gitlab-token YOUR_GITLAB_TOKEN

# Optional: Enable AI features
repopi config set openai-key YOUR_OPENAI_KEY

# Verify configuration
repopi config show
```

### 3. Basic Workflow

```bash
# Create a feature branch
repopi git branch feature/awesome-feature

# Make your code changes...
# Add files to staging
git add .

# Generate AI-powered commit message
repopi ai commit

# Push with enhanced workflow
repopi git push

# Create a pull request
repopi github pr create
```

## 📋 Commands Overview

RepoPi organizes commands into logical groups for intuitive usage.

### Git Commands

| Command | Description | Example |
|---------|-------------|---------|
| `repopi git branch <name>` | Create and switch to new branch | `repopi git branch feature/auth` |
| `repopi git push [message]` | Enhanced push with optional commit | `repopi git push "Fix auth bug"` |
| `repopi git log [--graph]` | Beautiful commit history | `repopi git log --graph` |
| `repopi git cleanup` | Clean up merged branches | `repopi git cleanup` |
| `repopi git status` | Enhanced git status with insights | `repopi git status` |

### AI Commands

| Command | Description | Use Case |
|---------|-------------|----------|
| `repopi ai commit` | Generate commit message from diff | Auto-generate conventional commits |
| `repopi ai review` | AI code review assistance | Get suggestions before PR |
| `repopi ai issue` | Analyze and categorize issues | Smart issue triage |

### Configuration Commands

| Command | Description | Scope |
|---------|-------------|-------|
| `repopi config show` | Display current configuration | User + Project |
| `repopi config set <key> <value>` | Set configuration values | Persistent storage |
| `repopi config get <key>` | Get specific configuration value | Quick lookup |
| `repopi config reset` | Reset to default configuration | Clean slate |

### GitHub Integration

| Command | Description | Output |
|---------|-------------|--------|
| `repopi github pr create` | Create pull request | Interactive PR creation |
| `repopi github pr list` | List repository PRs | Formatted table |
| `repopi github issues list` | List repository issues | Filter and search |
| `repopi github issues create` | Create new issue | Template-based |
| `repopi github release create` | Create new release | Automated changelog |

### GitLab Integration

| Command | Description | Features |
|---------|-------------|----------|
| `repopi gitlab mr create` | Create merge request | Smart templates |
| `repopi gitlab mr list` | List merge requests | Status filtering |
| `repopi gitlab issues list` | List project issues | Label filtering |
| `repopi gitlab pipeline status` | Check pipeline status | Real-time updates |

## 🛠️ Configuration

RepoPi uses a hierarchical configuration system that provides flexibility and security.

### Configuration Hierarchy

1. **Project Config** (`.repopi.yml`) - Highest priority
2. **User Config** (`~/.repopi/config.json`) - Global defaults
3. **Environment Variables** - Runtime overrides
4. **Built-in Defaults** - Fallback values

### User Configuration

```bash
# Location: ~/.repopi/config.json
repopi config set github-token ghp_your_token_here
repopi config set gitlab-token glpat-your-token-here
repopi config set openai-key sk-your-openai-key
repopi config set default-branch main
repopi config set commit-style conventional
```

### Project Configuration

```yaml
# Location: .repopi.yml (created by 'repopi init')
project:
  name: "My Awesome Project"
  default_branch: "main"
  commit_style: "conventional"

github:
  repository: "username/repo-name"
  auto_pr: true
  
gitlab:
  project_id: 12345
  auto_mr: true

ai:
  commit_template: "conventional"
  review_depth: "detailed"
```

### Environment Variables

```bash
export REPOPI_GITHUB_TOKEN="ghp_your_token"
export REPOPI_GITLAB_TOKEN="glpat_your_token"
export REPOPI_OPENAI_KEY="sk_your_key"
```

### Configuration Options

| Key | Type | Description | Default |
|-----|------|-------------|---------|
| `github-token` | String | GitHub personal access token | None |
| `gitlab-token` | String | GitLab personal access token | None |
| `openai-key` | String | OpenAI API key for AI features | None |
| `default-branch` | String | Default branch name | `main` |
| `commit-style` | String | Commit message style (`conventional`, `simple`) | `conventional` |
| `auto-push` | Boolean | Auto-push after commit | `false` |
| `auto-pr` | Boolean | Auto-create PR after push | `false` |

## 🤖 AI Features

RepoPi integrates cutting-edge AI to enhance your development workflow.

### Smart Commit Messages

```bash
# Make changes to your code
echo "console.log('Hello World');" > app.js
git add app.js

# Generate AI-powered commit message
repopi ai commit

# Output: "feat: add hello world functionality to app.js"
```

**Supported Commit Styles:**
- **Conventional Commits**: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`
- **Simple**: Clear, descriptive messages
- **Custom**: Define your own templates

### Code Review Assistant

```bash
# Get AI review of your changes
repopi ai review

# Sample output:
# 🔍 AI Code Review
# ✅ Good: Clear variable naming
# ⚠️  Warning: Consider error handling
# 💡 Suggestion: Add type hints for better maintainability
```

### Issue Analysis

```bash
# Analyze and categorize issues
repopi ai issue analyze

# Auto-categorize by:
# - Bug reports vs feature requests
# - Priority levels
# - Estimated complexity
# - Required expertise
```

### AI Configuration

```bash
# Configure AI behavior
repopi config set ai-model "gpt-4"
repopi config set ai-temperature 0.7
repopi config set ai-max-tokens 150
```

## 🌐 Platform Integration

### GitHub Integration

#### Authentication Setup

```bash
# Create a Personal Access Token at:
# https://github.com/settings/tokens/new

# Required scopes:
# - repo (for private repositories)
# - public_repo (for public repositories)
# - workflow (for GitHub Actions)

repopi config set github-token ghp_your_token_here
```

#### Common Workflows

```bash
# Create and push feature branch
repopi git branch feature/new-api
# ... make changes ...
repopi ai commit
repopi git push

# Create pull request with AI-generated description
repopi github pr create --ai-description

# Review and merge
repopi github pr review --ai-suggestions
repopi github pr merge
```

### GitLab Integration

#### Authentication Setup

```bash
# Create a Personal Access Token at:
# https://gitlab.com/-/profile/personal_access_tokens

# Required scopes:
# - api (full API access)
# - read_repository
# - write_repository

repopi config set gitlab-token glpat-your-token-here
```

#### Common Workflows

```bash
# Create merge request
repopi gitlab mr create --title "Add new feature" --description "Detailed description"

# Check pipeline status
repopi gitlab pipeline status

# Review merge request
repopi gitlab mr review --id 123
```

## 💡 Examples

### Example 1: Feature Development Workflow

```bash
# Start new feature
repopi git branch feature/user-authentication

# Make code changes...
# Add new files and modifications
git add .

# Generate commit with AI
repopi ai commit
# Output: "feat: implement JWT-based user authentication system"

# Push with enhanced workflow
repopi git push

# Create pull request with AI description
repopi github pr create --ai-description
```

### Example 2: Bug Fix Workflow

```bash
# Create hotfix branch
repopi git branch hotfix/fix-login-redirect

# Fix the bug...
git add .

# Generate fix commit
repopi ai commit
# Output: "fix: resolve login redirect loop in auth middleware"

# Quick push and PR
repopi git push && repopi github pr create --urgent
```

### Example 3: Code Review Automation

```bash
# Before creating PR, get AI review
repopi ai review

# Sample AI feedback:
# 🔍 Code Review Summary:
# ✅ Code quality: Good
# ⚠️  Security: Add input validation
# 💡 Performance: Consider caching
# 📝 Documentation: Add JSDoc comments

# Apply suggestions and commit
repopi ai commit --include-review-fixes
```

### Example 4: Team Collaboration

```bash
# Check team activity
repopi github activity --team

# Review pending PRs
repopi github pr list --status pending --assigned-to me

# Batch review PRs
repopi github pr review --batch --ai-assist
```

## 🏗️ Development

### Prerequisites

- **Python 3.9+** (3.11+ recommended for best performance)
- **Git 2.20+** with proper configuration
- **Poetry** (recommended) or pip for dependency management
- **Node.js 16+** (optional, for docs development)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/saky-semicolon/repopi.git
cd repopi

# Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Install pre-commit hooks
pre-commit install

# Verify installation
repopi --version
```

### Project Structure

```
repopi/
├── repopi/                 # Main package
│   ├── commands/          # CLI command modules
│   │   ├── ai/           # AI-related commands
│   │   ├── github/       # GitHub integration
│   │   └── gitlab/       # GitLab integration
│   └── utils/            # Utility modules
├── tests/                # Test suite
├── docs/                 # Documentation
├── pyproject.toml        # Project configuration
└── README.md            # This file
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=repopi --cov-report=html --cov-report=term

# Run specific test categories
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m slow          # Long-running tests

# Run tests for specific module
pytest tests/test_git.py

# Run with verbose output
pytest -v --tb=short
```

### Code Quality

RepoPi maintains high code quality standards:

```bash
# Format code
black .
isort .

# Lint code
ruff check .
ruff check . --fix  # Auto-fix issues

# Type checking
mypy .

# Security scan
bandit -r repopi/

# Run all quality checks
pre-commit run --all-files
```

### Quality Standards

- **Code Coverage**: Minimum 85%
- **Type Coverage**: 100% (strict mypy)
- **Security**: No high/critical vulnerabilities
- **Performance**: Commands under 2s response time
- **Documentation**: All public APIs documented

### Building Documentation

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve

# Deploy to GitHub Pages
mkdocs gh-deploy
```

### Release Process

```bash
# Use the automated release script
./release.sh 0.2.0

# Or manually:
# 1. Update version in pyproject.toml and __init__.py
# 2. Update CHANGELOG.md
# 3. Commit changes
# 4. Create tag and push
git tag v0.2.0
git push origin main --tags
```

## 📖 Documentation

### Complete Documentation Suite

- **[User Manual](USER_MANUAL.md)** - Comprehensive usage guide with examples
- **[API Reference](https://repopi.readthedocs.io/api/)** - Complete API documentation
- **[Contributing Guide](CONTRIBUTING.md)** - Development and contribution guidelines
- **[Security Policy](SECURITY.md)** - Security policies and vulnerability reporting
- **[Changelog](CHANGELOG.md)** - Detailed version history and breaking changes
- **[Release Checklist](RELEASE_CHECKLIST.md)** - Release process documentation

### Quick Links

- 📚 [Documentation Site](https://repopi.readthedocs.io)
- 🎥 [Video Tutorials](https://youtube.com/playlist?list=repopi-tutorials)
- 💬 [Community Forum](https://github.com/saky-semicolon/repopi/discussions)
- 🐛 [Issue Tracker](https://github.com/saky-semicolon/repopi/issues)

## 🤝 Contributing

We welcome contributions from developers of all skill levels! Here's how you can help:

### Ways to Contribute

- 🐛 **Report Bugs**: Submit detailed bug reports with reproduction steps
- ✨ **Request Features**: Propose new features with clear use cases
- 💻 **Code Contributions**: Submit pull requests for bug fixes or features
- 📖 **Documentation**: Improve docs, examples, and tutorials
- 🧪 **Testing**: Add test cases or improve test coverage
- 🌍 **Translations**: Help internationalize RepoPi

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
4. **Make your changes** with tests and documentation
5. **Run quality checks** (`pre-commit run --all-files`)
6. **Submit a pull request** with clear description

### Development Guidelines

- **Code Style**: Follow Black and isort formatting
- **Testing**: Maintain 85%+ test coverage
- **Documentation**: Update docs for all changes
- **Commits**: Use conventional commit messages
- **Reviews**: All PRs require review and CI passing

### Contributor Recognition

Contributors are recognized in:
- README.md acknowledgments
- CHANGELOG.md for each release
- GitHub contributors page
- Annual contributor spotlight

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### License Summary

- ✅ **Commercial use allowed**
- ✅ **Modification allowed**
- ✅ **Distribution allowed**
- ✅ **Private use allowed**
- ❗ **License and copyright notice required**

## 🙏 Acknowledgments

RepoPi is built on the shoulders of giants. Special thanks to:

### Core Technologies
- **[Typer](https://typer.tiangolo.com/)** - Modern CLI framework with excellent developer experience
- **[Rich](https://rich.readthedocs.io/)** - Beautiful and powerful terminal formatting library
- **[GitPython](https://gitpython.readthedocs.io/)** - Comprehensive Git repository interaction
- **[PyGithub](https://pygithub.readthedocs.io/)** - Complete GitHub API integration
- **[python-gitlab](https://python-gitlab.readthedocs.io/)** - Full-featured GitLab API client

### AI and ML
- **[OpenAI](https://openai.com/)** - GPT models for intelligent code assistance
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Data validation and settings management

### Development Tools
- **[Poetry](https://python-poetry.org/)** - Modern dependency management and packaging
- **[pytest](https://pytest.org/)** - Comprehensive testing framework
- **[Black](https://black.readthedocs.io/)** - Uncompromising code formatter
- **[Ruff](https://ruff.rs/)** - Extremely fast Python linter
- **[mypy](https://mypy.readthedocs.io/)** - Static type checker

### Community
- All our **[contributors](https://github.com/saky-semicolon/repopi/graphs/contributors)** who make RepoPi better
- The **Python community** for excellent tools and libraries
- **GitHub** and **GitLab** for providing excellent platforms and APIs

## 🆘 Support

### Getting Help

- 📖 **Documentation**: Check our [complete documentation](https://repopi.readthedocs.io)
- 💬 **Discussions**: Join [GitHub Discussions](https://github.com/saky-semicolon/repopi/discussions)
- 🐛 **Bug Reports**: Create an [issue](https://github.com/saky-semicolon/repopi/issues/new/choose)
- 💡 **Feature Requests**: Propose features in [discussions](https://github.com/saky-semicolon/repopi/discussions/categories/ideas)

### Community Guidelines

- Be respectful and inclusive
- Provide clear, detailed information
- Search existing issues before creating new ones
- Follow our [Code of Conduct](CODE_OF_CONDUCT.md)

### Commercial Support

For enterprise customers requiring:
- Priority support
- Custom feature development
- Training and consulting
- SLA agreements

Contact: **support@repopi.dev**

---

<div align="center">

**[🏠 Homepage](https://github.com/saky-semicolon/repopi) • [📚 Documentation](https://repopi.readthedocs.io) • [🐛 Report Bug](https://github.com/saky-semicolon/repopi/issues) • [✨ Request Feature](https://github.com/saky-semicolon/repopi/discussions)**

---

Made with ❤️ by [S M Asiful Islam Saky](https://github.com/saky-semicolon) and the RepoPi community

</div>
