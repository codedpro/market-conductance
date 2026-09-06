"""
Project Lambda - section 6.1 generalisation test.

"Lambda and Sigma should say something about markets other than gold... If it
only works on gold, it is a gold story dressed as a law and should be discarded."

Runs the KC4 measurement - is conductance a state variable or a constant with
noise - identically across nine other liquid, free-data instruments spanning
equity, rates, credit, FX, energy, metals and EM.
"""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))

import json, sys, pathlib, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import measure
from measure import build_panel, impact_exponent, kill_condition_4

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "out"

UNIVERSE = [
    ("gld_ohlcv", "GLD", "gold"),
    ("spy_ohlcv", "SPY", "US large-cap equity"),
    ("qqq_ohlcv", "QQQ", "US tech equity"),
    ("tlt_ohlcv", "TLT", "long Treasuries"),
    ("hyg_ohlcv", "HYG", "high-yield credit"),
    ("slv_ohlcv", "SLV", "silver"),
    ("uso_ohlcv", "USO", "crude oil"),
    ("fxe_ohlcv", "FXE", "euro"),
    ("eem_ohlcv", "EEM", "EM equity"),
    ("gdx_ohlcv", "GDX", "gold miners"),
]

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    rows = []
    print(f"{'asset':<6}{'class':<22}{'n':>6}{'alpha':>8}{'LB(22)':>11}{'null p99':>10}"
          f"{'VR66':>8}{'OOS R2':>9}{'p':>8}")
    for name, sym, cls in UNIVERSE:
        try:
            px = build_panel(instrument=name)
        except Exception as e:
            print(f"{sym:<6}{cls:<22}  SKIP {type(e).__name__}")
            continue
        a, _ = impact_exponent(px["r"].to_numpy(), px["v"].to_numpy())
        obs, res, _ = kill_condition_4(px, a, nsim=500, n_oos_sim=120)
        rows.append({"symbol": sym, "asset_class": cls, "n": int(len(px)),
                     "alpha": a, "stats": res})
        print(f"{sym:<6}{cls:<22}{len(px):>6}{a:>8.3f}"
              f"{res['ljungbox22']['observed']:>11.1f}{res['ljungbox22']['null_p99']:>10.1f}"
              f"{res['vr66']['observed']:>8.2f}{res['har_oos_r2']['observed']:>9.4f}"
              f"{res['har_oos_r2']['p_value']:>8.4f}")
    (OUT / "generalize.json").write_text(json.dumps(rows, indent=2, default=float))
    print("\nwrote out/generalize.json")
