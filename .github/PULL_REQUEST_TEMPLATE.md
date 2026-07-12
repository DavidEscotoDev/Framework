# Pull Request Template

## Description
<!-- Brief summary of changes -->

## Type of Change
<!-- Check all that apply -->
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactor (no functional changes)
- [ ] Performance improvement
- [ ] Test addition/update
- [ ] Chore (dependencies, build, CI, etc.)

## Related Issues
<!-- Link related issues: fixes #123, relates to #456 -->
- Fixes #
- Relates to #

## Changes Made
<!-- List the key changes -->
-
-
-

## Testing
<!-- Describe how you tested your changes -->
- [ ] Unit tests pass (`pytest tests/unit/ -v`)
- [ ] Integration tests pass (`pytest tests/integration/ -v`)
- [ ] Added new tests for new functionality
- [ ] Manual testing performed (describe below)

### Manual Test Steps
1.
2.
3.

## Checklist
<!-- Ensure all items are checked before requesting review -->
- [ ] Code follows project style (`ruff check . && ruff format .`)
- [ ] Type checks pass (`mypy src/coding_agent --ignore-missing-imports`)
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Documentation updated (README, docstrings, API reference)
- [ ] CHANGELOG.md updated (if user-facing change)
- [ ] No breaking changes without version bump discussion
- [ ] Conventional commit messages used

## Screenshots/Logs (if applicable)
<!-- Add screenshots for UI changes or relevant logs -->

## Breaking Changes
<!-- If this is a breaking change, describe impact and migration path -->