"""Page definitions. Content lives here; the generator handles every head tag."""

BASE = "https://codedpro.github.io/market-conductance"
REPO = "https://github.com/codedpro/market-conductance"

CROSS_ASSET = [
    ("HYG", "High-yield credit", "0.994", "1632.6", "7.21", "+10.1%"),
    ("SLV", "Silver", "0.797", "2459.0", "11.02", "+9.4%"),
    ("SPY", "US large-cap equity", "1.357", "1208.2", "8.01", "+8.7%"),
    ("QQQ", "US tech equity", "1.022", "1134.6", "7.68", "+8.1%"),
    ("USO", "Crude oil", "0.734", "964.4", "6.30", "+7.3%"),
    ("GLD", "Gold", "1.032", "1021.5", "6.82", "+7.3%"),
    ("EEM", "EM equity", "1.257", "1103.5", "7.45", "+7.3%"),
    ("GDX", "Gold miners", "1.240", "1173.6", "7.45", "+7.2%"),
    ("TLT", "Long Treasuries", "1.027", "729.5", "6.46", "+5.6%"),
    ("FXE", "Euro", "0.412", "777.0", "6.51", "+5.2%"),
]

def cross_asset_table(caption):
    rows = "\n".join(
        f'<tr><td><strong>{s}</strong></td><td>{c}</td><td class="n">{a}</td>'
        f'<td class="n">{lb}</td><td class="n">{vr}</td><td class="n">{r2}</td></tr>'
        for s, c, a, lb, vr, r2 in CROSS_ASSET)
    return f'''<div class="tscroll"><table>
<caption>{caption}</caption>
<thead><tr><th>Ticker</th><th>Asset class</th><th class="n">&alpha;&#770;</th>
<th class="n">Ljung-Box(22)</th><th class="n">VR(66)</th><th class="n">OOS R&sup2;</th></tr></thead>
<tbody>{rows}</tbody></table></div>'''

