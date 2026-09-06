# Project Lambda: Market Conductance as a Forecastable State Variable

**Status:** pre-build, theory defined, data inventory complete, nothing collected yet.
**Document date:** 6 September 2026.
**Purpose:** complete handoff. A fresh session should be able to resume from this file alone.

---

## 0. Read this first

This is not a gold prediction project. It is an attempt to forecast the *operator* that converts news into price movement, rather than forecasting price or news. Gold is the first laboratory because its holder base is unusually well documented, not because gold is economically special.

If a future session finds itself asking "what variables predict gold" or "which model architecture", it has lost the thread. The target is not the price. The target is the conductance.

---

## 1. The core reframe

Write price change as:

```
ΔP = G(t) · ε
```

Where `ε` is the shock (news, surprise, information) and `G(t)` is the market's conductance, the impact operator that converts shock into price movement.

Everyone forecasts `ΔP`. Almost nobody forecasts `G`.

Existing approaches either:
- treat `G` as a constant (beta, elasticity, a fixed multiplier), or
- back it out of realised returns after the fact, which conflates it with `ε` and locks the analysis into looking backwards.

Implied volatility is a partial exception, but it is an opinion carrying a risk premium, not a measurement of structure.

**Central claim:** `G` is far more forecastable than `ε`, and it is forecastable from documents and holdings rather than from returns. News is genuinely random. Conductance is not. It is made of who holds the asset, what forces their hand, when, and who is left standing to absorb them.

---

## 2. The primitive: discretion

Forget sentiment, positioning and flow. Those are records of decisions that already happened.

Every unit of capital sits somewhere on a spectrum:

- **Fully discretionary:** the holder can buy, sell, hold or do nothing. Nobody makes them act.
- **Fully non-discretionary:** a rule, mandate, margin threshold, maturity, index reconstitution or regulation forces an action, on a known date, at a size the holder does not control, regardless of their opinion.

Price is set by the marginal transaction. The marginal transaction is disproportionately made by the *least discretionary* holder in the system.

**Consequence:** price discovery is not opinion aggregation. It is the sound of constraints binding.

The object worth measuring is therefore the **discretion distribution of the holder base, plus its forward schedule of compulsion.** Both are largely documented, and both are knowable in advance.

---

## 3. The state variable

```
Λ(t, h) = (mass of capital facing a forced decision within horizon h)
          / (mass of capital able and willing to absorb it)
```

**Numerator (forced mass)** comes from trigger proximity: margin thresholds, option strikes with dealer hedging obligations, roll dates, redemption windows, quarter ends, mandate breach levels, maturity walls. Dated, published, mostly public.

**Denominator (absorption)** is slow moving and comes from plumbing: dealer balance sheet capacity, free float, lease market depth, deliverable inventory.

Λ is dimensionless. It is the conductance forecast. High Λ means small shocks produce large price moves. Low Λ means the market absorbs news and shrugs.

### 3.1 The part that makes it tradeable

Λ has a **sign**. Up-conductance and down-conductance are not the same number, and the asymmetry is set by *which side* is constrained.

If forced mass sits overwhelmingly on one side, a symmetric shock distribution produces a **drifted price distribution**. That yields a directional edge without ever forming a macro view. You never predict the news. You predict which direction the market conducts better.

This signed asymmetry, computed across a full holder base, is the piece not currently done anywhere as far as could be established.

---

## 4. Why gold is the right first laboratory

Gold's holder base is documentable in a way equities never are:

| Holder class | Discretion at short horizon | Data |
|---|---|---|
| Central bank reserves | Near zero (political, not price, decisions) | Monthly/quarterly, IMF IFS via WGC |
| ETF holders | Semi-discretionary | Daily per fund |
| Managed money futures | Low near margin thresholds | Weekly CFTC COT |
| Bullion banks / swap dealers | Constrained by balance sheet | Weekly COT, monthly BPR, quarterly OCC |
| Mining hedge books | Contractually forced | Quarterly |
| Jewellery / India | Seasonal, duty-sensitive | Monthly trade data |
| COMEX registered stock | Committed by definition | Daily |

