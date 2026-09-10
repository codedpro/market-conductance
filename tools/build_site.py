#!/usr/bin/env python3
"""
Static site generator for the study.

Five pages instead of one, because a single page cannot rank for the range of
queries this research answers. Every page carries its own canonical, Highwire
Press citation tags (Google Scholar), Dublin Core terms, Open Graph, breadcrumb
schema and page-specific structured data, all emitted from one place so they
cannot drift apart.

Run: python tools/build_site.py   (or: make site)
"""
import json, pathlib, shutil, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
BASE = "https://codedpro.github.io/market-conductance"
REPO = "https://github.com/codedpro/market-conductance"
PUBLISHED = "2026-09-06"
MODIFIED = datetime.date.today().isoformat()
TITLE = ("Is market conductance a forecastable state variable? A free-data "
         "falsification study of the impact operator in gold and nine other markets")
AUTHOR = "codedpro"
CONTRIBUTORS = [
    ("ITMaster", "https://itmaster.uk"),
    ("Code Nest", "https://code-nest.dev"),
]

# ---------------------------------------------------------------- shared head
def head(page):
    """Every discovery surface, emitted once: search, Scholar, social, AI."""
    url = f"{BASE}/{page['slug']}" if page["slug"] else f"{BASE}/"
    crumbs = [{"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"}]
    if page["slug"]:
        crumbs.append({"@type": "ListItem", "position": 2, "name": page["crumb"], "item": url})

    graph = [
        {"@type": "WebSite", "@id": f"{BASE}/#website", "url": f"{BASE}/",
         "name": "Market Conductance Study",
         "description": "Empirical falsification study of the market price-impact operator.",
         "inLanguage": "en",
         "publisher": {"@id": f"{BASE}/#org"}},
        {"@type": "Organization", "@id": f"{BASE}/#org", "name": "Project Lambda",
         "url": f"{BASE}/", "sameAs": [REPO],
         "member": [{"@type": "Organization", "name": n, "url": u} for n, u in CONTRIBUTORS]},
        {"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb", "itemListElement": crumbs},
        {"@type": "WebPage", "@id": f"{url}#webpage", "url": url,
         "name": page["title"], "description": page["desc"],
         "isPartOf": {"@id": f"{BASE}/#website"},
         "breadcrumb": {"@id": f"{url}#breadcrumb"},
         "datePublished": PUBLISHED, "dateModified": MODIFIED,
         "inLanguage": "en"},
    ] + page.get("schema", [])

    cite = "\n".join([
        f'<meta name="citation_title" content="{TITLE}">',
        f'<meta name="citation_author" content="{AUTHOR}">',
    ] + [
        f'<meta name="citation_author" content="{n}">' for n, _ in CONTRIBUTORS
    ] + [
        f'<meta name="citation_publication_date" content="{PUBLISHED.replace("-", "/")}">',
        f'<meta name="citation_online_date" content="{PUBLISHED.replace("-", "/")}">',
        f'<meta name="citation_abstract_html_url" content="{BASE}/">',
        f'<meta name="citation_public_url" content="{BASE}/">',
        f'<meta name="citation_fulltext_world_readable" content="">',
        f'<meta name="citation_language" content="en">',
        '<meta name="citation_keywords" content="market microstructure; price impact; '
        'Kyle lambda; Amihud illiquidity; market conductance; gold; Commitments of Traders; '
        'inelastic markets; event study; falsification">',
    ])
    dc = "\n".join([
        f'<meta name="DC.title" content="{TITLE}">',
        f'<meta name="DC.creator" content="{AUTHOR}">',
        f'<meta name="DC.date" content="{PUBLISHED}">',
        '<meta name="DC.type" content="Text">',
        '<meta name="DC.format" content="text/html">',
        '<meta name="DC.language" content="en">',
        '<meta name="DC.rights" content="MIT">',
        f'<meta name="DC.identifier" content="{BASE}/">',
    ])
    depth = "../" * len(page["slug"].strip("/").split("/")) if page["slug"] else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{page['title']}</title>
<meta name="description" content="{page['desc']}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1">
<meta name="author" content="{AUTHOR}">
<meta name="theme-color" content="#f7f8f9">

{cite}

{dc}

<meta property="og:type" content="article">
<meta property="og:site_name" content="Market Conductance Study">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{page['og']}">
<meta property="og:description" content="{page['desc']}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Market conductance study: forecastable in ten of ten asset classes; the holder-base explanation rejected at 5.4 sigma.">
<meta property="article:published_time" content="{PUBLISHED}">
<meta property="article:modified_time" content="{MODIFIED}">
<meta property="article:author" content="{AUTHOR}">
<meta property="article:section" content="Quantitative finance">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{page['og']}">
<meta name="twitter:description" content="{page['desc']}">
<meta name="twitter:image" content="{BASE}/og.png">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="{depth}assets/style.css">
<link rel="alternate" type="text/plain" href="{BASE}/llms.txt" title="llms.txt">

<script type="application/ld+json">
{json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=1)}
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="wrap">
"""


NAV = """<nav class="topnav" aria-label="Sections">
<a href="{d}">Study</a><a href="{d}results/">Results</a><a href="{d}methods/">Methods</a><a href="{d}data/">Data</a><a href="{d}faq/">FAQ</a>
<a class="gh" href="{repo}">Code &#8599;</a>
</nav>
"""


def foot(page):
    d = "../" * len(page["slug"].strip("/").split("/")) if page["slug"] else ""
    # plain anchors: no rel attribute at all, so these are unambiguously dofollow
    contrib = " and ".join(f'<a href="{u}">{n}</a>' for n, u in CONTRIBUTORS)
    return f"""
