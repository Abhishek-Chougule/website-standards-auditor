# Website Standards Auditor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![skills.sh](https://img.shields.io/badge/skills.sh-discoverable-blue)](https://skills.sh)

An open Agent Skill that audits any website (new, in development, or already live) against a fixed set of engineering, git, and SEO/GEO/AEO standards. It writes a `gap_identification.md` report and, after you approve, fixes the gaps and reconciles `.gitignore` and `README.md`.

## Skills in this repo

- **`website-standards-auditor`**: Two-phase audit-and-fix skill covering engineering rules, git policy, SEO, GEO, AEO, performance, structured data, Core Web Vitals, Lighthouse, and more. See [`skills/website-standards-auditor/README.md`](skills/website-standards-auditor/README.md).

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
4. On approval, fix the approved items using the bundled templates.
5. Reconcile `.gitignore` and `README.md`.
6. Write `fix_summary.md` summarizing all changes.

## Repository layout

```
website-standards-auditor/
  LICENSE
  README.md
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
      assets/
        gap_identification_template.md
        schema_templates.md
        robots_txt_template.txt
        llms_txt_template.md
        offline_page_template.html
        not_found_template.html
```

## Publishing and discovery

There is no submission form for skills.sh. A skill becomes discoverable by living in a public Git repository with the `skills/<name>/SKILL.md` layout used here. Once people install it with `npx skills add Abhishek-Chougule/website-standards-auditor`, it appears on skills.sh through anonymous install telemetry.

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Author

**Abhishek Chougule** - [Abhishek-Chougule](https://github.com/Abhishek-Chougule)

## License

[MIT](LICENSE) - Copyright (c) 2026 Abhishek Chougule
