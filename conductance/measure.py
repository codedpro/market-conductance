"""
Project Lambda - Layers 2/4: measure G, then run KILL CONDITION 4 (section 6.4)

  "If measured G turns out to be a stable constant with noise rather than a
   state variable, then Gabaix and Koijen were already right and there is
   nothing to add. Answer this question first."

Estimator (square-root impact law, r = G * eps):
      S_t = |r_t| / sqrt(v_t)      v_t = volume normalised by trailing median

Chosen because under H0 (G constant + mixture-of-distributions information
arrival, i.e. volume and volatility co-move only through news flow) S_t is
IID NOISE. Persistence in S_t is therefore evidence against H0.

Null: iid bootstrap of empirical shocks - preserves the exact fat-tailed
marginal, imposes constant G. The identical pipeline runs on real and
simulated data, so pipeline-induced persistence is controlled for.
"""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))

import json, pathlib, numpy as np, pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "data" / "raw", ROOT / "out"
RNG = np.random.default_rng(20260906)
VOL_WIN = 252          # trailing window for volume normalisation
NSIM    = 2000


def load(name):
    d = json.loads((RAW / f"{name}.json").read_text())
    df = pd.DataFrame(d["rows"])
    for c in ("reference_date", "release_date"):
        if c in df:
            df[c] = pd.to_datetime(df[c])
    return df, d["meta"]


# --------------------------------------------------------------- pipeline
def build_panel(min_year=2008, instrument="gld_ohlcv"):
    """GLD (NYSE Arca) is the primary instrument, per sections 10.3 and 13.3.
    Yahoo GC=F volume is unusable historically: it alternates between the
    front-month aggregate and a near-dead contract (median ~150 vs max ~200k,
    41 zero-volume days). GLD consolidated equity volume is clean throughout."""
    px, _ = load(instrument)
    px = px.sort_values("reference_date").set_index("reference_date")
    px = px[["close", "volume"]].astype(float)
    px = px[px.index.year >= min_year]
    px = px[(px["close"] > 0) & (px["volume"] > 0)].dropna()

    px["r"] = np.log(px["close"]).diff()
    # volume normalised by its own trailing median -> removes secular growth
    # and contract-roll drift without touching sub-annual variation
    px["v"] = px["volume"] / px["volume"].rolling(VOL_WIN, min_periods=60).median()
    px = px.dropna(subset=["r", "v"])
    px = px[px["v"] > 0]
    return px


def stat_pipeline(absr, v):
    """Identical transform for real and simulated returns -> log conductance."""
    s = np.asarray(absr) / np.sqrt(np.asarray(v))
    s = np.where(s <= 0, np.nan, s)
    return np.log(s)


# -------------------------------------------------------------- statistics
def var_ratio(x, q):
    """Lo-MacKinlay style VR on the level series: >1 => persistent."""
    x = x[~np.isnan(x)]
    n = len(x) // q * q
    if n < q * 5:
        return np.nan
    x = x[:n]
    v1 = np.var(x, ddof=1)
    agg = x.reshape(-1, q).mean(axis=1)
    return np.var(agg, ddof=1) * q / v1 if v1 > 0 else np.nan


def har_oos_r2(y, min_train=750):
    """Expanding-window OOS R^2 of a HAR forecast vs the expanding-mean
    benchmark. This is the operational definition of a state variable:
    a constant-with-noise has no forecastable component."""
    y = pd.Series(y).astype(float)
    X = pd.DataFrame({
        "d":  y.shift(1),
        "w":  y.shift(1).rolling(5).mean(),
        "m":  y.shift(1).rolling(22).mean(),
    })
    ok = X.notna().all(axis=1) & y.notna()
    X, yv = X[ok].to_numpy(), y[ok].to_numpy()
    n = len(yv)
    if n < min_train + 100:
        return np.nan, 0
    se_m, se_b = [], []
    Xd = np.column_stack([np.ones(n), X])
    b = None
    for t in range(min_train, n):
        if (t - min_train) % 21 == 0:          # refit monthly, forecast daily
            b, *_ = np.linalg.lstsq(Xd[:t], yv[:t], rcond=None)
        se_m.append((yv[t] - Xd[t] @ b) ** 2)
        se_b.append((yv[t] - yv[:t].mean()) ** 2)
    return 1 - np.sum(se_m) / np.sum(se_b), len(se_m)


def all_stats(logs):
    s = pd.Series(logs).dropna()
    x = s.to_numpy()
    ar1 = pd.Series(x).autocorr(1)
    lb = acorr_ljungbox(x, lags=[22], return_df=True)["lb_stat"].iloc[0]
    r2, noos = har_oos_r2(logs)
    return {
        "ar1": float(ar1),
        "ar5": float(pd.Series(x).autocorr(5)),
        "ar22": float(pd.Series(x).autocorr(22)),
        "ljungbox22": float(lb),
        "vr5": float(var_ratio(x, 5)),
        "vr22": float(var_ratio(x, 22)),
        "vr66": float(var_ratio(x, 66)),
        "har_oos_r2": float(r2),
        "n_oos": int(noos),
        "n": int(len(x)),
    }