</main>
<footer>
<p><strong>Contributing team.</strong> Research engineering and infrastructure by
{contrib}.</p>
<p><strong>Cite this work.</strong> {AUTHOR} ({PUBLISHED[:4]}). <em>{TITLE}.</em>
<a href="{BASE}/">{BASE}/</a></p>
<p><a href="{d}">Study</a> &middot; <a href="{d}results/">Full results</a> &middot;
<a href="{d}methods/">Methods</a> &middot; <a href="{d}data/">Data sources</a> &middot;
<a href="{d}faq/">FAQ</a> &middot; <a href="{REPO}">Code and data on GitHub</a></p>
<p>MIT licensed. Published {PUBLISHED}, last updated {MODIFIED}.
<strong>Not investment advice</strong> &mdash; this is empirical research and contains no
recommendation to trade any instrument.</p>
</footer>
</div>
</body>
</html>
"""


def build(pages):
    for p in pages:
        out = SITE / p["slug"] / "index.html" if p["slug"] else SITE / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        d = "../" * len(p["slug"].strip("/").split("/")) if p["slug"] else ""
        html = head(p) + NAV.format(d=d, repo=REPO) + '<main id="main">' + p["body"] + foot(p)
        out.write_text(html)
        print(f"  {out.relative_to(ROOT)}  ({len(html):,} bytes)")

    # sitemap
    urls = []
    for p in pages:
        loc = f"{BASE}/{p['slug']}" if p["slug"] else f"{BASE}/"
        urls.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{MODIFIED}</lastmod>\n"
                    f"    <changefreq>monthly</changefreq>\n    <priority>{p['prio']}</priority>\n  </url>")
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n</urlset>\n")
    print(f"  site/sitemap.xml ({len(pages)} urls)")


# ------------------------------------------------------------------- content
import sys as _s2
_s2.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from site_content import cross_asset_table, FAQ  # noqa: E402

CONTRIB_LINE = ('<p class="lede">Research engineering and infrastructure by '
                '<a href="https://itmaster.uk">ITMaster</a> and '
                '<a href="https://code-nest.dev">Code Nest</a>.</p>')

FAQ_SCHEMA = [{
    "@type": "FAQPage", "@id": f"{BASE}/faq/#faq",
    "mainEntity": [{"@type": "Question", "name": q,
                    "acceptedAnswer": {"@type": "Answer",
                                       "text": a.replace("<p>", "").replace("</p>", " ")
                                                .replace("<code>", "").replace("</code>", "")
                                                .replace("<strong>", "").replace("</strong>", "")
                                                .replace("&mdash;", "—").replace("&times;", "×")
                                                .strip()}}
                   for q, a in FAQ]}]

ARTICLE_SCHEMA = [{
    "@type": "ScholarlyArticle", "@id": f"{BASE}/#article",
    "headline": TITLE, "name": TITLE,
    "abstract": ("Tests whether the market impact operator G in dP = G x epsilon is a "
                 "forecastable state variable and whether it is explained by the discretion "
                 "distribution of the holder base. Conductance is strongly persistent and "
                 "forecastable in all ten liquid markets tested (p < 0.0001), but the "
                 "holder-base explanation fails three pre-registered kill conditions, and on "
                 "137 scheduled FOMC decisions pre-event conductance adds nothing beyond "
                 "option-implied volatility, with the predicted +1.0 coefficient excluded at "
                 "5.4 standard errors."),
    "datePublished": PUBLISHED, "dateModified": MODIFIED, "inLanguage": "en",
    "isAccessibleForFree": True, "license": "https://opensource.org/licenses/MIT",
    "keywords": ("market microstructure, price impact, Kyle lambda, Amihud illiquidity, market "
                 "conductance, gold, Commitments of Traders, inelastic markets, falsification, "
                 "FOMC event study, volatility clustering, liquidity"),
    "author": {"@type": "Person", "name": AUTHOR, "url": REPO},
    "contributor": [{"@type": "Organization", "name": n, "url": u} for n, u in CONTRIBUTORS],
    "publisher": {"@id": f"{BASE}/#org"},
    "mainEntityOfPage": f"{BASE}/", "image": f"{BASE}/og.png",
    "citation": [
        "Kyle, A. (1985). Continuous auctions and insider trading. Econometrica 53(6), 1315-1335.",
        "Amihud, Y. (2002). Illiquidity and stock returns. Journal of Financial Markets 5(1), 31-56.",
        "Gabaix, X. & Koijen, R. (2021). In search of the origins of financial fluctuations. NBER 28967.",
        "Brunnermeier, M. & Pedersen, L. (2009). Market liquidity and funding liquidity. RFS 22(6).",
        "Corsi, F. (2009). A simple approximate long-memory model of realized volatility. JFEC 7(2).",
    ]},
    {"@type": "Dataset", "@id": f"{BASE}/#dataset",
     "name": "Market conductance study results",
     "description": ("Machine-readable results for conductance persistence tests, holder-base "
                     "kill conditions, per-variable Commitments of Traders diagnostics, scheduled "
                     "FOMC event tests and a ten-asset generalisation study."),
     "license": "https://opensource.org/licenses/MIT", "isAccessibleForFree": True,
     "creator": {"@id": f"{BASE}/#org"}, "temporalCoverage": "2008-03-28/2026-09-04",
     "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json",
                       "contentUrl": f"{REPO}/tree/main/out"}],
     "variableMeasured": ["log conductance", "Ljung-Box statistic", "variance ratio",
                          "out-of-sample R-squared", "impact exponent alpha"]},
    {"@type": "SoftwareSourceCode", "@id": f"{BASE}/#code",
     "name": "Market conductance pipeline", "programmingLanguage": "Python",
     "codeRepository": REPO, "license": "https://opensource.org/licenses/MIT"},
    {"@type": "DefinedTerm", "@id": f"{BASE}/#term-conductance",
     "name": "Market conductance",
     "description": ("The operator converting a shock into price movement in dP = G x epsilon; "
                     "equivalent to Kyle's lambda, the price impact per unit of order flow."),
     "inDefinedTermSet": {"@type": "DefinedTermSet", "name": "Market microstructure"}}]


CARDS = f"""<div class="cards">
<a class="card" href="results/"><b>Full results &rarr;</b><span>All six tests in detail: the
persistence null, three kill conditions, the FOMC event study and the ten-asset
generalisation.</span></a>
<a class="card" href="methods/"><b>Methods &rarr;</b><span>How conductance is estimated, why the
exponent is fitted rather than assumed, and how the null is calibrated against synthetic
data.</span></a>
<a class="card" href="data/"><b>Data sources &rarr;</b><span>Every free endpoint used, what is now
blocked, and the volume series that is broken rather than merely noisy.</span></a>
<a class="card" href="faq/"><b>FAQ &rarr;</b><span>Sixteen direct answers on price impact, Kyle's
lambda, positioning data and reproduction.</span></a>
</div>"""

INDEX_BODY = f"""
<h1>Is market conductance a forecastable state variable?</h1>
<p class="sub">A falsification study of the price impact operator in gold and nine other markets.
The foundational claim survives everywhere. The mechanism proposed to explain it does not.</p>
<div class="meta"><span>4,640 trading days &times; 10 assets</span><span>2008&ndash;2026</span>
<span>148 scheduled FOMC decisions</span><span>Data cost $0</span></div>