The registered vs eligible split in COMEX vaults is a **discretion boundary made physical**: registered is committed metal, eligible is optional metal, and the conversion between them is a documented, timestamped decision. No other market has this.

### 4.1 The leading indicator claim

Λ should move before price, and it should move on the **absorption side first**, because plumbing degrades quietly.

Concrete, dated, falsifiable version:
- Registered COMEX stock falling while open interest holds flat is Λ rising with zero price signal.
- Lease rates and the EFP spread are the price of the constraint itself, and should widen before spot does anything interesting.

---

## 5. Candidates generated and killed

Do not re-propose these. They were considered and rejected, with reasons.

| Candidate | Claim | Why killed |
|---|---|---|
| Belief divergence topology | Persistent homology of the belief manifold | Hong-Stein disagreement with a technique bolted on. Unmeasurable without assuming the thing you want to measure. |
| Reversibility fields | Characterise the economy by distribution of undo-costs across committed capital | Dixit-Pindyck real options already owns irreversibility. Aggregation step adds no falsifiable content. Gold is genuinely singular in it (max reversible to hold, max irreversible to produce) but that is a description, not a prediction. |
| Commitment clocks | Reparameterise time by cumulative irreversible commitment instead of chronology | Volume clocks and volatility clocks already exist. A variant, not a primitive. Folded in as a possible subcomponent of Λ. |
| Optionality inventory | World stock of unexercised choices; crisis as its collapse | Poetic, unmeasurable, mostly the rehypothecation story in better clothes. |
| Synchronisation of expectations | Kuramoto oscillators for markets | Econophysics has run this for twenty five years without producing a falsifiable claim. |

### 5.1 The parallel thread: Σ, settlement substitution

An earlier and separate idea, not merged into Λ, retained because it may be the better *macro* companion to Λ's *micro*.

Define a settlement substitution matrix **S(t)** where `S_ij` is the degree to which asset *i* can discharge an obligation denominated in or collateralised by asset *j*. Not correlation: permission and practice. Repo haircuts, CCP eligible collateral schedules, central bank swap lines, convertibility, custody law, correspondent banking reach, HQLA and NSFR treatment.

Take the effective dimension via spectral entropy:

```
Σ(t) = exp( −Σ_k λ̃_k log λ̃_k )   over normalised eigenvalues of S
```

Σ is the number of genuinely independent ways the world can settle obligations. Under stress, edges are **deleted, not reweighted**. The graph fragments. Σ collapses toward 1.

**Conjectured law:** an asset's monetary premium is proportional to its centrality in S divided by Σ. Gold is singular because every entry in its row is unconditional on a counterparty, so edge deletions elsewhere cannot reduce its centrality.

```
d(gold monetary premium)/dt ∝ −dΣ/dt
```

Two things it explains that standard models are embarrassed by:
1. Gold is a famously poor inflation hedge over most horizons. Under Σ this is a prediction, not an anomaly: inflation does not delete edges, it reprices along existing ones.
2. 2022 to 2024, real rates rose and gold rose with them. Under Σ this is clean confirmation: freezing a G20 central bank's reserves was a mass edge deletion, and every other node recomputed its own edge fragility. No macro variable had to move.

**Status:** parked, not killed. Weaknesses are endogeneity (regulators change rules because prices moved) and thin N (major feasible-set events are rare, defence is to go granular across CCP haircut revisions, collateral eligibility updates, index rule changes). Honest novelty grade: segmented-markets theory taken seriously, made dynamic, and made measurable from primary documents. A real move, not new physics.

Λ was chosen over Σ as the primary because Λ is testable now with free data and Σ is not.

---

## 6. Kill conditions

Run these before building anything elaborate.