# ------------------------------------------------------------------ KC4
def impact_exponent(r, v):
    """Estimate alpha in |r| ~ v**alpha. Theory (square-root law) says 0.5;
    Amihud assumes 1.0. Using the EMPIRICAL alpha makes log S orthogonal to
    log v by construction, so no residual persistence can be blamed on volume."""
    m = (np.abs(r) > 0) & (v > 0)
    x, y = np.log(v[m]), np.log(np.abs(r[m]))
    A = np.column_stack([np.ones(x.size), x])
    b, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ b
    r2 = 1 - resid.var() / y.var()
    return float(b[1]), float(r2)


def conductance(r, v, alpha):
    """log G_t = log|r_t| - alpha*log v_t. NaN on zero-move days."""
    with np.errstate(divide="ignore", invalid="ignore"):
        s = np.abs(np.asarray(r)) / np.power(np.asarray(v), alpha)
        s = np.where(s > 0, s, np.nan)
        return np.log(s)


def kill_condition_4(px, alpha, nsim=NSIM, n_oos_sim=300):
    """H0: G is a constant with noise.  Under H0 + MDH information arrival,
    S_t = |r_t|/v_t**alpha is IID. Null = iid bootstrap of the empirical S,
    which preserves the exact fat-tailed marginal and imposes constant G.
    The identical statistic pipeline runs on real and simulated series."""
    r, v = px["r"].to_numpy(), px["v"].to_numpy()
    logS_real = conductance(r, v, alpha)
    obs = all_stats(logS_real)

    pool = logS_real[np.isfinite(logS_real)]      # empirical |shock| distribution
    keys = ["ar1", "ar5", "ar22", "ljungbox22", "vr5", "vr22", "vr66", "har_oos_r2"]
    sims = {k: [] for k in keys}
    for i in range(nsim):
        sim = RNG.choice(pool, size=len(pool), replace=True)   # iid, same marginal
        if i < n_oos_sim:
            st = all_stats(sim)
        else:
            st = all_stats_cheap(sim)
        for k in keys:
            sims[k].append(float(st.get(k, np.nan)))

    res = {}
    for k in keys:
        arr = np.array([x for x in sims[k] if np.isfinite(x)])
        o = obs[k]
        res[k] = {"observed": o, "null_mean": float(arr.mean()),
                  "null_p95": float(np.percentile(arr, 95)),
                  "null_p99": float(np.percentile(arr, 99)),
                  "p_value": float((arr >= o).mean()), "n_sim": int(len(arr))}
    return obs, res, logS_real


def all_stats_cheap(x):
    """Same statistics minus the costly OOS loop."""
    s = pd.Series(x).dropna(); a = s.to_numpy()
    return {"ar1": s.autocorr(1), "ar5": s.autocorr(5), "ar22": s.autocorr(22),
            "ljungbox22": acorr_ljungbox(a, lags=[22], return_df=True)["lb_stat"].iloc[0],
            "vr5": var_ratio(a, 5), "vr22": var_ratio(a, 22), "vr66": var_ratio(a, 66),
            "har_oos_r2": np.nan, "n": len(a)}


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    px = build_panel()
    r, v = px["r"].to_numpy(), px["v"].to_numpy()
    a_hat, a_r2 = impact_exponent(r, v)
    print(f"panel: {px.index.min().date()} -> {px.index.max().date()}  n={len(px)}")
    print(f"impact exponent alpha_hat = {a_hat:.3f}  (sqrt-law=0.5, Amihud=1.0)  R2={a_r2:.4f}")

    report = {"panel": {"start": str(px.index.min().date()), "end": str(px.index.max().date()),
                        "n": int(len(px)), "instrument": "GLD"},
              "alpha_hat": a_hat, "alpha_r2": a_r2, "variants": {}}

    for label, alpha in [("alpha_hat", a_hat), ("sqrt_law_0.5", 0.5), ("amihud_1.0", 1.0)]:
        obs, res, logS = kill_condition_4(px, alpha)
        report["variants"][label] = {"alpha": alpha, "observed": obs, "test": res}
        print(f"\n=== KILL CONDITION 4 | estimator: {label} (alpha={alpha:.3f}) ===")
        print(f"{'stat':<12}{'observed':>11}{'null mean':>11}{'null p99':>10}{'p-value':>10}")
        for k, d in res.items():
            print(f"{k:<12}{d['observed']:>11.4f}{d['null_mean']:>11.4f}"
                  f"{d['null_p99']:>10.4f}{d['p_value']:>10.4f}")
        if label == "alpha_hat":
            pd.DataFrame({"logS": logS}, index=px.index).to_csv(OUT / "conductance_S.csv")

    (OUT / "kc4.json").write_text(json.dumps(report, indent=2, default=float))
    print("\nwrote out/kc4.json, out/conductance_S.csv")
