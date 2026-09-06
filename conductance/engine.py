"""
Project Lambda - Layers 2/3/4: holder-base table -> signed Lambda -> kill conditions 1/2/3

POINT-IN-TIME DISCIPLINE (section 12.1, non-negotiable):
on trading day d we may only use COT rows whose RELEASE date <= d.
COT reference is Tuesday, released Friday 15:30 ET => a 3-day information lag.
"""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))

import json, pathlib, numpy as np, pandas as pd
import statsmodels.api as sm
from measure import load, build_panel, impact_exponent, conductance

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT  = ROOT / "out"
RNG  = np.random.default_rng(20260906)


# ------------------------------------------------- holder base (section 14.2)
def cost_basis(price, size):
    """Weighted-average entry price of an open position: basis moves toward the
    current price only when the position is ADDED to. Gives trigger distance."""
    b = np.full(len(price), np.nan)
    cur, held = np.nan, 0.0
    for i in range(len(price)):
        s, p = size[i], price[i]
        if not np.isfinite(s) or not np.isfinite(p):
            b[i] = cur; continue
        if not np.isfinite(cur) or held <= 0:
            cur, held = p, max(s, 0.0)
        elif s > held:                              # adding -> blend in new price
            cur = (cur * held + p * (s - held)) / s
            held = s
        else:                                       # trimming -> basis unchanged
            held = s
        b[i] = cur
    return b


def holder_base():
    """Normalise COT into the holder-base table of section 8.1."""
    cot, _ = load("cot_gold_088691")
    num = [c for c in cot.columns if c not in ("reference_date", "release_date",
                                               "report_date_as_yyyy_mm_dd")]
    for c in num:
        cot[c] = pd.to_numeric(cot[c], errors="coerce")
    cot = cot.sort_values("reference_date").reset_index(drop=True)

    h = pd.DataFrame({
        "reference_date": cot["reference_date"],
        "release_date":   cot["release_date"],
        "oi":             cot["open_interest_all"],
        # Managed Money: the margin-sensitive, least-discretionary fast holder
        "mm_long":        cot["m_money_positions_long_all"],
        "mm_short":       cot["m_money_positions_short_all"],
        # Swap dealers + producers: the natural absorbers (balance sheet / hedging)
        "swap_long":      cot["swap_positions_long_all"],
        "swap_short":     cot["swap__positions_short_all"],
        "prod_long":      cot["prod_merc_positions_long"],
        "prod_short":     cot["prod_merc_positions_short"],
        "traders":        cot["traders_tot_all"],
        "conc_long":      cot["conc_gross_le_4_tdr_long"],
        "conc_short":     cot["conc_gross_le_4_tdr_short"],
    })
    return h


def build_lambda(px, h_tbl, stress_scale=1.0):
    """Signed Lambda (section 3.1). Two numbers, never one.

      Lambda_down = forced LONG mass (must sell) / absorption
      Lambda_up   = forced SHORT mass (must buy) / absorption

    Forced mass = position size * a logistic weight on how far the position is
    underwater, measured in units of its own realised volatility (trigger
    distance). Absorption = open interest scaled by breadth of the trader base
    and the inverse of top-4 concentration.
    """
    # --- align COT to trading days by RELEASE date (point-in-time) ---
    h = h_tbl.sort_values("release_date").copy()
    px = px.copy()
    px["sigma"] = px["r"].rolling(66, min_periods=20).std()

    # weekly price at COT reference date, for the cost-basis tracker
    ref_px = px["close"].reindex(h["reference_date"], method="ffill").to_numpy()
    h["basis_long"]  = cost_basis(ref_px, h["mm_long"].to_numpy())
    h["basis_short"] = cost_basis(ref_px, h["mm_short"].to_numpy())

    # absorption: depth x breadth x (1 - concentration)
    breadth = h["traders"] / h["traders"].rolling(52, min_periods=13).median()
    conc    = ((h["conc_long"] + h["conc_short"]) / 200.0).clip(0.05, 0.95)
    h["absorb"] = h["oi"] * breadth * (1.0 - conc)

    # as-of merge onto daily grid, keyed on RELEASE date -> no lookahead
    daily = pd.merge_asof(
        px.reset_index().rename(columns={"reference_date": "date"}).sort_values("date"),
        h[["release_date", "mm_long", "mm_short", "basis_long", "basis_short",
           "absorb", "oi"]].sort_values("release_date"),
        left_on="date", right_on="release_date", direction="backward")
    daily = daily.set_index("date")

    # Trigger distance must be measured against the MARGIN BUFFER, not daily vol.
    # sigma is daily (~1%); positions sit ~10% from basis, so dividing by daily
    # sigma saturates the logistic to exactly 0/1 and Lambda becomes a binary
    # switch. Scale to a ~monthly horizon (sqrt(22)*daily ~ 4.7%), which is also
    # the order of the CME gold margin rate (5% from Jan 2026, section 11).
    sig = (daily["sigma"] * np.sqrt(22)).replace(0, np.nan)
    under_long  = (np.log(daily["basis_long"]  / daily["close"])) / sig   # long hurts as price falls
    under_short = (np.log(daily["close"] / daily["basis_short"])) / sig   # short hurts as price rises
    w_long  = 1.0 / (1.0 + np.exp(-under_long  * stress_scale))
    w_short = 1.0 / (1.0 + np.exp(-under_short * stress_scale))

    daily["forced_down"] = daily["mm_long"]  * w_long     # longs forced to sell
    daily["forced_up"]   = daily["mm_short"] * w_short    # shorts forced to buy
    daily["lam_down"] = daily["forced_down"] / daily["absorb"]
    daily["lam_up"]   = daily["forced_up"]   / daily["absorb"]
    daily["lam"]      = daily["lam_down"] + daily["lam_up"]
    daily["lam_asym"] = np.log(daily["lam_down"].clip(lower=1e-9) /
                               daily["lam_up"].clip(lower=1e-9))
    return daily


