#!/usr/bin/env python3
"""
Static website standards scanner.

Runs the deterministic part of the website standards audit over a repository or
site source tree and writes structured findings as JSON, plus a readable summary
to stdout. It never modifies the project.

What it checks:
- Presence of robots.txt, sitemap, llms.txt, a custom 404 page, an offline page,
  and a service worker.
- Metadata and structured data signals across source and template files
  (title, meta description, viewport, charset, canonical, hreflang, JSON-LD,
  FAQPage, common schema types, Open Graph, Twitter cards, analytics, search
  console verification).
- Em dash (hard) and emoji (advisory) occurrences in text bearing files.
- External image, video, audio, font, and media references (RESIL-03).
- The repository .gitignore against the bundled organization standard.
- Tracked secret files, when the tree is a git repository.

Usage:
    python3 audit_site.py --path <repo-root> --out <findings.json>

The script is intentionally conservative: when a signal is missing it reports
"no signal found" and a "Needs review" status rather than asserting a hard
failure, because some frameworks inject head tags at build time. Treat the JSON
as input to a human reviewed gap report, not as the final verdict.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Directories that are never part of the audited source.
EXCLUDED_DIRS = {
    ".git", "node_modules", "dist", "build", ".next", "out", "coverage",
    "__pycache__", ".cache", "tmp", "temp", "venv", "env", ".venv",
    ".pytest_cache", ".mypy_cache", ".history", ".local", "playwright-report",
    "test-results", ".svelte-kit", ".nuxt", ".astro", ".vercel", ".netlify",
}

# Extensions whose text we scan for em dashes and emojis.
TEXT_EXTS = {
    ".html", ".htm", ".md", ".mdx", ".txt", ".js", ".jsx", ".ts", ".tsx",
    ".vue", ".svelte", ".astro", ".css", ".scss", ".sass", ".less", ".json",
    ".php", ".ejs", ".njk", ".hbs", ".liquid", ".yml", ".yaml", ".xml",
}

# Extensions that may carry head tags and structured data.
MARKUP_EXTS = {
    ".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".ejs",
    ".njk", ".hbs", ".liquid", ".php", ".md", ".mdx",
}

# Media file extensions used to spot external media references.
MEDIA_EXTS = (
    "png", "jpg", "jpeg", "gif", "webp", "avif", "svg", "ico", "bmp",
    "mp4", "webm", "mov", "ogg", "ogv", "mp3", "wav", "m4a", "aac", "flac",
    "woff", "woff2", "ttf", "otf", "eot",
)

# Hosts that commonly serve third party media, fonts, or embeds.
MEDIA_HOSTS = (
    "fonts.googleapis.com", "fonts.gstatic.com", "use.typekit.net",
    "youtube.com", "youtu.be", "youtube-nocookie.com", "ytimg.com",
    "player.vimeo.com", "vimeo.com", "i.imgur.com", "imgur.com",
    "gravatar.com", "images.unsplash.com", "res.cloudinary.com",
    "googleusercontent.com", "ggpht.com", "fbcdn.net", "twimg.com",
    "google.com/maps", "maps.googleapis.com",
)

EM_DASH = "\u2014"
EN_DASH = "\u2013"

EMOJI_RANGES = (
    (0x1F300, 0x1FAFF),
    (0x1F000, 0x1F02F),
    (0x2600, 0x27BF),
    (0x2B00, 0x2BFF),
    (0x1F1E6, 0x1F1FF),
)
VARIATION_SELECTOR = 0xFE0F

OCCURRENCE_CAP = 200
MAX_FILE_BYTES = 2_000_000


def is_emoji_char(ch):
    cp = ord(ch)
    if cp == VARIATION_SELECTOR:
        return True
    return any(lo <= cp <= hi for lo, hi in EMOJI_RANGES)


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for name in filenames:
            yield Path(dirpath) / name


def read_text(path):
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return None
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def rel(path, root):
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def find_root_file(root, names):
    """Return the first matching root level file path, or None."""
    for name in names:
        candidate = root / name
        if candidate.exists():
            return rel(candidate, root)
    return None


def detect_custom_404(root, all_files):
    patterns = ("404", "not-found", "notfound", "not_found")
    hits = []
    for p in all_files:
        stem = p.stem.lower()
        if stem in patterns and p.suffix.lower() in MARKUP_EXTS:
            hits.append(rel(p, root))
    return hits


def detect_offline(root, all_files):
    hits = []
    for p in all_files:
        stem = p.stem.lower()
        if stem in ("offline", "no-internet", "nointernet") and p.suffix.lower() in MARKUP_EXTS:
            hits.append(rel(p, root))
    return hits


def detect_service_worker(root, all_files):
    hits = []
    for p in all_files:
        name = p.name.lower()
        if name in ("sw.js", "service-worker.js", "serviceworker.js"):
            hits.append(rel(p, root))
    return hits


SIGNAL_PATTERNS = {
    "title": re.compile(r"<title|next/head|react-helmet|svelte:head|@unhead|useHead|Helmet", re.I),
    "meta_description": re.compile(r"name=['\"]description['\"]|property=['\"]description['\"]", re.I),
    "viewport": re.compile(r"name=['\"]viewport['\"]", re.I),
    "charset": re.compile(r"charset", re.I),
    "canonical": re.compile(r"rel=['\"]canonical['\"]", re.I),
    "hreflang": re.compile(r"hreflang", re.I),
    "json_ld": re.compile(r"application/ld\+json", re.I),
    "schema_organization": re.compile(r"['\"]Organization['\"]"),
    "schema_website": re.compile(r"['\"]WebSite['\"]"),
    "schema_breadcrumb": re.compile(r"['\"]BreadcrumbList['\"]"),
    "schema_localbusiness": re.compile(r"['\"]LocalBusiness['\"]"),
    "schema_faqpage": re.compile(r"['\"]FAQPage['\"]"),
    "open_graph": re.compile(r"property=['\"]og:", re.I),
    "twitter_cards": re.compile(r"name=['\"]twitter:", re.I),
    "robots_meta": re.compile(r"name=['\"]robots['\"]", re.I),
    "analytics": re.compile(r"gtag\(|googletagmanager\.com|google-analytics\.com", re.I),
    "search_console": re.compile(r"google-site-verification", re.I),
    "lang_attr": re.compile(r"<html[^>]*\blang=", re.I),
}

URL_IN_ATTR = re.compile(r"""(?:src|href|content)\s*=\s*['"]([^'"]+)['"]""", re.I)
URL_IN_CSS = re.compile(r"""url\(\s*['"]?([^'")]+)['"]?\s*\)""", re.I)
SRCSET = re.compile(r"""srcset\s*=\s*['"]([^'"]+)['"]""", re.I)


def url_is_external_media(url):
    u = url.strip()
    low = u.lower()
    if not (low.startswith("http://") or low.startswith("https://") or low.startswith("//")):
        return False
    host_part = low.split("//", 1)[-1]
    if any(h in host_part for h in MEDIA_HOSTS):
        return True
    base = low.split("?", 1)[0].split("#", 1)[0]
    return any(base.endswith("." + ext) for ext in MEDIA_EXTS)


def scan_files(root):
    all_files = list(iter_files(root))
    signals = {k: {"present": False, "files": []} for k in SIGNAL_PATTERNS}
    em_dash_hits = []
    emoji_hits = []
    external_media_hits = []
    en_dash_count = 0
    em_dash_total = 0
    emoji_total = 0
    text_scanned = 0

    for path in all_files:
        ext = path.suffix.lower()
        if ext not in TEXT_EXTS:
            continue
        content = read_text(path)
        if content is None:
            continue
        text_scanned += 1
        relpath = rel(path, root)

        if ext in MARKUP_EXTS:
            for key, pat in SIGNAL_PATTERNS.items():
                if pat.search(content):
                    signals[key]["present"] = True
                    if len(signals[key]["files"]) < 50:
                        signals[key]["files"].append(relpath)

        # External media references (markup, css, js).
        if ext in MARKUP_EXTS or ext in {".css", ".scss", ".sass", ".less", ".js", ".jsx", ".ts", ".tsx"}:
            for lineno, line in enumerate(content.splitlines(), 1):
                for rx in (URL_IN_ATTR, URL_IN_CSS):
                    for m in rx.finditer(line):
                        if url_is_external_media(m.group(1)):
                            if len(external_media_hits) < OCCURRENCE_CAP:
                                external_media_hits.append({
                                    "file": relpath, "line": lineno,
                                    "url": m.group(1).strip()[:200],
                                })
                for m in SRCSET.finditer(line):
                    for candidate in m.group(1).split(","):
                        u = candidate.strip().split(" ")[0]
                        if url_is_external_media(u):
                            if len(external_media_hits) < OCCURRENCE_CAP:
                                external_media_hits.append({
                                    "file": relpath, "line": lineno, "url": u[:200],
                                })

        # Em dash, en dash, emoji.
        for lineno, line in enumerate(content.splitlines(), 1):
            if EM_DASH in line:
                em_dash_total += line.count(EM_DASH)
                if len(em_dash_hits) < OCCURRENCE_CAP:
                    em_dash_hits.append({
                        "file": relpath, "line": lineno, "snippet": line.strip()[:160],
                    })
            if EN_DASH in line:
                en_dash_count += line.count(EN_DASH)
            for ch in line:
                if is_emoji_char(ch):
                    emoji_total += 1
                    if len(emoji_hits) < OCCURRENCE_CAP:
                        emoji_hits.append({
                            "file": relpath, "line": lineno, "char": ch,
                            "codepoint": "U+%04X" % ord(ch),
                            "snippet": line.strip()[:160],
                        })

    return {
        "all_files": all_files,
        "text_scanned": text_scanned,
        "signals": signals,
        "em_dash": {"total": em_dash_total, "shown": em_dash_hits,
                    "truncated": em_dash_total > len(em_dash_hits)},
        "en_dash_count": en_dash_count,
        "emoji": {"total": emoji_total, "shown": emoji_hits,
                  "truncated": emoji_total > len(emoji_hits)},
        "external_media": {"shown": external_media_hits,
                           "truncated": len(external_media_hits) >= OCCURRENCE_CAP},
    }


def load_standard_patterns():
    standard = Path(__file__).resolve().parent.parent / "references" / "gitignore_standard.txt"
    if not standard.exists():
        return None, []
    patterns = []
    for line in standard.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        patterns.append(s)
    return standard, patterns


def check_gitignore(root):
    standard_path, standard_patterns = load_standard_patterns()
    repo_gitignore = root / ".gitignore"
    if not repo_gitignore.exists():
        return {"exists": False, "missing": standard_patterns,
                "standard_found": standard_path is not None}
    present = set()
    for line in repo_gitignore.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            present.add(s)
    missing = [p for p in standard_patterns if p not in present]
    return {"exists": True, "missing": missing,
            "standard_found": standard_path is not None}


def check_tracked_secrets(root):
    if not (root / ".git").exists():
        return {"is_git_repo": False, "tracked_secrets": []}
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files"],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return {"is_git_repo": True, "tracked_secrets": [], "error": "git ls-files failed"}
    if out.returncode != 0:
        return {"is_git_repo": True, "tracked_secrets": [], "error": out.stderr.strip()[:200]}

    secret_exts = (".pem", ".key", ".crt", ".p12", ".pfx")
    secret_names = {"secrets.json", "credentials.json", "service-account.json"}
    hits = []
    for line in out.stdout.splitlines():
        f = line.strip()
        if not f:
            continue
        base = os.path.basename(f).lower()
        is_secret = (
            base == ".env"
            or (base.startswith(".env.") and base != ".env.example")
            or base.endswith(secret_exts)
            or base in secret_names
        )
        if is_secret:
            hits.append(f)
    return {"is_git_repo": True, "tracked_secrets": hits}


def build_findings(scan, gi, secrets, root):
    findings = []

    def add(fid, category, criterion, status, severity, evidence, recommendation, info_required=""):
        findings.append({
            "id": fid, "category": category, "criterion": criterion,
            "status": status, "severity": severity, "evidence": evidence,
            "recommendation": recommendation, "info_required": info_required,
        })

    # Crawl and discovery.
    robots = find_root_file(root, ["robots.txt", "public/robots.txt", "static/robots.txt"])
    add("CRAWL-01", "Crawl and discovery", "robots.txt",
        "Pass" if robots else "Gap", "High",
        f"found at {robots}" if robots else "no robots.txt at root or in public/static",
        "Keep as is; confirm it references the sitemap." if robots else
        "Create robots.txt from assets/robots_txt_template.txt and add the sitemap URL.")

    sitemap = find_root_file(root, ["sitemap.xml", "sitemap_index.xml",
                                    "public/sitemap.xml", "static/sitemap.xml"])
    add("CRAWL-02", "Crawl and discovery", "sitemap.xml",
        "Pass" if sitemap else "Gap", "High",
        f"found at {sitemap}" if sitemap else "no sitemap found at root or in public/static",
        "Confirm it lists canonical URLs and is referenced in robots.txt." if sitemap else
        "Generate sitemap.xml of canonical URLs and reference it in robots.txt.")

    llms = find_root_file(root, ["llms.txt", "llms-full.txt", "llm.txt",
                                 "public/llms.txt", "static/llms.txt"])
    add("CRAWL-03", "Crawl and discovery", "llms.txt",
        "Pass" if llms else "Gap", "Medium",
        f"found at {llms}" if llms else "no llms.txt found",
        "Confirm it summarizes the site and links key pages." if llms else
        "Create llms.txt from assets/llms_txt_template.md.",
        "" if llms else "Site name, one line description, and the key pages to link.")

    # Resilience.
    p404 = detect_custom_404(root, scan["all_files"])
    add("RESIL-01", "Resilience", "Custom 404 page",
        "Pass" if p404 else "Needs review", "Medium",
        "found: " + ", ".join(p404) if p404 else "no file named 404 or not-found detected (a framework route may still exist)",
        "Confirm it is wired up and returns a 404 status." if p404 else
        "Add a custom 404 from assets/not_found_template.html and wire it to the framework's not found handling.")

    offline = detect_offline(root, scan["all_files"])
    sw = detect_service_worker(root, scan["all_files"])
    if offline or sw:
        ev = "; ".join(filter(None, [
            "offline page: " + ", ".join(offline) if offline else "",
            "service worker: " + ", ".join(sw) if sw else "",
        ]))
        add("RESIL-02", "Resilience", "Offline / no internet page",
            "Needs review", "Low", ev,
            "Confirm the service worker serves the offline page when the network is unavailable.")
    else:
        add("RESIL-02", "Resilience", "Offline / no internet page",
            "Gap", "Low", "no service worker or offline page detected",
            "Add a service worker with an offline fallback from assets/offline_page_template.html.")

    em = scan["external_media"]["shown"]
    if em:
        sample = "; ".join(f"{h['file']}:{h['line']} {h['url']}" for h in em[:5])
        suffix = " (more, see JSON)" if scan["external_media"]["truncated"] or len(em) > 5 else ""
        add("RESIL-03", "Resilience", "No external image/video/media links",
            "Gap", "High", f"{len(em)} external media reference(s); e.g. {sample}{suffix}",
            "Self host the media and fonts; replace third party embeds; use relative or same origin URLs.")
    else:
        add("RESIL-03", "Resilience", "No external image/video/media links",
            "Pass", "High", "no external media references detected in scanned files",
            "No action; keep media self hosted.")

    # On page SEO via signals.
    sig = scan["signals"]

    def signal_finding(fid, name, key, severity, present_rec, missing_rec, info=""):
        s = sig.get(key, {"present": False, "files": []})
        if s["present"]:
            ev = "signal found in: " + ", ".join(s["files"][:5]) + (" ..." if len(s["files"]) > 5 else "")
            add(fid, "On page SEO", name, "Needs review", severity, ev, present_rec, info)
        else:
            add(fid, "On page SEO", name, "Needs review", severity,
                "no signal found in scanned source (a build step may inject this)",
                missing_rec, info)

    signal_finding("SEO-01", "Title tags", "title", "High",
                   "Confirm each page has a unique, well sized title.",
                   "Add unique titles per page (or confirm the framework sets them).")
    signal_finding("SEO-02", "Meta descriptions", "meta_description", "Medium",
                   "Confirm each description is unique and well sized.",
                   "Add unique meta descriptions per page.")
    # Essential meta combines viewport and charset.
    vp = sig["viewport"]["present"]
    cs = sig["charset"]["present"]
    if vp and cs:
        add("SEO-03", "On page SEO", "Essential meta tags (charset, viewport)",
            "Needs review", "High", "viewport and charset signals found",
            "Confirm both are on every page.")
    else:
        missing = ", ".join(filter(None, ["viewport" if not vp else "", "charset" if not cs else ""]))
        add("SEO-03", "On page SEO", "Essential meta tags (charset, viewport)",
            "Gap", "High", f"missing signal for: {missing}",
            "Add charset and viewport meta to every page.")
    signal_finding("SEO-04", "Canonical tags", "canonical", "High",
                   "Confirm self referencing canonicals using the canonical host.",
                   "Add self referencing canonical links.",
                   "The canonical domain.")
    if sig["hreflang"]["present"]:
        add("SEO-05", "On page SEO", "hreflang",
            "Needs review", "High", "hreflang signal found",
            "Confirm the set is reciprocal and includes x-default.")
    else:
        add("SEO-05", "On page SEO", "hreflang",
            "Needs review", "High", "no hreflang signal found",
            "If the site targets multiple locales, add a reciprocal hreflang set with x-default; otherwise mark Not applicable.",
            "Whether the site targets multiple languages or regions, and the locale list.")

    # Structured data.
    if sig["json_ld"]["present"]:
        types = [t for t, k in [("Organization", "schema_organization"),
                                ("WebSite", "schema_website"),
                                ("BreadcrumbList", "schema_breadcrumb"),
                                ("LocalBusiness", "schema_localbusiness")] if sig[k]["present"]]
        add("STRUCT-01", "Structured data", "Schema markup (JSON-LD)",
            "Needs review", "High",
            "JSON-LD found; types seen: " + (", ".join(types) if types else "none of the common types matched"),
            "Validate the JSON-LD and confirm it matches each page type.")
    else:
        add("STRUCT-01", "Structured data", "Schema markup (JSON-LD)",
            "Gap", "High", "no application/ld+json found in scanned source",
            "Add JSON-LD from assets/schema_templates.md (Organization and WebSite site wide, plus per page types).",
            "Organization name, URL, logo, and social profile URLs.")
    if sig["schema_faqpage"]["present"]:
        add("STRUCT-02", "Structured data", "FAQ schema",
            "Needs review", "Medium", "FAQPage signal found",
            "Confirm it mirrors visible FAQ content exactly.")
    else:
        add("STRUCT-02", "Structured data", "FAQ schema",
            "Needs review", "Medium", "no FAQPage signal found",
            "Add FAQPage markup on pages that have a real FAQ; otherwise Not applicable.")
    add("STRUCT-03", "Structured data", "Entity SEO (Organization, sameAs)",
        "Needs review", "Medium",
        "Organization signal found" if sig["schema_organization"]["present"] else "no Organization signal found",
        "Confirm a single canonical entity with sameAs and consistent naming and contact details.",
        "Official organization name and authoritative profile URLs.")

    # GEO/AEO.
    add("GEO-02", "GEO and AEO", "Answer ready, semantic content",
        "Needs review", "Medium", "requires content review",
        "Confirm key questions are answered concisely and facts are in text, with semantic HTML.")

    # Performance / Lighthouse (cannot be measured statically).
    add("PERF-04", "Performance", "Lighthouse score optimization",
        "Needs review", "Medium", "not measured by static scan",
        "Run Lighthouse per references/website_criteria.md section 10; record scores and work the opportunities.")
    add("PERF-02", "Performance", "Page speed and asset optimization",
        "Needs review", "High", "requires asset and header review",
        "Review image formats and sizes, bundle output, lazy loading, compression, and cache headers.")
    add("PERF-03", "Performance", "Mobile optimization",
        "Needs review", "High",
        "viewport signal found" if sig["viewport"]["present"] else "no viewport signal found",
        "Confirm responsive layout, tap target sizing, and no overflow at narrow widths.")

    # Style rules.
    em_total = scan["em_dash"]["total"]
    if em_total:
        sample = "; ".join(f"{h['file']}:{h['line']}" for h in scan["em_dash"]["shown"][:5])
        add("STYLE-01", "Content and style", "No em dash",
            "Gap", "Medium",
            f"{em_total} em dash occurrence(s); e.g. {sample}" + (" (more, see JSON)" if scan["em_dash"]["truncated"] else ""),
            "Replace each em dash with a comma, colon, parentheses, or reworded text.")
    else:
        note = ""
        if scan["en_dash_count"]:
            note = f" Advisory: {scan['en_dash_count']} en dash occurrence(s) to review."
        add("STYLE-01", "Content and style", "No em dash",
            "Pass", "Medium", "no em dash found." + note, "No action.")

    emoji_total = scan["emoji"]["total"]
    if emoji_total:
        sample = "; ".join(f"{h['file']}:{h['line']} {h['codepoint']}" for h in scan["emoji"]["shown"][:5])
        add("STYLE-02", "Content and style", "No emojis (use icons)",
            "Gap", "Low",
            f"{emoji_total} emoji occurrence(s); e.g. {sample}" + (" (more, see JSON)" if scan["emoji"]["truncated"] else ""),
            "Replace each emoji with an equivalent icon from the project's icon system.")
    else:
        add("STYLE-02", "Content and style", "No emojis (use icons)",
            "Pass", "Low", "no emoji characters found", "No action.")

    # Git hygiene.
    if not gi["exists"]:
        add("GIT-01", "Git hygiene", ".gitignore conformance",
            "Gap", "High", "no .gitignore at repository root",
            "Create .gitignore from references/gitignore_standard.txt plus stack specific entries.")
    elif gi["missing"]:
        shown = ", ".join(gi["missing"][:12]) + (" ..." if len(gi["missing"]) > 12 else "")
        add("GIT-01", "Git hygiene", ".gitignore conformance",
            "Gap", "High", f"{len(gi['missing'])} required pattern(s) missing: {shown}",
            "Merge the missing standard patterns in; keep project additions; remove none of the required exclusions.")
    else:
        add("GIT-01", "Git hygiene", ".gitignore conformance",
            "Pass", "High", "all standard patterns present", "No action.")

    if secrets.get("is_git_repo"):
        if secrets["tracked_secrets"]:
            shown = ", ".join(secrets["tracked_secrets"][:10])
            add("GIT-02", "Git hygiene", "No tracked secrets",
                "Gap", "Blocking", f"tracked secret file(s): {shown}",
                "Stop tracking with git rm --cached, ensure the pattern is ignored, and rotate the exposed secret.")
        else:
            add("GIT-02", "Git hygiene", "No tracked secrets",
                "Pass", "Blocking", "no tracked secret files detected", "No action.")
    else:
        add("GIT-02", "Git hygiene", "No tracked secrets",
            "Needs review", "Blocking", "not a git repository (or git unavailable); could not check tracked files",
            "Re-check inside the git repository before relying on this result.")

    readme = find_root_file(root, ["README.md", "readme.md", "Readme.md", "README.MD"])
    add("GIT-03", "Git hygiene", "README up to date",
        "Needs review" if readme else "Gap", "Medium",
        f"found at {readme}" if readme else "no README.md at root",
        "Confirm it reflects the current project and newly added files." if readme else
        "Create README.md with name, description, setup, run and build steps, and env via .env.example.")

    # Optional.
    add("OPT-01", "Optional", "Open Graph",
        "Pass" if sig["open_graph"]["present"] else "Gap (optional)", "Low",
        "og: tags found" if sig["open_graph"]["present"] else "no og: tags found",
        "Optional: add per page Open Graph tags with a self hosted image.")
    add("OPT-02", "Optional", "Twitter cards",
        "Pass" if sig["twitter_cards"]["present"] else "Gap (optional)", "Low",
        "twitter: tags found" if sig["twitter_cards"]["present"] else "no twitter: tags found",
        "Optional: add summary_large_image card tags.")
    add("OPT-04", "Optional", "Google Search Console",
        "Pass" if sig["search_console"]["present"] else "Gap (optional)", "Low",
        "verification signal found" if sig["search_console"]["present"] else "no verification signal found",
        "Optional: add the verification token or DNS record the user provides.",
        "" if sig["search_console"]["present"] else "Verification token or DNS record (only if the user wants this).")
    add("OPT-05", "Optional", "Google Analytics",
        "Pass" if sig["analytics"]["present"] else "Gap (optional)", "Low",
        "analytics signal found" if sig["analytics"]["present"] else "no analytics signal found",
        "Optional: add the measurement ID the user provides, with consent handling.",
        "" if sig["analytics"]["present"] else "Measurement ID (only if the user wants this).")

    return findings


def summarize(findings):
    counts = {}
    by_category = {}
    for f in findings:
        status = f["status"].split(" ")[0]  # collapse "Gap (optional)" into "Gap"
        counts[status] = counts.get(status, 0) + 1
        cat = f["category"]
        by_category.setdefault(cat, {})
        by_category[cat][status] = by_category[cat].get(status, 0) + 1
    return {"by_status": counts, "by_category": by_category, "total": len(findings)}


def print_summary(report):
    print("Website standards scan")
    print("Path:", report["context"]["path"])
    print("Files scanned (text):", report["context"]["text_files_scanned"])
    print("Git repository:", report["context"]["is_git_repo"])
    print()
    print("Status counts:")
    for status, n in sorted(report["summary"]["by_status"].items()):
        print(f"  {status}: {n}")
    print()
    print("Findings needing attention (Gap or Blocking):")
    flagged = [f for f in report["findings"]
               if f["status"].startswith("Gap") or f["severity"] == "Blocking" and f["status"] != "Pass"]
    if not flagged:
        print("  none from the static scan; judgment checks still required.")
    for f in flagged:
        print(f"  [{f['severity']}] {f['id']} {f['criterion']}: {f['evidence']}")
    print()
    print("Note: Needs review items require human judgment and were not auto decided.")
    print("Findings JSON written to:", report["context"]["out"])


def main():
    ap = argparse.ArgumentParser(description="Static website standards scanner.")
    ap.add_argument("--path", default=".", help="Path to the repository or site source root.")
    ap.add_argument("--out", default="audit_findings.json", help="Where to write the findings JSON.")
    args = ap.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Error: path not found: {root}", file=sys.stderr)
        sys.exit(1)

    scan = scan_files(root)
    gi = check_gitignore(root)
    secrets = check_tracked_secrets(root)
    findings = build_findings(scan, gi, secrets, root)

    report = {
        "context": {
            "path": str(root),
            "text_files_scanned": scan["text_scanned"],
            "is_git_repo": secrets.get("is_git_repo", False),
            "gitignore_standard_found": gi.get("standard_found", False),
            "out": str(Path(args.out).resolve()),
        },
        "summary": summarize(findings),
        "findings": findings,
        "raw": {
            "signals": {k: v["present"] for k, v in scan["signals"].items()},
            "em_dash": scan["em_dash"],
            "en_dash_count": scan["en_dash_count"],
            "emoji": scan["emoji"],
            "external_media": scan["external_media"],
            "gitignore": gi,
            "tracked_secrets": secrets,
        },
    }

    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print_summary(report)


if __name__ == "__main__":
    main()
