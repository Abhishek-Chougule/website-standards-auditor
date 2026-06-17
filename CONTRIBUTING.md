# Contributing to website-standards-auditor

Thank you for considering a contribution. This document describes the process for reporting issues and submitting pull requests.

## Code of Conduct

By participating in this project you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## How to report a bug

1. Search [existing issues](https://github.com/Abhishek-Chougule/website-standards-auditor/issues) first to avoid duplicates.
2. Open a new issue and fill in the bug report template.
3. Include the command you ran, the full error output, and your OS and Python version.

## How to suggest an improvement

Open an issue with the label `enhancement` and describe:
- The current behaviour.
- The desired behaviour.
- Why this change would benefit other users.

## How to submit a pull request

1. Fork the repository and create a branch from `main`.
2. Make your changes. Keep commits focused and well described.
3. Ensure `scripts/audit_site.py` still runs without errors on the test fixtures.
4. Open a pull request against `main`. Fill in the PR template.
5. A maintainer will review your change. Please respond to review comments promptly.

## Coding standards

- Python code in `scripts/` must be compatible with Python 3.9 and later.
- Follow [PEP 8](https://peps.python.org/pep-0008/) for formatting.
- Do not use the em dash character (U+2014) anywhere in documentation or code comments.
- Do not use emojis in documentation. Use plain text equivalents.
- Every new standard or criterion added to `references/website_criteria.md` must include detect, fix, and severity fields.

## Commit message style

Use the imperative mood in the subject line (e.g., `Add hreflang check`, not `Added hreflang check`).
Keep the subject line to 72 characters or fewer.
Reference relevant issues in the body with `Fixes #<number>` or `Closes #<number>`.

## License

By contributing you agree that your contributions will be licensed under the [MIT License](LICENSE).
