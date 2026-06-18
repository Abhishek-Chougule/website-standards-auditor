# Website Standards Auditor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![skills.sh](https://img.shields.io/badge/skills.sh-discoverable-blue)](https://skills.sh)

An open Agent Skill that audits any website (new, in development, or already live) against a fixed set of engineering, git, SEO/GEO/AEO, LLMO, AISEO, E-E-A-T, performance, and compliance standards. It writes a `gap_identification.md` report and, after you approve, fixes the gaps, self-hosts external media, scaffolds missing pages, and reconciles `.gitignore` and `README.md`.

## Skills in this repo

- **`website-standards-auditor`**: Two-phase audit-and-fix skill. Covers engineering rules, git policy, SEO, GEO, AEO, LLMO, AISEO, E-E-A-T, structured data, Core Web Vitals, Lighthouse, caching, external media self-hosting (images to WebP, videos as-is), privacy page, Terms of Service page, custom 404, offline page, and more. See [`skills/website-standards-auditor/README.md`](skills/website-standards-auditor/README.md).

## Install

Replace `Abhishek-Chougule` with your own username if you fork this repo.

```bash
# Install every skill in this repo
npx skills add Abhishek-Chougule/website-standards-auditor

# List skills in the repo without installing
npx skills add Abhishek-Chougule/website-standards-auditor --list

# Install only this skill, into a specific agent
npx skills add Abhishek-Chougule/website-standards-auditor --skill website-standards-auditor -a claude-code
```

Skills install into your agent's skills directory (for example `.claude/skills/`).

## Quick start

After installing the skill, invoke it in your agent:

```
Audit my website at https://example.com against the organization standards.
```

The skill will:
1. Establish context (lifecycle, stack, URL, locales, business type) by detection.
2. Run `scripts/audit_site.py` for deterministic checks plus judgment checks by reading files.
3. Write `gap_identification.md`, then stop and wait for your approval.
4. On approval, fix the approved items using the bundled templates, self-host external media using `scripts/download_media.py`, scaffold missing pages (privacy, terms, 404, offline), and configure caching.
5. Reconcile `.gitignore` and `README.md`.
6. Write `fix_summary.md` summarizing all changes.

## What it covers

| Area | Details |
|---|---|
| Engineering rules | Never assume, no em dash, keep `.gitignore` and `README.md` current, never change existing UI/UX |
| Git hygiene | Standard `.gitignore` (OS, secrets, IDE, AI tools, build output, skill output), no tracked secrets |
| SEO | Titles, meta descriptions, canonical, hreflang, heading structure, keyword mapping, internal links |
| GEO and AEO | `llms.txt`, answer-ready content, semantic structure, entity consistency |
| LLMO and AISEO | LLM-optimized headings and passages, AI-readable `llms.txt`, citations, conversational intent |
| E-E-A-T | Author bylines, Person schema, `sameAs`, HTTPS, privacy page, Terms of Service page |
| Structured data | Organization, WebSite, BreadcrumbList, FAQPage, LocalBusiness JSON-LD |
| Performance | Core Web Vitals, Lighthouse, WebP images, lazy loading, `Cache-Control` headers, Brotli/gzip |
| External media | Download images (convert to WebP), download videos (as-is), download fonts, update all references |
| Resilience | Custom 404, offline page, privacy page, Terms of Service page, no external media hot-links |
| Content and style | No em dash, no emojis (use icons instead) |
| Optional | Open Graph, Twitter cards, Google Analytics, Google Search Console, conversion tracking |

## Repository layout

```
website-standards-auditor/
  LICENSE
  README.md
  CHANGELOG.md
  CONTRIBUTING.md
  .gitignore
  skills/
    website-standards-auditor/
      SKILL.md
      README.md
      references/
        coding_rules.md
        git_policy.md
        gitignore_standard.txt
        website_criteria.md
      scripts/
        audit_site.py
        download_media.py
      assets/
        gap_identification_template.md
        schema_templates.md
        robots_txt_template.txt
        llms_txt_template.md
        offline_page_template.html
        not_found_template.html
        privacy_page_template.html
        terms_page_template.html
```

## Generated files (not committed)

The skill produces these files during a run. They are excluded by `.gitignore` and should never be committed:

| File | Produced by |
|---|---|
| `audit_findings.json` | `scripts/audit_site.py` (Phase 1 scan) |
| `gap_identification.md` | Skill (Phase 1 report) |
| `fix_summary.md` | Skill (Phase 2 summary) |
| `media_replacements.json` | `scripts/download_media.py` |
| `lighthouse-report.json` / `.html` | Lighthouse (Phase 2 performance check) |

## Publishing and discovery

There is no submission form for skills.sh. A skill becomes discoverable by living in a public Git repository with the `skills/<name>/SKILL.md` layout used here. Once people install it with `npx skills add Abhishek-Chougule/website-standards-auditor`, it appears on skills.sh through anonymous install telemetry.

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of notable changes.

## Author

**Abhishek Chougule** - [Abhishek-Chougule](https://github.com/Abhishek-Chougule)

## License

[MIT](LICENSE) - Copyright (c) 2026 Abhishek Chougule
