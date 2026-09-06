"""Construction-free check: does ANY raw COT holder-base variable forecast future
conductance, beyond realised + implied vol (+ conductance's own history)?
If nothing does, the failure is not specific to how Lambda was built."""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))

import sys, json, numpy as np, pandas as pd, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from measure import load, build_panel, impact_exponent, conductance
from engine import holder_base, oos_r2, hac_ols

px = build_panel()
alpha, _ = impact_exponent(px["r"].to_numpy(), px["v"].to_numpy())
h = holder_base().sort_values("release_date")

# point-in-time as-of merge on RELEASE date
base = px.reset_index().rename(columns={"reference_date": "date"}).sort_values("date")
d = pd.merge_asof(base, h.sort_values("release_date"),
                  left_on="date", right_on="release_date",
                  direction="backward").set_index("date")

oi = d["oi"]
feat = pd.DataFrame(index=d.index)
feat["mm_long_oi"]   = d["mm_long"] / oi
feat["mm_short_oi"]  = d["mm_short"] / oi
feat["mm_net_oi"]    = (d["mm_long"] - d["mm_short"]) / oi
feat["mm_gross_oi"]  = (d["mm_long"] + d["mm_short"]) / oi
feat["swap_short_oi"]= d["swap_short"] / oi
feat["prod_short_oi"]= d["prod_short"] / oi
feat["log_oi"]       = np.log(oi)
feat["traders"]      = d["traders"]
feat["conc_long"]    = d["conc_long"]
feat["conc_short"]   = d["conc_short"]
feat["d_mm_net"]     = feat["mm_net_oi"].diff(5)
feat["d_oi"]         = feat["log_oi"].diff(5)

gvz, _ = load("gvz"); gvz = gvz.set_index("reference_date")["close"].astype(float).sort_index()
d["logG"]   = conductance(d["r"].to_numpy(), d["v"].to_numpy(), alpha)
d["log_rv"] = np.log(d["r"].rolling(22, min_periods=15).std())
d["log_iv"] = np.log(gvz.reindex(d.index).ffill(limit=5))
d["g_d"] = d["logG"].shift(1); d["g_w"] = d["logG"].shift(1).rolling(5).mean()
d["g_m"] = d["logG"].shift(1).rolling(22).mean()

out = {}
for H in (5, 22):
    tgt = d["logG"].shift(-1).rolling(H).mean().shift(-(H - 1))
    ctrl = ["log_rv", "log_iv", "g_d", "g_w", "g_m"]
    sub = pd.concat([tgt.rename("y"), d[ctrl], feat], axis=1).replace([np.inf,-np.inf],np.nan).dropna()
    y = sub["y"].to_numpy(); C = sub[ctrl].to_numpy()
    _, r2c = hac_ols(y, C, ctrl, lags=H*2)
    oos_c  = oos_r2(y, C)
    rows = []
    for f in feat.columns:
        X = np.column_stack([C, sub[f].to_numpy()])
        st, r2 = hac_ols(y, X, ctrl + [f], lags=H*2)
        rows.append({"var": f, "t": st[f]["t"], "p": st[f]["p"],
                     "incr_r2": r2 - r2c, "oos_r2": oos_r2(y, X), "d_oos": oos_r2(y, X) - oos_c})
    Xall = np.column_stack([C, sub[feat.columns].to_numpy()])
    _, r2all = hac_ols(y, Xall, ctrl + list(feat.columns), lags=H*2)
    out[f"h{H}"] = {"n": int(len(sub)), "r2_ctrl": r2c, "oos_ctrl": oos_c,
                    "single": rows,
                    "all_cot": {"incr_r2": r2all - r2c, "oos_r2": oos_r2(y, Xall),
                                "d_oos": oos_r2(y, Xall) - oos_c}}
    print(f"\n=== horizon {H}d   n={len(sub)}   controls: RV+IV+HAR(G)  R2={r2c:.4f}  OOS={oos_c:+.4f} ===")
    print(f"{'COT variable':<16}{'t':>8}{'p':>9}{'incr R2':>10}{'dOOS R2':>10}")
    for r in sorted(rows, key=lambda z: -abs(z["t"])):
        print(f"{r['var']:<16}{r['t']:>+8.2f}{r['p']:>9.4f}{r['incr_r2']:>+10.4f}{r['d_oos']:>+10.4f}")
    a = out[f"h{H}"]["all_cot"]
    print(f"{'ALL 12 jointly':<16}{'':>8}{'':>9}{a['incr_r2']:>+10.4f}{a['d_oos']:>+10.4f}")

pathlib.Path("out/cot_generic.json").write_text(json.dumps(out, indent=2, default=float))
print("\nwrote out/cot_generic.json")
