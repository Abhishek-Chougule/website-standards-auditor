# Website criteria

This is the full checklist the site is audited against. Every criterion has an ID, what it means, how to detect it, how to fix it, a severity, and when it applies. Use the IDs in `gap_identification.md`.

Severity scale: Blocking (ship stopper or security), High (clear standards failure with real impact), Medium (should fix), Low (nice to have or polish). "Applies" tells you when a criterion is relevant; mark a criterion Not applicable when its condition is not met (for example hreflang on a single language site).

## Table of contents

1. Crawl and discovery files (CRAWL)
2. On page SEO (SEO)
3. Structured data and entities (STRUCT)
4. Generative and answer engine optimization (GEO)
5. Performance, Core Web Vitals, and mobile (PERF)
6. Resilience and self contained delivery (RESIL)
7. Content and style rules (STYLE)
8. Git and repository hygiene (GIT)
9. Optional enhancements (OPT)
10. Running Lighthouse
11. How SEO, GEO, and AEO relate

---

## 1. Crawl and discovery files (CRAWL)

**CRAWL-01 robots.txt.** A `robots.txt` at the site root that allows the right crawling, blocks what should be private, and points to the sitemap. Detect: file presence at root, a `Sitemap:` line, no accidental site wide `Disallow: /` in production. Fix: create from `assets/robots_txt_template.txt`, set sane directives, add the absolute sitemap URL. Severity: High. Applies: always.

**CRAWL-02 sitemap.xml.** A valid XML sitemap listing canonical, indexable URLs. Detect: file presence, well formed XML, URLs use the canonical host and scheme, referenced from robots.txt. Fix: generate from routes or pages, use absolute canonical URLs, keep it under the per file URL limit and split with a sitemap index if larger, reference it in robots.txt. Severity: High. Applies: always.

**CRAWL-03 llms.txt.** An `llms.txt` (and optionally `llms-full.txt`) at the site root that gives language models a clean, structured summary of the site and links to its key pages. Detect: file presence at root. Fix: create from `assets/llms_txt_template.md` with the site name, a one line description, and curated links to primary pages and docs. This supports GEO and AEO. Severity: Medium. Applies: always.

**CRAWL-04 Redirects.** Redirect rules are correct and minimal: no redirect chains, no loops, consistent trailing slash behavior, and a single canonical host and scheme (for example force https and one of www or non www). Detect: read redirect config (framework config, server rules, host config) and, for a live URL, follow redirects on key paths. Fix: collapse chains to a single hop, remove loops, standardize trailing slash and host, use permanent redirects for permanent moves. Severity: Medium. Applies: always.

---

## 2. On page SEO (SEO)

**SEO-01 Title tags.** Every page has a unique, descriptive `<title>`, roughly 50 to 60 characters. Detect: scan for `<title>` in source or head components; for live pages confirm it renders and is unique per page. Fix: add or rewrite titles, make each unique and descriptive, front load the primary term. Severity: High. Applies: always.

**SEO-02 Meta descriptions.** Every page has a unique meta description, roughly 140 to 160 characters, that reads as a useful summary. Detect: scan for `name="description"`; confirm uniqueness. Fix: write distinct descriptions per page. Severity: Medium. Applies: always.

**SEO-03 Essential meta tags.** Each page declares charset and viewport, and uses a robots meta only where intentional. Detect: scan for `charset`, `name="viewport"`, and any `name="robots"`. Fix: add `<meta charset="utf-8">` and `<meta name="viewport" content="width=device-width, initial-scale=1">`; remove stray `noindex` from production pages. Severity: High. Applies: always.

**SEO-04 Canonical tags.** Each page has a self referencing canonical link using the absolute canonical URL. Detect: scan for `rel="canonical"`; confirm it points to the canonical host. Fix: add self referencing canonicals; for duplicates point them at the preferred URL. Requires the canonical domain (ask if unknown). Severity: High. Applies: always.