<h2 id="abstract">Abstract</h2>
<p class="lede">Most market forecasting targets the price. This study targets the operator that
converts news into price movement &mdash; written <code>G</code> in
<code>&Delta;P = G &middot; &epsilon;</code>, where <code>&epsilon;</code> is the shock and
<code>G</code> is the market's <em>conductance</em>. Two questions were pre-registered: is
<code>G</code> a genuine state variable rather than a constant with noise, and is it explained by
the <strong>discretion distribution of the holder base</strong> &mdash; who is forced to act, when,
and who is left to absorb them?</p>
<div class="key"><p><strong>The first is true and universal. The second is not supported.</strong>
Conductance is strongly persistent and forecastable in every liquid market tested, at
p &lt; 0.0001. But a signed conductance measure built from holder-base data fails three
pre-registered kill conditions, is essentially uncorrelated with what it was built to forecast
(corr = 0.014), and adds nothing on scheduled policy events where its predicted effect would be
largest.</p></div>
{CONTRIB_LINE}

<h2 id="findings">Findings at a glance</h2>
<div class="tscroll"><table>
<caption>Six tests. The first four were written down before any data was collected.</caption>
<thead><tr><th>Test</th><th>Result</th><th class="n">Verdict</th></tr></thead>
<tbody>
<tr><td>Is <code>G</code> a state variable, or a constant with noise?</td><td>Ljung-Box(22) = 1021.5 vs null p99 = 40.0; out-of-sample R&sup2; +7.3%</td><td class="n"><span class="stamp pass">STATE VARIABLE</span></td></tr>
<tr><td>Does holder-base &Lambda; beat realised + implied volatility?</td><td>Out-of-sample R&sup2; falls in 5 of 6 specifications; corr(log &Lambda;, log G) = 0.014</td><td class="n"><span class="stamp fail">FAILED</span></td></tr>
<tr><td>Does signed asymmetry produce signed drift?</td><td>Correct sign at every horizon, |t| &le; 1.09</td><td class="n"><span class="stamp fail">FAILED</span></td></tr>
<tr><td>Do large moves cluster in high-&Lambda; states?</td><td>Non-monotone; high/low quintile ratio 0.68</td><td class="n"><span class="stamp fail">FAILED</span></td></tr>
<tr><td>On scheduled events, does pre-event <code>G</code> predict the response?</td><td>Coefficient &minus;0.123; predicted +1.0 excluded at 5.4 standard errors</td><td class="n"><span class="stamp fail">FAILED</span></td></tr>
<tr><td>Does the conductance result generalise beyond gold?</td><td>Identical signature in all 10 assets, p &lt; 0.0001</td><td class="n"><span class="stamp pass">UNIVERSAL</span></td></tr>
</tbody></table></div>
<p><a href="results/">Read the full results, with every coefficient and confidence interval &rarr;</a></p>

<h2 id="universal">Conductance is real &mdash; and it is everywhere</h2>
<p>The same measurement, run unchanged across ten liquid instruments. Every one rejects the
constant-impact null decisively, and gold sits mid-pack rather than standing out.</p>
{cross_asset_table("Null 99th percentile is about 40 for Ljung-Box(22) and about 1.4 for VR(66) in every case. 4,640 trading days each, 2008-03-28 to 2026-09-04. Sorted by out-of-sample forecastability.")}
<div class="key"><p>A mechanism built on gold's uniquely documented holder base cannot explain a
signature that appears just as strongly in high-yield credit and the euro.</p></div>

<h2 id="why">Why the holder-base explanation fails</h2>
<p>Two independent tests point the same way. First, every Commitments of Traders variable tested
individually: <strong>Managed Money positioning</strong> &mdash; the theory's proxy for
margin-sensitive, least-discretionary capital &mdash; does not forecast conductance at any horizon,
with every t-statistic below 1.2 in absolute value. What does forecast it is generic market
<strong>depth and breadth</strong>, with the negative sign absorption implies. That is textbook
microstructure, not a new mechanism.</p>
<p>Second, the scheduled-event test. FOMC decision dates are fixed years ahead, so news
<em>arrival</em> carries no information and the size of each policy surprise is close to
unpredictable. On 137 decisions, pre-event conductance carried a coefficient of &minus;0.123
(t = &minus;0.59) while option-implied volatility priced the same risk at 1.005 (t = +2.75). The
theory's predicted +1.0 sits 5.4 standard errors outside the confidence interval.</p>
<p><a href="results/#fomc">See the event study in full &rarr;</a></p>

