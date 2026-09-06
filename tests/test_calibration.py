"""
Calibration and integrity tests.

The KC4 result rests entirely on the claim that the test rejects a constant-G
world at roughly its nominal rate and has power against a varying-G world.
That claim is checked here against SYNTHETIC data with known ground truth,
not asserted. Also checks the point-in-time discipline of section 12.1, which
is the single easiest way to produce a brilliant and meaningless backtest.

Run: pytest -q tests/
"""
import sys, pathlib, numpy as np, pandas as pd, pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "conductance"))
from measure import impact_exponent, conductance, all_stats, var_ratio, har_oos_r2  # noqa: E402


def synth(n, rng, g_ar=0.0, g_sd=0.0, alpha=1.0):
    """Synthetic market with a KNOWN conductance process.

    g_sd = 0 -> G is a constant with noise (the KC4 null).
    g_sd > 0 -> G is a persistent state variable (the KC4 alternative).
    Volume is autocorrelated in both cases, so volume persistence alone can
    never explain a rejection.
    """
    logv = np.zeros(n)
    for t in range(1, n):                      # persistent volume, as in real data
        logv[t] = 0.95 * logv[t - 1] + rng.normal(0, 0.3)
    v = np.exp(logv)
    logG = np.zeros(n)
    if g_sd > 0:
        for t in range(1, n):
            logG[t] = g_ar * logG[t - 1] + rng.normal(0, g_sd)
    eps = rng.standard_t(4, n)                 # fat-tailed shocks
    r = np.exp(logG) * np.abs(eps) * v ** alpha * np.sign(eps)
    return r, v


def kc4_pvalue(r, v, alpha, rng, nsim=200):
    """Ljung-Box(22) of log G against an iid bootstrap null. Same logic as
    measure.kill_condition_4, trimmed to one statistic for test speed."""
    logS = conductance(r, v, alpha)
    obs = all_stats(logS)["ljungbox22"]
    pool = logS[np.isfinite(logS)]
    null = np.empty(nsim)
    for i in range(nsim):
        sim = rng.choice(pool, size=len(pool), replace=True)
        null[i] = all_stats(sim)["ljungbox22"]
    return float((null >= obs).mean())


# ------------------------------------------------------------------ size
def test_null_is_not_over_rejected():
    """Constant G: the test must NOT systematically reject. A test that
    rejects a constant-G world would make the whole KC4 finding an artefact."""
    rng = np.random.default_rng(7)
    p = [kc4_pvalue(*synth(1500, rng, g_sd=0.0), 1.0, rng, nsim=150) for _ in range(12)]
    reject = np.mean([x < 0.05 for x in p])
    assert reject <= 0.25, f"over-rejection under the null: {reject:.2f} of runs (p={p})"


# ----------------------------------------------------------------- power
def test_power_against_varying_G():
    """Persistent G: the test must detect it. Otherwise a null result would be
    uninformative rather than evidence of a constant."""
    rng = np.random.default_rng(11)
    p = [kc4_pvalue(*synth(1500, rng, g_ar=0.97, g_sd=0.08), 1.0, rng, nsim=150)
         for _ in range(6)]
    assert np.mean([x < 0.05 for x in p]) >= 0.8, f"insufficient power: {p}"


# ------------------------------------------------------- estimator recovery
@pytest.mark.parametrize("true_alpha", [0.5, 1.0])
def test_impact_exponent_recovers_truth(true_alpha):
    rng = np.random.default_rng(3)
    r, v = synth(6000, rng, alpha=true_alpha)
    est, _ = impact_exponent(r, v)
    assert abs(est - true_alpha) < 0.06, f"alpha {est:.3f} vs truth {true_alpha}"


def test_conductance_is_orthogonal_to_volume_at_estimated_alpha():
    """Using the EMPIRICAL alpha is what stops volume persistence leaking into
    log G. Verify the residual really is orthogonal to log volume."""
    rng = np.random.default_rng(5)
    r, v = synth(4000, rng, g_ar=0.97, g_sd=0.08, alpha=0.8)
    a, _ = impact_exponent(r, v)
    lg = conductance(r, v, a)
    m = np.isfinite(lg)
    corr = np.corrcoef(lg[m], np.log(v[m]))[0, 1]
    assert abs(corr) < 0.02, f"log G still correlated with log volume: {corr:.4f}"


# -------------------------------------------------------- statistic sanity
def test_variance_ratio_iid_is_one():
    rng = np.random.default_rng(2)
    vals = [var_ratio(rng.normal(size=4000), q) for q in (5, 22, 66) for _ in range(1)]
    assert all(abs(v - 1.0) < 0.25 for v in vals), vals


def test_oos_r2_of_pure_noise_is_not_positive():
    rng = np.random.default_rng(4)
    r2, n = har_oos_r2(rng.normal(size=3000))
    assert n > 0 and r2 < 0.01, f"HAR found signal in noise: {r2:.4f}"


# --------------------------------------------------- point-in-time discipline
def test_cot_merge_never_uses_unreleased_data():
    """Section 12.1: on day d only COT rows RELEASED on or before d may be used."""
    import engine
    px = pd.DataFrame(
        {"close": np.linspace(100, 120, 40), "r": np.zeros(40), "v": np.ones(40)},
        index=pd.bdate_range("2024-01-01", periods=40))
    px.index.name = "reference_date"
    ref = pd.bdate_range("2024-01-02", periods=6, freq="W-TUE")
    h = pd.DataFrame({
        "reference_date": ref, "release_date": ref + pd.Timedelta(days=3),
        "oi": 1000.0, "mm_long": 100.0, "mm_short": 50.0,
        "swap_long": 10.0, "swap_short": 10.0, "prod_long": 10.0, "prod_short": 10.0,
        "traders": 100.0, "conc_long": 20.0, "conc_short": 20.0})
    out = engine.build_lambda(px, h)
    used = out["release_date"].dropna()
    assert (used.index >= used.values).all(), "lookahead: COT used before its release date"