**SEO-05 hreflang.** Language and region variants reference each other with `hreflang`, reciprocally, plus an `x-default`. Detect: scan for `hreflang`; check reciprocity. Fix: add a complete, reciprocal set with `x-default`. Requires the locale list (ask if unknown). Severity: High. Applies: multilingual or multiregional sites only.

**SEO-06 Heading structure.** One `<h1>` per page and a logical, sequential heading hierarchy. Detect: scan headings per page. Fix: ensure a single descriptive `<h1>` and ordered subheadings. Severity: Medium. Applies: always.

**SEO-07 Keyword mapping.** Each important page targets a clear primary topic and supporting terms, with no two pages competing for the same query. Detect: review page content and the user supplied keyword list against pages. Fix: map one primary topic per page, resolve cannibalization, reflect terms naturally in titles, headings, and copy. Note: the legacy `meta keywords` tag is not used for ranking and is not added; this is about content and information architecture. Severity: Medium. Applies: always.

**SEO-08 Internal links.** A coherent internal link structure with descriptive anchor text, no orphan pages, and no broken internal links. Detect: build the internal link graph from the source and find pages with no inbound links and links that resolve to nothing. Fix: add contextual internal links, give anchors descriptive text, repair or remove broken links. Severity: Medium. Applies: always.

---

## 3. Structured data and entities (STRUCT)

**STRUCT-01 Schema markup.** Pages carry valid JSON-LD structured data appropriate to their type (for example `Organization` and `WebSite` site wide, `BreadcrumbList` on deep pages, `Article` on posts, `Product` on product pages). Detect: scan for `application/ld+json` blocks and check they parse and match the page. Fix: add JSON-LD from `assets/schema_templates.md`, validate the syntax. Severity: High. Applies: always.

**STRUCT-02 FAQ schema.** Pages that contain a genuine question and answer section expose `FAQPage` JSON-LD. Detect: find FAQ content and check for matching markup. Fix: add `FAQPage` markup that mirrors the visible questions and answers exactly. Do not add FAQ markup where there is no visible FAQ. Severity: Medium. Applies: pages with real FAQs.

**STRUCT-03 Entity SEO.** A consistent entity definition for the organization: an `Organization` (or `LocalBusiness`) node with `name`, `url`, `logo`, and `sameAs` links to authoritative profiles, plus consistent naming and contact details across the site. Detect: check for the entity node and `sameAs`, and look for inconsistent names or contact details across pages. Fix: define one canonical entity, add `sameAs`, make naming and contact details consistent. Requires the official name and profile URLs (ask if unknown). Severity: Medium. Applies: always.

**STRUCT-04 Knowledge graph readiness.** The entity markup and `sameAs` references are complete enough to support a knowledge panel: organization node, logo, founding or contact details where appropriate, and links to recognized profiles. Detect: review the entity node for completeness. Fix: complete the entity fields and `sameAs` set. Requires organization facts (ask if unknown). Severity: Low. Applies: always.

**STRUCT-05 Topic clusters.** Content is organized into pillar pages with supporting cluster pages that link up to the pillar and across to siblings. Detect: review the content map and internal links for pillar and cluster structure. Fix: define pillars, group related pages under them, and wire the internal links. Severity: Low. Applies: content and marketing sites.

**STRUCT-06 Local SEO.** For a local or physical business: `LocalBusiness` schema with name, address, phone, geo, and opening hours, consistent NAP (name, address, phone) across the site, and any location pages structured correctly. Detect: check for `LocalBusiness` markup and NAP consistency. Fix: add `LocalBusiness` markup, make NAP consistent. Requires the real NAP (ask if unknown). Severity: Medium. Applies: local or physical businesses only.

---

## 4. Generative and answer engine optimization (GEO)

**GEO-01 llms.txt present.** Covered by CRAWL-03; listed here because it is the primary GEO and AEO signal. Severity: Medium. Applies: always.

**GEO-02 Answer ready content.** Key pages answer real questions directly and early, in clear, self contained passages that a model or answer engine can quote. Detect: review whether important questions are answered concisely near the top of the relevant page. Fix: add or restructure concise, factual answers; use clear question style headings where natural. Severity: Medium. Applies: always.