<h2 id="explore">Explore the study</h2>
{CARDS}
"""

RESULTS_BODY = f"""
<h1>Full results</h1>
<p class="sub">Every test, coefficient and confidence interval. Newey-West standard errors
throughout; out-of-sample figures use expanding windows refit monthly, or leave-one-year-out where
the event sample is too thin.</p>
<div class="toc"><b>On this page</b><ul>
<li><a href="#persistence">1. Is conductance a constant?</a></li>
<li><a href="#kc1">2. Does &Lambda; beat volatility forecasts?</a></li>
<li><a href="#kc2">3. Signed drift</a></li>
<li><a href="#kc3">4. Large moves by &Lambda; state</a></li>
<li><a href="#fomc">5. The FOMC event study</a></li>
<li><a href="#generalisation">6. Ten-asset generalisation</a></li>
<li><a href="#cot">Per-variable COT diagnostic</a></li>
<li><a href="#settles">What this settles</a></li>
</ul></div>

<h2 id="persistence">1. Is conductance a constant with noise?</h2>
<p>Under the null that <code>G</code> is constant and volume co-moves with volatility only through
information arrival, log conductance is <strong>iid</strong>. The null distribution comes from
2,000 iid bootstraps preserving the exact fat-tailed marginal.</p>
<div class="tscroll"><table>
<caption>Gold (GLD), 4,640 trading days, estimator at the fitted exponent &alpha;&#770; = 1.032.</caption>
<thead><tr><th>Statistic</th><th class="n">Observed</th><th class="n">Null mean</th><th class="n">Null p99</th><th class="n">p</th></tr></thead>
<tbody>
<tr><td>AR(1)</td><td class="n">0.0549</td><td class="n">&minus;0.0003</td><td class="n">0.0350</td><td class="n">&lt;0.0005</td></tr>
<tr><td>AR(22)</td><td class="n">0.0911</td><td class="n">0.0004</td><td class="n">0.0352</td><td class="n">&lt;0.0005</td></tr>
<tr><td>Ljung-Box(22)</td><td class="n"><strong>1021.5</strong></td><td class="n">22.2</td><td class="n">40.0</td><td class="n">&lt;0.0005</td></tr>
<tr><td>Variance ratio, 5d</td><td class="n">1.34</td><td class="n">1.00</td><td class="n">1.10</td><td class="n">&lt;0.0005</td></tr>
<tr><td>Variance ratio, 22d</td><td class="n">3.11</td><td class="n">1.00</td><td class="n">1.23</td><td class="n">&lt;0.0005</td></tr>
<tr><td>Variance ratio, 66d</td><td class="n"><strong>6.82</strong></td><td class="n">1.00</td><td class="n">1.42</td><td class="n">&lt;0.0005</td></tr>
<tr><td>HAR out-of-sample R&sup2;</td><td class="n"><strong>+7.29%</strong></td><td class="n">&minus;0.15%</td><td class="n">+0.04%</td><td class="n">&lt;0.0005</td></tr>
</tbody></table></div>
<p>Variance ratios rising with horizon indicate genuine low-frequency structure rather than
short-lived noise. Conductance is also not volatility relabelled: corr(log G, log realised vol) =
0.262 and corr(log G, log implied vol) = 0.242.</p>

<h2 id="kc1">2. Does holder-base &Lambda; beat realised and implied volatility?</h2>
<div class="tscroll"><table>
<caption>Target: mean log conductance over the forward window. &Delta;OOS is the change in
out-of-sample R&sup2; from adding &Lambda;; negative means it made the forecast worse.</caption>
<thead><tr><th>Horizon</th><th>Benchmark</th><th class="n">&Lambda; t-stat</th><th class="n">Incremental R&sup2;</th><th class="n">&Delta;OOS R&sup2;</th></tr></thead>
<tbody>
<tr><td>1 day</td><td>Realised + implied vol</td><td class="n">+2.79</td><td class="n">+0.0020</td><td class="n">&minus;0.0046</td></tr>
<tr><td>1 week</td><td>Realised + implied vol</td><td class="n">+2.86</td><td class="n">+0.0068</td><td class="n">&minus;0.0098</td></tr>
<tr><td>1 month</td><td>Realised + implied vol</td><td class="n">+2.33</td><td class="n">+0.0102</td><td class="n">+0.0067</td></tr>
<tr><td>1 day</td><td>+ conductance's own history</td><td class="n">+1.15</td><td class="n">+0.0003</td><td class="n">&minus;0.0039</td></tr>
<tr><td>1 week</td><td>+ conductance's own history</td><td class="n">+1.39</td><td class="n">+0.0014</td><td class="n">&minus;0.0122</td></tr>
<tr><td>1 month</td><td>+ conductance's own history</td><td class="n">+1.58</td><td class="n">+0.0040</td><td class="n">&minus;0.0041</td></tr>
</tbody></table></div>
<p>&Lambda; reaches in-sample significance against the benchmark the theory named, but that
survives neither out-of-sample evaluation nor the inclusion of conductance's own past. The blunt
number: <strong>corr(log &Lambda;, log G) = 0.014</strong>.</p>

<h2 id="kc2">3. Does signed asymmetry produce signed drift?</h2>
<div class="tscroll"><table>
<caption>Forward returns regressed on log(&Lambda;<sub>down</sub> / &Lambda;<sub>up</sub>).</caption>
<thead><tr><th>Horizon</th><th class="n">Coefficient</th><th class="n">t</th><th class="n">p</th><th class="n">R&sup2;</th></tr></thead>
<tbody>
<tr><td>1 day</td><td class="n">&minus;0.00009</td><td class="n">&minus;0.63</td><td class="n">0.53</td><td class="n">0.0001</td></tr>
<tr><td>1 week</td><td class="n">&minus;0.00038</td><td class="n">&minus;0.62</td><td class="n">0.53</td><td class="n">0.0005</td></tr>
<tr><td>1 month</td><td class="n">&minus;0.00230</td><td class="n">&minus;1.09</td><td class="n">0.28</td><td class="n">0.0047</td></tr>
</tbody></table></div>
<p>Signs are consistently negative &mdash; the direction the theory predicts, since stressed longs
should make a market conduct better downward &mdash; but nothing approaches significance.</p>