# ------------------------------------------------------------ test utilities
def oos_r2(y, X, min_train=750, refit=21):
    """Expanding-window OOS R^2 vs the expanding-mean benchmark."""
    y = np.asarray(y, float); X = np.asarray(X, float)
    n = len(y); Xd = np.column_stack([np.ones(n), X])
    se_m, se_b, b = [], [], None
    for t in range(min_train, n):
        if (t - min_train) % refit == 0:
            b, *_ = np.linalg.lstsq(Xd[:t], y[:t], rcond=None)
        se_m.append((y[t] - Xd[t] @ b) ** 2)
        se_b.append((y[t] - y[:t].mean()) ** 2)
    if not se_m:
        return np.nan
    return 1 - np.sum(se_m) / np.sum(se_b)


def hac_ols(y, X, names, lags):
    Xd = sm.add_constant(np.asarray(X, float))
    m = sm.OLS(np.asarray(y, float), Xd).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    return {n: {"coef": float(m.params[i + 1]), "t": float(m.tvalues[i + 1]),
                "p": float(m.pvalues[i + 1])} for i, n in enumerate(names)}, float(m.rsquared)


# ------------------------------------------------------------------- KC 1/2/3
def assemble(alpha):
    px = build_panel()
    daily = build_lambda(px, holder_base())

    gvz, _ = load("gvz")
    gvz = gvz.set_index("reference_date")["close"].astype(float).sort_index()

    d = daily.copy()
    d["logG"] = conductance(d["r"].to_numpy(), d["v"].to_numpy(), alpha)
    d["rv"]   = d["r"].rolling(22, min_periods=15).std()          # realised vol
    d["iv"]   = gvz.reindex(d.index).ffill(limit=5)               # implied vol (section 15)
    d["log_rv"], d["log_iv"] = np.log(d["rv"]), np.log(d["iv"])
    d["log_lam"] = np.log(d["lam"].clip(lower=1e-12))
    # HAR terms on measured conductance itself (a stricter benchmark than the doc asks)
    d["g_d"] = d["logG"].shift(1)
    d["g_w"] = d["logG"].shift(1).rolling(5).mean()
    d["g_m"] = d["logG"].shift(1).rolling(22).mean()
    return d


def kc1(d, horizons=(1, 5, 22)):
    """PRIMARY TEST (section 6.1): does Lambda add explanatory power for FUTURE
    conductance over realised vol and implied vol?"""
    res = {}
    for h in horizons:
        tgt = d["logG"].shift(-1).rolling(h).mean().shift(-(h - 1))   # mean logG over t+1..t+h
        cols = ["log_rv", "log_iv", "log_lam", "g_d", "g_w", "g_m"]
        sub = pd.concat([tgt.rename("y"), d[cols]], axis=1).dropna()
        y = sub["y"].to_numpy()
        base_v   = sub[["log_rv", "log_iv"]].to_numpy()
        full_v   = sub[["log_rv", "log_iv", "log_lam"]].to_numpy()
        base_har = sub[["log_rv", "log_iv", "g_d", "g_w", "g_m"]].to_numpy()
        full_har = sub[["log_rv", "log_iv", "g_d", "g_w", "g_m", "log_lam"]].to_numpy()

        stats, r2_full = hac_ols(y, full_v, ["log_rv", "log_iv", "log_lam"], lags=max(h * 2, 10))
        _,     r2_base = hac_ols(y, base_v, ["log_rv", "log_iv"], lags=max(h * 2, 10))
        stats_h, r2_fh = hac_ols(y, full_har,
                                 ["log_rv", "log_iv", "g_d", "g_w", "g_m", "log_lam"],
                                 lags=max(h * 2, 10))
        _, r2_bh = hac_ols(y, base_har, ["log_rv", "log_iv", "g_d", "g_w", "g_m"],
                           lags=max(h * 2, 10))

        res[f"h{h}"] = {
            "n": int(len(y)),
            "vs_rv_iv": {
                "r2_base": r2_base, "r2_with_lambda": r2_full,
                "incremental_r2": r2_full - r2_base,
                "lambda_t": stats["log_lam"]["t"], "lambda_p": stats["log_lam"]["p"],
                "oos_r2_base": oos_r2(y, base_v),
                "oos_r2_with_lambda": oos_r2(y, full_v),
            },
            "vs_rv_iv_plus_har": {
                "r2_base": r2_bh, "r2_with_lambda": r2_fh,
                "incremental_r2": r2_fh - r2_bh,
                "lambda_t": stats_h["log_lam"]["t"], "lambda_p": stats_h["log_lam"]["p"],
                "oos_r2_base": oos_r2(y, base_har),
                "oos_r2_with_lambda": oos_r2(y, full_har),
            },
        }
    return res


