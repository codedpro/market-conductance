"""Validate the published site: structured data, SEO surface, and link policy."""
import json, re, pathlib, sys

SITE = pathlib.Path("site")
BASE = "https://codedpro.github.io/market-conductance"
PAGES = ["index.html", "results/index.html", "methods/index.html",
         "data/index.html", "faq/index.html"]
CONTRIB = ["https://itmaster.uk", "https://code-nest.dev"]
fail, notes = [], []

for rel in PAGES:
    f = SITE / rel
    if not f.exists():
        fail.append(f"missing page {rel}"); continue
    h = f.read_text()
    tag = f"[{rel}]"

    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try:
            d = json.loads(m)
        except json.JSONDecodeError as e:
            fail.append(f"{tag} JSON-LD parse error: {e}"); continue
        types = {g.get("@type") for g in d.get("@graph", [])}
        for need in ("WebSite", "Organization", "BreadcrumbList", "WebPage"):
            if need not in types:
                fail.append(f"{tag} missing schema {need}")

    m = re.search(r'name="description" content="([^"]*)"', h)
    if not m:
        fail.append(f"{tag} no meta description")
    elif not 110 <= len(m.group(1)) <= 175:
        fail.append(f"{tag} meta description {len(m.group(1))} chars (want 110-175)")

    t = re.search(r"<title>([^<]*)</title>", h)
    if not t:
        fail.append(f"{tag} no title")
    elif len(t.group(1)) > 65:
        notes.append(f"{tag} title {len(t.group(1))} chars (Google truncates ~60-65)")

    if h.count("<h1") != 1:
        fail.append(f"{tag} h1 count is {h.count('<h1')}, must be 1")
    for need in ('rel="canonical"', "og:title", "og:image", "twitter:card", 'lang="en"',
                 'name="citation_title"', 'name="DC.title"'):
        if need not in h:
            fail.append(f"{tag} missing {need}")
    if "USERNAME" in h or "project-lambda" in h:
        fail.append(f"{tag} stale placeholder URL")

    # link policy: contributor links must be dofollow
    for url in CONTRIB:
        for a in re.findall(r'<a\s[^>]*href="' + re.escape(url) + r'"[^>]*>', h):
            if re.search(r'rel="[^"]*\b(nofollow|sponsored|ugc)\b', a):
                fail.append(f"{tag} contributor link is NOT dofollow: {a}")

# contributor links present somewhere
allhtml = "".join((SITE / p).read_text() for p in PAGES if (SITE / p).exists())
for url in CONTRIB:
    n = allhtml.count(f'href="{url}"')
    if n == 0:
        fail.append(f"contributor link missing entirely: {url}")
    else:
        notes.append(f"contributor {url}: {n} dofollow links")

for f_ in ("robots.txt", "sitemap.xml", "llms.txt", "llms-full.txt", "og.png",
           ".nojekyll", "assets/style.css"):
    if not (SITE / f_).exists():
        fail.append(f"missing {f_}")

sm = (SITE / "sitemap.xml").read_text() if (SITE / "sitemap.xml").exists() else ""
for rel in PAGES:
    loc = f"{BASE}/" if rel == "index.html" else f"{BASE}/{rel.replace('index.html', '')}"
    if loc not in sm:
        fail.append(f"sitemap missing {loc}")

print("FAIL:" if fail else "site checks passed")
for x in fail:
    print("  -", x)
for n in notes:
    print("  note:", n)
sys.exit(1 if fail else 0)