<h2 id="kc3">4. Do large moves cluster in high-&Lambda; states?</h2>
<div class="tscroll"><table>
<caption>Probability of a 2&sigma; move in the following five days, by quintile of &Lambda;.</caption>
<thead><tr><th>&Lambda; quintile</th><th class="n">Q1 (low)</th><th class="n">Q2</th><th class="n">Q3</th><th class="n">Q4</th><th class="n">Q5 (high)</th></tr></thead>
<tbody><tr><td>P(large move)</td><td class="n">0.320</td><td class="n">0.206</td><td class="n">0.238</td><td class="n">0.238</td><td class="n">0.219</td></tr></tbody>
</table></div>
<p>Non-monotone, and the highest-&Lambda; quintile carries fewer large moves than the lowest &mdash;
a ratio of 0.68, the wrong direction.</p>

<h2 id="fomc">5. The FOMC event study</h2>
<p>This is the test that separates a transmission operator from ordinary volatility clustering.
FOMC decision dates are fixed years ahead, so news arrival carries no information and the size of
each policy surprise is close to unpredictable by construction. Under clustered news, pre-event
conductance should add nothing to what options already price. Under a genuine operator, it should
forecast the response with a coefficient near 1.</p>
<div class="tscroll"><table>
<caption>137 scheduled FOMC decisions, 2008&ndash;2026. Target: log absolute return on the decision
day. Unscheduled and emergency actions are excluded.</caption>
<thead><tr><th>Predictor</th><th class="n">Coefficient</th><th class="n">t</th><th class="n">p</th><th class="n">95% interval</th></tr></thead>
<tbody>
<tr><td>Pre-event log conductance</td><td class="n"><strong>&minus;0.123</strong></td><td class="n">&minus;0.59</td><td class="n">0.555</td><td class="n">[&minus;0.53, +0.29]</td></tr>
<tr><td>Pre-event log realised volatility</td><td class="n">&minus;0.096</td><td class="n">&minus;0.36</td><td class="n">0.718</td><td class="n">&mdash;</td></tr>
<tr><td>Pre-event log implied volatility (GVZ)</td><td class="n"><strong>+1.005</strong></td><td class="n">+2.75</td><td class="n">0.006</td><td class="n">&mdash;</td></tr>
</tbody></table></div>
<p>Implied volatility prices scheduled-event risk almost exactly right. Structural conductance adds
nothing, with the wrong sign. The HAC standard error is 0.208, so the predicted +1.0 sits
<strong>5.4 standard errors</strong> outside the interval &mdash; an informative null, not an
underpowered one. The result is stable across pre-event windows ending 2, 6 and 11 days out.</p>
<h3>The detail that settles it</h3>
<p>Pre-event conductance <em>does</em> load strongly on ordinary days (t = +7.98) and loses its
significance precisely on days when news arrival is known in advance (t = +1.57). That ordering is
backwards for a transmission operator, which should not care whether news was on the calendar. It is
exactly what volatility clustering predicts.</p>

<h2 id="generalisation">6. Ten-asset generalisation</h2>
<p>The pre-registered bar: <em>if it only works on gold, it is a gold story dressed as a law.</em>
It does not only work on gold.</p>
{cross_asset_table("Identical measurement across ten liquid instruments, each with its exponent re-estimated and its own iid null. All p < 0.0001.")}
<p>Estimated impact exponents span 0.41 for the euro to 1.36 for the S&amp;P 500, so no single
assumed exponent &mdash; square-root or Amihud &mdash; would have been correct anywhere near
universally.</p>

<h2 id="cot">Per-variable Commitments of Traders diagnostic</h2>
<p>Construction-free: each raw variable added individually to the full control set, so the result
does not depend on how &Lambda; was assembled.</p>
<div class="tscroll"><table>
<caption>Forecasting mean log conductance one month ahead, over realised vol + implied vol +
conductance's own history.</caption>
<thead><tr><th>Variable</th><th>Role in the theory</th><th class="n">t</th><th class="n">&Delta;OOS R&sup2;</th></tr></thead>
<tbody>
<tr><td>Trader count (breadth)</td><td>Absorption</td><td class="n"><strong>&minus;3.18</strong></td><td class="n"><strong>+0.79 pp</strong></td></tr>
<tr><td>Open interest (depth)</td><td>Absorption</td><td class="n"><strong>&minus;2.88</strong></td><td class="n"><strong>+0.46 pp</strong></td></tr>
<tr><td>Managed Money net / OI</td><td>Forced mass</td><td class="n">&minus;1.18</td><td class="n">&minus;0.21 pp</td></tr>
<tr><td>Managed Money long / OI</td><td>Forced mass</td><td class="n">&minus;1.17</td><td class="n">&minus;0.09 pp</td></tr>
<tr><td>Managed Money short / OI</td><td>Forced mass</td><td class="n">+0.99</td><td class="n">&minus;0.74 pp</td></tr>
<tr><td>Managed Money gross / OI</td><td>Forced mass</td><td class="n">&minus;0.04</td><td class="n">&minus;0.49 pp</td></tr>
<tr><td>&Delta; Managed Money net, 5d</td><td>Forced mass</td><td class="n">&minus;0.25</td><td class="n">&minus;0.26 pp</td></tr>
<tr><td>Swap dealer short / OI</td><td>Forced mass</td><td class="n">&minus;0.49</td><td class="n">&minus;1.58 pp</td></tr>
<tr><td>Producer short / OI</td><td>Forced mass</td><td class="n">&minus;0.41</td><td class="n">&minus;1.29 pp</td></tr>
</tbody></table></div>
<p>All twelve variables jointly add +2.0 percentage points of in-sample R&sup2; and lose 5.2 points
out of sample &mdash; the signature of overfitting.</p>