**GEO-03 Semantic, citable structure.** Content uses semantic HTML (headings, lists, tables, `article`, `section`) so machines can parse and cite it, and important facts are in text rather than locked inside images. Detect: review markup semantics and whether key facts are real text. Fix: convert key facts to text, use semantic elements, label tables and figures. Severity: Medium. Applies: always.

**GEO-04 Brand and entity consistency for AI.** The organization is described consistently across the site and matches the entity markup in STRUCT-03, so answer engines attribute content correctly. Detect: compare on page descriptions of the organization against the entity node. Fix: align them. Severity: Low. Applies: always.

---

## 5. Performance, Core Web Vitals, and mobile (PERF)

**PERF-01 Core Web Vitals.** The site meets good thresholds for Largest Contentful Paint, Interaction to Next Paint, and Cumulative Layout Shift. Detect: run Lighthouse or read field data if available (see "Running Lighthouse"). Fix: address the specific causes the report names, for example a heavy hero image for LCP, long tasks for INP, or unsized media for CLS. Severity: High. Applies: always (best measured on a live or served build).

**PERF-02 Page speed.** Assets are optimized: images are compressed and right sized in modern formats, scripts and styles are minified and code split, render blocking resources are reduced, and caching and compression are configured. Detect: inspect asset sizes and formats, bundle output, and (for a live URL) response headers for compression and cache control. Fix: compress and convert images, lazy load below the fold media, split and defer scripts, enable text compression and sensible cache headers. Severity: High. Applies: always.

**PERF-03 Mobile optimization.** The layout is responsive, the viewport meta is correct, tap targets are large enough and spaced, text is legible without zooming, and nothing overflows on small screens. Detect: review responsive styles and the viewport tag; test narrow widths. Fix: correct responsive rules, size and space tap targets, fix overflow. Severity: High. Applies: always.

**PERF-04 Lighthouse score optimization.** The Inspect to Lighthouse to score optimization loop is run and the Performance, Accessibility, Best Practices, and SEO categories are improved against their findings. Detect: run Lighthouse (see below) and read the per category opportunities and diagnostics. Fix: work through the named items; re-run to confirm improvement. Severity: Medium. Applies: always (record as not run if the environment cannot run it).

---

## 6. Resilience and self contained delivery (RESIL)

**RESIL-01 Custom 404 page.** A branded, helpful 404 page with navigation back into the site, not a raw server error. Detect: check for a custom not found route or page; for a live URL request a missing path and inspect the response. Fix: add a custom 404 from `assets/not_found_template.html`, wire it to the framework's not found handling, return the correct 404 status. Severity: Medium. Applies: always.

**RESIL-02 Offline or no internet page.** A graceful page shown when the user has no connection, typically a service worker with an offline fallback. Detect: check for a service worker and an offline fallback page or route. Fix: add a service worker that serves `assets/offline_page_template.html` (or the project equivalent) when the network is unavailable; cache the shell. Severity: Low. Applies: always (especially progressive web apps).

**RESIL-03 No external image, video, or media links.** Images, video, fonts, and other media are served from the site's own origin, not hot linked from third party hosts or third party CDNs, and embeds are reviewed. Detect: the scanner flags absolute http or https references to media and known media or font CDNs and third party embeds; review each. Fix: self host the media and fonts, replace third party embeds with self hosted media or a privacy reviewed alternative, update references to relative or same origin URLs. Severity: High. Applies: always.

---

## 7. Content and style rules (STYLE)

**STYLE-01 No em dash.** No em dash character (U+2014) appears in site content or code. Detect: the scanner reports every U+2014 with file and line; en dash and double hyphen used as a dash are advisory. Fix: replace each em dash with the grammatically correct alternative (comma, colon, parentheses, reworded sentence, or spaced hyphen as a last resort). Severity: Medium. Applies: always.

**STYLE-02 No emojis, use icons.** Site content uses icons rather than emojis. Detect: the scanner reports emoji characters with file and line. Fix: replace each emoji with an equivalent icon from the project's existing icon system; do not delete meaning and do not add a dependency for a single glyph. Severity: Low. Applies: always.

