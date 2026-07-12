# Contributing to Coding Agent Framework

Thank you for your interest in contributing! This document outlines the process for contributing to this project.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/coding-agent-framework.git
   cd coding-agent-framework
   ```
3. **Create a virtual environment** and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -e .[dev]
   ```
4. **Run tests** to verify setup:
   ```bash
   pytest tests/ -v
   ```

## 📋 Development Workflow

### Branch Naming Convention

| Type | Prefix | Example |
|------|--------|---------|
| Feature | `feat/` | `feat/add-azure-openai-support` |
| Bug Fix | `fix/` | `fix/sandbox-timeout-windows` |
| Documentation | `docs/` | `docs/update-api-reference` |
| Refactor | `refactor/` | `refactor/llm-factory-pattern` |
| Test | `test/` | `test/integration-pipeline` |
| Chore | `chore/` | `chore/update-dependencies` |

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>

<body>

<footer>
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`

**Examples:**
```
feat(llm): add support for Azure OpenAI managed identity auth

fix(sandbox): handle resource limits on Windows platform

docs(readme): add WebSocket streaming example
```

### Pull Request Process

1. **Open a draft PR** early for discussion
2. **Ensure all checks pass**:
   - `ruff check .` (linting)
   - `ruff format .` (formatting)
   - `mypy src/coding_agent --ignore-missing-imports` (type checking)
   - `pytest tests/ -v` (tests)
3. **Update documentation** if needed
4. **Request review** from maintainers
5. **Address feedback** and push updates
6. **Squash and merge** when approved

## 🧪 Testing Guidelines

### Writing Tests

- **Unit tests**: Test individual functions/classes in isolation with mocks
- **Integration tests**: Test full pipeline with mocked LLM providers
- **Location**: `tests/unit/` or `tests/integration/`
- **Naming**: `test_<module>_<functionality>.py`

### Test Fixtures

Use the existing fixtures in `tests/conftest.py`:
- `mock_llm_response` - Standard LLM response
- `mock_llm_provider` - AsyncMock with health_check and estimate_cost

### Adding New Tests

```python
# tests/unit/test_new_feature.py
import pytest
from coding_agent.module import NewFeature

def test_new_feature_basic():
    feature = NewFeature()
    assert feature.do_something() == expected_result

@pytest.mark.asyncio
async def test_new_feature_async(mock_llm_provider):
    # Integration-style test
    pass
```

## 🎨 Code Style

We use **Ruff** for linting and formatting (replaces Black, isort, flake8):

```bash
# Check
ruff check .

# Auto-fix
ruff check --fix .

# Format
ruff format .
```

**Key rules:**
- Line length: 100 characters
- Target: Python 3.11+
- Import sorting: isort-compatible
- Type hints required for public APIs

### Type Hints

- Use `X | None` instead of `Optional[X]` (Python 3.10+)
- Annotate all public function signatures
- Use `TypedDict` for dictionary shapes
- Prefer `list[str]` over `List[str]` (Python 3.9+)

## 📝 Documentation

- **Docstrings**: Google-style for all public classes/functions
- **README**: Update for new features, CLI commands, config options
- **API Reference**: Update `docs/api_reference.md` for new endpoints
- **Architecture**: Update `docs/architecture.md` for structural changes

## 🐛 Reporting Bugs

Use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.yml) with:
- Python version (`python --version`)
- OS and version
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs/config (sanitized)

## 💡 Feature Requests

Use the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.yml) with:
- Problem statement
- Proposed solution
- Alternatives considered
- Implementation approach (if known)

## 🔒 Security Issues

**Do not open public issues** for security vulnerabilities. Email security@yourdomain.com or use GitHub Security Advisories.

---

## 🏷 Release Process

Maintainers only:
1. Update `CHANGELOG.md`
2. Bump version in `pyproject.toml`
3. Create git tag: `git tag v0.x.x`
4. Push tag: `git push origin v0.x.x`
5. GitHub Actions builds and publishes to PyPI

---

## 📞 Getting Help

- **Discussions**: GitHub Discussions for questions
- **Issues**: Bug reports and feature requests
- **Discord**: [Community Server](https://discord.gg/example) (if available)

---

Thank you for contributing! 🎉