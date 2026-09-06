"""
Project Lambda - the discriminating test.

KC4 established that measured conductance is persistent. It could not establish
WHY. Two stories fit equally well:

  (A) conductance  - G is a transmission operator that varies with market
                     structure, exactly as the theory claims;
  (B) clustered news - |eps| itself is autocorrelated, and the persistence is
                     news arrival, not transmission.

Scheduled FOMC decisions separate them. The date is fixed years ahead, so news
ARRIVAL carries no information. The size of the policy surprise on the day is,
by construction of an event study, close to unpredictable. So under (B),
pre-event conductance should add nothing to what implied volatility already
prices for that day. Under (A), pre-event conductance forecasts the
TRANSMISSION of whatever surprise lands, and should predict the response.

The benchmark is deliberately hostile: GVZ is a forward-looking option-implied
forecast that already knows the FOMC meeting is coming.

Prediction under (A): log|r_event| loads on pre-event log G with a coefficient
near 1, incremental to realised and implied volatility.
"""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))

import json, sys, pathlib, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from measure import load, build_panel, impact_exponent, conductance
from engine import hac_ols

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
PRE_END, PRE_LEN = 6, 20      # window [t-25, t-6]: strictly pre-event, no overlap


def assemble_events():
    px = build_panel()
    alpha, _ = impact_exponent(px["r"].to_numpy(), px["v"].to_numpy())
    d = px.copy()
    d["logG"] = conductance(d["r"].to_numpy(), d["v"].to_numpy(), alpha)

    gvz, _ = load("gvz")
    gvz = gvz.set_index("reference_date")["close"].astype(float).sort_index()
    d["iv"] = gvz.reindex(d.index).ffill(limit=5)

    # strictly-prior windows, shifted so nothing from the event day leaks in
    d["G_pre"]  = d["logG"].shift(PRE_END).rolling(PRE_LEN).mean()
    d["RV_pre"] = np.log(d["r"].shift(PRE_END).rolling(PRE_LEN).std())
    d["IV_pre"] = np.log(d["iv"].shift(1))          # last close before the event

    d["resp_total"]  = np.log(d["r"].abs().replace(0, np.nan))
    d["resp_impact"] = d["logG"]                    # |r| per unit of flow, same alpha

    fomc, _ = load("fomc_dates")
    ev = pd.to_datetime(fomc["reference_date"])
    d["is_event"] = d.index.isin(ev)
    return d, alpha, int(d["is_event"].sum())


def run(d, mask, label, target):
    sub = d.loc[mask, [target, "G_pre", "RV_pre", "IV_pre"]].replace(
        [np.inf, -np.inf], np.nan).dropna()
    y = sub[target].to_numpy()
    full = sub[["G_pre", "RV_pre", "IV_pre"]].to_numpy()
    base = sub[["RV_pre", "IV_pre"]].to_numpy()
    st, r2f = hac_ols(y, full, ["G_pre", "RV_pre", "IV_pre"], lags=5)
    _, r2b = hac_ols(y, base, ["RV_pre", "IV_pre"], lags=5)
    # leave-one-year-out: with ~148 events an expanding window is too thin
    yrs = sub.index.year.to_numpy()
    sef, seb, sec = [], [], []
    for yr in np.unique(yrs):
        tr, te = yrs != yr, yrs == yr
        if tr.sum() < 40 or te.sum() == 0:
            continue
        for X, acc in ((full, sef), (base, seb)):
            Xd = np.column_stack([np.ones(tr.sum()), X[tr]])
            b, *_ = np.linalg.lstsq(Xd, y[tr], rcond=None)
            pred = np.column_stack([np.ones(te.sum()), X[te]]) @ b
            acc.append(((y[te] - pred) ** 2).sum())
        sec.append(((y[te] - y[tr].mean()) ** 2).sum())
    oos_f = 1 - np.sum(sef) / np.sum(sec) if sec else np.nan
    oos_b = 1 - np.sum(seb) / np.sum(sec) if sec else np.nan
    return {"label": label, "target": target, "n": int(len(y)),
            "G_pre": st["G_pre"], "RV_pre": st["RV_pre"], "IV_pre": st["IV_pre"],
            "r2_base": r2b, "r2_full": r2f, "incremental_r2": r2f - r2b,
            "loyo_oos_base": float(oos_b), "loyo_oos_full": float(oos_f),
            "loyo_delta": float(oos_f - oos_b)}


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    d, alpha, n_ev = assemble_events()
    print(f"alpha={alpha:.3f}   FOMC decision days matched to trading days: {n_ev}")

    res = []
    for target in ("resp_total", "resp_impact"):
        res.append(run(d, d["is_event"], "FOMC decision days", target))
        res.append(run(d, ~d["is_event"], "placebo: all non-FOMC days", target))

    names = {"resp_total": "log |r| on the day",
             "resp_impact": "log |r| per unit of flow"}
    for r in res:
        g = r["G_pre"]
        print(f"\n=== {r['label']}  |  target: {names[r['target']]}  (n={r['n']}) ===")
        print(f"    G_pre  coef={g['coef']:+.3f}  t={g['t']:+.2f}  p={g['p']:.4f}"
              f"   [theory predicts coef near +1]")
        for k in ("RV_pre", "IV_pre"):
            print(f"    {k:6s} coef={r[k]['coef']:+.3f}  t={r[k]['t']:+.2f}  p={r[k]['p']:.4f}")
        print(f"    R2 {r['r2_base']:.4f} -> {r['r2_full']:.4f}  (incremental {r['incremental_r2']:+.4f})")
        print(f"    leave-one-year-out OOS R2 {r['loyo_oos_base']:+.4f} -> {r['loyo_oos_full']:+.4f}"
              f"  (delta {r['loyo_delta']:+.4f})")

    (OUT / "events.json").write_text(json.dumps(
        {"alpha": alpha, "n_events": n_ev, "results": res}, indent=2, default=float))
    print("\nwrote out/events.json")
