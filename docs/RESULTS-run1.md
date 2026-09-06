# Project Lambda - Test Run 1: results

**Date:** 6 September 2026. **Status:** free-only Track 1 executed end to end.
**Code:** `lambda_proj/` (collect -> measure -> engine). **Outputs:** `out/`.

Companion to `lambda-conductance-project.md`. Numbers below are reproducible
via `collect.py`, `measure.py`, `engine.py`, `cot_generic.py`.

---

## Headline

| Kill condition | Result |
|---|---|
| **4.** Is measured `G` a constant with noise? | **PASSED decisively.** `G` is a real, persistent, forecastable state variable. |
| **1.** Does `Λ` beat realised + implied vol? | **FAILED.** Marginal in-sample, negative out-of-sample, gone once `G`'s own history is controlled for. |
| **2.** Does signed asymmetry produce signed drift? | **FAILED.** Correct sign, no significance (\|t\| ≤ 1.09). |
| **3.** Are big moves independent of `Λ`? | **FAILED.** No monotone relation; high/low quintile ratio 0.68. |

The theory's *foundational* claim survives. The *distinctive* claim - that the
holder-base discretion decomposition is what drives it - does not, on free data.

---

## 1. Data actually collected (section 13)

| Source | Role | Status | Coverage |
|---|---|---|---|
| CFTC Disaggregated COT, gold `088691` | numerator | **OK** | 1,056 weeks, 2006-06-13 → 2026-09-01 |
| GLD (NYSE Arca) daily OHLCV | instrument | **OK** | 5,483 days, 2004-11 → 2026-09 |
| LBMA gold PM fix | price | **OK** | 14,676 days, 1968 → 2026 |
| CBOE GVZ (implied vol) | control | **OK** | 4,594 days, 2008-06 → 2026-09 |
| DXY, 10y yield | control | **OK** | 2001 → 2026 |
| GC=F daily volume | instrument | **UNUSABLE** | see §2 |
| COMEX warehouse stocks | **denominator** | **BLOCKED** 403 (Akamai) | - |
| LBMA vault holdings | **denominator** | **BLOCKED** 404, URLs moved | - |
| FRED CSV | control | rate-limited after ~6 calls | replaced with Yahoo/CBOE |
| WGC Goldhub | denominator | registration required | not attempted |

**Two corrections to section 10's data inventory.** The doc lists the COMEX
warehouse file as a free direct download and LBMA vault holdings as free
monthly. Neither is retrievable today: CME returns 403 behind bot protection,
LBMA's vault-data URLs 404. The absorption stack - the doc's own denominator,
and the "discretion boundary made physical" - could **not** be built.

---

## 2. Yahoo `GC=F` volume is unusable

Median daily volume by year runs 56-905 contracts against a max of ~200,000,
with 41 zero-volume days. The series alternates between the front-month
aggregate and a near-dead contract. Section 13.3 already flagged this feed as
"breaks sometimes"; for historical volume it is broken outright.

All conductance measurement therefore uses **GLD**, which sections 10.3 and
13.3 explicitly sanction. GLD consolidated volume is clean: median 6-15M
shares, no zeros, stable across 19 years.

---

## 3. How `G` was measured

`ΔP = G·ε`. With daily free data, Kyle's `λ` *is* the conductance, so:

```
log G_t = log|r_t| − α · log v_t          v_t = volume / trailing 252d median
```

`α` is estimated, not assumed: **α̂ = 1.032** (R² = 0.176). Gold impact scales
close to *linearly* in volume - Amihud's assumption - not as the square-root
law's 0.5. Results are reported for α̂, 0.5 and 1.0; all three agree.

Using the empirical `α` makes `log G` orthogonal to `log v` by construction, so
no residual persistence can be attributed to volume.

---

## 4. Kill condition 4 - PASSED

**H0:** `G` is constant; all variation in the estimator is noise. Under H0 plus
mixture-of-distributions information arrival, `log G_t` is **iid**.
**Null:** iid bootstrap of the empirical `log G`, preserving the exact
fat-tailed marginal. Identical statistic pipeline on real and simulated series,
2,000 simulations.

Sample: GLD, 2008-03-28 → 2026-09-04, n = 4,640.

| Statistic | Observed | Null mean | Null p99 | p |
|---|---|---|---|---|
| AR(1) | 0.0549 | −0.0003 | 0.0350 | <0.0005 |
| AR(22) | 0.0911 | 0.0004 | 0.0352 | <0.0005 |
| Ljung-Box(22) | **1021.5** | 22.2 | 40.0 | <0.0005 |
| Variance ratio (22d) | 3.11 | 1.00 | 1.23 | <0.0005 |
| Variance ratio (66d) | **6.82** | 1.00 | 1.42 | <0.0005 |
| HAR out-of-sample R² | **+7.29%** | −0.15% | +0.04% | <0.0005 |

Conductance is forecastable from its own history at ~7% OOS R², expanding
window, refit monthly. Variance ratios rising with horizon (1.34 → 3.11 → 6.82)
indicate genuine low-frequency structure, not short-lived noise.

**`G` is not a constant with noise.** Gabaix/Koijen's constant-impact reading is
rejected on this data. And `G` is not merely volatility relabelled:
corr(log G, log RV) = **0.262**, corr(log G, log IV) = **0.242**.

---

## 5. Kill condition 1 (primary) - FAILED

`Λ` built point-in-time from COT (release date, never reference date - §12.1):

```
Λ_down = MM_long  · w(underwater_long)  / absorption
Λ_up   = MM_short · w(underwater_short) / absorption
absorption = OI · breadth · (1 − top-4 concentration)
```

