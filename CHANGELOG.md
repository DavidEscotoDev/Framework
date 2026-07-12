# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure with multi-agent pipeline (Planner, Coder, Reviewer, Tester)
- LLM provider abstraction with 5 backends: NVIDIA NIM, OpenAI, Azure OpenAI, Ollama, llama.cpp
- Automatic fallback chain for LLM providers
- FastAPI REST API with WebSocket streaming
- Typer CLI (`generate`, `serve`, `config` commands)
- Python library client for programmatic access
- Static malware scanner (regex-based)
- Subprocess sandbox with CPU/memory limits (cross-platform)
- Prometheus metrics (pipeline latency, request counts, agent latency, review scores)
- OpenTelemetry tracing with OTLP export
- Structured JSON logging with structlog
- Pydantic Settings + YAML + environment variable configuration
- Comprehensive unit tests (config, malware scanner)
- Integration tests with mocked LLM providers
- GitHub Actions CI (Ubuntu 3.11/3.12, Windows 3.12)
- Docker multi-stage build with docker-compose

### Changed
- N/A

### Deprecated
- N/A

### Removed
- Dead code: `state_store.py` (never used)
- Scaffold scripts: `gen_*.py` (generator scripts)

### Fixed
- Windows sandbox compatibility (uses timeout instead of `resource.setrlimit`)
- Lint issues across entire codebase (120+ ruff fixes)
- Type annotations (mypy clean with `--ignore-missing-imports`)
- Test syntax errors in malware scanner tests

### Security
- Malware scanner blocks code execution for dangerous patterns (`os.system`, `eval`, `subprocess`)

---

## [0.1.0] - 2026-07-12

### Added
- Initial release with all core features listed above

---

## Release Process

1. Update version in `pyproject.toml`
2. Update this CHANGELOG.md
3. Create git tag: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`
5. GitHub Actions builds and publishes to PyPI (configured in CI)