1. **If Λ has no incremental explanatory power over realised vol and implied vol, the theory is dead.** This is the primary test.
2. **If conductance asymmetry does not produce signed drift**, the directional claim collapses and this is a risk model wearing a hat, not an alpha model.
3. **If large moves occur with Λ low as often as with Λ high**, the primitive is wrong.
4. **The one that really ends it:** if measured `G` turns out to be a stable constant with noise rather than a state variable, then Gabaix and Koijen were already right and there is nothing to add. **Answer this question first, from the historical archive, before risking any capital.**

### 6.1 Generalisation test (matters more than the gold result)

Λ and Σ should say something about markets other than gold: reserve currency share shifts, which currencies gain safe-haven bid, why Treasuries lost some premium after 2022, bitcoin's beta to sanctions events specifically rather than to risk-off generally.

If it only works on gold, it is a gold story dressed as a law and should be discarded.

---

## 7. Honest novelty grade

Pieces of this exist. Dealer gamma models for equity indices. CTA flow estimation. Inelastic markets (Gabaix, Koijen). Brunnermeier and Pedersen on margin spirals. Bullion desks already watch EFP and lease rates.

What does not appear to exist: a unified, ex-ante, dated conductance curve built from a full holder-base discretion decomposition, with **signed asymmetry** as the output, treating the impact operator rather than the price as the forecast target.

**Riskiest assumption:** that discretion weights are stable enough to estimate. If holders' constraints are themselves reflexive and reshuffle under stress, Λ becomes unmeasurable exactly when it matters most. Test this first.

---

## 8. Ideal system output

Not a price forecast. A **conductance print**. Four numbers, daily:

1. **Λ(h)** for h = 1 day, 1 week, 1 month. Dimensionless.
2. **Sign.** Up-conductance and down-conductance as two separate numbers, never one.
3. **Impact multiplier.** Expected move per unit of shock, quoted both directions.
4. **Trigger calendar.** Dated map of forced decisions 90 days forward: roll dates, expiries, margin thresholds by distance, redemption windows, quarter ends.

The call it produces reads like:

> Over the next five days gold conducts 2.3x better down than up.

Never:

> Gold will fall.

You trade that through sizing, skew and option structure, not directional guesses. You never need to know what the news will be.

### 8.1 Flow

```
raw timestamped snapshots
  → holder base table (mass, discretion weight, trigger distance, trigger date)
  → forced mass curve by horizon
  → absorption stack
  → signed Λ
  → impact multiplier
  → position rules
```

### 8.2 Two design rules that keep it honest

**Most days it should print nothing.** If Λ is flat and symmetric, the system says flat and symmetric. A system that finds a signal every day is fitting noise.

**Keep a residual log.** Every day Λ was high and nothing happened. Every day Λ was low and something big did. That log either kills the theory or turns it into something real. It is the part most people skip and it is the most valuable output long term.

---

## 9. Realistic profitability assessment

Written down so a future session does not talk itself into optimism.

**Best case, and it is modest.** A persistent edge showing up mostly in risk management, not directional calls:
- Sizing: more when conductance is low, less when high. Improves risk-adjusted returns without predicting anything.
- Skew and options: if up and down conductance genuinely differ and options are not priced for it, sell the overpriced side. **This is where the actual money would be.**
- Avoiding the worst days: not being in size when Λ is extreme.

**Why it probably earns less than the theory suggests:**
- Λ high says moves will be large. It does not say when the shock arrives. You can sit in a high-conductance state for weeks earning nothing while paying to hold.
- Margin-driven forced mass is an hours-to-days phenomenon. Vault and balance sheet data is monthly to quarterly. The timescales do not line up, and the fast layer is the expensive part.
- Options market makers already price some of this. Your edge is only the residual.
- **The January 2026 CME percentage-margin change removes the discrete step-function that created the sharpest historical forced-selling cascades.** The mechanism the theory leans on just got softer.

