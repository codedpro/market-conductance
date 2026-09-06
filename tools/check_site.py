"""Validate the published site's structured data and SEO surface."""
import json, re, pathlib, sys

h = pathlib.Path("site/index.html").read_text()
fail = []

blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
if not blocks:
    fail.append("no JSON-LD block")
for b in blocks:
    try:
        d = json.loads(b)
    except json.JSONDecodeError as e:
        fail.append(f"JSON-LD does not parse: {e}"); continue
    types = {g.get("@type") for g in d.get("@graph", [])}
    for need in ("ScholarlyArticle", "Dataset", "FAQPage", "SoftwareSourceCode"):
        if need not in types:
            fail.append(f"missing schema type: {need}")
    for g in d.get("@graph", []):
        if g.get("@type") == "FAQPage":
            for q in g["mainEntity"]:
                if q.get("@type") != "Question" or q["acceptedAnswer"].get("@type") != "Answer":
                    fail.append("malformed FAQ entry")

m = re.search(r'name="description" content="([^"]*)"', h)
if not m:
    fail.append("no meta description")
elif not 110 <= len(m.group(1)) <= 165:
    fail.append(f"meta description {len(m.group(1))} chars (want 110-165)")

for tag in ('rel="canonical"', 'og:title', 'og:image', 'twitter:card', 'lang="en"'):
    if tag not in h:
        fail.append(f"missing {tag}")
if h.count("<h1") != 1:
    fail.append(f"h1 count is {h.count('<h1')}, must be 1")

for f in ("site/robots.txt", "site/sitemap.xml", "site/llms.txt", "site/og.png", "site/.nojekyll"):
    if not pathlib.Path(f).exists():
        fail.append(f"missing {f}")

if "USERNAME" in h:
    print("note: USERNAME placeholder still present - run `make site-url USER=... REPO=...`")

print("FAIL:" if fail else "site checks passed")
for f in fail:
    print("  -", f)
sys.exit(1 if fail else 0)
