# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-06-17

### Added
- Initial release of the `website-standards-auditor` Agent Skill.
- Two-phase audit-and-fix flow with a hard approval gate between phases.
- `scripts/audit_site.py`: deterministic static scanner for em dashes, emojis, missing files, metadata signals, `.gitignore` compliance, and tracked secrets.
- `references/website_criteria.md`: full checklist covering SEO, GEO, AEO, structured data, performance, Core Web Vitals, Lighthouse, mobile, metadata, canonicals, hreflang, redirects, and internal linking.
- `references/coding_rules.md`: engineering and content rules.
- `references/git_policy.md` and `references/gitignore_standard.txt`: mandatory git policy and standard `.gitignore`.
- Asset templates: `gap_identification_template.md`, `schema_templates.md`, `robots_txt_template.txt`, `llms_txt_template.md`, `offline_page_template.html`, `not_found_template.html`.
- MIT License.
- `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`.