**Outcome distribution:**
- *Most likely:* works as a conditioning layer. Improves an existing gold book's Sharpe somewhat. Not a business on its own.
- *Possible:* asymmetry signal is real and tradeable in options. A genuine strategy, capacity-limited, a few good trades a year rather than continuous income.
- *Also possible, hold seriously:* Λ has no incremental power over implied vol and it dies at kill condition 1. That is not a bad outcome. It costs a data bill and a few months, and it settles a real question.

---

## 10. Data inventory

Organised by role in the framework, not by provider.

### 10.1 Numerator: forced mass

| Source | Cost | Frequency | History | Notes |
|---|---|---|---|---|
| **CFTC Commitments of Traders (disaggregated)** | Free | Weekly | Legacy from Jan 1986; disaggregated and TFF from Jun 2006 | Socrata API at `publicreporting.cftc.gov`, no key. Tuesday snapshot, Friday release: **3-day information lag**. Managed Money is closest proxy for margin-sensitive holders. |
| **CFTC Bank Participation Report** | Free | Monthly | Long | First Tuesday data, published first Friday after 3:30 ET. Splits US vs non-US bank gross long/short. The bullion bank leg. |
| **CFTC Cleared Margin Report** | Free | Monthly | Cumulative from Dec 2013 | PDF and Excel. Aggregate initial margin by DCO including CME. Updated within 10 business days of month end. Not gold-specific but the only public read on total margin capital at CME. |
| **CME margin schedule** | Free | Event | PDFs from 2003 to present | Announced via Clearing advisory service. Scrapeable from the notices archive. |
| **Options OI by strike (COMEX gold)** | **Paid** | Daily | 40 years via DataMine | Current-day reports free (Daily Volume and OI Report is preliminary; official data in next morning's Daily Bulletin). History is behind CME DataMine or Barchart. **Biggest paid gap in the build.** |

### 10.2 Denominator: absorption capacity

| Source | Cost | Frequency | History | Notes |
|---|---|---|---|---|
| **COMEX warehouse stocks** | Free | Daily | Long | Direct file: `cmegroup.com/delivery_reports/Gold_Stocks.xls`. Per depository, registered vs eligible. The discretion boundary made physical. |
| **LBMA London vault holdings** | Free | Monthly | From Jul 2016 | Seven custodians plus Bank of England. Originally 3 months in arrears; gold now published on the fifth business day of the following month. |
| **LBMA clearing statistics** | Free | Monthly | Continuous since Oct 1996 | Net clearing volume and value. |
| **Bank of England gold custody** | Free | Monthly | From 2017 | Separate spreadsheet from LBMA data. |
| **OCC Quarterly Report on Bank Trading and Derivatives** | Free | Quarterly | Long | PDF plus XML. **Table 21** gives precious metals notional by maturity for top banks. |
| **Swiss customs (SwissImpex)** | Free | Monthly | By country from 2012 | Gold in raw form under tariff heading **7108.1200**. Origin subdivisions added from 1 Jan 2021. Physical relocation is the slowest and most binding constraint. |
| **SGE / SHFE** | Free | Weekly + daily | Long | SGE weekly delivery volumes and vault inventory published each Monday. Benchmark AM/PM fixings from auction results. Chinese-language source. WGC mirrors some with lag. |
| **World Gold Council Goldhub** | Free (registration) | Weekly/monthly/quarterly | Long | ETF holdings and flows, central bank reserves via IMF IFS, mine production, AISC, above-ground stock, open interest across nine global gold exchanges. |

### 10.3 Paid or missing, with workarounds

| Item | Situation | Workaround |
|---|---|---|
| **Lease rates** | GOFO discontinued after **30 January 2015**. Forward rates now quoted bilaterally by dealers, not public. | Synthesise implied lease rate from COMEX futures curve against SOFR. **Validate against real GOFO 1989 to 2015 on Nasdaq Data Link (LBMA/GOFO) before trusting the post-2015 synthetic.** |
| **LBMA Trade Data** | Covers spot, swap/forward, options and **lease/loan/deposit (LLD)**, daily T+1 and weekly. Distributed via Bloomberg Terminal, B-PIPE and Refinitiv Eikon. | Nasdaq publishes a free weekly summary. Not a substitute for the LLD series. |
| **EFP spread** | No official free series. | Reconstruct as front-month GC settlement minus LBMA PM fix, carry-adjusted. Both legs free and daily. Validation: EFP blew out to roughly $50/oz in the Dec 2024 to Feb 2025 tariff episode, and a record 151 tonnes left London for New York in January 2025 alone. An event that size shows in the synthetic without ambiguity. |
| **COMEX gold options OI by strike, history** | Paid. | **Use GLD listed options instead.** Equity options chains including OI by strike are free from public sources. GLD is large, liquid, physically backed. Weaker instrument than COMEX gold options and the two can diverge, but it is free and archivable from today. |
| **Mining hedge books** | Metals Focus / Société Générale Global Hedge Book Analysis. **Free availability not confirmed.** | Scrape producer quarterlies. Slow but free. |

---

## 11. Known structural breaks

Every one of these will corrupt a naive regression. Handle explicitly.

| Date | Break | Consequence |
|---|---|---|
| **30 Jan 2015** | GOFO discontinued | Lease rate series ends. Post-2015 must be synthetic. |
| **Jul 2016** | LBMA vault data series begins | Full-stack Λ cannot be built before this date. |
| **1 Jan 2021** | Swiss customs adds gold origin subdivisions | Series composition change. |
| **1 Jan 2022** | SA-CCR: gold derivatives reclassified from exchange rate contracts to precious metals contracts | **Inflates reported precious metals notional in the OCC report versus prior quarters.** Not a real increase in exposure. |
| **13 Jan 2026** | CME switches precious metals margin from fixed dollar to **percentage of contract value**. COMEX 100 gold set at 5%, silver and platinum 9%, palladium 11%. | **The compulsion mechanism itself changed.** Margin now auto-scales with price instead of stepping discretely after volatility. Pre-2026 and post-2026 Λ are not the same variable. Also a live natural experiment for the theory. |

---

## 12. Two things that will break a naive build

### 12.1 Point-in-time discipline

The numerator is mostly lagged (COT 3 days, LBMA vaults ~5 business days, OCC ~60 days, Swiss customs ~3 weeks) while the denominator has a daily component.

**If you timestamp by reference date instead of release date, you will produce a backtest that looks brilliant and means nothing.**

Every series must store **both** dates from day one: reference date and release date. Non-negotiable.

### 12.2 The archive problem

Options OI by strike, the CME Daily Bulletin, and CME advisories are cheap or free going forward and expensive or gone backwards.

**Every day of delay is a day of history that must later be bought or lost.** The collector should start before anything else is built. Raw snapshots are cheap to store and cheap to reinterpret later.

---

## 13. Free-only architecture

Decision taken: build the free version first.

### 13.1 What survives intact

The **entire denominator**. Every absorption source above is free.

Most of the **slow numerator**: COT, Bank Participation, Cleared Margin, CME margin advisories.

Therefore: **the slow Λ is fully backtestable today, for free.** Full stack back to July 2016 (LBMA vault data start), COT-only version back to 2006. That tests the theory's core claim at zero cost.

### 13.2 What free real-time actually buys

This is better than the paid version in one specific way.

With paid position data you **infer** forced flow from where positions sit relative to triggers. With free real-time volume you **observe** it directly, because compulsion has a timestamp signature that discretion does not.

A discretionary trader can trade at any hour. A forced trader trades in a specific window:

- London AM and PM fix windows
- COMEX close
- Margin settlement cycles
- Roll windows and first notice day
- Option expiry
- Month and quarter end
- Asia and Europe handoffs

**Fast Λ = volume concentration inside compulsion windows, measured against that same window's own historical baseline.** Needs only timestamp plus volume. Both free. Observation instead of inference.

### 13.3 Free real-time sources, practically

| Source | What it gives | Caveats |
|---|---|---|
| **Broker API (e.g. IBKR)** | Real-time GC futures with volume | The practical answer. CME non-professional real-time runs a couple of dollars a month, effectively free. **Verify current fees, they change.** |
| **Yahoo Finance GC=F** | ~10-minute delayed with volume | Free, unofficial, breaks sometimes. |
| **GLD on NYSE Arca** | Volume plus the free options chain | Easier free data than futures, same underlying. |
| **PAXG on major crypto exchanges** | Genuinely free real-time full-depth order book, 24/7, no account | Thin, not the real market. **Stress detector only, never a primary feed.** |
| **Stooq** | Free EOD history | Backup. |

### 13.4 Latency does not matter here

Λ moves over days and weeks. It is a state variable, not a microstructure signal. Ten-minute delayed data costs almost nothing.

**If a future session finds itself needing sub-second data, the theory has quietly turned into something else. Stop and re-read section 2.**

### 13.5 The one paid thing worth breaking the rule for

If the fast track looks promising: buy a **targeted slice** of CME historical tick or MBP data for gold. Not years. Roughly 40 event days is enough to test whether compulsion windows behave as claimed. Pay-per-slice vendors make that cheap. Everything else stays free.

---

## 14. Build order

Four layers, nothing exotic:

1. **Collectors.** One per source. Each writes raw immutable snapshots with **both** reference and release timestamps. Tiers: daily, weekly, monthly, event (advisories).
2. **Normaliser.** Into a single holder-base table: holder class, estimated mass, discretion weight, trigger distance, trigger date.
3. **Λ engine.** Forced mass over absorption, by horizon, signed by side.
4. **Test harness.** Runs the kill conditions against realised and implied vol. **Never against price alone.**

### 14.1 Two tracks, running in parallel

**Track 1: slow Λ.** Backtestable now, free. Answers the load-bearing question (kill condition 4: is conductance a state variable or a constant with noise). Costs nothing but time.

**Track 2: fast Λ.** No free history exists, so it is collect-forward only. Paper run for six to twelve months before it says anything.

Start both now. **Track 1 tells you whether Track 2 is worth finishing.**

### 14.2 Frequency tiers for the collector

- **Daily:** COMEX warehouse stocks, CME daily settlements + volume + OI, CME Daily Bulletin (OI by strike, current only), GLD/IAU holdings from issuer sites, LBMA gold price AM/PM, SGE daily prices and OI, SHFE, GLD options chain.
- **Weekly:** CFTC COT, SGE weekly delivery and withdrawals, WGC ETF weekly, LBMA trade data weekly summary via Nasdaq.
- **Monthly:** LBMA vault holdings, BoE gold custody, CFTC Bank Participation, CFTC Cleared Margin, SwissImpex, WGC central bank reserves / IMF IFS.
- **Quarterly:** OCC derivatives report, WGC Gold Demand Trends, mining hedge books, producer filings.
- **Event-driven:** CME clearing advisories (margin changes), rule changes, sanctions orders.

### 14.3 Immediate next decision

Whether to start the collector immediately against a thin schema, or spec the holder-base table properly first and lose a few weeks of history.

**Recommendation: start collecting first.** Raw snapshots are cheap to store and reinterpret. Lost days are not recoverable.

---

## 15. Control variables for the tests

Λ must beat these, not merely correlate with them:

- Real rates (10y TIPS)
- DXY
- CPI surprises
- ETF flows
- Realised volatility
- **Implied volatility (GVZ, CME CVOL)** ← the hardest hurdle, and the one that matters

---

## 16. Standard of success

Not: "this could improve a trading bot."

The standard is: **if this were validated, researchers might have to describe part of market behaviour differently.**

A negative result that cleanly settles kill condition 4 is a good outcome and should be written up, not buried.
