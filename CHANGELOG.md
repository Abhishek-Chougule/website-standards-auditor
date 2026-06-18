# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **LLMO, AISEO, E-E-A-T criteria** (9 new criterion IDs: LLMO-01 to LLMO-03, AISEO-01 to AISEO-02, EEAT-01 to EEAT-04) in `references/website_criteria.md` and `scripts/audit_site.py`.
- **Rule 4: Never change existing UI/UX** in `references/coding_rules.md`, binding on every fix run.
- **External media self-hosting** workflow in `SKILL.md`: download images and convert to WebP, download videos as-is, download fonts; reference replacement map via `media_replacements.json`.
- **`scripts/download_media.py`**: new helper that reads `audit_findings.json`, downloads external images (WebP via Pillow, urllib fallback), videos (as-is), and fonts, and writes `media_replacements.json`.
- **RESIL-03** extended with step-by-step self-hosting instructions (WebP `<picture>` element, video `preload`, font `font-display: swap`).
- **RESIL-04 Privacy page** criterion, detection in scanner, and `assets/privacy_page_template.html` (same design tokens as 404 and offline templates).
- **RESIL-05 Terms of Service page** criterion, detection in scanner, and `assets/terms_page_template.html` (same design tokens).
- **PERF-05 Caching configuration** criterion: `Cache-Control` headers for all asset types, example configs for Netlify, Cloudflare Pages, Vercel, nginx; service worker caching strategy.
- **Privacy and terms page detection** in `audit_site.py`: file name matching and footer link heuristic.
- **Caching config detection** in `audit_site.py`: `_headers`, `vercel.json`, `netlify.toml`, `next.config.*`, `.htaccess`, nginx `.conf` files.
- **Media type classification** (`media_type` field) on every external media hit in `audit_findings.json`.
- **LLMO/AISEO/E-E-A-T signal detection** in `audit_site.py`: author/byline, date, cite, mixed content, HTTPS base href.
- Skill output files added to `.gitignore` and `references/gitignore_standard.txt`: `audit_findings.json`, `gap_identification.md`, `fix_summary.md`, `media_replacements.json`, `lighthouse-report.*`.
- **AI tools section in `.gitignore` expanded** to cover 20+ tools: Claude, Gemini, Codex, Cursor, Windsurf/Codeium, Kilo Code, Cline/Roo, Continue.dev, Aider, GitHub Copilot, Tabnine, Supermaven, Amp, Devin, Pythagora, Qodo, Replit, Zed, OMC, Pear AI, Bolt.new, Lovable, and generic agent directories.
- `CHANGELOG.md`, `CONTRIBUTING.md`, and `LICENSE` (MIT, Abhishek Chougule) added to the repo root.
- Gap report template updated with new category rows: LLMO and AISEO, E-E-A-T, RESIL-04, RESIL-05, PERF-05.

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