Trigger distance uses a cost-basis tracker (weighted-average entry price that
moves only when a position is added to), scaled to a ~monthly vol horizon.

Target: mean `log G` over t+1..t+h. HAC (Newey-West) standard errors.

| Horizon | vs RV+IV: incr. R² | Λ t-stat | ΔOOS R² | vs RV+IV+HAR(G): Λ t-stat | ΔOOS R² |
|---|---|---|---|---|---|
| 1d | +0.0020 | +2.79 | **−0.0045** | +1.15 | **−0.0040** |
| 5d | +0.0068 | +2.86 | **−0.0099** | +1.39 | **−0.0122** |
| 22d | +0.0102 | +2.33 | +0.0066 | +1.58 | **−0.0041** |

`Λ` is marginally significant in-sample against the doc's stated benchmark, but
**out-of-sample R² falls in 5 of 6 specifications**, and significance vanishes
once conductance's own history is included. corr(log Λ, log G) = **0.014**.

Λ is essentially orthogonal to the thing it was built to forecast.

> Note: an earlier version of `Λ` was degenerate - trigger distance was divided
> by *daily* vol (~1%) while positions sit ~10% from basis, saturating the
> logistic to exactly 0/1 and making `Λ` a binary switch (`Λ_asym` ranged ±20).
> Fixed to a monthly vol scale before the numbers above. Both versions fail.

---

## 6. Kill conditions 2 and 3 - FAILED

**KC2, signed drift.** Regressing forward returns on `log(Λ_down/Λ_up)`:

| Horizon | coef | t | p |
|---|---|---|---|
| 1d | −0.00009 | −0.63 | 0.53 |
| 5d | −0.00038 | −0.62 | 0.53 |
| 22d | −0.00230 | −1.09 | 0.28 |

Signs are consistently negative - the direction the theory predicts, since
stressed longs should make the market conduct better downward - but nothing is
close to significant. No directional edge.

**KC3, big moves by Λ quintile.** P(2σ move in next 5 days):

| Λ quintile | Q1 (low) | Q2 | Q3 | Q4 | Q5 (high) |
|---|---|---|---|---|---|
| P(big move) | 0.320 | 0.206 | 0.238 | 0.238 | 0.219 |

Non-monotone, and the *highest* Λ quintile has *fewer* big moves than the
lowest (ratio 0.68). Section 6.3's condition - "if large moves occur with Λ low
as often as with Λ high, the primitive is wrong" - is met.

---

## 7. The most useful result: which half of the theory survives

To separate "my Λ is badly built" from "COT carries no signal", every raw COT
variable was tested individually against the strict RV+IV+HAR(G) benchmark.

**Numerator variables (forced mass) - the theory's distinctive claim:**

| Variable | t (5d) | t (22d) |
|---|---|---|
| MM long / OI | −0.90 | −1.17 |
| MM short / OI | +0.31 | +0.99 |
| MM net / OI | −0.64 | −1.18 |
| MM gross / OI | −0.70 | −0.04 |
| Δ MM net (5d) | +0.08 | −0.25 |
| Swap dealer short / OI | −0.46 | −0.49 |
| Producer short / OI | +0.03 | −0.41 |

Nothing. Managed Money positioning - the doc's proxy for margin-sensitive,
least-discretionary capital - does not forecast conductance at any horizon.

**Denominator variables (absorption):**

| Variable | t (5d) | t (22d) | ΔOOS R² (22d) |
|---|---|---|---|
| Trader count (breadth) | **−3.33** | **−3.18** | **+0.0079** |
| log Open Interest (depth) | **−2.78** | **−2.88** | **+0.0046** |

Both significant, both **negative** - more breadth and more depth means *lower*
conductance - and both survive out-of-sample at 22 days. That is precisely the
denominator logic of section 3, and it matches section 4.1's own prediction
that "Λ should move on the absorption side first".

All 12 COT variables jointly: in-sample incremental R² +0.013/+0.020, but ΔOOS
R² −0.047/−0.052. Overfitting.

---

## 8. What this does and does not settle

**Settled.** Conductance is a genuine state variable, distinct from realised and
implied volatility, forecastable at ~7% OOS R² from its own history. The
foundational question of section 6.4 - answer it first, before risking capital -
is answered, and answered in the theory's favour.

**Not settled, and the honest caveat.** Rejecting "constant `G`" is not the same
as proving the persistence *is* conductance in the doc's sense. Persistent
`|ε|` - clustered news - would produce the same signature. The doc assumes news
is iid (§1, "news is genuinely random"); that assumption is doing real work and
is not itself tested here. The clean way to discriminate is exactly kill
condition 1: show `G` is forecastable from *structural* holder data, which is
not news. That test failed.

**Not a fair test of the theory.** The absorption stack the doc actually
specifies - COMEX registered vs eligible, LBMA vaults, Bank of England custody,
Swiss customs - is entirely absent, because the two primary sources are now
blocked. The signal that *did* appear came from the two weakest absorption
proxies available (trader count, open interest). That is the opposite of a
discouraging result for the denominator.

---

## 9. Recommended next step

The evidence points one way: **the denominator is carrying the signal and the
numerator is not.** That inverts the build priority in section 14.

1. Solve the absorption data problem first. COMEX warehouse stocks and LBMA
   vault holdings are the gap; both need a route that is not a bare HTTP GET.
2. Re-test with a real absorption stack before spending anything on the
   numerator, and before buying options OI history (section 10.1's "biggest
   paid gap") - which is numerator data, the half currently showing nothing.
3. Start the forward collector now regardless (section 12.2): every day of
   delay is unrecoverable history.
4. Per section 16, this negative result on KC1/2/3 and positive result on KC4
   is worth writing up either way.