FAQ = [
 ("What is market conductance?",
  "<p>Market conductance is the operator that converts a shock into price movement, written "
  "<code>G</code> in the relation <code>&Delta;P = G &times; &epsilon;</code>, where "
  "<code>&epsilon;</code> is the shock. It is equivalent to Kyle's lambda &mdash; the price "
  "impact per unit of order flow. Forecasting conductance means forecasting how hard a market "
  "will move for a given piece of news, rather than forecasting the news itself.</p>"),
 ("Is market impact a constant or a state variable?",
  "<p>It is a state variable. Measured conductance is strongly persistent: Ljung-Box(22) = 1021.5 "
  "for gold against an iid-bootstrap null 99th percentile of 40.0, variance ratios rising from "
  "1.34 at one week to 6.82 at one quarter, and a HAR out-of-sample R&sup2; of +7.3%. The "
  "constant-impact model is rejected at p &lt; 0.0001 in all ten markets tested.</p>"),
 ("Does the conductance result apply only to gold?",
  "<p>No. The identical signature appears in all ten liquid markets tested &mdash; gold, S&amp;P 500, "
  "Nasdaq, long Treasuries, high-yield credit, silver, crude oil, the euro, emerging-market equity "
  "and gold miners &mdash; each at p &lt; 0.0001. High-yield credit shows the strongest "
  "out-of-sample forecastability at +10.1%; gold sits mid-pack. Because the effect is universal, "
  "a mechanism specific to gold's holder base cannot explain it.</p>"),
 ("Does Commitments of Traders positioning predict volatility or market impact?",
  "<p>No. Managed Money positioning from the CFTC Commitments of Traders report &mdash; the standard "
  "proxy for margin-sensitive, forced capital &mdash; does not forecast conductance at any horizon, "
  "with every t-statistic below 1.2 in absolute value. The only Commitments of Traders variables "
  "with predictive power are generic market depth (open interest, t = &minus;2.88) and breadth "
  "(trader count, t = &minus;3.18), both with the negative sign that absorption capacity implies.</p>"),
 ("Does conductance predict how markets respond to scheduled events like FOMC?",
  "<p>No. On 137 scheduled FOMC decisions between 2008 and 2026, pre-event conductance carried a "
  "coefficient of &minus;0.123 (t = &minus;0.59) on the size of the decision-day move, adding "
  "nothing beyond option-implied volatility. The theory predicted a coefficient near +1.0, which "
  "lies 5.4 standard errors outside the 95% confidence interval of [&minus;0.53, +0.29]. Implied "
  "volatility priced the same risk almost exactly right, with a coefficient of 1.005.</p>"),
 ("What is the market impact exponent, and why estimate it rather than assume it?",
  "<p>The exponent &alpha; governs how price impact scales with volume in "
  "<code>log|r| = log G + &alpha; &times; log v</code>. The square-root law of market impact "
  "assumes &alpha; = 0.5; Amihud illiquidity assumes &alpha; = 1.0. Estimating it gives 1.032 for "
  "gold and a range from 0.41 (euro) to 1.36 (S&amp;P 500), so no single assumed exponent would "
  "have been correct. Using the empirical &alpha; also makes log conductance orthogonal to log "
  "volume by construction, so persistence cannot be an artefact of volume.</p>"),
 ("How do you tell a real impact operator from ordinary volatility clustering?",
  "<p>Use scheduled events. If persistence in measured impact were just clustered news, then on a "
  "date fixed years in advance &mdash; where arrival carries no information and the surprise size "
  "is near-unpredictable &mdash; pre-event conductance should add nothing beyond what options "
  "already price. If it were a genuine transmission operator, it should forecast the response with "
  "a coefficient near 1. In this study it added nothing, and pre-event conductance lost "
  "significance precisely on scheduled days (t = +1.57) while loading strongly on ordinary days "
  "(t = +7.98). That ordering favours volatility clustering.</p>"),
 ("What is a kill condition?",
  "<p>A falsification criterion written down before any data is collected, specifying in advance "
  "what result would end the project. Four were pre-registered here. Pre-registration is what stops "
  "the decision being made in the moment by whoever most wants the theory to be true.</p>"),
 ("Is Kyle's lambda the same as Amihud illiquidity?",
  "<p>They are closely related measures of price impact. Kyle's lambda is the structural coefficient "
  "in <code>r = &lambda; &times; flow</code>. Amihud's ILLIQ is a daily proxy, absolute return "
  "divided by dollar volume, which corresponds to assuming an impact exponent of 1.0. This study "
  "nests both by estimating the exponent rather than fixing it.</p>"),
 ("Can this be traded?",
  "<p>No trading strategy is supported by these results. The signed-asymmetry test, which was the "
  "route to a directional edge, produced no significant drift at any horizon. Adding the "
  "holder-base measure to a volatility forecast reduced out-of-sample accuracy in five of six "
  "specifications. This is empirical research and contains no investment advice.</p>"),
 ("Is COMEX warehouse stock data still freely available?",
  "<p>Not by direct download. The COMEX gold warehouse file at "
  "<code>cmegroup.com/delivery_reports/Gold_Stocks.xls</code> now returns HTTP 403 behind bot "
  "protection, and LBMA's vault-holdings URLs return 404. Together these are the entire absorption "
  "side of the framework, which is why that half could only be tested through weaker proxies.</p>"),
 ("Is Yahoo Finance GC=F volume data reliable?",
  "<p>No, not historically. Median daily volume by year runs 56&ndash;905 contracts against a "
  "maximum near 200,000, with 41 zero-volume days &mdash; the series alternates between the "
  "front-month aggregate and a near-dead contract. Price is usable; volume is not. This study "
  "measures on GLD, whose consolidated NYSE Arca volume is clean across nineteen years.</p>"),
 ("How is point-in-time discipline enforced?",
  "<p>Commitments of Traders data is a Tuesday snapshot published the following Friday at 15:30 ET. "
  "Every series stores both a reference date and a release date, and all joins use release date "
  "only. An automated test asserts that no row is ever used before the day it was published. "
  "Timestamping by reference date instead produces a backtest that looks excellent and means "
  "nothing.</p>"),
 ("How was the null distribution constructed?",
  "<p>Under the joint hypothesis that conductance is constant and that volume co-moves with "
  "volatility only through information arrival, log conductance is iid. The null distribution comes "
  "from 2,000 iid bootstrap resamples of the empirical series, preserving its exact fat-tailed "
  "marginal while destroying time structure. The identical statistic pipeline runs on real and "
  "simulated data, so anything the pipeline itself induces appears in the null too.</p>"),
 ("Was the test powerful enough to detect the predicted effect?",
  "<p>Yes. The HAC standard error on the pre-event conductance coefficient is 0.208, so the "
  "theory's own prediction of +1.0 would have appeared at roughly five sigma had it been present. "
  "This is an informative null rather than an underpowered one, and it is stable across pre-event "
  "windows ending 2, 6 and 11 days before the event.</p>"),
 ("Can I reproduce these results?",
  f"<p>Yes, at zero cost. Clone the repository, run <code>make setup</code> then <code>make all</code>. "
  f"Every number regenerates from public endpoints in roughly fifteen minutes; no third-party data "
  f"is redistributed and random seeds are fixed. The code is MIT licensed at "
  f'<a href="{REPO}">{REPO}</a>.</p>'),
]