---

## 8. Git and repository hygiene (GIT)

These come from the mandatory git policy (`git_policy.md`) and the engineering rules (`coding_rules.md`). They are reconciled on every fix run.

**GIT-01 .gitignore conformance.** A root `.gitignore` exists and contains every required category from `gitignore_standard.txt`. Detect: the scanner compares the repository `.gitignore` against the standard and reports missing categories. Fix: merge in missing lines, keep project additions, never remove required exclusions. Severity: High. Applies: always.

**GIT-02 No tracked secrets.** No secret bearing file is tracked by git. Detect: when git is present the scanner flags tracked files matching secret patterns (`.env`, `*.pem`, `*.key`, `*.crt`, `*.p12`, `*.pfx`, `secrets.json`, `credentials.json`, `service-account.json`), with `.env.example` allowed. Fix: stop tracking the file, ensure the pattern is ignored, and advise rotating the exposed secret. Severity: Blocking. Applies: always.

**GIT-03 README up to date.** `README.md` exists and reflects the current project. Detect: check presence and whether core sections are present and current. Fix: create or update with name, description, prerequisites, setup, run and build steps, environment variables (via `.env.example`), and any newly added top level files. Severity: Medium. Applies: always.

---

## 9. Optional enhancements (OPT)

Include these in the report as optional. Implement them only if the user approves.

**OPT-01 Open Graph.** `og:` tags (title, description, type, url, image) for rich link previews. Fix: add per page Open Graph tags; self host the OG image per RESIL-03. Applies: optional.

**OPT-02 Twitter cards.** `twitter:` card tags for rich previews on that platform. Fix: add `summary_large_image` card tags. Applies: optional.

**OPT-03 Brand mentions.** Encourage and track consistent brand mentions and citations off site. This is strategy, not code; note it as advisory. Applies: optional.

**OPT-04 Google Search Console.** Site verification and Search Console setup. Fix: add the verification token or DNS record the user provides; never invent one. Applies: optional.

**OPT-05 Google Analytics.** Analytics tag setup. Fix: add the measurement ID the user provides, with attention to consent and privacy; never invent an ID. Applies: optional.

**OPT-06 Conversion tracking.** Goal and conversion event tracking. Fix: implement the events the user defines on top of the analytics setup. Applies: optional.

---

## 10. Running Lighthouse

Lighthouse needs a running page (a live URL or a local served build) and a headless Chrome. Do not assume either is present; detect first.

1. Check for tooling: `npx --yes lighthouse --version` or a local `lighthouse` binary, and a Chrome or Chromium install.
2. Make sure there is something to test: a public URL, or start the project's preview or build server locally and use that URL.
3. Run, capturing all four categories, for example:
   ```bash
   npx --yes lighthouse <url> \
     --only-categories=performance,accessibility,best-practices,seo \
     --output=json --output=html \
     --output-path=<workdir>/lighthouse-report \
     --chrome-flags="--headless --no-sandbox"
   ```
4. Read the JSON for category scores and the named opportunities and diagnostics. Use those to drive PERF and SEO fixes, then re-run to confirm.

If the environment cannot run Lighthouse (no browser, no network, no server), record PERF-04 and the Core Web Vitals items as "not run", include the exact command above in `gap_identification.md` and `fix_summary.md`, and ask the user to run it. Never fabricate a score.

---

## 11. How SEO, GEO, and AEO relate

These three overlap and share most of the work, which is why the checklist treats them together rather than as separate tracks.

- SEO (search engine optimization) targets ranking in traditional search results: crawlability, metadata, structured data, internal links, and performance.
- AEO (answer engine optimization) targets direct answers and featured snippets: concise question and answer content, FAQ schema, and clean semantic structure.
- GEO (generative engine optimization) targets being surfaced and cited by AI systems: `llms.txt`, citable text based facts, consistent entity definition, and the same structured data and semantics.

A site that satisfies the SEO items here is most of the way to AEO and GEO; the GEO and AEO specific additions are `llms.txt`, answer ready content, and entity consistency.