<h2 id="settles">What this settles</h2>
<h3>Settled, in the theory's favour</h3>
<p>The impact operator is a genuine state variable: persistent, forecastable at 7.3% out-of-sample
R&sup2;, distinct from realised and implied volatility, and present in every liquid market tested.
A constant-impact reading is decisively rejected.</p>
<h3>Settled, against the theory</h3>
<p>That the persistence is produced by the discretion distribution of the holder base. The
forced-mass side is flat, the only signal is generic depth and breadth, and the effect disappears
on scheduled events where it should be strongest.</p>
<h3>Still open</h3>
<p>The absorption stack the theory specifies &mdash; COMEX registered versus eligible stocks, LBMA
vault holdings, Bank of England custody, Swiss customs &mdash; was never testable, because the
primary sources are blocked. But note the bar it now faces: it would have to explain a signature
identical in markets with no vaults at all.</p>
"""


METHODS_BODY = f"""
<h1>How to measure price impact from free daily data</h1>
<p class="sub">The estimator, why the impact exponent is fitted rather than assumed, how the null is
calibrated against synthetic data, and the point-in-time discipline that keeps a backtest honest.</p>
<div class="toc"><b>On this page</b><ul>
<li><a href="#estimator">The estimator</a></li>
<li><a href="#alpha">Fitting the impact exponent</a></li>
<li><a href="#null">The null, and why it is sharp</a></li>
<li><a href="#calibration">Calibrating size and power</a></li>
<li><a href="#lambda">Constructing signed &Lambda;</a></li>
<li><a href="#pit">Point-in-time discipline</a></li>
<li><a href="#event">The scheduled-event design</a></li>
<li><a href="#breaks">Structural breaks</a></li>
<li><a href="#refs">References</a></li>
</ul></div>

<h2 id="estimator">The estimator</h2>
<p>In a Kyle (1985) framework <code>r = &lambda; &middot; flow</code>, so &lambda; &mdash; price
impact per unit of trade &mdash; <em>is</em> the conductance. With daily free data:</p>
<pre><code>log G_t = log |r_t| &minus; &alpha; &middot; log v_t

v_t = V_t / median(V, trailing 252 days)</code></pre>
<p>Normalising volume by a trailing median removes secular volume growth and contract-roll drift
without touching sub-annual variation. The window is trailing only, so it introduces no lookahead.</p>

<h2 id="alpha">Fitting the impact exponent</h2>
<p>The <strong>square-root law of market impact</strong> assumes &alpha; = 0.5. <strong>Amihud
illiquidity</strong> assumes &alpha; = 1.0. Rather than pick, regress <code>log|r|</code> on
<code>log v</code> and read the exponent off the data: &alpha;&#770; = 1.032 for gold, and a range
from 0.41 (euro) to 1.36 (S&amp;P 500) across the universe. No single assumed exponent would have
been right.</p>
<p>Fitting &alpha; has a second benefit that matters more than accuracy. At the fitted value,
<code>log G</code> is <strong>orthogonal to <code>log v</code> by construction</strong>, so
persistence in conductance cannot be an artefact of volume persistence. An automated test verifies
the residual correlation stays below 0.02 on synthetic data. Results are reported at
&alpha;&#770;, 0.5 and 1.0; all three agree.</p>

<h2 id="null">The null, and why it is sharp</h2>
<p>Under the joint hypothesis that</p>
<ul><li><code>G</code> is a constant, and</li>
<li>volume and volatility co-move only through information arrival (the mixture-of-distributions
hypothesis),</li></ul>
<p><code>log G</code> is <strong>iid</strong>. That is the reason for this particular estimator: it
turns a vague hypothesis into a sharp, testable one.</p>
<p>The null distribution comes from 2,000 <strong>iid bootstrap</strong> resamples of the empirical
series, preserving its exact fat-tailed marginal while destroying time structure. The identical
statistic pipeline runs on real and simulated series, so anything the pipeline itself induces
appears in the null too. Statistics: AR(1), AR(5), AR(22), Ljung-Box(22), variance ratios at 5, 22
and 66 days, and out-of-sample R&sup2; of a HAR forecast benchmarked against the expanding mean.</p>

<h2 id="calibration">Calibrating size and power</h2>
<p>The headline result rests on the test rejecting a constant-conductance world at roughly its
nominal rate and having power against a varying one. That is checked, not asserted. Synthetic
markets are built with known ground truth &mdash; persistent volume in both arms, conductance
constant in one and an AR(1) state variable in the other &mdash; and the suite verifies the test
does not over-reject under the null and does detect the alternative. It also verifies exponent
recovery and the orthogonality property above.</p>

<h2 id="lambda">Constructing signed &Lambda;</h2>
<pre><code>&Lambda;_down = MM_long  &times; w(underwater_long)  / absorption
&Lambda;_up   = MM_short &times; w(underwater_short) / absorption

absorption = OI &times; breadth &times; (1 &minus; top-4 concentration)</code></pre>
<p>Trigger distance uses a cost-basis tracker: a weighted-average entry price that moves toward the
current price only when a position is <em>added to</em>, and stays put when trimmed. Distance from
basis is scaled to a monthly volatility horizon and passed through a logistic.</p>
<div class="key"><p><strong>Correction applied mid-run.</strong> The first version scaled by
<em>daily</em> volatility (about 1%) while positions sit about 10% from basis. That saturated the
logistic to exactly 0 or 1, turning &Lambda; into a binary switch. It was fixed before the reported
numbers were produced. Both versions fail their kill conditions; the fixed version fails less
badly.</p></div>

