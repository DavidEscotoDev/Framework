# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities via public GitHub issues.**

Instead, please report them via one of these channels:

### Preferred: GitHub Private Vulnerability Reporting
1. Go to the **Security** tab of this repository
2. Click **Report a vulnerability**
3. Fill out the form with details

### Alternative: Email
Send details to **security@yourdomain.com** with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Response Timeline

| Severity | Initial Response | Fix Target |
|----------|-----------------|------------|
| Critical | 24 hours        | 72 hours   |
| High     | 48 hours        | 1 week     |
| Medium   | 1 week          | 2 weeks    |
| Low      | 2 weeks         | Next release |

## Security Features

This project includes several security measures:

### Code Execution Safety
- **Static malware scanner** blocks dangerous patterns before execution:
  - `os.system`, `os.popen`, `subprocess.*`
  - `eval`, `exec`, `compile`
  - `__import__`, `importlib`
  - File system access outside sandbox
- **Subprocess sandbox** with resource limits:
  - CPU time limit (configurable, default 10s)
  - Memory limit (configurable, default 512MB)
  - Isolated temporary directory per execution

### API Security
- No authentication built-in (deploy behind reverse proxy with auth)
- Input validation via Pydantic v2 on all endpoints
- Rate limiting recommended at infrastructure level

### Dependency Security
- `bandit` in dev dependencies for static analysis
- `pip-audit` recommended for CI
- Minimal dependencies with pinned versions

## Best Practices for Users

1. **Never run untrusted code** without reviewing sandbox output
2. **Use API keys with minimal permissions** (read-only where possible)
3. **Deploy behind authentication** (OAuth, API gateway, VPN)
4. **Monitor sandbox metrics** for anomalous execution patterns
5. **Keep dependencies updated** - run `pip-audit` regularly

## Disclosure Policy

When a security vulnerability is reported:
1. We acknowledge receipt within the timeline above
2. We investigate and develop a fix
3. We coordinate disclosure with the reporter
4. We release a patch and publish a security advisory
5. We credit the reporter (unless they request anonymity)

## Contact

For security questions or concerns:
- **Email**: security@yourdomain.com
- **PGP Key**: [Available on request]