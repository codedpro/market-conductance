# Project Lambda — is market conductance a forecastable state variable?

**A free-data falsification study of the impact operator in gold and nine other markets.**

[![tests](https://img.shields.io/badge/calibration%20tests-8%20passing-brightgreen)](tests/test_calibration.py)
[![data](https://img.shields.io/badge/data%20cost-%240-blue)](#data-sources)
[![license](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

Most market forecasting targets the price. This study targets the **operator that
converts news into price movement** — written `G` in `ΔP = G · ε`, where `ε` is the
shock and `G` is the market's *conductance*. The hypothesis under test is that `G`
is (a) a genuine, forecastable state variable rather than a constant with noise,
and (b) explained by the **discretion distribution of the holder base** — who is
forced to act, when, and who is left to absorb them.

**Result in one line: (a) is true and universal. (b) is not supported.**

---

## Findings

| # | Test | Result |
|---|---|---|
| **1** | Is `G` a state variable, or a constant with noise? | **Rejected the constant.** Ljung-Box(22) = 1021.5 vs null p99 = 40.0; out-of-sample R² **+7.3%** |
| **2** | Does holder-base `Λ` beat realised + implied volatility? | **No.** Out-of-sample R² *falls* in 5 of 6 specifications; corr(log Λ, log G) = **0.014** |
| **3** | Does signed conductance asymmetry produce signed drift? | **No.** Correct sign at every horizon, \|t\| ≤ 1.09 |
| **4** | Do large moves cluster in high-`Λ` states? | **No.** Non-monotone; high/low quintile ratio 0.68 |
| **5** | On *scheduled* events, does pre-event `G` predict the response? | **No.** Coefficient −0.12; the predicted +1.0 excluded at **5.4 standard errors** |
| **6** | Does the `G` result generalise beyond gold? | **Yes — everywhere.** Identical signature in all 10 assets, p < 0.0001 |

Tests 1–4 are the kill conditions written into the [original theory document](docs/THEORY.md)
before any data was collected. Tests 5 and 6 were added to discriminate between two
explanations that tests 1–4 cannot separate.

---

## The central result

Conductance is real, strongly persistent, and forecastable — and that is true of
**every liquid market tested**, not gold specifically:

| Asset | Class | α̂ | Ljung-Box(22) | VR(66) | OOS R² |
|---|---|---|---|---|---|
| GLD | gold | 1.032 | 1021.5 | 6.82 | +7.3% |
| SPY | US large-cap equity | 1.357 | 1208.2 | 8.01 | +8.7% |
| QQQ | US tech equity | 1.022 | 1134.6 | 7.68 | +8.1% |
| TLT | long Treasuries | 1.027 | 729.5 | 6.46 | +5.6% |
| HYG | high-yield credit | 0.994 | 1632.6 | 7.21 | +10.1% |
| SLV | silver | 0.797 | 2459.0 | 11.02 | +9.4% |
| USO | crude oil | 0.734 | 964.4 | 6.30 | +7.3% |
| FXE | euro | 0.412 | 777.0 | 6.51 | +5.2% |
| EEM | EM equity | 1.257 | 1103.5 | 7.45 | +7.3% |
| GDX | gold miners | 1.240 | 1173.6 | 7.45 | +7.2% |

Null 99th percentile for Ljung-Box(22) is ≈ 40 and for VR(66) ≈ 1.4 in every case.
All p < 0.0001. Sample: 4,640 trading days each, 2008-03-28 → 2026-09-04.

**This cuts both ways.** It clears the theory's own generalisation bar — "if it only
works on gold, it is a gold story dressed as a law." But a mechanism built on *gold's*
uniquely documented holder base cannot explain a signature that appears just as
strongly in high-yield credit and the euro.

---

## Why the holder-base explanation fails

Two independent tests point the same way.

**Every COT variable, tested individually** against realised vol + implied vol +
conductance's own history, forecasting mean log `G` one month ahead:

| Variable | Role | t (1 month) | ΔOOS R² |
|---|---|---|---|
| Trader count (breadth) | absorption | **−3.18** | **+0.79 pp** |
| Open interest (depth) | absorption | **−2.88** | **+0.46 pp** |
| Managed Money net / OI | forced mass | −1.18 | −0.21 pp |
| Managed Money long / OI | forced mass | −1.17 | −0.09 pp |
| Managed Money short / OI | forced mass | +0.99 | −0.74 pp |
| Managed Money gross / OI | forced mass | −0.04 | −0.49 pp |
| Δ Managed Money net, 5d | forced mass | −0.25 | −0.26 pp |
| Swap dealer short / OI | forced mass | −0.49 | −1.58 pp |
| Producer short / OI | forced mass | −0.41 | −1.29 pp |

Managed Money positioning is the theory's proxy for margin-sensitive,
least-discretionary capital — the primitive the whole framework rests on. It does
not forecast conductance at any horizon. What does forecast it is **depth and
breadth**, with the negative sign the absorption logic requires. That is textbook
microstructure (Kyle 1985, Amihud 2002), not a new mechanism.

**The scheduled-event test.** FOMC decision dates are fixed years ahead, so news
*arrival* carries no information, and the size of the policy surprise is close to
unpredictable. If `G` is a transmission operator, pre-event `G` should forecast the
response to whatever lands, with a coefficient near 1. On 137 scheduled decisions:

| Predictor | Coefficient | t |
|---|---|---|
| Pre-event log `G` | **−0.123** | −0.59 |
| Pre-event log realised vol | −0.096 | −0.36 |
| Pre-event log implied vol (GVZ) | **+1.005** | **+2.75** |

Implied volatility prices scheduled-event risk almost exactly right (coefficient
1.005). Structural conductance adds nothing, with the wrong sign. The 95% confidence
interval on pre-event `G` is [−0.53, +0.29] — the theory's predicted +1.0 sits 5.4
standard errors outside it. **This is an informative null, not an underpowered one.**

Notably, pre-event `G` *does* load on ordinary days (t = +7.98) and loses its
significance precisely on the days when news arrival is known in advance
(t = +1.57). That ordering is what volatility clustering predicts, not what a
transmission operator predicts.

---

## What this settles

**Settled.** The impact operator is a persistent, forecastable state variable,
distinct from realised and implied volatility (corr with log RV = 0.26), present in
every liquid market tested. A constant-impact model is rejected decisively.

**Not supported.** That the persistence is produced by the discretion distribution of
the holder base. The forced-mass side is flat, the signal that exists is generic
depth and breadth, and the effect disappears on scheduled events.

**Still open.** The absorption stack the theory actually specifies — COMEX registered
vs eligible, LBMA vault holdings, Bank of England custody, Swiss customs — could not
be built: [both primary sources are now blocked](#data-sources). The one half of the
framework showing signal was tested only through its weakest available proxies.

---

## Reproduce

```bash
make setup      # venv + pinned dependencies
make all        # collect → measure → engine → cot → events → generalize
make test       # calibration: size, power, point-in-time discipline
```

Every result in this README is regenerated from public endpoints. No data is
redistributed. Total cost: $0. Runtime: roughly 15 minutes.

Random seeds are fixed (`20260906`). Outputs land in `out/` as JSON.

---

## Method

Full detail in [docs/METHODS.md](docs/METHODS.md). The three decisions that matter:

**1. Measuring `G`.** In a Kyle framework `r = λ · flow`, so `λ` *is* the conductance.
With daily free data:

```
log G_t  =  log |r_t|  −  α · log v_t
```

where `v_t` is volume normalised by its own trailing 252-day median. `α` is
**estimated, not assumed** (α̂ = 1.032 for gold — close to Amihud's linear
assumption, not the square-root law's 0.5). Using the empirical `α` makes `log G`
orthogonal to `log v` by construction, so no residual persistence can be blamed on
volume. This is verified in [the test suite](tests/test_calibration.py).

**2. The null.** Under the hypothesis that `G` is constant and volume co-moves with
volatility only through information arrival, `log G` is **iid**. That is what makes
this estimator worth using. The null distribution comes from 2,000 iid bootstraps
preserving the exact fat-tailed marginal, with the identical statistic pipeline run
on real and simulated series. Test size and power are checked against synthetic data
with known ground truth.

**3. Point-in-time discipline.** COT is a Tuesday snapshot published Friday 15:30 ET.
Every series stores **both** reference date and release date, and joins use release
date only. No result here uses a COT figure before the day it was published; this is
enforced by a test.

---

## Data sources

All free. Collectors write immutable raw snapshots with provenance attached.

| Source | Role | Status |
|---|---|---|
| CFTC Disaggregated COT, gold `088691` | holder base | 1,056 weeks, 2006–2026 |
| GLD + 9 ETFs (daily OHLCV) | instruments | 2008–2026 |
| LBMA gold PM fix | price | 1968–2026 |
| CBOE GVZ | implied volatility | 2008–2026 |
| Federal Reserve FOMC calendar | event dates | 148 scheduled decisions, 2008–2026 |
| COMEX warehouse stocks | absorption | **403 — bot-blocked** |
| LBMA vault holdings | absorption | **404 — URLs moved** |
| Yahoo `GC=F` volume | instrument | **unusable** — see below |

Two corrections to the original data inventory. The COMEX warehouse file is no longer
a free direct download (403 behind bot protection) and LBMA's vault-holdings URLs now
404. Together these are the entire absorption stack.

Separately, Yahoo's `GC=F` historical *volume* is broken, not merely noisy: median
56–905 contracts per year against a maximum near 200,000, with 41 zero-volume days.
It alternates between the front-month aggregate and a near-dead contract. All
measurement uses GLD, which the theory document independently sanctions.

FOMC dates use **regularly scheduled meetings only**. Unscheduled and emergency
actions happen *because* markets are stressed; including them would manufacture the
exact correlation the event test measures. Exclusion follows the Fed's own labels
("(unscheduled)", "(cancelled)", "Conference Call", "notation vote").

---

## Limitations

- **The absorption stack is missing.** The half of the framework that showed signal
  was tested through proxies (trader count, open interest), not the vault and
  balance-sheet data the theory specifies.
- **Instrument mismatch.** `G` is measured on GLD; `Λ` is built from COMEX futures
  positioning. The two can diverge.
- **Event scope.** FOMC only. CPI and payroll dates were unavailable (BLS returns
  403), and gold may respond more to inflation prints than to policy decisions.
- **Event-type, not surprise-size, is held constant.** The scheduled-event test
  removes the "was there news at all" channel; it does not hold the magnitude of
  each policy surprise fixed.
- **`Λ` is one construction.** Falsifying this `Λ` is not the same as falsifying
  every possible holder-base decomposition — though the per-variable COT diagnostic
  is construction-free and points the same way.
- **A structural break sits inside the sample.** In January 2026 CME moved precious
  metals margin from fixed dollar amounts to a percentage of contract value, changing
  the compulsion mechanism itself.

---

## Repository layout

```
conductance/          pipeline: collect → measure → engine → cot_generic → events → generalize
tests/                calibration: test size, power, estimator recovery, point-in-time
docs/THEORY.md        the original pre-registered theory and kill conditions
docs/METHODS.md       estimator, null construction, regression specifications
docs/RESULTS-run1.md  first run write-up (kill conditions 1–4)
out/                  machine-readable results (JSON)
```

---

## Published site

`site/` is a self-contained GitHub Pages build of the study, with structured data for
search and AI answer engines: `ScholarlyArticle`, `Dataset`, `SoftwareSourceCode` and a
seven-question `FAQPage`, plus `llms.txt`, `robots.txt`, `sitemap.xml` and a social card.

**Live at [codedpro.github.io/market-conductance](https://codedpro.github.io/market-conductance/).**

```bash
make site-check   # validate structured data + SEO surface
```

If you fork this to a different host, `make site-url USER=you REPO=yourrepo`
rewrites every canonical, Open Graph and sitemap URL in one pass.

---

## Citation

See [CITATION.cff](CITATION.cff).

> Project Lambda (2026). *Is market conductance a forecastable state variable?
> A free-data falsification study of the impact operator in gold and nine other
> markets.* https://github.com/codedpro/market-conductance

**Not investment advice.** This is empirical research. Nothing here is a
recommendation to trade any instrument.