<h2 id="pit">Point-in-time discipline</h2>
<p>The CFTC Commitments of Traders report is a Tuesday snapshot published the following Friday at
15:30 ET &mdash; a three-day information lag. Every series stores <strong>both</strong> a reference
date and a release date, and every join uses release date only. Timestamping by reference date
instead produces a backtest that looks excellent and means nothing. An automated test asserts no row
is ever consumed before the day it was published.</p>

<h2 id="event">The scheduled-event design</h2>
<p>Persistence alone cannot say <em>why</em> conductance persists. Two stories fit: a transmission
operator varying with market structure, or autocorrelated shock magnitudes &mdash; clustered news.
Scheduled FOMC decisions separate them, because the date is fixed years ahead and the surprise size
is close to unpredictable by construction of an event study.</p>
<pre><code>log|r_event| ~ &beta; &middot; log G_pre + &gamma;&#8321; &middot; log RV_pre + &gamma;&#8322; &middot; log IV_pre</code></pre>
<p><code>G_pre</code> and <code>RV_pre</code> are means over a strictly prior window; <code>IV_pre</code>
is the last GVZ close before the event. The benchmark is deliberately hostile: GVZ is forward-looking
and already knows the meeting is coming. With about 148 events an expanding window is too thin, so
out-of-sample uses <strong>leave-one-year-out</strong> cross-validation. A placebo runs the identical
specification on all non-FOMC days.</p>
<p>Only <strong>regularly scheduled</strong> meetings are used. Unscheduled and emergency actions
happen <em>because</em> markets are stressed; including them would manufacture the exact correlation
under test. Exclusion follows the Federal Reserve's own labels.</p>

<h2 id="breaks">Structural breaks handled explicitly</h2>
<div class="tscroll"><table>
<thead><tr><th>Date</th><th>Break</th><th>Consequence</th></tr></thead>
<tbody>
<tr><td>30 Jan 2015</td><td>GOFO discontinued</td><td>Lease-rate series ends; anything post-2015 must be synthetic</td></tr>
<tr><td>1 Jan 2022</td><td>SA-CCR reclassifies gold derivatives</td><td>Inflates reported precious-metals notional in OCC data</td></tr>
<tr><td>13 Jan 2026</td><td>CME moves precious metals to percentage margin (gold 5%)</td><td>The compulsion mechanism itself changed; pre- and post-2026 &Lambda; are not the same variable</td></tr>
</tbody></table></div>

<h2 id="refs">References</h2>
<ul>
<li>Kyle, A. (1985). Continuous auctions and insider trading. <em>Econometrica</em> 53(6), 1315&ndash;1335.</li>
<li>Amihud, Y. (2002). Illiquidity and stock returns. <em>Journal of Financial Markets</em> 5(1), 31&ndash;56.</li>
<li>Gabaix, X. &amp; Koijen, R. (2021). In search of the origins of financial fluctuations: the inelastic markets hypothesis. NBER 28967.</li>
<li>Brunnermeier, M. &amp; Pedersen, L. (2009). Market liquidity and funding liquidity. <em>Review of Financial Studies</em> 22(6).</li>
<li>Corsi, F. (2009). A simple approximate long-memory model of realized volatility. <em>Journal of Financial Econometrics</em> 7(2).</li>
</ul>
"""

DATA_BODY = f"""
<h1>Free market data sources used in this study</h1>
<p class="sub">Every endpoint, what it costs, what it covers, and which sources that were free are
now blocked. No third-party data is redistributed &mdash; collectors fetch at run time.</p>

<h2 id="working">Sources that work</h2>
<div class="tscroll"><table>
<caption>All free, no API key required except where noted. Probed 6 September 2026.</caption>
<thead><tr><th>Source</th><th>Role</th><th>Coverage</th><th class="n">Status</th></tr></thead>
<tbody>
<tr><td><strong>CFTC Disaggregated Commitments of Traders</strong> &mdash; Socrata API at <code>publicreporting.cftc.gov</code>, gold contract <code>088691</code></td><td>Holder base</td><td>1,056 weeks, 2006&ndash;2026</td><td class="n"><span class="stamp pass">OK</span></td></tr>
<tr><td><strong>Daily OHLCV for ten ETFs</strong> &mdash; GLD, SPY, QQQ, TLT, HYG, SLV, USO, FXE, EEM, GDX</td><td>Instruments</td><td>4,640 days each, 2008&ndash;2026</td><td class="n"><span class="stamp pass">OK</span></td></tr>
<tr><td><strong>LBMA gold price</strong> &mdash; official PM fix feed</td><td>Price</td><td>14,676 days, 1968&ndash;2026</td><td class="n"><span class="stamp pass">OK</span></td></tr>
<tr><td><strong>CBOE GVZ</strong> &mdash; gold implied volatility index</td><td>Control</td><td>4,594 days, 2008&ndash;2026</td><td class="n"><span class="stamp pass">OK</span></td></tr>
<tr><td><strong>Federal Reserve FOMC calendar</strong> &mdash; meeting blocks and statement links</td><td>Event dates</td><td>148 scheduled decisions, 2008&ndash;2026</td><td class="n"><span class="stamp pass">OK</span></td></tr>
<tr><td>Dollar index, 10-year Treasury yield</td><td>Controls</td><td>2001&ndash;2026</td><td class="n"><span class="stamp pass">OK</span></td></tr>
</tbody></table></div>

