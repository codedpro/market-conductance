"""
Project Lambda - Layer 1: Collectors (section 14.1)

Writes raw immutable snapshots. Every series stores BOTH reference_date and
release_date (section 12.1, non-negotiable). Free sources only (section 13).
"""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))

import json, io, csv, time, datetime as dt, pathlib, subprocess, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW  = ROOT / "data" / "raw"
UA   = "Mozilla/5.0 (X11; Linux x86_64) research/lambda-conductance"
FETCHED_AT = dt.datetime.now(dt.timezone.utc).isoformat()

# Section 6.1: "If it only works on gold, it is a gold story dressed as a law."
GENERALISE = [
    ("SPY", "spy_ohlcv"),   # US large-cap equity
    ("QQQ", "qqq_ohlcv"),   # US tech
    ("TLT", "tlt_ohlcv"),   # long Treasuries
    ("HYG", "hyg_ohlcv"),   # high-yield credit
    ("SLV", "slv_ohlcv"),   # silver
    ("USO", "uso_ohlcv"),   # crude oil
    ("FXE", "fxe_ohlcv"),   # euro
    ("EEM", "eem_ohlcv"),   # emerging market equity
    ("GDX", "gdx_ohlcv"),   # gold miners
]


def _get(url, timeout=60, tries=4):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError:
            raise
        except Exception as e:
            last = e
            time.sleep(1 + i)
    # urllib hangs on some hosts here; curl succeeds on the identical URL
    try:
        return subprocess.run(["curl", "-sL", "--max-time", "60", "-A", UA, url],
                              capture_output=True, check=True).stdout
    except Exception:
        raise last


def _write(name, rows, meta):
    """Immutable raw snapshot: one JSON per source, provenance attached."""
    RAW.mkdir(parents=True, exist_ok=True)
    p = RAW / f"{name}.json"
    p.write_text(json.dumps({"meta": meta, "rows": rows}, default=str))
    print(f"  wrote {p.relative_to(ROOT)}  n={len(rows)}")
    return rows


# ---------------------------------------------------------------- numerator
def cot_gold():
    """CFTC Disaggregated COT, COMEX Gold 088691. Weekly.
    Reference = Tuesday snapshot. Release = Friday 15:30 ET => ref + 3 days."""
    base = "https://publicreporting.cftc.gov/resource/72hh-3qpy.json"
    cols = ",".join([
        "report_date_as_yyyy_mm_dd", "open_interest_all",
        "prod_merc_positions_long", "prod_merc_positions_short",
        "swap_positions_long_all", "swap__positions_short_all", "swap__positions_spread_all",
        "m_money_positions_long_all", "m_money_positions_short_all", "m_money_positions_spread",
        "other_rept_positions_long", "other_rept_positions_short", "other_rept_positions_spread",
        "nonrept_positions_long_all", "nonrept_positions_short_all",
        "traders_tot_all", "traders_m_money_long_all", "traders_m_money_short_all",
        "conc_gross_le_4_tdr_long", "conc_gross_le_4_tdr_short",
    ])
    url = (f"{base}?$select={cols}&$where=cftc_contract_market_code='088691'"
           f"&$order=report_date_as_yyyy_mm_dd&$limit=5000")
    rows = json.loads(_get(url))
    for r in rows:
        ref = dt.date.fromisoformat(r["report_date_as_yyyy_mm_dd"][:10])
        r["reference_date"] = ref.isoformat()
        r["release_date"]   = (ref + dt.timedelta(days=3)).isoformat()  # Fri 15:30 ET
    return _write("cot_gold_088691", rows, {
        "source": "CFTC Disaggregated COT (Socrata 72hh-3qpy)", "cost": "free",
        "contract": "088691 GOLD - COMMODITY EXCHANGE INC.",
        "lag_rule": "release = reference + 3 days (Tue snapshot, Fri 15:30 ET release)",
        "fetched_at": FETCHED_AT, "url": url})


# ------------------------------------------------------------- price / vol
def yahoo_ohlcv(symbol, name):
    """Daily OHLCV. Reference = release = trade date (settles same day)."""
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
           f"?period1=1000000000&period2=9999999999&interval=1d")
    d = json.loads(_get(url))["chart"]["result"][0]
    q = d["indicators"]["quote"][0]
    rows = []
    for i, ts in enumerate(d["timestamp"]):
        c, v = q["close"][i], q["volume"][i]
        if c is None:
            continue
        day = dt.datetime.fromtimestamp(ts, dt.timezone.utc).date().isoformat()
        rows.append({"reference_date": day, "release_date": day, "close": c,
                     "open": q["open"][i], "high": q["high"][i], "low": q["low"][i],
                     "volume": v})
    return _write(name, rows, {
        "source": f"Yahoo Finance {symbol}", "cost": "free",
        "lag_rule": "reference = release = trade date",
        "caveat": "unofficial endpoint (section 13.3)",
        "fetched_at": FETCHED_AT, "url": url})


