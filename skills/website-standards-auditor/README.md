# Website Standards Auditor (skill)

An Agent Skill that audits any website (new, in development, or already live) against one fixed set of organization standards, then fixes the gaps after the user approves. It runs in two phases with a hard approval gate: it produces a written gap report first, then repairs only the approved items and reconciles `.gitignore` and `README.md`.

## What it covers

- Engineering and content rules: never assume, never use the em dash, always keep `.gitignore` and `README.md` current.
- Git policy: a project `.gitignore` based on the organization standard, with no tracked secrets.
- Website quality: SEO, GEO, AEO, `llms.txt`, sitemap, robots, metadata, canonical and hreflang, schema and FAQ markup, entity and knowledge graph readiness, internal links and topic clusters, Core Web Vitals, page speed, mobile, Lighthouse, custom 404, offline page, no external media, no emojis, and optional items such as Open Graph, Twitter cards, and analytics.

## How it works

1. Establish context (lifecycle, stack, URL, locales, business type) by detection, asking only for what cannot be derived.
2. Audit: run `scripts/audit_site.py` for deterministic checks, apply the git policy, and do judgment checks by reading files. For a live URL, also inspect the served HTML and headers. Run Lighthouse when the environment allows.
3. Write `gap_identification.md` from the template, then stop and wait for approval.
4. On approval, fix the approved items in priority order, using the templates in `assets/`, filling them with real values supplied by the user.
5. Reconcile `.gitignore` and `README.md` on every fix run.
6. Write `fix_summary.md` and present the changed files.

## Layout

```
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

## Running the scanner directly

```bash
python3 scripts/audit_site.py --path <repo-root> --out audit_findings.json
```

It writes structured findings as JSON and prints a readable summary. It never modifies the project. Use it as input to the gap report, not as the final verdict, since some items need human judgment.