<h2 id="blocked">Sources that are no longer freely accessible</h2>
<p>Two corrections to the standard data inventory, both discovered by probing rather than assumed:</p>
<div class="tscroll"><table>
<thead><tr><th>Source</th><th>Role</th><th class="n">Status</th></tr></thead>
<tbody>
<tr><td><strong>COMEX warehouse stocks</strong> &mdash; registered versus eligible, <code>cmegroup.com/delivery_reports/Gold_Stocks.xls</code></td><td>Absorption</td><td class="n"><span class="stamp fail">403 &mdash; bot-blocked</span></td></tr>
<tr><td><strong>LBMA vault holdings</strong> &mdash; seven custodians plus Bank of England</td><td>Absorption</td><td class="n"><span class="stamp fail">404 &mdash; URLs moved</span></td></tr>
<tr><td>World Gold Council Goldhub</td><td>Absorption</td><td class="n"><span class="stamp warn">registration</span></td></tr>
<tr><td>FRED CSV endpoint</td><td>Control</td><td class="n"><span class="stamp warn">rate-limited</span></td></tr>
</tbody></table></div>
<p>Together the first two are the <strong>entire absorption stack</strong> &mdash; the denominator of
&Lambda;, including the registered-versus-eligible split that makes COMEX unusual. That half of the
framework could only be tested through weaker proxies (open interest and trader count), which is a
material limitation on the result.</p>

<h2 id="gcf">A warning: Yahoo GC=F historical volume is broken</h2>
<p>Not merely noisy &mdash; unusable. Median daily volume by year runs 56 to 905 contracts against a
maximum near 200,000, with 41 zero-volume days. The series alternates between the front-month
aggregate and a near-dead contract. Price is fine; volume is not. Any study that computes turnover,
Amihud illiquidity or impact from this series will produce nonsense. This study measures on GLD,
whose consolidated NYSE Arca volume is clean across nineteen years: median 6&ndash;15 million shares,
no zeros.</p>

<h2 id="fomc-dates">Extracting FOMC decision dates correctly</h2>
<p>Each FOMC policy decision publishes exactly one statement, so the Federal Reserve's own statement
links are an authoritative, non-derived list of decision dates. Two traps:</p>
<ul>
<li><strong>Exclude unscheduled meetings.</strong> Emergency actions happen because markets are
stressed. The Fed labels them &mdash; "(unscheduled)", "(cancelled)", "Conference Call", "notation
vote" &mdash; so exclusion follows their taxonomy, not a judgement call.</li>
<li><strong>Watch month-straddling meetings.</strong> A two-day meeting spanning a month end is
headed "April/May 30-1" or "Jan/Feb 31-1", so a naive month filter silently drops it.</li>
<li><strong>Not every <code>monetary&lt;date&gt;</code> link is a decision.</strong> Framework
releases use the same URL pattern. Cross-checking against press-conference links and the
Wednesday decision convention removes them.</li>
</ul>

<h2 id="reproduce">Reproducing the study</h2>
<pre><code>git clone {REPO}
cd market-conductance
make setup      # venv and pinned dependencies
make all        # collect, measure, engine, cot, events, generalize
make test       # calibration: size, power, point-in-time discipline</code></pre>
<p>Roughly fifteen minutes, total cost $0. Random seeds are fixed. Collectors write immutable raw
snapshots with provenance attached, and every series carries both its reference and release dates.
Machine-readable results land in <code>out/</code> as JSON.</p>
"""

FAQ_BODY = ('<h1>Questions about market conductance and price impact</h1>'
            '<p class="sub">Direct answers on the impact operator, Kyle\'s lambda, positioning '
            'data, free data sources and reproduction.</p>'
            + "".join(f'<div class="faqitem"><h3 id="q{i}">{q}</h3>{a}</div>'
                      for i, (q, a) in enumerate(FAQ, 1))
            + '<h2>Read further</h2>' + CARDS.replace('href="results/"', 'href="../results/"')
              .replace('href="methods/"', 'href="../methods/"')
              .replace('href="data/"', 'href="../data/"')
              .replace('href="faq/"', 'href="../faq/"'))


PAGES = [
 dict(slug="", crumb="Home", prio="1.0",
      title="Is Market Conductance a Forecastable State Variable?",
      og="Is market conductance a forecastable state variable?",
      desc="Market conductance is a forecastable state variable in all 10 asset classes tested, at p<0.0001. The holder-base explanation for it fails at 5.4 sigma.",
      schema=ARTICLE_SCHEMA, body=INDEX_BODY),
 dict(slug="results/", crumb="Results", prio="0.9",
      title="Full Results: Six Tests of the Market Impact Operator",
      og="Full results: six tests of the market impact operator",
      desc="Every coefficient and confidence interval: the persistence null, three kill conditions, a 137-event FOMC study and a ten-asset generalisation of price impact.",
      schema=[], body=RESULTS_BODY),
 dict(slug="methods/", crumb="Methods", prio="0.8",
      title="How to Measure Price Impact From Free Daily Data | Methods",
      og="How to measure price impact from free daily data",
      desc="Estimating Kyle's lambda from daily data: fitting the impact exponent instead of assuming the square-root law, building a sharp iid null, and calibrating test size and power.",
      schema=[], body=METHODS_BODY),
 dict(slug="data/", crumb="Data", prio="0.8",
      title="Free Market Data Sources: CFTC COT, LBMA, GVZ, FOMC Dates",
      og="Free market data sources used in this study",
      desc="Every free endpoint used: CFTC Commitments of Traders API, LBMA gold fix, CBOE GVZ, FOMC dates. Which sources are now blocked, and why Yahoo GC=F volume is unusable.",
      schema=[], body=DATA_BODY),
 dict(slug="faq/", crumb="FAQ", prio="0.7",
      title="Market Conductance and Price Impact: 16 Questions Answered",
      og="Market conductance and price impact: questions answered",
      desc="What is market conductance? Is market impact constant? Does COT positioning predict volatility? Sixteen direct answers on the price impact operator and Kyle's lambda.",
      schema=FAQ_SCHEMA, body=FAQ_BODY),
]

if __name__ == "__main__":
    print("building site...")
    build(PAGES)