def kc2(d, horizons=(1, 5, 22)):
    """Does conductance ASYMMETRY produce SIGNED drift? (section 6.2)
    lam_asym = log(lam_down/lam_up). If the down side conducts better, forward
    returns should drift NEGATIVE -> expect a negative coefficient."""
    res = {}
    for h in horizons:
        fwd = d["r"].shift(-1).rolling(h).sum().shift(-(h - 1))
        sub = pd.concat([fwd.rename("y"), d[["lam_asym"]]], axis=1).dropna()
        st, r2 = hac_ols(sub["y"], sub[["lam_asym"]].to_numpy(), ["lam_asym"], lags=max(h * 2, 10))
        res[f"h{h}"] = {"n": int(len(sub)), "coef": st["lam_asym"]["coef"],
                        "t": st["lam_asym"]["t"], "p": st["lam_asym"]["p"], "r2": r2}
    return res


def kc3(d, q=5):
    """Do large moves occur with Lambda LOW as often as with Lambda HIGH?
    (section 6.3). If yes, the primitive is wrong."""
    sub = d[["log_lam", "r", "rv"]].dropna().copy()
    sub["big"] = (sub["r"].abs() > 2 * sub["rv"]).astype(float)
    sub["fwd_big"] = sub["big"].shift(-1).rolling(5).max().shift(-4)   # big move next week
    sub = sub.dropna()
    sub["bucket"] = pd.qcut(sub["log_lam"], q, labels=False, duplicates="drop")
    g = sub.groupby("bucket").agg(n=("big", "size"), freq_big_next5=("fwd_big", "mean"),
                                  mean_absr=("r", lambda x: float(np.abs(x).mean())))
    lo, hi = g["freq_big_next5"].iloc[0], g["freq_big_next5"].iloc[-1]
    return {"by_lambda_quintile": g.reset_index().to_dict("records"),
            "lowest_quintile_freq": float(lo), "highest_quintile_freq": float(hi),
            "ratio_high_over_low": float(hi / lo) if lo > 0 else None}


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    px0 = build_panel()
    alpha, _ = impact_exponent(px0["r"].to_numpy(), px0["v"].to_numpy())
    d = assemble(alpha)
    span = d[["logG", "log_lam", "log_iv"]].dropna()
    print(f"alpha={alpha:.3f}   test sample {span.index.min().date()} -> {span.index.max().date()}  n={len(span)}")

    r1, r2, r3 = kc1(d), kc2(d), kc3(d)

    print("\n=== KILL CONDITION 1 (primary): does Lambda beat realised + implied vol? ===")
    for h, v in r1.items():
        a, b = v["vs_rv_iv"], v["vs_rv_iv_plus_har"]
        print(f"\n  horizon {h}  (n={v['n']})")
        print(f"    vs RV+IV          : R2 {a['r2_base']:.4f} -> {a['r2_with_lambda']:.4f} "
              f"(incr {a['incremental_r2']:+.4f})  lambda t={a['lambda_t']:+.2f} p={a['lambda_p']:.4f}")
        print(f"                        OOS R2 {a['oos_r2_base']:+.4f} -> {a['oos_r2_with_lambda']:+.4f}")
        print(f"    vs RV+IV+HAR(G)   : R2 {b['r2_base']:.4f} -> {b['r2_with_lambda']:.4f} "
              f"(incr {b['incremental_r2']:+.4f})  lambda t={b['lambda_t']:+.2f} p={b['lambda_p']:.4f}")
        print(f"                        OOS R2 {b['oos_r2_base']:+.4f} -> {b['oos_r2_with_lambda']:+.4f}")

    print("\n=== KILL CONDITION 2: does signed asymmetry produce signed drift? ===")
    for h, v in r2.items():
        print(f"  {h}: coef={v['coef']:+.5f}  t={v['t']:+.2f}  p={v['p']:.4f}  R2={v['r2']:.5f}  n={v['n']}")

    print("\n=== KILL CONDITION 3: are big moves independent of Lambda? ===")
    for row in r3["by_lambda_quintile"]:
        print(f"  Q{int(row['bucket'])+1}: n={int(row['n']):>4}  P(big move next 5d)={row['freq_big_next5']:.3f}"
              f"  mean|r|={row['mean_absr']:.4f}")
    print(f"  high/low ratio = {r3['ratio_high_over_low']:.3f}")

    (OUT / "kc123.json").write_text(json.dumps(
        {"alpha": alpha, "kc1": r1, "kc2": r2, "kc3": r3}, indent=2, default=float))
    d.to_csv(OUT / "lambda_daily.csv")
    print("\nwrote out/kc123.json, out/lambda_daily.csv")