def fred(series, name):
    """FRED CSV. Reference = observation date; release ~ next business day."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
    txt = _get(url).decode()
    rows = []
    for r in csv.DictReader(io.StringIO(txt)):
        val = r[series]
        if val in (".", "", None):
            continue
        ref = dt.date.fromisoformat(r["observation_date"])
        rows.append({"reference_date": ref.isoformat(),
                     "release_date": (ref + dt.timedelta(days=1)).isoformat(),
                     "value": float(val)})
    return _write(name, rows, {
        "source": f"FRED {series}", "cost": "free",
        "lag_rule": "release = reference + 1 day",
        "fetched_at": FETCHED_AT, "url": url})


def lbma_fix():
    """LBMA official gold PM fix, USD. Reference = fix date, released same day."""
    url = "https://prices.lbma.org.uk/json/gold_pm.json"
    rows = []
    for r in json.loads(_get(url)):
        v = r.get("v") or []
        if not v or v[0] is None:
            continue
        rows.append({"reference_date": r["d"], "release_date": r["d"],
                     "usd_pm": float(v[0])})
    return _write("lbma_gold_pm", rows, {
        "source": "LBMA official price feed (prices.lbma.org.uk)", "cost": "free",
        "lag_rule": "reference = release = fix date",
        "fetched_at": FETCHED_AT, "url": url})


# ----------------------------------------------------------- event calendar
_MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July",
                "August", "September", "October", "November", "December"]
# Straddling meetings are headed with abbreviations ("Jan/Feb 31-1 Meeting - 2017")
MONTHS = {m: i + 1 for i, m in enumerate(_MONTH_NAMES)}
MONTHS.update({m[:3]: i + 1 for i, m in enumerate(_MONTH_NAMES)})


def fomc_dates():
    """Regularly SCHEDULED FOMC decision days, 2008-2026.

    Why scheduled-only matters: unscheduled/emergency actions happen *because*
    markets are stressed. Including them would manufacture the exact
    correlation the event test is trying to measure. The Fed's own pages label
    each meeting block, so exclusion is by their label, not our judgement:
    "(unscheduled)", "(cancelled)", "Conference Call" and "notation vote" are
    all dropped.

    Decision date is taken from the statement link inside each meeting block
    (/press/monetary/<YYYYMMDD>a.htm, or monetary<YYYYMMDD>a.htm on newer
    pages), which for a two-day meeting is day two.
    """
    import re
    urls = ["https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"]
    urls += [f"https://www.federalreserve.gov/monetarypolicy/fomchistorical{y}.htm"
             for y in range(2008, 2021)]
    EXCLUDE = ("unscheduled", "cancelled", "canceled", "conference call", "notation vote")
    keep, dropped = {}, []
    for u in urls:
        try:
            html = _get(u, timeout=45).decode("utf-8", "ignore")
        except Exception as e:
            print(f"  warn: {u} -> {type(e).__name__}")
            continue
        blocks = re.split(r"<h5[^>]*>", html)[1:]
        for b in blocks:
            head = re.split(r"</h5>", b)[0]
            head_txt = re.sub(r"<[^>]+>", " ", head).strip()
            low = head_txt.lower()
            if not re.search(r"\bmeeting\b", low):
                continue
            if any(x in low for x in EXCLUDE):
                dropped.append(head_txt)
                continue
            ym = re.search(r"-\s*(\d{4})\s*$", head_txt)
            if not ym:
                continue
            yr = int(ym.group(1))
            # headings name every month the meeting touches, written as
            # "April/May 30-1 Meeting - 2013" when it straddles a month end
            mons = [MONTHS[w] for w in re.findall(r"[A-Z][a-z]+", head_txt) if w in MONTHS]
            if not mons:
                continue
            ok = {(yr, mo) for mo in mons}
            if 12 in mons and 1 in mons:              # December/January rolls the year
                ok.discard((yr, 1)); ok.add((yr + 1, 1))
            cands = [c for c in re.findall(r"monetary/?(\d{8})[a-z]*\.htm", b)
                     if (int(c[:4]), int(c[4:6])) in ok]
            if not cands:
                continue
            d = max(cands)                      # two-day meeting -> statement on day two
            keep[d] = head_txt
    # The 2021+ calendar page is not block-structured. Taking every
    # monetary<date> link there is too loose - it also matches non-decision
    # releases (e.g. monetary20250822a.htm, the Jackson Hole framework
    # release). Every FOMC decision since 2019 holds a press conference, so
    # intersecting statement links with fomcpresconf links isolates decisions.
    try:
        cal = _get(urls[0], timeout=45).decode("utf-8", "ignore")
        stmts = set(re.findall(r"monetary/?(\d{8})[a-z]*\.htm", cal))
        confs = set(re.findall(r"fomcpresconf(\d{8})", cal))
        rejected = []
        for d in sorted(stmts):
            if int(d[:4]) < 2021:
                continue
            iso = dt.date(int(d[:4]), int(d[4:6]), int(d[6:]))
            # A scheduled decision is the final day of a scheduled meeting: every
            # one since 2021 has fallen on a Wednesday and holds a press
            # conference. Requiring either filters non-decision releases such as
            # monetary20250822a.htm (the Friday Jackson Hole framework release)
            # without dropping decisions whose presser link is simply absent.
            if d in confs or iso.weekday() == 2:
                keep.setdefault(d, "calendar page - scheduled decision")
            else:
                rejected.append(d)
        if rejected:
            print(f"  calendar: rejected {len(rejected)} non-decision releases: {rejected}")
    except Exception as e:
        print(f"  warn: calendar page -> {type(e).__name__}")

    rows = []
    for d in sorted(keep):
        rows.append({"reference_date": f"{d[:4]}-{d[4:6]}-{d[6:]}",
                     "release_date":   f"{d[:4]}-{d[4:6]}-{d[6:]}",
                     "event": "FOMC", "meeting": keep[d]})
    print(f"  kept {len(rows)} scheduled meetings; dropped {len(dropped)} unscheduled/call/cancelled")
    return _write("fomc_dates", rows, {
        "source": "federalreserve.gov FOMC meeting blocks", "cost": "free",
        "selection": "regularly scheduled meetings only; unscheduled, cancelled, "
                     "conference-call and notation-vote blocks excluded by the Fed's own label",
        "lag_rule": "scheduled years ahead; statement 14:00 ET on the date",
        "n_dropped": len(dropped), "fetched_at": FETCHED_AT, "urls": urls})


# ------------------------------------------------------------------ blocked
def probe_blocked():
    """Sources section 10 assumes are free-and-direct but that now refuse robots."""
    out = []
    for label, url in [
        ("COMEX warehouse stocks", "https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls"),
        ("LBMA vault holdings",    "https://www.lbma.org.uk/prices-and-data/vault-holdings-data"),
        ("FRED GVZCLS",            "https://fred.stlouisfed.org/graph/fredgraph.csv?id=GVZCLS"),
    ]:
        try:
            _get(url, timeout=30); status = "200 OK"
        except urllib.error.HTTPError as e:
            status = f"{e.code} {e.reason}"
        except Exception as e:
            status = f"ERR {type(e).__name__}"
        out.append({"source": label, "url": url, "status": status})
        print(f"  probe: {label:26s} {status}")
    return _write("_blocked_probe", out, {"note": "denominator gap audit",
                                          "fetched_at": FETCHED_AT})


if __name__ == "__main__":
    print("== numerator ==");   cot_gold()
    print("== price/vol ==")
    yahoo_ohlcv("GC=F", "gcf_ohlcv")     # kept: price ok, VOLUME UNUSABLE (see measure.py)
    yahoo_ohlcv("GLD", "gld_ohlcv")      # primary instrument (sections 10.3 / 13.3)
    lbma_fix()
    print("== controls (section 15) ==")
    yahoo_ohlcv("%5EGVZ", "gvz")         # implied vol - the hardest hurdle
    yahoo_ohlcv("DX-Y.NYB", "dxy")       # dollar
    yahoo_ohlcv("%5ETNX", "tnx")         # 10y nominal yield
    for series, name in [("DFII10", "tips10")]:   # best-effort: FRED rate-limits
        try:
            fred(series, name)
        except Exception as e:
            print(f"  SKIP FRED {series}: {type(e).__name__} (rate-limited)")
    print("== event calendar =="); fomc_dates()
    print("== generalisation universe (section 6.1) ==")
    for sym, name in GENERALISE:
        try:
            yahoo_ohlcv(sym, name)
        except Exception as e:
            print(f"  SKIP {sym}: {type(e).__name__}")
    print("== gap audit =="); probe_blocked()
    print("done.")
