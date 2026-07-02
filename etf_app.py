#!/usr/bin/env python3
"""
================================================================================
 ETF INVESTOR BRO v4  —  complete personal investing platform
================================================================================
 Run:    python -m streamlit run etf_app.py
 Mobile: open the Network URL from terminal on any device on the same WiFi
 Deploy: push to GitHub -> share.streamlit.io
================================================================================
 NEW IN v4:
   • Wealth Target Goal Planner       • Annual Returns Heatmap
   • Crash & Recovery Analyzer        • Market Sentiment (Fear & Greed)
   • Portfolio Overlap Analyzer       • Dividend Income Tracker
   • Portfolio Drift Monitor          • Macro Context (VIX, Rates, DXY)
   • Smart Daily Recommendations      • World News impacting ETFs
================================================================================
"""
import datetime as dt, json, os, base64, numpy as np, pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import yfinance as yf
from PIL import Image as _PIL_Image

# ================================================================ CONSTANTS
OWNED          = ["VOO", "VGT", "SMH", "VXUS", "SCHG"]
RF             = 0.02
PORTFOLIO_FILE = Path(__file__).parent / "portfolio.json"
TARGETS_FILE   = Path(__file__).parent / "targets.json"

CRASHES = {
    "2008 Financial Crisis": ("2007-10-09", "2009-03-09"),
    "2020 COVID Crash":      ("2020-02-19", "2020-03-23"),
    "2022 Bear Market":      ("2021-12-27", "2022-10-12"),
}

CATALOG = {
    "VOO":dict(name="Vanguard S&P 500",cat="core",role="US S&P 500",er=0.03),
    "VTI":dict(name="Vanguard Total US Market",cat="core",role="US Total Market",er=0.03),
    "SCHB":dict(name="Schwab US Broad Market",cat="core",role="US Total Market",er=0.03),
    "IVV":dict(name="iShares Core S&P 500",cat="core",role="US S&P 500",er=0.03),
    "SPY":dict(name="SPDR S&P 500",cat="core",role="US S&P 500",er=0.0945),
    "SCHG":dict(name="Schwab US Large-Cap Growth",cat="growth",role="US Growth",er=0.04),
    "VUG":dict(name="Vanguard Growth",cat="growth",role="US Growth",er=0.04),
    "QQQ":dict(name="Invesco QQQ (Nasdaq-100)",cat="growth",role="Nasdaq-100",er=0.20),
    "QQQM":dict(name="Invesco Nasdaq-100",cat="growth",role="Nasdaq-100",er=0.15),
    "IWF":dict(name="iShares Russell 1000 Growth",cat="growth",role="US Growth",er=0.19),
    "MGK":dict(name="Vanguard Mega Cap Growth",cat="growth",role="Mega-cap Growth",er=0.07),
    "VGT":dict(name="Vanguard Info Technology",cat="tech",role="Tech sector",er=0.09),
    "XLK":dict(name="Tech Select Sector SPDR",cat="tech",role="Tech sector",er=0.08),
    "FTEC":dict(name="Fidelity MSCI Info Tech",cat="tech",role="Tech sector",er=0.084),
    "IYW":dict(name="iShares US Technology",cat="tech",role="Tech sector",er=0.38),
    "SMH":dict(name="VanEck Semiconductor",cat="semis",role="Semiconductors",er=0.35),
    "SOXX":dict(name="iShares Semiconductor",cat="semis",role="Semiconductors",er=0.34),
    "MAGS":dict(name="Roundhill Magnificent 7",cat="tech",role="Mag-7",er=0.29),
    "SCHD":dict(name="Schwab US Dividend Equity",cat="dividend",role="US Dividend",er=0.06),
    "VYM":dict(name="Vanguard High Dividend",cat="dividend",role="US Dividend",er=0.04),
    "DGRO":dict(name="iShares Core Dividend Growth",cat="dividend",role="Dividend Growth",er=0.08),
    "VIG":dict(name="Vanguard Dividend Appreciation",cat="dividend",role="Dividend Growth",er=0.05),
    "DGRW":dict(name="WisdomTree US Quality Div Growth",cat="dividend",role="Dividend Growth",er=0.28),
    "VLUE":dict(name="iShares MSCI USA Value",cat="value",role="US Value",er=0.15),
    "MTUM":dict(name="iShares MSCI USA Momentum",cat="factor",role="Momentum",er=0.15),
    "QUAL":dict(name="iShares MSCI USA Quality",cat="factor",role="Quality",er=0.15),
    "USMV":dict(name="iShares MSCI USA Min Vol",cat="factor",role="Low Volatility",er=0.15),
    "SPMO":dict(name="Invesco S&P 500 Momentum",cat="factor",role="Momentum",er=0.13),
    "COWZ":dict(name="Pacer US Cash Cows 100",cat="value",role="Value/Cash Flow",er=0.49),
    "XLV":dict(name="Health Care Select SPDR",cat="sector",role="Healthcare",er=0.09),
    "XLF":dict(name="Financial Select SPDR",cat="sector",role="Financials",er=0.09),
    "XLE":dict(name="Energy Select SPDR",cat="sector",role="Energy",er=0.09),
    "XLP":dict(name="Consumer Staples SPDR",cat="sector",role="Consumer Staples",er=0.09),
    "XLU":dict(name="Utilities Select SPDR",cat="sector",role="Utilities",er=0.09),
    "XLI":dict(name="Industrial Select SPDR",cat="sector",role="Industrials",er=0.09),
    "XLY":dict(name="Consumer Disc. SPDR",cat="sector",role="Consumer Discretionary",er=0.09),
    "XLB":dict(name="Materials Select SPDR",cat="sector",role="Materials",er=0.09),
    "XLC":dict(name="Communication Svcs SPDR",cat="sector",role="Communications",er=0.09),
    "XLRE":dict(name="Real Estate Select SPDR",cat="sector",role="Real Estate",er=0.09),
    "VXUS":dict(name="Vanguard Total International",cat="intl",role="International",er=0.05),
    "VEA":dict(name="Vanguard Developed Markets",cat="intl",role="Intl Developed",er=0.03),
    "VWO":dict(name="Vanguard Emerging Markets",cat="intl",role="Emerging Markets",er=0.07),
    "IEFA":dict(name="iShares Core MSCI EAFE",cat="intl",role="Intl Developed",er=0.07),
    "IEMG":dict(name="iShares Core Emerging Mkts",cat="intl",role="Emerging Markets",er=0.09),
    "DXJ":dict(name="WisdomTree Japan Hedged",cat="intl",role="Japan",er=0.48),
    "VT":dict(name="Vanguard Total World",cat="intl",role="Global All-Cap",er=0.06),
    "VEU":dict(name="Vanguard All-World ex-US",cat="intl",role="International",er=0.04),
    "IJR":dict(name="iShares Core S&P Small-Cap",cat="smallmid",role="Small Cap",er=0.06),
    "IJH":dict(name="iShares Core S&P Mid-Cap",cat="smallmid",role="Mid Cap",er=0.05),
    "VB":dict(name="Vanguard Small-Cap",cat="smallmid",role="Small Cap",er=0.05),
    "VO":dict(name="Vanguard Mid-Cap",cat="smallmid",role="Mid Cap",er=0.04),
    "IWM":dict(name="iShares Russell 2000",cat="smallmid",role="Small Cap",er=0.19),
    "VNQ":dict(name="Vanguard Real Estate",cat="realasset",role="Real Estate",er=0.13),
    "SCHH":dict(name="Schwab US REIT",cat="realasset",role="Real Estate",er=0.07),
    "GLDM":dict(name="SPDR Gold MiniShares",cat="realasset",role="Gold",er=0.10),
    "GLD":dict(name="SPDR Gold Trust",cat="realasset",role="Gold",er=0.40),
    "IAU":dict(name="iShares Gold Trust",cat="realasset",role="Gold",er=0.25),
    "SLV":dict(name="iShares Silver Trust",cat="realasset",role="Silver",er=0.50),
    "PDBC":dict(name="Invesco Optimum Yield Commodities",cat="realasset",role="Commodities",er=0.59),
    "BND":dict(name="Vanguard Total Bond",cat="bond",role="US Bonds",er=0.03),
    "AGG":dict(name="iShares Core US Aggregate Bond",cat="bond",role="US Bonds",er=0.03),
    "TLT":dict(name="iShares 20+ Year Treasury",cat="bond",role="Long Treasury",er=0.15),
    "IEF":dict(name="iShares 7-10 Year Treasury",cat="bond",role="Mid Treasury",er=0.15),
    "SGOV":dict(name="iShares 0-3 Month Treasury",cat="bond",role="Cash/T-Bills",er=0.09),
    "SCHP":dict(name="Schwab US TIPS",cat="bond",role="Inflation-Protected",er=0.03),
    "TIP":dict(name="iShares TIPS Bond",cat="bond",role="Inflation-Protected",er=0.19),
    "BNDX":dict(name="Vanguard Total Intl Bond",cat="bond",role="Intl Bonds",er=0.07),
    "ARKK":dict(name="ARK Innovation",cat="thematic",role="Disruptive Innovation",er=0.75),
    "PAVE":dict(name="Global X US Infrastructure",cat="thematic",role="Infrastructure",er=0.47),
    "IFRA":dict(name="iShares US Infrastructure",cat="thematic",role="Infrastructure",er=0.30),
    "ICLN":dict(name="iShares Global Clean Energy",cat="thematic",role="Clean Energy",er=0.41),
    "JEPI":dict(name="JPMorgan Equity Premium Income",cat="dividend",role="Covered-Call Income",er=0.35),
    "JEPQ":dict(name="JPMorgan Nasdaq Equity Premium",cat="dividend",role="Covered-Call Income",er=0.35),
}
CAT_LABEL   = {"core":"US Core","growth":"Growth","tech":"Tech","semis":"Semis",
               "dividend":"Dividend","value":"Value","factor":"Factor","sector":"Sector",
               "intl":"International","smallmid":"Small/Mid","realasset":"Real Asset",
               "bond":"Bond","thematic":"Thematic","custom":"Custom"}
MEGACAP     = ["NVDA","AAPL","MSFT","AMZN","GOOGL","META","TSLA"]
RANGES      = {"1D":("intraday","1d","5m"),"1W":("intraday","5d","15m"),
               "1M":("daily",30,None),"1Y":("daily",365,None),
               "3Y":("daily",3*365,None),"5Y":("daily",5*365,None),
               "10Y/MAX":("daily",10*365,None)}

# ================================================================ DATA LAYER

@st.cache_data(ttl=60*60*6, show_spinner=False)
def load_prices(tickers: tuple, days: int = 3650) -> pd.DataFrame:
    end   = dt.date.today()
    start = end - dt.timedelta(days=days+15)
    df = yf.download(list(tickers), start=start, end=end, auto_adjust=True, progress=False)["Close"]
    if isinstance(df, pd.Series): df = df.to_frame(name=tickers[0])
    return df.dropna(how="all")

@st.cache_data(ttl=60*5, show_spinner=False)
def load_intraday(tickers: tuple, period: str, interval: str) -> pd.DataFrame:
    df = yf.download(list(tickers), period=period, interval=interval,
                     auto_adjust=True, progress=False)["Close"]
    if isinstance(df, pd.Series): df = df.to_frame(name=tickers[0])
    return df.dropna(how="all")

def trailing_ann(s: pd.Series, years: int):
    cut = s.index[-1] - pd.DateOffset(years=years)
    sub = s[s.index >= cut].dropna()
    if len(sub) < 2: return np.nan
    r = sub.iloc[-1] / sub.iloc[0] - 1
    return ((1+r)**(1/years)-1)*100

def compute_metrics(prices: pd.DataFrame, bench: str = "VOO") -> pd.DataFrame:
    rows, bench_ret, bench_y5 = [], None, np.nan
    if bench in prices.columns:
        bench_ret = prices[bench].pct_change().dropna()
        bench_y5  = trailing_ann(prices[bench].dropna(), 5)
    for t in prices.columns:
        s = prices[t].dropna()
        if len(s) < 30: continue
        rets = s.pct_change().dropna()
        yrs  = (s.index[-1]-s.index[0]).days/365.25
        cagr = (s.iloc[-1]/s.iloc[0])**(1/max(yrs,0.1))-1
        vol  = float(rets.std())*np.sqrt(252)
        down = float(rets[rets<0].std())*np.sqrt(252)
        cum  = (1+rets).cumprod()
        mdd  = float(((cum-cum.cummax())/cum.cummax()).min())
        corr = np.nan
        if bench_ret is not None and t != bench:
            al = pd.concat([rets, bench_ret], axis=1, sort=False).dropna()
            corr = float(al.iloc[:,0].corr(al.iloc[:,1])) if len(al)>2 else np.nan
        elif t == bench: corr = 1.0
        y5   = trailing_ann(s, 5)
        meta = CATALOG.get(t, dict(name=t, cat="custom", role="Custom", er=np.nan))
        rows.append(dict(
            Ticker=t, Name=meta["name"], Category=CAT_LABEL.get(meta["cat"],""),
            Held="\u2705" if t in OWNED else "",
            Price=round(float(s.iloc[-1]),2), ER=meta["er"],
            **{"1Y TR %":round(trailing_ann(s,1),1),"3Y Ann %":round(trailing_ann(s,3),1),
               "5Y Ann %":round(y5,1),"10Y Ann %":round(trailing_ann(s,10),1)},
            **{"Vol %":round(vol*100,1),
               "Sharpe":round((cagr-RF)/vol,2) if vol>0 else np.nan,
               "Sortino":round((cagr-RF)/down,2) if down>0 else np.nan,
               "Max DD %":round(mdd*100,1),
               "Corr\u2192VOO":round(corr,2) if pd.notna(corr) else np.nan,
               "vs S&P 5Y":round(y5-bench_y5,1) if pd.notna(y5) and pd.notna(bench_y5) else np.nan}))
    return pd.DataFrame(rows)

def compute_rsi(s: pd.Series, period: int = 14) -> pd.Series:
    delta = s.diff()
    gain  = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    loss  = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100-(100/(1+rs))

def compute_signals(prices: pd.DataFrame) -> dict:
    out = {}
    for t in prices.columns:
        s = prices[t].dropna()
        if len(s)<55: continue
        rsi    = compute_rsi(s)
        ma50   = s.rolling(50).mean()
        ma200  = s.rolling(200).mean() if len(s)>=200 else None
        price  = float(s.iloc[-1])
        hi52   = float(s[-252:].max()) if len(s)>=252 else float(s.max())
        lo52   = float(s[-252:].min()) if len(s)>=252 else float(s.min())
        golden = bool(float(ma50.iloc[-1])>float(ma200.iloc[-1])) if ma200 is not None else None
        r1m    = (s.iloc[-1]/s.iloc[-22]-1)*100 if len(s)>=22 else np.nan
        r3m    = (s.iloc[-1]/s.iloc[-66]-1)*100 if len(s)>=66 else np.nan
        out[t] = dict(rsi=round(float(rsi.iloc[-1]),1), price=price,
                      ma50=round(float(ma50.iloc[-1]),2),
                      ma200=round(float(ma200.iloc[-1]),2) if ma200 is not None else None,
                      hi52=hi52, lo52=lo52,
                      pct_from_hi=round((price-hi52)/hi52*100,1),
                      pct_from_lo=round((price-lo52)/lo52*100,1),
                      golden=golden,
                      ret_1m=round(float(r1m),1), ret_3m=round(float(r3m),1))
    return out

# ================================================================ NEW: ANNUAL HEATMAP

def compute_annual_returns(prices: pd.DataFrame) -> pd.DataFrame:
    result = {}
    for t in prices.columns:
        s = prices[t].dropna()
        yr_rets = {}
        for yr in sorted(s.index.year.unique()):
            yd = s[s.index.year==yr]
            if len(yd)>20:
                yr_rets[yr] = round((yd.iloc[-1]/yd.iloc[0]-1)*100, 1)
        result[t] = yr_rets
    df = pd.DataFrame(result).T
    df.index.name = "ETF"
    return df

# ================================================================ NEW: CRASH & RECOVERY

def compute_crash_recovery(s: pd.Series) -> list:
    results = []
    for name, (p_str, t_str) in CRASHES.items():
        p_dt, t_dt = pd.Timestamp(p_str), pd.Timestamp(t_str)
        before = s[s.index <= p_dt]
        if before.empty: continue
        peak = float(before.iloc[-1])
        during = s[(s.index >= p_dt) & (s.index <= t_dt + pd.Timedelta(days=90))]
        if during.empty: continue
        trough = float(during.min())
        if peak == 0: continue
        dd = (trough-peak)/peak*100
        after = s[s.index > t_dt]
        rec   = after[after >= peak]
        rm    = round((rec.index[0]-t_dt).days/30.4, 0) if not rec.empty else None
        results.append({"event":name,"drawdown_pct":round(dd,1),
                        "trough":t_dt.strftime("%b %Y"),
                        "recovery_months":rm, "recovered": not rec.empty})
    return results

# ================================================================ NEW: OVERLAP ANALYZER

@st.cache_data(ttl=60*60*12, show_spinner=False)
def get_fund_overview(ticker: str) -> dict:
    out = dict(top_holdings=None, sector_weights=None, description=None, category=None, error=None)
    try:
        fd = yf.Ticker(ticker).funds_data
        for attr, key in [("top_holdings","top_holdings"),("sector_weightings","sector_weights"),
                          ("description","description")]:
            try:
                val = getattr(fd, attr)
                if val is not None and (not hasattr(val,"empty") or not val.empty):
                    out[key] = val
            except Exception: pass
        try: out["category"] = (fd.fund_overview or {}).get("categoryName")
        except Exception: pass
    except Exception as e: out["error"] = str(e)
    return out

def compute_overlap(focus: str, compare: list) -> dict:
    focus_ov = get_fund_overview(focus)
    focus_th = focus_ov.get("top_holdings")
    if focus_th is None or focus_th.empty: return {}
    if "Holding Percent" not in focus_th.columns: return {}
    focus_h  = {s: float(focus_th.loc[s,"Holding Percent"])*100 for s in focus_th.index}
    overlap  = {}
    for t in compare:
        if t == focus: continue
        ov = get_fund_overview(t)
        th = ov.get("top_holdings")
        if th is None or th.empty or "Holding Percent" not in th.columns: continue
        t_h = {s: float(th.loc[s,"Holding Percent"])*100 for s in th.index}
        for stock in focus_h:
            if stock in t_h:
                if stock not in overlap:
                    overlap[stock] = {"in_focus": focus_h[stock], "in_others": {}}
                overlap[stock]["in_others"][t] = t_h[stock]
    return overlap

# ================================================================ NEW: LIVE QUOTES (3-min cache)

@st.cache_data(ttl=60*3, show_spinner=False)
def get_live_quotes(tickers: tuple) -> dict:
    """
    Current prices that match what a broker (Schwab, Fidelity) shows.

    KEY: uses RAW / UNADJUSTED prices (auto_adjust=False) so the number equals
    the actual market price your broker displays. (Our historical metrics use
    auto_adjust=True for total-return math — that's correct there, but adjusted
    prices are dividend-back-adjusted and won't match a broker's quote.)

    Day-change = (last_price - previous_close) / previous_close, exactly the
    basis brokers use. Primary source is yf fast_info (last_price +
    previous_close, both raw). Falls back to a raw daily download.

    Yahoo's free data is ~15 min delayed during market hours — unavoidable
    without a paid real-time feed. After close, prices match the broker exactly.
    Returns: dict  ticker -> {price, prev_close, chg_pct, as_of, source}
    """
    quotes = {}
    for t in tickers:
        price = prev = None
        as_of = "~15 min delayed"
        source = "fast_info"
        # ---- Primary: fast_info (raw last price + official previous close) ----
        try:
            fi = yf.Ticker(t).fast_info
            price = fi.get("last_price") or fi.get("lastPrice")
            prev  = fi.get("previous_close") or fi.get("previousClose")
        except Exception:
            pass
        # ---- Fallback: raw daily bars (auto_adjust=False = broker prices) ----
        if price is None or prev is None:
            try:
                h = yf.download(t, period="5d", interval="1d",
                                auto_adjust=False, progress=False)["Close"].dropna()
                if len(h) >= 2:
                    today = dt.date.today()
                    # If last bar is today's (partial) bar, prev close is the one before
                    if h.index[-1].date() == today:
                        if price is None: price = float(h.iloc[-1])
                        if prev  is None: prev  = float(h.iloc[-2])
                    else:
                        if price is None: price = float(h.iloc[-1])
                        if prev  is None: prev  = float(h.iloc[-2])
                    source = "daily close (raw)"
                    as_of  = h.index[-1].strftime("%b %d")
                elif len(h) == 1 and price is None:
                    price = float(h.iloc[-1]); prev = price
            except Exception:
                pass
        if price is None:
            continue
        chg = ((price - prev) / prev * 100) if prev else 0.0
        quotes[t] = {
            "price":      round(float(price), 2),
            "prev_close": round(float(prev), 2) if prev else None,
            "chg_pct":    round(float(chg), 2),
            "as_of":      as_of,
            "source":     source,
        }
    return quotes

def get_market_status() -> dict:
    """Check whether NYSE is currently open (no external API needed)."""
    try:
        import pytz
        et = dt.datetime.now(pytz.timezone("America/New_York"))
    except Exception:
        # Rough UTC-4 approximation (EDT) if pytz not installed
        et = dt.datetime.utcnow() - dt.timedelta(hours=4)
    is_weekday = et.weekday() < 5
    is_hours   = dt.time(9, 30) <= et.time() <= dt.time(16, 0)
    is_open    = is_weekday and is_hours
    return {
        "is_open": is_open,
        "label":   "\U0001f7e2 MARKET OPEN" if is_open else "\U0001f534 MARKET CLOSED",
        "tip":     "prices ~15 min delayed" if is_open else "showing last close",
        "time_et": et.strftime("%H:%M ET"),
    }

# ================================================================ NEW: MARKET DATA

@st.cache_data(ttl=60*60*3, show_spinner=False)
def get_fear_greed() -> dict:
    import requests
    # Try feargreedchart.com (stock-market specific, free, no key)
    try:
        r = requests.get("https://feargreedchart.com/api/?action=all", timeout=8)
        if r.status_code == 200:
            data = r.json()
            score = (data.get("score") or {}).get("score")
            if score is not None:
                val = int(score)
                hist = []
                raw_hist = (data.get("history") or {}).get("scores", [])
                for item in raw_hist[:30]:
                    try:
                        hist.append({"date": item.get("date",""), "value": int(item.get("score",50))})
                    except Exception:
                        pass
                return {"value": val,
                        "label": ("Extreme Fear" if val<=20 else "Fear" if val<=40
                                  else "Neutral" if val<=60 else "Greed" if val<=80 else "Extreme Greed"),
                        "source": "feargreedchart.com", "history": hist}
    except Exception:
        pass
    # Fallback: compute from VIX + SPY RSI (no external API required)
    try:
        raw = yf.download(["^VIX","SPY"], period="3mo", auto_adjust=True, progress=False)["Close"]
        if isinstance(raw, pd.Series): raw = raw.to_frame()
        vix_s = raw["^VIX"].dropna() if "^VIX" in raw.columns else pd.Series(dtype=float)
        spy_s = raw["SPY"].dropna()   if "SPY"  in raw.columns else pd.Series(dtype=float)
        vix_v = float(vix_s.iloc[-1]) if not vix_s.empty else 20.0
        spy_rsi_v = float(compute_rsi(spy_s).iloc[-1]) if len(spy_s)>20 else 50.0
        ma200 = spy_s.rolling(200).mean()
        above = float(spy_s.iloc[-1]) > float(ma200.iloc[-1]) if len(ma200.dropna())>0 else True
        vix_score   = max(0, min(100, 100-(vix_v-10)*2.5))
        trend_score = 70 if above else 30
        val = max(0, min(100, round(vix_score*0.5 + spy_rsi_v*0.3 + trend_score*0.2)))
        return {"value": val,
                "label": ("Extreme Fear" if val<=20 else "Fear" if val<=40
                          else "Neutral" if val<=60 else "Greed" if val<=80 else "Extreme Greed"),
                "source": "computed (VIX+RSI)", "history": []}
    except Exception:
        return {"value": 50, "label": "Neutral", "source": "unavailable", "history": []}

@st.cache_data(ttl=60*60*6, show_spinner=False)
def get_macro_snapshot() -> dict:
    symbols = {"VIX":"^VIX","10Y Rate":"^TNX","US Dollar":"DX-Y.NYB","Oil":"CL=F"}
    try:
        raw = yf.download(list(symbols.values()), period="3mo", auto_adjust=True, progress=False)["Close"]
        if isinstance(raw, pd.Series): raw = raw.to_frame()
        out = {}
        for label, sym in symbols.items():
            if sym not in raw.columns: continue
            s = raw[sym].dropna()
            if s.empty: continue
            curr  = round(float(s.iloc[-1]), 2)
            chg1m = round((s.iloc[-1]/s.iloc[-22]-1)*100, 1) if len(s)>=22 else None
            out[label] = {"current": curr, "chg_1m": chg1m, "sym": sym, "series": s}
        return out
    except Exception:
        return {}

@st.cache_data(ttl=60*60*24, show_spinner=False)
def get_dividend_info(tickers: tuple) -> dict:
    out = {}
    for t in tickers:
        try:
            dy = (yf.Ticker(t).info or {}).get("dividendYield") or 0
            out[t] = round(float(dy)*100, 2)
        except Exception:
            out[t] = CATALOG.get(t, {}).get("er", 0) * 0  # 0 default
    return out

@st.cache_data(ttl=60*60*2, show_spinner=False)
def get_market_news() -> list:
    """Pull news from broad market tickers + held ETFs for macro context."""
    articles, seen = [], set()
    sources = list(OWNED) + ["SPY","QQQ"]
    for t in sources:
        try:
            raw = yf.Ticker(t).news or []
            for item in raw[:3]:
                content = item.get("content", {})
                title   = content.get("title","") if content else item.get("title","")
                url     = (content.get("canonicalUrl") or {}).get("url","") if content else item.get("link","")
                pub     = (content.get("provider") or {}).get("displayName","") if content else item.get("publisher","")
                ptime   = content.get("pubDate","") if content else str(item.get("providerPublishTime",""))
                if title and title not in seen:
                    seen.add(title)
                    articles.append(dict(ticker=t, title=title, url=url,
                                         publisher=pub, time=ptime))
        except Exception: pass
    articles.sort(key=lambda x: x.get("time",""), reverse=True)
    return articles[:30]

# ================================================================ NEW: SMART RECOMMENDATIONS

def _rec_reason(cat, sharpe, avg_corr, fg, cat_count):
    r = []
    if sharpe > 0.8:   r.append("strong 3M momentum")
    if avg_corr < 0.5: r.append("genuine diversifier")
    if cat_count == 0: r.append("fills a portfolio gap")
    if fg <= 30 and cat in {"bond","realasset","dividend","value"}:
        r.append("defensive in fearful market")
    elif fg >= 70 and cat in {"tech","semis","growth","thematic"}:
        r.append("momentum pick in bullish market")
    return " \u00b7 ".join(r) if r else "balanced risk-adjusted pick"

@st.cache_data(ttl=60*60*4, show_spinner=False)
def smart_recommendations(owned: tuple, sel: tuple, fg_val: int = 50) -> list:
    candidates = [t for t in list(CATALOG)[:50] if t not in sel]
    try:
        px = yf.download(candidates + list(sel), period="6mo",
                         auto_adjust=True, progress=False)["Close"]
        if isinstance(px, pd.Series): px = px.to_frame()
        held_cats = [CATALOG.get(t,{}).get("cat","") for t in owned]
        results   = []
        for t in candidates:
            if t not in px.columns: continue
            s = px[t].dropna()
            if len(s) < 45: continue
            rets = s.pct_change().dropna()
            r3m  = (s.iloc[-1]/s.iloc[-66]-1)*100 if len(s)>=66 else np.nan
            vol  = float(rets.std())*np.sqrt(252)*100
            sharpe = (r3m-0.5)/vol if vol>0 and pd.notna(r3m) else -99
            corr_list = []
            for h in sel:
                if h in px.columns:
                    al = pd.concat([rets, px[h].pct_change().dropna()], axis=1, sort=False).dropna()
                    if len(al)>10: corr_list.append(float(al.iloc[:,0].corr(al.iloc[:,1])))
            avg_corr = np.mean(corr_list) if corr_list else 0.5
            meta = CATALOG.get(t, {})
            cat  = meta.get("cat","")
            er   = meta.get("er", 0.3)
            cat_count    = held_cats.count(cat)
            sector_score = 1.0/(1+cat_count)
            er_score     = max(0, 1-er*1.5)
            defensive    = {"bond","realasset","dividend","value","factor"}
            aggressive   = {"tech","semis","growth","thematic"}
            if fg_val <= 30:
                sent = 0.85 if cat in defensive else 0.25
            elif fg_val >= 70:
                sent = 0.85 if cat in aggressive else 0.30
            else:
                sent = 0.55
            sh_norm = min(max((sharpe+1)/4.0, 0), 1)
            corr_sc = max(0, 1-avg_corr)
            score   = (0.30*sh_norm + 0.20*sector_score + 0.20*corr_sc +
                       0.15*sent    + 0.15*er_score)
            results.append({"ticker":t, "name":meta.get("name",t),
                            "cat":CAT_LABEL.get(cat,""), "score":round(score,3),
                            "sharpe_3m":round(sharpe,2),
                            "ret_3m":round(r3m,1) if pd.notna(r3m) else None,
                            "avg_corr":round(avg_corr,2), "er":er,
                            "reason":_rec_reason(cat,sharpe,avg_corr,fg_val,cat_count)})
        results.sort(key=lambda x: -x["score"])
        return results[:6]
    except Exception:
        return []

# ================================================================ FUND VALIDATION

@st.cache_data(ttl=60*60*6, show_spinner=False)
def validate_ticker(ticker: str):
    ticker = ticker.strip().upper()
    if not ticker or not ticker.replace(".","").replace("-","").isalnum(): return None
    try:
        fi = yf.Ticker(ticker).fast_info
        p  = fi.get("lastPrice") or fi.get("last_price")
        return {"ticker": ticker, "price": float(p)} if p else None
    except Exception: return None

# ================================================================ MONTE CARLO

def monte_carlo(s: pd.Series, n_years=10, n_paths=2000, monthly_add=100.0) -> dict:
    rets    = s.pct_change().dropna()
    mu, sig = float(rets.mean()), float(rets.std())
    sv      = float(s.iloc[-1])
    rng     = np.random.default_rng(42)
    finals  = []
    for _ in range(n_paths):
        val = sv
        for day in range(n_years*252):
            val = val * np.exp(rng.normal(mu-0.5*sig**2, sig))
            if monthly_add>0 and day%21==0: val += monthly_add
        finals.append(val)
    finals.sort(); n = len(finals)
    return dict(p10=finals[int(n*.10)], p25=finals[int(n*.25)], p50=finals[int(n*.50)],
                p75=finals[int(n*.75)], p90=finals[int(n*.90)], current=sv)

# ================================================================ GOAL PLANNER

def goal_planner(target, current_pv, monthly_pmt, annual_rate, years):
    r = (1+annual_rate)**(1/12)-1
    n = years*12
    if r == 0:
        fv_pv  = current_pv
        fv_pmt = monthly_pmt*n
    else:
        fv_pv  = current_pv*(1+r)**n
        fv_pmt = monthly_pmt*((1+r)**n-1)/r
    total = fv_pv + fv_pmt
    shortfall = max(target - fv_pv, 0)
    req_pmt = shortfall*r/((1+r)**n-1) if r>0 and n>0 else (shortfall/n if n>0 else 0)
    return {"fv_pv":round(fv_pv), "fv_pmt":round(fv_pmt), "total":round(total),
            "req_pmt":round(max(req_pmt,0), 2)}

# ================================================================ PORTFOLIO (SUPABASE + LOCAL)

def _get_sb():
    try:
        from supabase import create_client
        url = (st.secrets.get("SUPABASE_URL","") if hasattr(st,"secrets") else "") \
              or os.environ.get("SUPABASE_URL","")
        key = (st.secrets.get("SUPABASE_KEY","") if hasattr(st,"secrets") else "") \
              or os.environ.get("SUPABASE_KEY","")
        if url and key: return create_client(url, key)
    except Exception: pass
    return None

def load_portfolio() -> list:
    sb = _get_sb()
    if sb:
        try:
            rows = sb.table("portfolio_trades").select("*").execute().data or []
            return [{"id":r["id"],"ticker":r["ticker"],"date":str(r["date_bought"]),
                     "amount":r["amount_usd"],"note":r.get("note","")} for r in rows]
        except Exception: pass
    try:
        return json.loads(PORTFOLIO_FILE.read_text()) if PORTFOLIO_FILE.exists() else []
    except Exception: return []

def save_portfolio(trades: list):
    sb = _get_sb()
    if sb:
        try:
            existing = sb.table("portfolio_trades").select("id").execute().data or []
            if existing:
                sb.table("portfolio_trades").delete().in_("id",[r["id"] for r in existing]).execute()
            if trades:
                sb.table("portfolio_trades").insert(
                    [{"id":t.get("id",str(dt.datetime.now().timestamp())),
                      "ticker":t["ticker"],"date_bought":t["date"],
                      "amount_usd":float(t["amount"]),"note":t.get("note","")}
                     for t in trades]).execute()
        except Exception: pass
    try: PORTFOLIO_FILE.write_text(json.dumps(trades, indent=2))
    except Exception: pass

def load_targets() -> dict:
    try:
        return json.loads(TARGETS_FILE.read_text()) if TARGETS_FILE.exists() else {}
    except Exception: return {}

def save_targets(targets: dict):
    try: TARGETS_FILE.write_text(json.dumps(targets, indent=2))
    except Exception: pass

# ================================================================ AI CONVERSATION PERSISTENCE

def save_conversation(conv_id: str, title: str, messages: list):
    """Upsert a conversation to Supabase."""
    sb = _get_sb()
    if sb:
        try:
            sb.table("ai_conversations").upsert({
                "id": conv_id, "title": title, "messages": messages,
                "updated_at": dt.datetime.utcnow().isoformat()
            }).execute()
        except Exception: pass

@st.cache_data(ttl=30, show_spinner=False)
def load_past_conversations() -> list:
    """Load past conversations from Supabase, newest first."""
    sb = _get_sb()
    if sb:
        try:
            res = (sb.table("ai_conversations")
                   .select("id,title,created_at,updated_at,messages")
                   .order("updated_at", desc=True)
                   .limit(25)
                   .execute())
            return res.data or []
        except Exception: pass
    return []

def delete_conversation(conv_id: str):
    sb = _get_sb()
    if sb:
        try: sb.table("ai_conversations").delete().eq("id", conv_id).execute()
        except Exception: pass

def build_memory_context(current_conv_id: str) -> str:
    """
    Extract the most recent advisor exchanges from past conversations
    and inject them as memory so Claude knows what it said before.
    Only pulls the first user question + first assistant reply from
    each of the last 4 conversations (keeps tokens low).
    """
    past = load_past_conversations()
    past = [c for c in past if c.get("id") != current_conv_id]
    if not past: return ""
    lines = ["MEMORY FROM PRIOR CONVERSATIONS (what the user asked and what you said):"]
    for conv in past[:4]:
        msgs = conv.get("messages", [])
        date = (conv.get("updated_at") or conv.get("created_at",""))[:10]
        user_q  = next((m["content"][:200] for m in msgs if m.get("role")=="user"), None)
        ai_resp = next((m["content"][:300] for m in msgs if m.get("role")=="assistant"), None)
        if user_q:
            lines.append(f"\n[{date}] User asked: \"{user_q}\"")
        if ai_resp:
            lines.append(f"You responded: \"{ai_resp}...\"")
    return "\n".join(lines) if len(lines) > 1 else ""


def compute_pnl(trades: list, prices: pd.DataFrame, live_quotes: dict = None) -> pd.DataFrame:
    rows = []
    for trade in trades:
        t, amount = trade["ticker"], float(trade["amount"])
        if t not in prices.columns: continue
        s = prices[t].dropna()
        buy_dt = pd.Timestamp(trade["date"])
        future = s[s.index >= buy_dt]
        buy_px = float(future.iloc[0]) if not future.empty else float(s.iloc[0])
        # Use live quote when available — most current price
        if live_quotes and t in live_quotes:
            curr_px = live_quotes[t]["price"]
        else:
            curr_px = float(s.iloc[-1])
        curr_v = (amount / buy_px) * curr_px
        gain   = curr_v - amount
        pct    = gain / amount * 100
        days   = max((pd.Timestamp.today() - buy_dt).days, 1)
        try:
            ann = pct if days < 14 else float(np.clip((curr_v/amount)**(365.0/days)-1, -0.999, 500)*100)
        except (OverflowError, ZeroDivisionError, ValueError):
            ann = pct
        rows.append({"ID": trade.get("id",""), "Ticker": t, "Date": trade["date"],
                     "Invested $": round(amount, 2), "Cur. Value $": round(curr_v, 2),
                     "Gain $": round(gain, 2), "Return %": round(pct, 2),
                     "Ann. %": round(ann, 2), "Days": days, "Note": trade.get("note","")})
    return pd.DataFrame(rows) if rows else pd.DataFrame()

# ================================================================ v5: HEALTH SCORE ENGINE

def compute_health_score(holdings_vals: dict, prices: pd.DataFrame) -> dict:
    """
    Transparent 5-factor portfolio grade (0-100 -> A-F). Self-built, no black box.
      1. Diversification breadth (20): distinct asset categories held
      2. Concentration (20): position sizing (VOO exempt up to 50% by design)
      3. Correlation redundancy (20): avg pairwise correlation of holdings
      4. Fee efficiency (20): dollar-weighted expense ratio
      5. Sector balance (20): aggregate tech/growth/semis weight
    """
    total = sum(holdings_vals.values())
    if total <= 0 or not holdings_vals:
        return {"score": 0, "grade": "\u2014", "factors": [], "total": 0}
    weights = {t: v/total for t, v in holdings_vals.items()}
    factors = []

    # 1 — breadth
    cats = set(CATALOG.get(t, {}).get("cat", "custom") for t in holdings_vals)
    breadth_pts = min(len(cats)/6, 1.0) * 20
    factors.append({"name": "Diversification breadth", "pts": round(breadth_pts,1), "max": 20,
                    "detail": f"{len(cats)} asset categories held (6+ for full marks)"})

    # 2 — concentration (VOO core exempt to 50%)
    conc_pen = 0.0
    for t, w in weights.items():
        limit = 0.50 if t == "VOO" else 0.25
        if w > limit: conc_pen += (w - limit) * 100
    conc_pts = max(0, 20 - conc_pen)
    worst = max(weights, key=weights.get)
    factors.append({"name": "Position concentration", "pts": round(conc_pts,1), "max": 20,
                    "detail": f"largest: {worst} at {weights[worst]*100:.0f}% "
                              f"(VOO allowed 50%, others 25%)"})

    # 3 — correlation redundancy
    corr_pts, corr_detail = 10.0, "insufficient data"
    tickers = [t for t in holdings_vals if t in prices.columns]
    if len(tickers) >= 2:
        rets = prices[tickers].pct_change().dropna()
        if len(rets) > 30:
            cm = rets.corr().values
            n  = len(tickers)
            avg_corr = (cm.sum() - n) / (n*n - n)
            corr_pts = max(0.0, min(20.0, (1.05 - avg_corr) * 40))
            corr_detail = f"avg pairwise correlation {avg_corr:.2f} (lower = truer diversification)"
    factors.append({"name": "Correlation redundancy", "pts": round(corr_pts,1), "max": 20,
                    "detail": corr_detail})

    # 4 — fee efficiency (dollar-weighted ER)
    w_er = sum(weights[t] * (CATALOG.get(t, {}).get("er") or 0.20) for t in weights)
    fee_pts = max(0.0, min(20.0, (0.40 - w_er) / 0.35 * 20))
    factors.append({"name": "Fee efficiency", "pts": round(fee_pts,1), "max": 20,
                    "detail": f"dollar-weighted expense ratio {w_er:.3f}% "
                              f"(\u22640.05% full marks)"})

    # 5 — sector balance (tech-family weight)
    tech_w = sum(w for t, w in weights.items()
                 if CATALOG.get(t, {}).get("cat") in ("tech","semis","growth"))
    sector_pts = 20.0 if tech_w <= 0.35 else max(0.0, 20 - (tech_w-0.35)*60)
    factors.append({"name": "Sector balance", "pts": round(sector_pts,1), "max": 20,
                    "detail": f"tech/growth/semis = {tech_w*100:.0f}% of portfolio "
                              f"(\u226435% full marks)"})

    score = round(sum(f["pts"] for f in factors), 1)
    grade = ("A" if score >= 85 else "B" if score >= 70 else
             "C" if score >= 55 else "D" if score >= 40 else "F")
    return {"score": score, "grade": grade, "factors": factors, "total": total}

# ================================================================ v5: TIME-WEIGHTED RETURN

def compute_twr(trades: list, prices: pd.DataFrame) -> dict:
    """
    True Time-Weighted Return: strips out WHEN you added money, isolating the
    strategy's own performance. Chain-links daily returns, adjusting the
    denominator on days cash flowed in:  factor_t = V_t / (V_{t-1} + flow_t).
    """
    if not trades: return {}
    try:
        events = {}
        for tr in trades:
            t = tr["ticker"]
            if t not in prices.columns: continue
            s = prices[t].dropna()
            bd = pd.Timestamp(tr["date"])
            fut = s[s.index >= bd]
            if fut.empty: continue
            d0, px0 = fut.index[0], float(fut.iloc[0])
            events.setdefault(d0, []).append((t, float(tr["amount"])/px0, float(tr["amount"])))
        if not events: return {}
        start = min(events)
        idx = prices.index[prices.index >= start]
        shares, factors, prev_v = {}, [], None
        for d in idx:
            flow = 0.0
            if d in events:
                for t, sh, amt in events[d]:
                    shares[t] = shares.get(t, 0) + sh
                    flow += amt
            v = sum(sh * float(prices[t].asof(d)) for t, sh in shares.items()
                    if t in prices.columns and pd.notna(prices[t].asof(d)))
            if prev_v is not None and (prev_v + flow) > 0:
                factors.append(v / (prev_v + flow))
            prev_v = v
        if not factors: return {}
        twr_total = float(np.prod(factors)) - 1
        days = max((idx[-1] - idx[0]).days, 1)
        twr_ann = (1 + twr_total) ** (365.0/days) - 1 if days >= 14 else twr_total
        return {"twr_total": round(twr_total*100, 2),
                "twr_ann":   round(float(np.clip(twr_ann*100, -99.9, 999)), 2),
                "days": days}
    except Exception:
        return {}

# ================================================================ v5: AGGREGATE EXPOSURE

def aggregate_exposure(holdings_vals: dict) -> dict:
    """
    Blend every held ETF's sector weights and top holdings, weighted by YOUR
    dollars, into one true portfolio-level exposure. Auto-adjusts when
    holdings change (add VNQ -> real estate appears instantly).
    """
    total = sum(holdings_vals.values())
    if total <= 0: return {}
    sectors, stocks = {}, {}
    for t, v in holdings_vals.items():
        ov = get_fund_overview(t)
        sw = ov.get("sector_weights") or {}
        for k, w in sw.items():
            if w and w > 0.001:
                key = k.replace("_"," ").title()
                sectors[key] = sectors.get(key, 0) + w * v
        th = ov.get("top_holdings")
        if th is not None and not th.empty and "Holding Percent" in th.columns:
            for sym, row in th.iterrows():
                w = float(row["Holding Percent"])
                if w <= 0: continue
                if sym not in stocks:
                    stocks[sym] = {"dollars": 0.0, "in_etfs": {}}
                stocks[sym]["dollars"] += w * v
                stocks[sym]["in_etfs"][t] = round(w*100, 1)
    sector_pct = {k: round(v/total*100, 1) for k, v in
                  sorted(sectors.items(), key=lambda x: -x[1])}
    stock_rows = [{"symbol": s, "pct_of_pf": round(d["dollars"]/total*100, 2),
                   "dollars": round(d["dollars"], 2), "in_etfs": d["in_etfs"]}
                  for s, d in stocks.items()]
    stock_rows.sort(key=lambda x: -x["pct_of_pf"])
    return {"sectors": sector_pct, "stocks": stock_rows, "total": total}

# ================================================================ v5: REBALANCING ASSISTANT

def rebalance_plan(actual_vals: dict, targets_pct: dict, contribution: float) -> dict:
    """
    Buy-only rebalancing: allocate the next contribution across underweight
    ETFs, proportional to each one's dollar deficit vs target. Never sells.
    """
    cur_total = sum(actual_vals.values())
    new_total = cur_total + contribution
    deficits  = {}
    for t, tgt in targets_pct.items():
        desired = new_total * tgt / 100.0
        deficits[t] = max(desired - actual_vals.get(t, 0.0), 0.0)
    tot_def = sum(deficits.values())
    if tot_def <= 0:
        n = max(len(targets_pct), 1)
        buys = {t: round(contribution/n, 2) for t in targets_pct}
    else:
        buys = {t: round(contribution * d / tot_def, 2) for t, d in deficits.items() if d > 0}
    after = {t: actual_vals.get(t,0) + buys.get(t,0) for t in targets_pct}
    after_pct = {t: round(v/new_total*100, 1) for t, v in after.items()} if new_total>0 else {}
    return {"buys": {t: b for t, b in buys.items() if b >= 0.01}, "after_pct": after_pct}

# ================================================================ v5: WHAT-IF LAB ENGINES

@st.cache_data(ttl=60*60*6, show_spinner=False)
def backtest_dca(ticker: str, monthly: float, start: str, _key: str = "") -> dict:
    """DCA backtest on real history: buy on first trading day each month."""
    try:
        px = yf.download(ticker, start=start, auto_adjust=True, progress=False)["Close"].dropna()
        if isinstance(px, pd.DataFrame): px = px.iloc[:, 0]
        if len(px) < 25: return {}
        monthly_firsts = px.groupby([px.index.year, px.index.month]).head(1)
        shares = invested = 0.0
        for d, p in monthly_firsts.items():
            shares += monthly / float(p); invested += monthly
        end_val = shares * float(px.iloc[-1])
        yrs = max((px.index[-1] - px.index[0]).days / 365.25, 0.1)
        return {"invested": round(invested, 2), "end_value": round(end_val, 2),
                "gain": round(end_val - invested, 2),
                "gain_pct": round((end_val/invested - 1) * 100, 1) if invested else 0,
                "n_buys": len(monthly_firsts), "years": round(yrs, 1)}
    except Exception:
        return {}

def backtest_swap(trades: list, swap_from: str, swap_to: str, prices_all: pd.DataFrame) -> dict:
    """Replay your ACTUAL trade history with one ticker swapped for another."""
    def _end_val(tks):
        total_in = total_out = 0.0
        for tr in tks:
            t = tr["ticker"]
            if t not in prices_all.columns: continue
            s = prices_all[t].dropna()
            bd = pd.Timestamp(tr["date"]); fut = s[s.index >= bd]
            if fut.empty: continue
            px0 = float(fut.iloc[0]); amt = float(tr["amount"])
            total_in  += amt
            total_out += amt / px0 * float(s.iloc[-1])
        return total_in, total_out
    real_in, real_out = _end_val(trades)
    swapped = [dict(tr, ticker=swap_to) if tr["ticker"] == swap_from else tr for tr in trades]
    _, swap_out = _end_val(swapped)
    return {"real_value": round(real_out, 2), "swap_value": round(swap_out, 2),
            "difference": round(swap_out - real_out, 2), "invested": round(real_in, 2)}

def compound_series(monthly: float, years: int, annual_rate: float, start_val: float = 0.0):
    """Exact monthly compounding series for the Money Machine visualizer."""
    r = (1 + annual_rate) ** (1/12) - 1
    vals, v = [], start_val
    for m in range(years * 12 + 1):
        vals.append(v)
        v = v * (1 + r) + monthly
    return pd.Series(vals, index=[m/12 for m in range(years*12 + 1)])

# ================================================================ v5: DIVIDEND TAX ESTIMATOR

def dividend_tax_estimate(div_by_ticker: dict, income_bracket: str) -> dict:
    """
    Informational estimate of tax owed on dividends (owed even if reinvested,
    in a taxable account). Qualified share per ETF type; rates by bracket.
    """
    QUAL_SHARE = {"VXUS": 0.70, "VEA": 0.72, "VWO": 0.60, "IEFA": 0.72, "IEMG": 0.60,
                  "BND": 0.0, "AGG": 0.0, "TLT": 0.0, "SGOV": 0.0, "JEPI": 0.20, "JEPQ": 0.20}
    qual_rate = {"~$0-47k (student)": 0.00, "$47k-100k": 0.15, "$100k-500k": 0.15, "$500k+": 0.20}[income_bracket]
    ord_rate  = {"~$0-47k (student)": 0.12, "$47k-100k": 0.22, "$100k-500k": 0.32, "$500k+": 0.37}[income_bracket]
    rows, total_tax, total_div = [], 0.0, 0.0
    for t, ann_div in div_by_ticker.items():
        qs   = QUAL_SHARE.get(t, 0.95)
        qtax = ann_div * qs * qual_rate
        otax = ann_div * (1-qs) * ord_rate
        tax  = qtax + otax
        rows.append({"Ticker": t, "Annual Div $": round(ann_div, 2),
                     "Qualified %": int(qs*100), "Est. Tax $": round(tax, 2)})
        total_tax += tax; total_div += ann_div
    return {"rows": rows, "total_tax": round(total_tax, 2), "total_div": round(total_div, 2),
            "qual_rate": qual_rate, "ord_rate": ord_rate}

# ================================================================ v5: INVESTOR PROFILE

PROFILE_FILE = Path(__file__).parent / "profile.json"

def load_profile() -> dict:
    sb = _get_sb()
    if sb:
        try:
            res = sb.table("user_profile").select("*").eq("id", "me").execute().data
            if res: return res[0].get("data", {}) or {}
        except Exception: pass
    try:
        return json.loads(PROFILE_FILE.read_text()) if PROFILE_FILE.exists() else {}
    except Exception: return {}

def save_profile(profile: dict):
    sb = _get_sb()
    if sb:
        try:
            sb.table("user_profile").upsert({"id": "me", "data": profile,
                "updated_at": dt.datetime.utcnow().isoformat()}).execute()
        except Exception: pass
    try: PROFILE_FILE.write_text(json.dumps(profile, indent=2))
    except Exception: pass

QUIZ = [
    ("horizon", "When will you realistically need this money?",
     [("Within 5 years", 1), ("5-15 years", 2), ("15-30 years", 3), ("30+ years \u2014 this is retirement money", 4)]),
    ("drawdown", "Your portfolio drops 35% in a crash. What do you actually do?",
     [("Sell everything \u2014 can't sleep", 1), ("Sell some, keep the rest", 2),
      ("Hold and wait it out", 3), ("Buy more \u2014 stocks are on sale", 4)]),
    ("income", "How stable is your income / cash cushion?",
     [("Unstable, no emergency fund", 1), ("Some savings, income varies", 2),
      ("Stable income, 3mo emergency fund", 3), ("Very stable + 6mo+ cushion", 4)]),
    ("knowledge", "How well do you understand what you own?",
     [("I buy what people recommend", 1), ("I know the basics of my ETFs", 2),
      ("I read holdings, fees, and metrics", 3), ("I analyze overlap, factor exposure, macro", 4)]),
    ("goal", "What is the primary job of this portfolio?",
     [("Preserve what I have", 1), ("Steady income", 2),
      ("Balanced growth", 3), ("Maximum long-term growth", 4)]),
    ("checking", "How often do you check your portfolio?",
     [("Multiple times a day \u2014 it stresses me", 1), ("Daily, calmly", 3),
      ("Weekly", 4), ("Monthly or less", 4)]),
]

def score_quiz(answers: dict) -> dict:
    total = sum(answers.values())
    max_t = len(QUIZ) * 4
    pct   = total / max_t
    if pct >= 0.85:
        ptype, desc = "Aggressive Growth Accumulator", \
            ("Long horizon, strong stomach, stable base. Equity-heavy portfolios (90-100% stocks) "
             "with growth tilts suit you. Your biggest risk isn't volatility \u2014 it's under-investing.")
    elif pct >= 0.65:
        ptype, desc = "Growth-Oriented Builder", \
            ("You can handle meaningful volatility for higher returns. 80-90% equities with a "
             "diversified core is your zone. Watch concentration in any single sector.")
    elif pct >= 0.45:
        ptype, desc = "Balanced Strategist", \
            ("You value growth but feel drawdowns. 60-75% equities with international and "
             "some defensive ballast (dividends, bonds) fits your temperament.")
    else:
        ptype, desc = "Capital Preserver", \
            ("Stability matters more than maximum growth right now. Broad core funds, "
             "dividend payers, and bonds deserve larger weights until your base strengthens.")
    return {"type": ptype, "description": desc, "score": total, "max": max_t,
            "pct": round(pct*100), "answers": answers,
            "taken_at": str(dt.date.today())}

# ================================================================ v5: GLOSSARY

GLOSSARY = {
    "Sharpe": "Return earned per unit of volatility you sat through, vs parking cash at 2%. Above 1.0 = you were well paid for the ride's bumps.",
    "Sortino": "Like Sharpe, but only counts DOWNWARD swings as risk \u2014 upside surprises don't get penalized.",
    "Max DD": "Max Drawdown: the worst peak-to-bottom fall in history. The pain you must be able to endure without selling.",
    "Vol": "Volatility: how violently the price swings around its average, annualized. Higher = wilder ride, not necessarily worse returns.",
    "Corr\u2192VOO": "Correlation to the S&P 500 from -1 to 1. Near 1.0 = moves in lockstep (little diversification). Below 0.6 = genuinely different behavior.",
    "ER": "Expense Ratio: the fund's annual fee, silently deducted. 0.03% = $3/yr per $10k. Compounds against you forever.",
    "TR": "Total Return: price change PLUS dividends reinvested \u2014 the real return an investor actually experienced.",
    "Ann": "Annualized: converted to a per-year rate so different time periods compare fairly.",
    "TWR": "Time-Weighted Return: your strategy's true performance with the timing of your deposits mathematically removed. The fair way to judge your picks.",
    "RSI": "Relative Strength Index (0-100): momentum gauge. Below 30 = historically oversold (potential value), above 70 = overheated.",
    "Golden cross": "50-day average price rises above the 200-day \u2014 a classic long-term bullish trend signal.",
    "Death cross": "50-day average falls below the 200-day \u2014 a bearish trend signal. Historically noisy, not destiny.",
    "DCA": "Dollar-Cost Averaging: investing a fixed amount on a schedule regardless of price. Buys more shares when cheap, fewer when expensive.",
    "HHI": "A concentration measure: sums squared weights. High = eggs in few baskets.",
    "Beta": "Sensitivity to the market: 1.3 beta rises/falls ~30% harder than the S&P 500.",
    "Qualified dividend": "Dividends taxed at the lower capital-gains rate (0% if your income is under ~$47k) instead of ordinary income rates.",
    "Roth IRA": "Retirement account: pay tax now, then ALL growth and withdrawals after 59\u00bd are tax-free forever. Best home for high-dividend funds.",
    "NAV": "Net Asset Value: the per-share worth of everything the fund holds.",
}

def gloss(term: str, label: str = None) -> str:
    """Wrap a term with a hover tooltip from the glossary."""
    tip = GLOSSARY.get(term, "")
    lbl = label or term
    if not tip: return lbl
    safe = tip.replace('"', '&quot;')
    return f'<span class="gl" title="{safe}">{lbl}</span>'

# ================================================================ UI SETUP
try:
    _icon = _PIL_Image.open(Path(__file__).parent/"icon.png")
    st.set_page_config(page_title="ETF Investor Bro", layout="wide",
                       page_icon=_icon, initial_sidebar_state="expanded")
except Exception:
    st.set_page_config(page_title="ETF Investor Bro", layout="wide",
                       page_icon="\U0001f4c8", initial_sidebar_state="expanded")

T = dict(bg="#0d1f2d", bg2="#132233", bg3="#1f3b4d",
         gold="#d4af37", orange="#f5900a",
         green="#00e676", red="#ff5252",
         text="#dde8f0", text2="#7a9db5", text3="#3d6070")

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&family=Oswald:wght@500;600;700&display=swap');
html,body,[class*="css"]{{font-family:'Roboto Mono',monospace;}}
.stApp{{background:{T['bg']} !important;}}
section[data-testid="stSidebar"]{{background:{T['bg2']};border-right:1px solid {T['bg3']};}}
.masthead{{display:flex;align-items:center;gap:16px;border-bottom:2px solid {T['gold']};padding-bottom:10px;margin-bottom:6px;}}
.masthead h1{{font-family:Oswald,sans-serif;font-weight:700;font-size:28px;letter-spacing:1px;color:{T['text']};margin:0;text-transform:uppercase;}}
.tag{{color:{T['text2']};font-size:11px;letter-spacing:1.5px;text-transform:uppercase;}}
.tape-wrap{{overflow:hidden;white-space:nowrap;background:{T['bg2']};border:1px solid {T['bg3']};border-radius:4px;padding:10px 0;margin:10px 0 18px;}}
.tape{{display:inline-block;animation:scroll-left 36s linear infinite;padding-left:100%;}}
.tape:hover{{animation-play-state:paused;}}
@keyframes scroll-left{{0%{{transform:translateX(0);}}100%{{transform:translateX(-100%);}}}}
.tape-item{{display:inline-block;margin-right:48px;font-size:14px;font-weight:500;}}
.tape-tk{{color:{T['text']};font-weight:700;}}
.up{{color:{T['green']};font-weight:600;}}.dn{{color:{T['red']};font-weight:600;}}
.lbl{{font-family:Oswald,sans-serif;font-size:12.5px;letter-spacing:2px;color:{T['gold']};text-transform:uppercase;margin:20px 0 10px;border-left:3px solid {T['gold']};padding-left:10px;}}
.board{{width:100%;border-collapse:collapse;font-size:13px;}}
.board th{{text-align:left;padding:9px 11px;color:{T['text2']};font-size:10px;letter-spacing:1px;text-transform:uppercase;border-bottom:1px solid {T['bg3']};background:{T['bg2']};position:sticky;top:0;}}
.board td{{padding:9px 11px;border-bottom:1px solid {T['bg3']};color:{T['text']};}}
.board tr:hover td{{background:{T['bg3']};}}
.row-h td:first-child{{border-left:3px solid {T['gold']};}}
.row-w td:first-child{{border-left:3px solid #4f8ef7;}}
.tk{{font-weight:700;font-size:14px;color:{T['text']};}}
.tkn{{font-size:10px;color:{T['text3']};display:block;margin-top:1px;}}
.htag{{font-size:8.5px;background:rgba(212,175,55,.18);color:{T['gold']};padding:1px 6px;border-radius:3px;margin-left:5px;letter-spacing:.5px;}}
.sbg{{background:{T['bg3']};border-radius:2px;height:12px;width:65px;display:inline-block;vertical-align:middle;overflow:hidden;margin-right:5px;}}
.sfill{{height:100%;background:linear-gradient(90deg,{T['bg3']},{T['gold']});}}
.card{{background:{T['bg2']};border:1px solid {T['bg3']};border-radius:8px;padding:16px 18px;margin-bottom:12px;}}
.news-item{{border-left:3px solid {T['orange']};padding:8px 12px;margin-bottom:8px;background:{T['bg2']};border-radius:0 6px 6px 0;}}
.news-tk{{font-size:10px;font-weight:700;color:{T['gold']};}}
.news-title{{font-size:13px;color:{T['text']};line-height:1.4;}}
.news-meta{{font-size:10.5px;color:{T['text3']};margin-top:3px;}}
.fg-box{{border-radius:10px;padding:20px;text-align:center;}}
.gl{{border-bottom:1px dotted {T['text2']};cursor:help;}}
.disclaim{{color:{T['text3']};font-size:10.5px;line-height:1.6;border-top:1px solid {T['bg3']};padding-top:14px;margin-top:24px;}}
</style>""", unsafe_allow_html=True)

# ================================================================ SESSION STATE
for k, v in [("selected",list(OWNED)),("selected_etf",None),
              ("ai_key",""),("ai_messages",[]),("show_overlap",False),
              ("conv_id", str(dt.datetime.now().timestamp())),
              ("conv_title", "New conversation"),
              ("viewing_past", None)]:
    if k not in st.session_state: st.session_state[k] = v

# ================================================================ SIDEBAR
with st.sidebar:
    st.markdown(f'<div style="font-family:Oswald;font-size:16px;color:{T["gold"]};'
                f'letter-spacing:1px;text-transform:uppercase;margin-bottom:12px;">'
                f'\u2699 Controls</div>', unsafe_allow_html=True)
    st.markdown("**Holdings (always shown):**")
    st.markdown(" ".join(f'<code style="background:{T["bg3"]};color:{T["gold"]};'
                         f'padding:2px 6px;border-radius:3px;">{t}</code>' for t in OWNED),
                unsafe_allow_html=True)
    st.markdown("---")
    addable = [f"{t} \u2014 {CATALOG[t]['name']}" for t in CATALOG if t not in st.session_state.selected]
    to_add  = st.multiselect("Add from 70+ ETF database:", addable, label_visibility="visible")
    for lbl in to_add:
        tk = lbl.split(" \u2014 ")[0]
        if tk not in st.session_state.selected: st.session_state.selected.append(tk)
    removable = [t for t in st.session_state.selected if t not in OWNED]
    if removable:
        to_rem = st.multiselect("Remove from watchlist:", removable)
        st.session_state.selected = [t for t in st.session_state.selected if t not in to_rem]
    st.markdown("---")
    ai_default = (st.secrets.get("ANTHROPIC_KEY","") if hasattr(st,"secrets") else "") \
                 or os.environ.get("ANTHROPIC_KEY","")
    if not st.session_state.ai_key and ai_default:
        st.session_state.ai_key = ai_default
    if not st.session_state.ai_key:
        st.markdown(f'<div style="font-size:10.5px;color:{T["gold"]};">\U0001f916 AI Advisor key</div>',
                    unsafe_allow_html=True)
        typed = st.text_input("Anthropic key:", type="password",
                              placeholder="sk-ant-...", label_visibility="collapsed")
        if typed: st.session_state.ai_key = typed; st.rerun()
        st.caption("Get free key at console.anthropic.com")
    else:
        st.markdown(f'<div style="font-size:10.5px;color:{T["green"]};">\U0001f916 AI Advisor: ready</div>',
                    unsafe_allow_html=True)
        if st.button("Clear AI key", use_container_width=False):
            st.session_state.ai_key = ""; st.rerun()
    st.markdown("---")
    new_tk = st.text_input("Add any ticker:", placeholder="JEPI, SPLG, NVDY\u2026")
    if st.button("\u2795 Add", use_container_width=True) and new_tk:
        info = validate_ticker(new_tk)
        if info is None: st.error(f"'{new_tk.upper()}' not found.")
        elif info["ticker"] in st.session_state.selected: st.info("Already added.")
        else:
            st.session_state.selected.append(info["ticker"])
            if info["ticker"] not in CATALOG:
                CATALOG[info["ticker"]] = dict(name=info["ticker"], cat="custom",
                                               role="Custom", er=float("nan"))
            st.success(f"Added {info['ticker']} @ ${info['price']:.2f}")
    st.markdown("---")
    mkt = get_market_status()
    mkt_color = T["green"] if mkt["is_open"] else T["red"]
    st.markdown(f'<div style="font-size:11px;color:{mkt_color};font-weight:600;">{mkt["label"]}</div>'
                f'<div style="font-size:10px;color:{T["text3"]};">{mkt["time_et"]} \u00b7 {mkt["tip"]}</div>',
                unsafe_allow_html=True)
    if st.button("\U0001f504 Refresh prices now", use_container_width=True):
        load_prices.clear()
        get_live_quotes.clear()
        get_market_news.clear()
        st.rerun()
    st.markdown(f'<div style="font-size:10.5px;color:{T["text3"]};line-height:1.7;margin-top:8px;">'
                f'\U0001f4f1 <b>Mobile:</b> Network URL in terminal \u2192 phone browser<br>'
                f'\U0001f310 <b>Live site:</b> push to GitHub \u2192 share.streamlit.io<br>'
                f'\U0001f504 Historical 6h \u00b7 live quotes 3min \u00b7 intraday 5min</div>',
                unsafe_allow_html=True)

sel = tuple(dict.fromkeys(st.session_state.selected))

# ================================================================ LOAD PRICES + LIVE QUOTES
with st.spinner(f"Fetching total-return history for {len(sel)} ETFs\u2026"):
    try:
        prices = load_prices(sel, days=3650)
    except Exception as e:
        st.error(f"Data fetch failed: {e}"); st.stop()

# Live quotes: short-cache refresh separate from historical bars
with st.spinner("Fetching current prices\u2026"):
    try:
        live_q = get_live_quotes(sel)
    except Exception:
        live_q = {}

mkt = get_market_status()

# ================================================================ MASTHEAD + TAPE
_icon_path = Path(__file__).parent/"icon.png"
_b64 = base64.b64encode(_icon_path.read_bytes()).decode() if _icon_path.exists() else ""
_img = f"<img src='data:image/png;base64,{_b64}' style='width:54px;height:54px;border-radius:10px;'>" if _b64 else ""

mkt_color = T["green"] if mkt["is_open"] else T["red"]
# Find the freshest quote timestamp across all tickers
_as_of_times = [q.get("as_of","") for q in live_q.values() if q.get("as_of","")]
_freshest    = max(_as_of_times) if _as_of_times else "historical close"

st.markdown(
    f'<div class="masthead">{_img}'
    f'<div style="flex:1;">'
    f'<h1>ETF INVESTOR BRO</h1>'
    f'<span class="tag">Total-Return Terminal \u00b7 Dividends Reinvested \u00b7 {dt.date.today()}</span>'
    f'</div>'
    f'<div style="text-align:right;">'
    f'<div style="font-size:12px;font-weight:700;color:{mkt_color};">{mkt["label"]}</div>'
    f'<div style="font-size:10px;color:{T["text3"]};">{mkt["time_et"]} \u00b7 quotes as of {_freshest}</div>'
    f'<div style="font-size:10px;color:{T["text3"]};">{mkt["tip"]} \u00b7 auto-refresh 3 min</div>'
    f'</div></div>',
    unsafe_allow_html=True)

# Ticker tape — uses live quotes for price & day-change
tape_html = ""
for t in sel:
    # Prefer live quote; fall back to last historical close
    q = live_q.get(t)
    if q:
        price  = q["price"]
        chg    = q.get("chg_pct", 0)
    elif t in prices.columns:
        s      = prices[t].dropna()
        if len(s) < 2: continue
        price  = float(s.iloc[-1])
        chg    = (s.iloc[-1]/s.iloc[-2]-1)*100
    else:
        continue
    cls = "up" if chg >= 0 else "dn"
    arr = "&#9650;" if chg >= 0 else "&#9660;"
    tape_html += (f'<span class="tape-item"><span class="tape-tk">{t}</span> '
                  f'${price:.2f} <span class="{cls}">{arr} {chg:+.2f}%</span></span>')
st.markdown(f'<div class="tape-wrap"><div class="tape">{tape_html*3}</div></div>',
            unsafe_allow_html=True)

# ================================================================ TABS
tab_board, tab_pf, tab_pulse, tab_lab, tab_ai, tab_profile, tab_chart = st.tabs([
    "\U0001f4cb  BOARD", "\U0001f4bc  MY PORTFOLIO",
    "\U0001f4f0  MARKET PULSE", "\U0001f9ea  WHAT-IF LAB",
    "\U0001f916  AI ADVISOR", "\U0001f464  MY PROFILE", "\U0001f4c8  CHART"])

# ================================================================ TAB 1: BOARD
with tab_board:
    st.markdown('<div class="lbl">Performance Board \u2014 Total Return (dividends reinvested, fees included)</div>',
                unsafe_allow_html=True)
    # Show data freshness note
    if live_q:
        as_of_list = [q.get("as_of","") for q in live_q.values() if q.get("as_of","")]
        fresh_str  = f"Prices as of {max(as_of_list)} (Yahoo ~15 min delayed)" if as_of_list else ""
        if fresh_str:
            st.caption(f"\U0001f551 {fresh_str} \u00b7 raw market prices (match your broker) \u00b7 "
                       f"{'Market open \u2014 updates every 3 min' if mkt['is_open'] else 'Market closed \u2014 showing last close'} "
                       f"\u00b7 hit \u201cRefresh prices now\u201d in sidebar to force update")
    dfm   = compute_metrics(prices, "VOO")
    order = {t:i for i,t in enumerate(sel)}
    dfm   = dfm.sort_values("Ticker", key=lambda c: c.map(lambda t: order.get(t,99)))

    def cell(v, suf="%", dp=1):
        if pd.isna(v): return f'<span style="color:{T["text3"]}">n/a</span>'
        cls, sign = ("up","+") if v>=0 else ("dn","")
        return f'<span class="{cls}">{sign}{v:.{dp}f}{suf}</span>'

    rows_html = ""
    for _, r in dfm.iterrows():
        held     = r["Ticker"] in OWNED
        held_tag = '<span class="htag">HELD</span>' if held else ""
        er_str   = f'{r["ER"]:.2f}%' if pd.notna(r["ER"]) else "\u2014"
        sh       = r["Sharpe"]
        sh_html  = (f'<span class="sbg"><span class="sfill" style="width:{max(min(sh/2.0,1),0)*100:.0f}%">'
                    f'</span></span>{sh:.2f}') if pd.notna(sh) else "n/a"
        corr_v   = r["Corr\u2192VOO"]
        corr_s   = "n/a" if pd.isna(corr_v) else f"{float(corr_v):.2f}"
        lq       = live_q.get(r["Ticker"], {})
        live_px  = lq.get("price")
        # Green dot ● next to price = live quote; no dot = historical close
        if live_px:
            price_html = (f'${live_px:.2f} '
                          f'<span style="color:{T["green"]};font-size:9px;" title="live quote">\u25cf</span>')
        else:
            price_html = f'${r["Price"]:.2f}'
        rows_html += (f'<tr class="{"row-h" if held else "row-w"}">'
            f'<td><span class="tk">{r["Ticker"]}</span>{held_tag}'
            f'<span class="tkn">{r["Category"]}</span></td>'
            f'<td>{price_html}</td><td>{er_str}</td>'
            f'<td>{cell(r["1Y TR %"])}</td><td>{cell(r["3Y Ann %"])}</td>'
            f'<td>{cell(r["5Y Ann %"])}</td><td>{cell(r["10Y Ann %"])}</td>'
            f'<td>{r["Vol %"]:.1f}%</td><td>{sh_html}</td>'
            f'<td class="dn">{r["Max DD %"]:.0f}%</td>'
            f'<td>{corr_s}</td>'
            f'<td>{cell(r["vs S&P 5Y"],suf=" pts")}</td></tr>')
    rows_html = rows_html.replace('\\"htag\\"', '"htag"')

    st.markdown(f'<div style="overflow-x:auto;border:1px solid {T["bg3"]};border-radius:6px;">'
                f'<table class="board"><thead><tr>'
                f'<th>ETF</th><th>Price</th><th>{gloss("ER","Expense")}</th>'
                f'<th>{gloss("TR","1Y TR")}</th><th>{gloss("Ann","3Y Ann")}</th>'
                f'<th>{gloss("Ann","5Y Ann")}</th><th>{gloss("Ann","10Y Ann")}</th>'
                f'<th>{gloss("Vol")}</th><th>{gloss("Sharpe","Sharpe\u2020")}</th>'
                f'<th>{gloss("Max DD")}</th>'
                f'<th>{gloss("Corr\u2192VOO")}</th><th>vs S&P 5Y</th></tr></thead>'
                f'<tbody>{rows_html}</tbody></table></div>', unsafe_allow_html=True)
    st.caption("Hover any dotted-underline term for a plain-English explanation. "
               "Total returns: dividends reinvested + fees already deducted. \u2020Sharpe uses 2% risk-free rate. Past performance \u2260 future results.")
    # Cost of waiting — worked into the board as requested
    if "VOO" in prices.columns:
        _voo10 = trailing_ann(prices["VOO"].dropna(), 10)
        if pd.notna(_voo10):
            _cost1y = 1000 * ((1 + _voo10/100) ** 1 - 1)
            st.markdown(f'<div style="font-size:11.5px;color:{T["orange"]};margin:4px 0 0;">'
                        f'\u23f3 <b>Cost of waiting:</b> at VOO\u2019s 10-yr average ({_voo10:.1f}%/yr), '
                        f'every $1,000 left uninvested for a year historically forfeited ~${_cost1y:,.0f} of growth '
                        f'\u2014 and that gap compounds for decades.</div>', unsafe_allow_html=True)

    # ---- Annual Returns Heatmap ----
    st.markdown('<div class="lbl">Annual Returns Heatmap \u2014 year-by-year at a glance</div>',
                unsafe_allow_html=True)
    with st.spinner("Building heatmap\u2026"):
        ar_df = compute_annual_returns(prices[[t for t in sel if t in prices.columns]])
    if not ar_df.empty:
        cols_sorted = sorted([c for c in ar_df.columns], key=lambda x: int(x))
        ar_plot     = ar_df[cols_sorted].astype(float)
        hfig = px.imshow(ar_plot, color_continuous_scale=[[0,"#c0392b"],[0.5,"#1f3b4d"],[1,"#00e676"]],
                         color_continuous_midpoint=0, aspect="auto",
                         labels={"color":"Return %"},
                         zmin=-50, zmax=50)
        hfig.update_traces(text=ar_plot.values,
                           texttemplate="%{text:.1f}%",
                           textfont=dict(size=11, color="white"))
        hfig.update_layout(template="plotly_dark", height=max(200, 38*len(ar_plot)),
                           paper_bgcolor=T["bg"], plot_bgcolor=T["bg"],
                           font=dict(family="Roboto Mono",size=11),
                           margin=dict(l=10,r=10,t=10,b=10),
                           coloraxis_showscale=False)
        st.plotly_chart(hfig, use_container_width=True)
        st.caption("Green = positive year, red = negative. Current year is partial. Reveals which ETFs are consistent vs. volatile year-to-year.")

    # ---- ETF Deep Dive ----
    st.markdown('<div class="lbl">Click a ticker for deep dive \u2014 holdings, crash history, overlap</div>',
                unsafe_allow_html=True)
    btn_cols = st.columns(len(sel))
    for i, t in enumerate(sel):
        with btn_cols[i]:
            active = st.session_state.selected_etf == t
            if st.button(f"{'&#9654; ' if active else ''}{t}", key=f"btn_{t}"):
                st.session_state.selected_etf = None if active else t
                st.rerun()

    pick = st.session_state.selected_etf
    if pick and pick in sel:
        meta   = CATALOG.get(pick, dict(name=pick, cat="custom", role="Custom", er=float("nan")))
        er_s   = f'{meta["er"]:.2f}%' if pd.notna(meta["er"]) else "\u2014"
        held_s = f'&middot; <span style="color:{T["gold"]}">HELD</span>' if pick in OWNED else ""
        st.markdown(f'<div style="border:1px solid {T["gold"]};border-radius:8px;'
                    f'padding:16px 20px;background:{T["bg2"]};margin:12px 0 16px;">'
                    f'<span style="font-family:Oswald;font-size:22px;font-weight:700;color:{T["text"]};">'
                    f'{pick}</span>'
                    f'<span style="color:{T["gold"]};font-size:13px;margin-left:12px;">{meta["name"]}</span>'
                    f'<span style="color:{T["text3"]};font-size:11px;margin-left:10px;">'
                    f'{CAT_LABEL.get(meta["cat"],"")} &middot; ER {er_s} {held_s}</span></div>',
                    unsafe_allow_html=True)

        d1, d2, d3 = st.columns([1.2, 1, 1])

        with d1:
            st.markdown("##### \U0001f4cc Top holdings")
            with st.spinner("Loading\u2026"):
                ov = get_fund_overview(pick)
            th = ov.get("top_holdings")
            if th is not None and not th.empty:
                td = th.copy()
                if "Holding Percent" in td.columns:
                    td = td.rename(columns={"Holding Percent":"Weight %"})
                    td["Weight %"] = (td["Weight %"]*100).round(2)
                st.dataframe(td, use_container_width=True)
                if "Holding Percent" in th.columns:
                    olap = th[th.index.isin(MEGACAP)]
                    if not olap.empty:
                        pct_t = float(olap["Holding Percent"].sum())*100
                        st.markdown(f"**\U0001f534 Mag-7 overlap: ~{pct_t:.1f}%**")
                        for tkr, row_h in olap.iterrows():
                            w  = float(row_h["Holding Percent"])*100
                            bw = int(w*3)
                            st.markdown(
                                f'<span style="font-family:monospace;font-size:12px;color:{T["text2"]};">'
                                f'{tkr:6s}</span>'
                                f'<span style="display:inline-block;width:{bw}px;height:10px;'
                                f'background:{T["gold"]};border-radius:2px;margin:0 8px;vertical-align:middle;"></span>'
                                f'<span style="color:{T["gold"]};font-size:12px;">{w:.1f}%</span>',
                                unsafe_allow_html=True)
            else:
                st.caption("Holdings not available (commodities, bonds, smaller ETFs).")

        with d2:
            st.markdown("##### \U0001f3ed Sector weights")
            sw = ov.get("sector_weights")
            if sw:
                sw_c = {k.replace("_"," ").title(): round(v*100,1) for k,v in sw.items() if v and v>0.001}
                sw_s = dict(sorted(sw_c.items(), key=lambda x: -x[1]))
                sfig = go.Figure(go.Bar(x=list(sw_s.values()), y=list(sw_s.keys()), orientation="h",
                    marker=dict(color=list(sw_s.values()),
                                colorscale=[[0,T["bg3"]],[1,T["gold"]]],showscale=False),
                    text=[f"{v:.1f}%" for v in sw_s.values()], textposition="outside",
                    textfont=dict(color=T["text2"],size=11)))
                sfig.update_layout(template="plotly_dark", height=max(240,28*len(sw_s)),
                    margin=dict(l=10,r=60,t=10,b=10), paper_bgcolor=T["bg2"],
                    xaxis_title="% of fund", font=dict(family="Roboto Mono",size=11),
                    xaxis=dict(gridcolor=T["bg3"]))
                st.plotly_chart(sfig, use_container_width=True)
            else:
                st.caption("Sector breakdown not available.")
            if pick in prices.columns and "VOO" in prices.columns and pick != "VOO":
                al = pd.concat([prices[pick].pct_change().dropna(),
                                prices["VOO"].pct_change().dropna()], axis=1, sort=False).dropna()
                if len(al)>2:
                    cv  = float(al.iloc[:,0].corr(al.iloc[:,1]))
                    bc  = T["red"] if cv>.9 else T["orange"] if cv>.6 else T["green"]
                    msg = ("Very high \u2014 little diversification benefit." if cv>.9
                           else "Moderate \u2014 meaningful S&P overlap." if cv>.6
                           else "Low \u2014 a genuine diversifier.")
                    st.markdown(f'<div style="border:1px solid {bc};border-radius:6px;'
                                f'padding:12px 16px;margin-top:10px;background:{T["bg"]};">'
                                f'<span style="color:{bc};font-family:Oswald;font-size:18px;font-weight:700;">'
                                f'Corr\u2192VOO: {cv:.2f}</span>'
                                f'<div style="color:{T["text2"]};font-size:11.5px;margin-top:5px;">{msg}</div>'
                                f'</div>', unsafe_allow_html=True)

        with d3:
            st.markdown("##### \U0001f4c9 Crash & Recovery history")
            if pick in prices.columns:
                cr = compute_crash_recovery(prices[pick].dropna())
                if cr:
                    for ev in cr:
                        dd_color = T["red"] if ev["drawdown_pct"] < -30 else T["orange"]
                        rec_str  = (f'{int(ev["recovery_months"])} months' if ev["recovery_months"]
                                    else "\u26a0 Not yet recovered")
                        rec_color = T["green"] if ev["recovered"] else T["orange"]
                        st.markdown(
                            f'<div class="card" style="margin-bottom:8px;padding:12px 14px;">'
                            f'<div style="font-size:11px;font-weight:700;color:{T["gold"]};">{ev["event"]}</div>'
                            f'<div style="display:flex;justify-content:space-between;margin-top:6px;">'
                            f'<div><div style="font-size:9px;color:{T["text3"]};">DRAWDOWN</div>'
                            f'<div style="color:{dd_color};font-size:16px;font-weight:700;">{ev["drawdown_pct"]:.1f}%</div></div>'
                            f'<div><div style="font-size:9px;color:{T["text3"]};">TROUGH</div>'
                            f'<div style="color:{T["text2"]};font-size:13px;">{ev["trough"]}</div></div>'
                            f'<div><div style="font-size:9px;color:{T["text3"]};">RECOVERY</div>'
                            f'<div style="color:{rec_color};font-size:13px;">{rec_str}</div></div>'
                            f'</div></div>', unsafe_allow_html=True)
                else:
                    st.caption("Not enough history to analyze crash periods.")
            st.markdown("##### \U0001f504 Overlap with your holdings")
            if st.button("Analyze overlap", key="overlap_btn"):
                st.session_state.show_overlap = not st.session_state.show_overlap
            if st.session_state.show_overlap:
                with st.spinner("Comparing top holdings\u2026"):
                    olap_data = compute_overlap(pick, list(OWNED))
                if olap_data:
                    st.markdown(f'<div style="font-size:11px;color:{T["text2"]};margin-bottom:8px;">'
                                f'Stocks in <b>{pick}</b> that also appear in your holdings:</div>',
                                unsafe_allow_html=True)
                    for stock, info in sorted(olap_data.items(), key=lambda x: -x[1]["in_focus"])[:10]:
                        others = " + ".join(f"{t}:{v:.1f}%" for t,v in info["in_others"].items())
                        st.markdown(
                            f'<div style="display:flex;justify-content:space-between;'
                            f'padding:5px 0;border-bottom:1px solid {T["bg3"]};">'
                            f'<span style="font-family:monospace;font-size:12px;color:{T["text"]};">{stock}</span>'
                            f'<span style="font-size:11px;color:{T["gold"]};">{pick}: {info["in_focus"]:.1f}%</span>'
                            f'<span style="font-size:10px;color:{T["text3"]};">{others}</span></div>',
                            unsafe_allow_html=True)
                    total_overlap = sum(v["in_focus"] for v in olap_data.values())
                    st.markdown(f'<div style="margin-top:8px;font-size:12px;color:{T["orange"]};">'
                                f'\u26a0 {total_overlap:.1f}% of {pick} overlaps with your current holdings.</div>',
                                unsafe_allow_html=True)
                else:
                    st.caption("No significant top-holding overlap found, or holdings data unavailable.")

        if ov.get("description"):
            d = ov["description"]
            st.markdown(f'<div style="color:{T["text2"]};font-size:12px;line-height:1.7;">'
                        f'{d[:600]}{"..." if len(d)>600 else ""}</div>', unsafe_allow_html=True)

    # ---- Concentration donut ----
    st.markdown('<div class="lbl">Portfolio Concentration</div>', unsafe_allow_html=True)
    cats = {}
    for t in sel:
        c = CAT_LABEL.get(CATALOG.get(t,{}).get("cat",""), "Other")
        cats[c] = cats.get(c,0)+1
    cfig = go.Figure(go.Pie(labels=list(cats.keys()), values=list(cats.values()), hole=0.5,
        marker=dict(colors=[T["gold"],T["orange"],T["green"],"#4f8ef7","#a78bfa","#2dd4bf","#f87171"])))
    cfig.update_layout(template="plotly_dark", height=340, paper_bgcolor=T["bg"],
                       title="ETFs by category", font=dict(family="Roboto Mono"))
    st.plotly_chart(cfig, use_container_width=True)
    techish = sum(1 for t in sel if CATALOG.get(t,{}).get("cat") in ("tech","semis","growth"))
    if techish/max(len(sel),1) > 0.5:
        st.warning(f"\u26a0\ufe0f {techish}/{len(sel)} selected ETFs are tech/growth/semis. High concentration.")

# ================================================================ TAB 2: MY PORTFOLIO
with tab_pf:
    st.markdown('<div class="lbl">My Investment Tracker</div>', unsafe_allow_html=True)
    trades = load_portfolio()

    with st.expander("\u2795 Add a new investment", expanded=len(trades)==0):
        with st.form("add_trade", clear_on_submit=True):
            fc1,fc2,fc3,fc4 = st.columns([1,1,1,2])
            with fc1: pf_tk = st.text_input("Ticker", placeholder="VOO")
            with fc2: pf_dt = st.date_input("Date bought", value=dt.date.today())
            with fc3: pf_am = st.number_input("$ Amount", min_value=1.0, value=100.0, step=10.0)
            with fc4: pf_nt = st.text_input("Note", placeholder="First buy, DCA\u2026")
            if st.form_submit_button("Record investment", use_container_width=True) and pf_tk:
                tk_up = pf_tk.strip().upper()
                trades.append({"id":str(dt.datetime.now().timestamp()),
                               "ticker":tk_up,"date":str(pf_dt),
                               "amount":float(pf_am),"note":pf_nt})
                save_portfolio(trades)
                if tk_up not in CATALOG:
                    CATALOG[tk_up] = dict(name=tk_up,cat="custom",role="Custom",er=float("nan"))
                st.success(f"Recorded ${pf_am:.0f} in {tk_up} on {pf_dt}.")
                st.rerun()

    if trades:
        all_t = tuple(set(t["ticker"] for t in trades)|set(sel))
        try:    pf_px = load_prices(all_t)
        except: pf_px = prices
        # Pass live quotes so P&L reflects most current prices
        pnl_df = compute_pnl(trades, pf_px, live_quotes=live_q)

        if not pnl_df.empty:
            ti  = pnl_df["Invested $"].sum()
            tc  = pnl_df["Cur. Value $"].sum()
            tg  = tc-ti
            tp  = tg/ti*100

            m1,m2,m3,m4 = st.columns(4)
            def mc(col, lbl, val, color=None):
                col.markdown(f'<div class="card"><div style="font-size:10px;color:{T["text3"]};'
                             f'text-transform:uppercase;letter-spacing:1px;">{lbl}</div>'
                             f'<div style="font-size:22px;font-weight:600;color:{color or T["text"]};'
                             f'margin-top:4px;">{val}</div></div>', unsafe_allow_html=True)
            mc(m1,"Total invested",f"${ti:,.0f}")
            mc(m2,"Current value",f"${tc:,.0f}")
            mc(m3,"Total gain",f'{"+" if tg>=0 else ""}${tg:,.0f}',
               T["green"] if tg>=0 else T["red"])
            mc(m4,"Total return",f'{"+" if tp>=0 else ""}{tp:.1f}%',
               T["green"] if tp>=0 else T["red"])

            # ---- v5: PORTFOLIO HEALTH SCORE ----
            st.markdown('<div class="lbl">Portfolio Health Score</div>', unsafe_allow_html=True)
            hv = pnl_df.groupby("Ticker")["Cur. Value $"].sum().to_dict()
            hs = compute_health_score(hv, prices)
            g_color = (T["green"] if hs["grade"]=="A" else "#9ccc65" if hs["grade"]=="B"
                       else T["orange"] if hs["grade"]=="C" else "#ff8a65" if hs["grade"]=="D" else T["red"])
            hc1, hc2 = st.columns([1, 2.5])
            with hc1:
                st.markdown(f'<div class="card" style="text-align:center;padding:24px;">'
                            f'<div style="font-family:Oswald;font-size:64px;font-weight:700;color:{g_color};line-height:1;">{hs["grade"]}</div>'
                            f'<div style="font-size:20px;color:{T["text"]};margin-top:6px;">{hs["score"]}/100</div>'
                            f'<div style="font-size:10px;color:{T["text3"]};margin-top:4px;">5-factor transparent algorithm</div>'
                            f'</div>', unsafe_allow_html=True)
            with hc2:
                for f_ in hs["factors"]:
                    pct_f = f_["pts"]/f_["max"]*100
                    bar_c = T["green"] if pct_f>=75 else T["orange"] if pct_f>=45 else T["red"]
                    st.markdown(
                        f'<div style="margin-bottom:7px;">'
                        f'<div style="display:flex;justify-content:space-between;font-size:11.5px;">'
                        f'<span style="color:{T["text"]};">{f_["name"]}</span>'
                        f'<span style="color:{bar_c};font-weight:600;">{f_["pts"]}/{f_["max"]}</span></div>'
                        f'<div style="background:{T["bg3"]};border-radius:3px;height:7px;margin:3px 0;">'
                        f'<div style="background:{bar_c};width:{pct_f:.0f}%;height:100%;border-radius:3px;"></div></div>'
                        f'<div style="font-size:10px;color:{T["text3"]};">{f_["detail"]}</div></div>',
                        unsafe_allow_html=True)

            # ---- v5: TIME-WEIGHTED RETURN ----
            twr = compute_twr(trades, pf_px)
            if twr:
                st.markdown(f'<div class="lbl">{gloss("TWR","True Performance \u2014 Time-Weighted Return")}</div>',
                            unsafe_allow_html=True)
                tw1, tw2, tw3 = st.columns(3)
                tw_c = T["green"] if twr["twr_ann"]>=0 else T["red"]
                mc(tw1, "TWR (annualized)", f'{twr["twr_ann"]:+.1f}%/yr', tw_c)
                mc(tw2, "TWR (total)", f'{twr["twr_total"]:+.1f}%', tw_c)
                mc(tw3, "Simple return", f'{tp:+.1f}%',
                   T["green"] if tp>=0 else T["red"])
                st.caption("TWR removes the timing of your deposits \u2014 it grades your STRATEGY. "
                           "Simple return mixes in when you happened to add cash. If TWR > simple return, "
                           "your recent deposits haven't had time to grow yet; the strategy itself is doing better than the raw number suggests.")

            rpf = ""
            for _, r in pnl_df.iterrows():
                pos  = r["Gain $"]>=0
                gc   = T["green"] if pos else T["red"]
                sign = "+" if pos else ""
                rpf += (f'<tr><td style="font-weight:700;color:{T["text"]};">{r["Ticker"]}</td>'
                        f'<td>{r["Date"]}</td><td>${r["Invested $"]:,.2f}</td>'
                        f'<td>${r["Cur. Value $"]:,.2f}</td>'
                        f'<td style="color:{gc};font-weight:600;">{sign}${r["Gain $"]:,.2f}</td>'
                        f'<td style="color:{gc};font-weight:600;">{sign}{r["Return %"]:.1f}%</td>'
                        f'<td style="color:{gc};">{sign}{r["Ann. %"]:.1f}%</td>'
                        f'<td style="color:{T["text3"]};">{r["Days"]}d</td>'
                        f'<td style="color:{T["text3"]};font-size:11px;">{r["Note"]}</td></tr>')
            st.markdown(
                f'<div style="overflow-x:auto;border:1px solid {T["bg3"]};border-radius:6px;margin-top:16px;">'
                f'<table class="board"><thead><tr>'
                f'<th>Ticker</th><th>Date</th><th>Invested</th><th>Value Now</th>'
                f'<th>Gain $</th><th>Return %</th><th>Ann. %</th><th>Held</th><th>Note</th>'
                f'</tr></thead><tbody>{rpf}</tbody></table></div>', unsafe_allow_html=True)

            # Allocation bar
            st.markdown('<div class="lbl">Allocation breakdown</div>', unsafe_allow_html=True)
            tk_sum = pnl_df.groupby("Ticker").agg({"Invested $":"sum","Cur. Value $":"sum"}).reset_index()
            bfig   = go.Figure()
            bfig.add_bar(x=tk_sum["Ticker"], y=tk_sum["Invested $"], name="Invested", marker_color=T["bg3"])
            bfig.add_bar(x=tk_sum["Ticker"], y=tk_sum["Cur. Value $"], name="Current value", marker_color=T["gold"])
            bfig.update_layout(template="plotly_dark", barmode="group", height=300,
                               paper_bgcolor=T["bg"], font=dict(family="Roboto Mono"),
                               legend=dict(orientation="h",y=-0.25))
            st.plotly_chart(bfig, use_container_width=True)

            # Dividend Income Tracker
            st.markdown('<div class="lbl">Dividend Income Tracker</div>', unsafe_allow_html=True)
            with st.spinner("Fetching dividend yields\u2026"):
                div_info = get_dividend_info(tuple(pnl_df["Ticker"].unique()))
            div_rows = []
            for _, r in tk_sum.iterrows():
                t   = r["Ticker"]
                yld = div_info.get(t, 0)
                ann = round(r["Cur. Value $"]*yld/100, 2)
                div_rows.append({"Ticker":t,"Value $":round(r["Cur. Value $"],2),
                                 "Yield %":yld,"Annual Income $":ann,"Monthly $":round(ann/12,2)})
            div_df = pd.DataFrame(div_rows)
            if not div_df.empty:
                total_ann = div_df["Annual Income $"].sum()
                st.markdown(
                    f'<div class="card" style="display:flex;gap:30px;">'
                    f'<div><div style="font-size:10px;color:{T["text3"]};text-transform:uppercase;">Annual dividends</div>'
                    f'<div style="font-size:22px;color:{T["green"]};font-weight:600;">${total_ann:,.2f}</div></div>'
                    f'<div><div style="font-size:10px;color:{T["text3"]};text-transform:uppercase;">Monthly avg.</div>'
                    f'<div style="font-size:22px;color:{T["green"]};font-weight:600;">${total_ann/12:,.2f}</div></div>'
                    f'</div>', unsafe_allow_html=True)
                st.dataframe(div_df, hide_index=True, use_container_width=True)
                hi_yield = div_df[div_df["Yield %"]>2]["Ticker"].tolist()
                if hi_yield:
                    st.caption(f"\U0001f4a1 High-yield ETFs ({', '.join(hi_yield)}) generate ordinary income. "
                               f"Hold these in your Roth IRA to shelter dividends from taxes.")

            # Delete trade
            ids = [(f'{r["Ticker"]} {r["Date"]} ${r["Invested $"]:.0f}', r["ID"])
                   for _, r in pnl_df.iterrows()]
            dl = st.selectbox("Delete a trade:", ["\u2014"]+[i[0] for i in ids])
            if dl != "\u2014":
                del_id = next(i[1] for i in ids if i[0]==dl)
                if st.button("\U0001f5d1 Delete selected trade"):
                    trades = [t for t in trades if t.get("id")!=del_id]
                    save_portfolio(trades); st.rerun()

        # Portfolio Drift Monitor
        st.markdown('<div class="lbl">Portfolio Drift Monitor</div>', unsafe_allow_html=True)
        st.caption("Set your target allocation for each ETF. The app signals when to buy more (never sell).")
        saved_targets = load_targets()
        targets       = {}
        t_cols = st.columns(len(OWNED))
        for i, t in enumerate(OWNED):
            default = saved_targets.get(t, round(100/len(OWNED)))
            with t_cols[i]:
                targets[t] = st.number_input(f"{t} %", min_value=0, max_value=100,
                                             value=default, step=5, key=f"tgt_{t}")
        if st.button("Save targets", use_container_width=True):
            save_targets(targets); st.success("Targets saved.")
        total_pct = sum(targets.values())
        if abs(total_pct-100) > 1:
            st.warning(f"Targets sum to {total_pct}% — adjust to reach 100%.")
        elif not pnl_df.empty:
            total_val  = pnl_df["Cur. Value $"].sum()
            actual     = pnl_df.groupby("Ticker")["Cur. Value $"].sum().to_dict()
            actual_pct = {t: round(actual.get(t,0)/total_val*100,1) for t in OWNED if total_val>0}
            drift_rows = []
            for t in OWNED:
                tgt    = targets.get(t,0)
                act    = actual_pct.get(t,0)
                diff   = act - tgt
                action = ""
                if diff < -3: action = f"\u2705 Buy more {t}"
                elif diff > 5: action = f"\u26a0 {t} is overweight vs target (don\u2019t sell — just buy others)"
                else:          action = "\u2714 On track"
                drift_rows.append({"ETF":t,"Target %":tgt,"Actual %":act,"Drift":round(diff,1),"Signal":action})
            drift_df = pd.DataFrame(drift_rows)
            dfig     = go.Figure()
            dfig.add_bar(x=drift_df["ETF"], y=drift_df["Target %"], name="Target", marker_color=T["bg3"])
            dfig.add_bar(x=drift_df["ETF"], y=drift_df["Actual %"], name="Actual", marker_color=T["gold"])
            dfig.update_layout(template="plotly_dark", barmode="group", height=280,
                               paper_bgcolor=T["bg"], font=dict(family="Roboto Mono"),
                               legend=dict(orientation="h",y=-0.3), yaxis_title="%")
            st.plotly_chart(dfig, use_container_width=True)
            for _, dr in drift_df.iterrows():
                color = T["green"] if "\u2705" in dr["Signal"] else T["orange"] if "\u26a0" in dr["Signal"] else T["text2"]
                st.markdown(f'<span style="color:{color};font-size:12.5px;">{dr["Signal"]}</span> '
                            f'<span style="color:{T["text3"]};font-size:11px;">(target {dr["Target %"]}% / actual {dr["Actual %"]}%)</span>',
                            unsafe_allow_html=True)

            # ---- v5: REBALANCING ASSISTANT ----
            st.markdown('<div class="lbl">Rebalancing Assistant \u2014 exact dollars for your next buy</div>',
                        unsafe_allow_html=True)
            contrib = st.number_input("Your next contribution ($)", min_value=10.0,
                                      value=200.0, step=25.0, key="reb_contrib")
            plan = rebalance_plan(actual, targets, contrib)
            if plan["buys"]:
                rb1, rb2 = st.columns([1.3, 1])
                with rb1:
                    st.markdown(f'<div class="card"><div style="font-size:11px;color:{T["gold"]};'
                                f'font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">'
                                f'Split your ${contrib:,.0f} like this:</div>', unsafe_allow_html=True)
                    for t_, b_ in sorted(plan["buys"].items(), key=lambda x: -x[1]):
                        pct_b = b_/contrib*100
                        st.markdown(
                            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
                            f'<span style="font-family:Oswald;font-weight:700;color:{T["text"]};width:52px;">{t_}</span>'
                            f'<div style="flex:1;background:{T["bg3"]};height:14px;border-radius:3px;">'
                            f'<div style="background:{T["gold"]};width:{pct_b:.0f}%;height:100%;border-radius:3px;"></div></div>'
                            f'<span style="color:{T["green"]};font-weight:600;font-size:14px;width:70px;text-align:right;">${b_:,.2f}</span>'
                            f'</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with rb2:
                    pie_after = go.Figure(go.Pie(
                        labels=list(plan["after_pct"].keys()),
                        values=list(plan["after_pct"].values()), hole=0.45,
                        marker=dict(colors=[T["gold"],T["orange"],T["green"],"#4f8ef7","#a78bfa","#2dd4bf"]),
                        textinfo="label+percent"))
                    pie_after.update_layout(template="plotly_dark", height=260,
                        paper_bgcolor=T["bg"], margin=dict(l=10,r=10,t=30,b=10),
                        title=dict(text="Allocation after this buy", font=dict(size=12)),
                        showlegend=False, font=dict(family="Roboto Mono", size=10))
                    st.plotly_chart(pie_after, use_container_width=True)
                st.caption("Buy-only rebalancing: your contribution goes to whichever ETFs are furthest below target, "
                           "proportionally to their dollar deficit. Nothing is ever sold.")

        # ---- v5: TRUE AGGREGATE EXPOSURE ----
        if not pnl_df.empty:
            st.markdown('<div class="lbl">True Exposure X-Ray \u2014 what you ACTUALLY own across all ETFs</div>',
                        unsafe_allow_html=True)
            with st.spinner("Blending fund holdings, dollar-weighted\u2026"):
                agg = aggregate_exposure(pnl_df.groupby("Ticker")["Cur. Value $"].sum().to_dict())
            if agg and (agg.get("sectors") or agg.get("stocks")):
                x1, x2 = st.columns(2)
                with x1:
                    st.markdown("##### \U0001f3ed Portfolio-wide sector mix")
                    swp = agg["sectors"]
                    if swp:
                        xfig = go.Figure(go.Bar(
                            x=list(swp.values()), y=list(swp.keys()), orientation="h",
                            marker=dict(color=list(swp.values()),
                                        colorscale=[[0,T["bg3"]],[1,T["gold"]]], showscale=False),
                            text=[f"{v:.1f}%" for v in swp.values()], textposition="outside",
                            textfont=dict(color=T["text2"], size=11)))
                        xfig.update_layout(template="plotly_dark", height=max(260, 26*len(swp)),
                            paper_bgcolor=T["bg"], margin=dict(l=10,r=55,t=10,b=10),
                            xaxis=dict(gridcolor=T["bg3"], title="% of your total dollars"),
                            font=dict(family="Roboto Mono", size=11))
                        st.plotly_chart(xfig, use_container_width=True)
                        top_sec = next(iter(swp.items()), None)
                        if top_sec and top_sec[1] > 35:
                            st.warning(f"\u26a0 {top_sec[1]:.0f}% of your money is in {top_sec[0]} "
                                       f"once every fund is blended. That's real concentration \u2014 "
                                       f"the sector chart per-ETF hides this.")
                with x2:
                    st.markdown("##### \U0001f50d Your true top stock positions")
                    st.caption("Dollar-weighted across every ETF you own. One company in 3 funds = one combined position.")
                    for srow in agg["stocks"][:10]:
                        etf_list = " + ".join(f"{e} ({w}%)" for e, w in srow["in_etfs"].items())
                        multi = len(srow["in_etfs"]) > 1
                        flag = f' <span style="color:{T["orange"]};font-size:9px;">\u26a0 {len(srow["in_etfs"])} funds</span>' if multi else ""
                        st.markdown(
                            f'<div style="display:flex;justify-content:space-between;align-items:baseline;'
                            f'padding:5px 0;border-bottom:1px solid {T["bg3"]};">'
                            f'<span style="font-family:monospace;font-weight:700;color:{T["text"]};">{srow["symbol"]}{flag}</span>'
                            f'<span style="color:{T["gold"]};font-weight:600;">{srow["pct_of_pf"]:.1f}% \u00b7 ${srow["dollars"]:,.0f}</span>'
                            f'</div>'
                            f'<div style="font-size:9.5px;color:{T["text3"]};margin-bottom:3px;">{etf_list}</div>',
                            unsafe_allow_html=True)
                    known_top = sum(s["pct_of_pf"] for s in agg["stocks"][:10])
                    st.markdown(f'<div style="margin-top:8px;font-size:12px;color:{T["text2"]};">'
                                f'Your top 10 real positions = <b style="color:{T["gold"]};">{known_top:.0f}%</b> '
                                f'of your portfolio (from disclosed top holdings). '
                                f'Add or remove ETFs and this recalculates automatically.</div>',
                                unsafe_allow_html=True)
            else:
                st.caption("Holdings data unavailable for aggregation right now.")

        # Monte Carlo
        st.markdown('<div class="lbl">10-Year Projection (Monte Carlo, 2,000 paths)</div>', unsafe_allow_html=True)
        st.caption("Based on historical daily volatility — not a prediction. Log-normal returns assumed.")
        proj_tk = st.selectbox("Project ticker:", [t for t in sel if t in prices.columns])
        monthly = st.number_input("Monthly contribution ($)", min_value=0.0, value=100.0, step=50.0)
        if proj_tk and proj_tk in prices.columns:
            mc_res = monte_carlo(prices[proj_tk].dropna(), n_years=10, n_paths=2000, monthly_add=monthly)
            p1,p2,p3,p4,p5 = st.columns(5)
            for col,lbl,val,clr in [
                (p1,"Pessimistic\n(10th %ile",mc_res["p10"],T["red"]),
                (p2,"Conservative\n(25th %ile)",mc_res["p25"],T["orange"]),
                (p3,"Median\n(50th %ile)",mc_res["p50"],T["gold"]),
                (p4,"Optimistic\n(75th %ile)",mc_res["p75"],T["green"]),
                (p5,"Best case\n(90th %ile)",mc_res["p90"],"#00bfff")]:
                col.markdown(f'<div class="card" style="text-align:center;">'
                             f'<div style="font-size:10px;color:{T["text3"]};">{lbl.replace(chr(10),"<br>")}</div>'
                             f'<div style="font-size:20px;font-weight:700;color:{clr};margin-top:6px;">${val:,.0f}</div>'
                             f'<div style="font-size:10px;color:{T["text3"]};margin-top:3px;">'
                             f'{val/mc_res["current"]:.1f}\u00d7 current</div></div>', unsafe_allow_html=True)

        # Goal Planner
        st.markdown('<div class="lbl">Wealth Target Goal Planner</div>', unsafe_allow_html=True)
        gp_cols = st.columns(4)
        with gp_cols[0]: target_w = st.number_input("Wealth target ($)", min_value=10000, value=1000000, step=50000)
        with gp_cols[1]: current_age = st.number_input("Your age", min_value=15, max_value=70, value=20)
        with gp_cols[2]: target_age  = st.number_input("Target age", min_value=current_age+1, max_value=90, value=55)
        with gp_cols[3]: cur_pv      = st.number_input("Portfolio value today ($)", min_value=0.0, value=float(pnl_df["Cur. Value $"].sum() if not pnl_df.empty else 944), step=100.0)

        years_left  = target_age - current_age
        monthly_inp = st.number_input("Planned monthly investment ($)", min_value=0.0, value=300.0, step=50.0)

        gp_scenarios = [
            ("Conservative",  0.07, T["text2"]),
            ("Moderate",      0.10, T["gold"]),
            ("Optimistic",    0.13, T["green"]),
            ("Your VOO hist.", trailing_ann(prices["VOO"].dropna(), 10)/100 if "VOO" in prices.columns else 0.10, "#00bfff"),
        ]
        st.markdown(f"**{years_left} years to target. Projections at different return assumptions:**")
        sc_cols = st.columns(4)
        for i, (label, rate, color) in enumerate(gp_scenarios):
            gp = goal_planner(target_w, cur_pv, monthly_inp, rate, years_left)
            on_track = gp["total"] >= target_w
            on_track_str = "&#9989; On track" if on_track else f"&#128308; Short by ${target_w-gp['total']:,.0f}"
            with sc_cols[i]:
                st.markdown(
                    f'<div class="card" style="text-align:center;">'
                    f'<div style="font-size:10px;color:{T["text3"]};margin-bottom:6px;">{label}<br>({rate*100:.1f}%/yr)</div>'
                    f'<div style="font-size:18px;font-weight:700;color:{color};">${gp["total"]:,.0f}</div>'
                    f'<div style="font-size:10px;color:{T["text3"]};margin-top:4px;">{on_track_str}</div>'
                    f'<div style="font-size:10px;color:{T["text2"]};margin-top:4px;">Need ${gp["req_pmt"]:,.0f}/mo to hit target</div>'
                    f'</div>', unsafe_allow_html=True)
    else:
        st.info("No investments recorded yet. Use the form above to add your first position.")

# ================================================================ TAB 3: MARKET PULSE
with tab_pulse:
    # ---- Fear & Greed ----
    st.markdown('<div class="lbl">Market Sentiment \u2014 Fear & Greed Index</div>',
                unsafe_allow_html=True)
    with st.spinner("Fetching market sentiment\u2026"):
        fg = get_fear_greed()
    fg_val = fg["value"]
    fg_lbl = fg["label"]
    fg_color = (T["red"] if fg_val<=20 else T["orange"] if fg_val<=40
                else T["text2"] if fg_val<=60 else T["green"] if fg_val<=80 else "#00e676")
    gauge = go.Figure(go.Indicator(mode="gauge+number",value=fg_val,
        gauge=dict(axis=dict(range=[0,100]),
                   bar=dict(color=fg_color),
                   steps=[dict(range=[0,20],color="#3d0000"),
                          dict(range=[20,40],color="#4d1a00"),
                          dict(range=[40,60],color=T["bg3"]),
                          dict(range=[60,80],color="#0d3d1a"),
                          dict(range=[80,100],color="#0a3020")],
                   threshold=dict(line=dict(color=fg_color,width=4),
                                  thickness=0.75,value=fg_val)),
        title=dict(text=f"{fg_lbl}", font=dict(size=16,color=fg_color,family="Oswald")),
        number=dict(font=dict(size=36,color=fg_color))))
    gauge.update_layout(template="plotly_dark", height=220, paper_bgcolor=T["bg"],
                        margin=dict(l=20,r=20,t=40,b=10), font=dict(family="Roboto Mono"))
    gc1, gc2 = st.columns([1,2])
    with gc1:
        st.plotly_chart(gauge, use_container_width=True)
        st.caption(f"Source: {fg.get('source','')}")
    with gc2:
        st.markdown(f"""<div class="card" style="height:180px;">
        <div style="font-size:12px;color:{T['text2']};line-height:1.8;">
        <b style="color:{fg_color};">{fg_val} \u2014 {fg_lbl}</b><br>
        {"&#128308; Extreme fear = historically a strong buying opportunity. Markets tend to overreact downward. Consider adding to your positions." if fg_val<=20
         else "&#128993; Fear in the market. Investors are worried. Long-term holders like you benefit from buying at lower prices." if fg_val<=40
         else "&#9898; Neutral. Markets are fairly valued by sentiment. Continue your regular DCA schedule." if fg_val<=60
         else "&#129001; Greed. Markets are optimistic. Be careful not to chase performance. Stick to your allocation plan." if fg_val<=80
         else "&#128994; Extreme greed. Markets may be overextended. Don\u2019t add large lump sums now \u2014 spread it out."}
        <br><br><span style="font-size:10.5px;color:{T['text3']};">
        For ETFs with long horizons (30+ yrs), sentiment should influence timing slightly \u2014 not strategy fundamentally.</span>
        </div></div>""", unsafe_allow_html=True)

    # History sparkline
    if fg.get("history"):
        hist_vals = [h["value"] for h in fg["history"]]
        hist_dts  = [h.get("date","") for h in fg["history"]]
        spark = go.Figure(go.Scatter(x=hist_dts, y=hist_vals, mode="lines+markers",
            line=dict(color=fg_color, width=2), marker=dict(size=4)))
        spark.add_hline(y=50, line_dash="dot", line_color=T["text3"])
        spark.update_layout(template="plotly_dark", height=120, paper_bgcolor=T["bg"],
            margin=dict(l=10,r=10,t=10,b=10), showlegend=False,
            yaxis=dict(range=[0,100],gridcolor=T["bg3"],tickfont=dict(size=9)),
            xaxis=dict(gridcolor=T["bg3"],tickfont=dict(size=9)))
        st.plotly_chart(spark, use_container_width=True)

    # ---- Macro Snapshot ----
    st.markdown('<div class="lbl">Macro Context \u2014 market forces affecting your ETFs</div>',
                unsafe_allow_html=True)
    with st.spinner("Loading macro indicators\u2026"):
        macro = get_macro_snapshot()

    macro_meta = {
        "VIX":      {"desc":"Market volatility (fear gauge)","low":"<15 = calm markets (good for equities)","high":">25 = turbulence, risk-off. Tech/growth ETFs face pressure."},
        "10Y Rate": {"desc":"10-Year Treasury Yield","low":"<3.5% = growth ETFs (VGT, SMH, SCHG) benefit","high":">4.5% and rising = headwind for tech/growth. Bond yields compete."},
        "US Dollar":{"desc":"US Dollar Strength (DXY)","low":"<100 = weaker dollar, good for VXUS & international","high":">104 = strong dollar, headwind for international ETFs like VXUS"},
        "Oil":      {"desc":"Crude Oil (proxy for inflation)","low":"<70 = low inflation, benign for consumers & growth","high":">90 = inflation risk. Energy ETFs (XLE) benefit. Growth ETFs face pressure."},
    }
    if macro:
        mc_cols = st.columns(len(macro))
        for i, (label, data) in enumerate(macro.items()):
            chg = data.get("chg_1m")
            chg_color = T["green"] if (chg or 0)>0 else T["red"]
            chg_str   = f'{chg:+.1f}% (1M)' if chg is not None else ""
            meta_info = macro_meta.get(label, {})
            with mc_cols[i]:
                st.markdown(
                    f'<div class="card" style="text-align:center;">'
                    f'<div style="font-size:10px;color:{T["text3"]};text-transform:uppercase;">{label}</div>'
                    f'<div style="font-size:22px;font-weight:700;color:{T["text"]};margin:6px 0;">{data["current"]}</div>'
                    f'<div style="font-size:12px;color:{chg_color};">{chg_str}</div>'
                    f'<div style="font-size:10px;color:{T["text3"]};margin-top:6px;">{meta_info.get("desc","")}</div>'
                    f'</div>', unsafe_allow_html=True)

        # Auto-generated macro interpretation
        interp = []
        vix_v  = (macro.get("VIX",{}).get("current") or 20)
        tnx_v  = (macro.get("10Y Rate",{}).get("current") or 4.0)
        dxy_v  = (macro.get("US Dollar",{}).get("current") or 100)
        oil_v  = (macro.get("Oil",{}).get("current") or 75)
        if vix_v > 25:   interp.append(f"\u26a0\ufe0f **VIX at {vix_v}** \u2014 elevated volatility. Tech/growth ETFs face selling pressure during risk-off.")
        elif vix_v < 15: interp.append(f"\u2705 **VIX at {vix_v}** \u2014 calm markets. Favorable for growth ETFs.")
        if tnx_v > 4.5:  interp.append(f"\u26a0\ufe0f **10Y yield at {tnx_v}%** \u2014 high rates pressure long-duration assets. SCHG, VGT, SMH may face valuation headwinds.")
        elif tnx_v < 3.5: interp.append(f"\u2705 **10Y yield at {tnx_v}%** \u2014 low rates benefit growth ETFs. Positive for VGT, SMH, SCHG.")
        if dxy_v > 104:  interp.append(f"\u26a0\ufe0f **Dollar at {dxy_v}** \u2014 strong USD hurts international ETFs. VXUS returns eroded when converted back to dollars.")
        elif dxy_v < 98: interp.append(f"\u2705 **Dollar at {dxy_v}** \u2014 weak USD benefits VXUS & international exposure.")
        if oil_v > 90:   interp.append(f"\u26a0\ufe0f **Oil at ${oil_v}** \u2014 high energy costs increase inflation risk, pressuring consumer ETFs.")
        if interp:
            st.markdown('<div class="lbl" style="margin-top:8px;">Current macro read</div>',
                        unsafe_allow_html=True)
            for line in interp:
                st.markdown(f'<div style="font-size:12.5px;color:{T["text2"]};margin-bottom:6px;">{line}</div>',
                            unsafe_allow_html=True)

    # ---- Smart AI-Weighted Recommendations ----
    st.markdown('<div class="lbl">Smart Daily Picks \u2014 AI-weighted model (Sharpe + sentiment + overlap + sector + fee)</div>',
                unsafe_allow_html=True)
    st.caption("Scored across 50+ ETFs by: 30% 3M risk-adjusted return \u00b7 20% portfolio gap \u00b7 20% low overlap \u00b7 15% sentiment alignment \u00b7 15% expense efficiency. Refreshes every 4 hours.")
    with st.spinner("Running scoring model across 50+ ETFs\u2026"):
        smart_picks = smart_recommendations(tuple(OWNED), sel, fg_val)
    if smart_picks:
        pk_cols = st.columns(len(smart_picks))
        for i, p in enumerate(smart_picks):
            clr = T["green"] if (p.get("ret_3m") or 0)>=0 else T["red"]
            with pk_cols[i]:
                st.markdown(
                    f'<div style="background:{T["bg3"]};border:1px solid {T["gold"]};border-radius:8px;'
                    f'padding:14px;text-align:center;">'
                    f'<div style="font-family:Oswald;font-size:20px;font-weight:700;color:{T["gold"]};">{p["ticker"]}</div>'
                    f'<div style="font-size:10.5px;color:{T["text2"]};margin-top:2px;">{p["name"][:25]}</div>'
                    f'<div style="font-size:11px;color:{T["text3"]};margin:3px 0;">{p["cat"]}</div>'
                    f'<div style="font-size:14px;font-weight:600;color:{clr};margin:6px 0;">'
                    f'{"+" if (p.get("ret_3m") or 0)>=0 else ""}{p.get("ret_3m","?"):.1f}% (3M)</div>'
                    f'<div style="font-size:10px;color:{T["text3"]};">Score: {p["score"]:.2f} \u00b7 Sharpe: {p["sharpe_3m"]:.2f}</div>'
                    f'<div style="font-size:10px;color:{T["text3"]};margin-top:2px;">ER: {p["er"]:.2f}%</div>'
                    f'<div style="font-size:10px;color:{T["text2"]};margin-top:6px;line-height:1.4;">{p["reason"]}</div>'
                    f'</div>', unsafe_allow_html=True)
    else:
        st.caption("Recommendation engine unavailable. Check internet connection.")

    # ---- Technical Signals ----
    st.markdown('<div class="lbl">Technical Signals \u2014 Your Holdings</div>', unsafe_allow_html=True)
    sigs = compute_signals(prices[[t for t in OWNED if t in prices.columns]])
    if sigs:
        for t, sg in sigs.items():
            rsi     = sg["rsi"]
            rc      = "signal-bad" if rsi>70 else "signal-ok" if rsi<30 else "signal-warn"
            rl      = "Overbought" if rsi>70 else "Oversold" if rsi<30 else "Neutral"
            gc_str  = ("\u2705 Golden cross (MA50>MA200)" if sg.get("golden") is True
                       else "\u26a0 Death cross (MA50<MA200)" if sg.get("golden") is False else "\u2014")
            r1c     = T["green"] if sg["ret_1m"]>=0 else T["red"]
            r3c     = T["green"] if sg["ret_3m"]>=0 else T["red"]
            hc      = (T["red"] if sg["pct_from_hi"]<-20 else T["orange"] if sg["pct_from_hi"]<-5 else T["green"])
            st.markdown(f'''<div class="card" style="margin-bottom:10px;">
            <span style="font-family:Oswald;font-size:17px;font-weight:700;color:{T["gold"]};">{t}</span>
            <span style="color:{T["text2"]};font-size:11px;margin-left:10px;">${sg["price"]:.2f}</span>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:10px;">
              <div><div style="font-size:10px;color:{T["text3"]};">RSI (14)</div>
                <div class="{rc}" style="font-size:16px;">{rsi} \u2014 {rl}</div></div>
              <div><div style="font-size:10px;color:{T["text3"]};">vs 52-wk High</div>
                <div style="color:{hc};font-size:16px;font-weight:600;">{sg["pct_from_hi"]:+.1f}%</div></div>
              <div><div style="font-size:10px;color:{T["text3"]};">MA Crossover</div>
                <div style="font-size:12px;color:{T["text2"]};">{gc_str}</div></div>
              <div><div style="font-size:10px;color:{T["text3"]};">1M Return</div>
                <div style="color:{r1c};font-size:16px;font-weight:600;">{sg["ret_1m"]:+.1f}%</div></div>
              <div><div style="font-size:10px;color:{T["text3"]};">3M Return</div>
                <div style="color:{r3c};font-size:16px;font-weight:600;">{sg["ret_3m"]:+.1f}%</div></div>
              <div><div style="font-size:10px;color:{T["text3"]};">MA50</div>
                <div style="font-size:14px;color:{T["text2"]};">${sg["ma50"]:,.2f}</div></div>
            </div></div>''', unsafe_allow_html=True)

    # ---- News ----
    st.markdown('<div class="lbl">Latest News \u2014 Your Holdings + Broad Market</div>',
                unsafe_allow_html=True)
    with st.spinner("Fetching headlines\u2026"):
        news = get_market_news()
    if news:
        for art in news:
            lh = (f'<a href="{art["url"]}" target="_blank" '
                  f'style="color:{T["text"]};text-decoration:none;">{art["title"]}</a>'
                  if art.get("url") else art["title"])
            st.markdown(f'<div class="news-item"><span class="news-tk">{art["ticker"]}</span>'
                        f'<div class="news-title">{lh}</div>'
                        f'<div class="news-meta">{art.get("publisher","")} '
                        f'\u00b7 {art.get("time","")[:10]}</div></div>', unsafe_allow_html=True)
    else:
        st.caption("No news available right now.")

# ================================================================ TAB: WHAT-IF LAB
with tab_lab:
    st.markdown('<div class="lbl">What-If Lab \u2014 test decisions on real history before making them</div>',
                unsafe_allow_html=True)
    lab_trades = load_portfolio()

    # ---- Scenario 1: extra monthly contribution ----
    st.markdown("##### \U0001f4b0 What if I invested $___/month more?")
    st.caption("Backtested with actual historical prices \u2014 monthly buys on the first trading day of each month, dividends reinvested.")
    w1, w2, w3 = st.columns(3)
    with w1: dca_tk  = st.selectbox("Into which ETF:", [t for t in sel], key="lab_dca_tk")
    with w2: dca_amt = st.number_input("Monthly amount ($)", min_value=10.0, value=100.0, step=25.0, key="lab_dca_amt")
    with w3: dca_yrs = st.selectbox("Looking back:", ["3 years", "5 years", "10 years"], index=1, key="lab_dca_yrs")
    yrs_n = int(dca_yrs.split()[0])
    dca_start = str(dt.date.today() - dt.timedelta(days=yrs_n*365))
    bt = backtest_dca(dca_tk, dca_amt, dca_start, _key=f"{dca_tk}{dca_amt}{yrs_n}")
    if bt:
        b1, b2, b3, b4 = st.columns(4)
        gc = T["green"] if bt["gain"] >= 0 else T["red"]
        for col, lbl_, val_, c_ in [
            (b1, "You'd have invested", f"${bt['invested']:,.0f}", T["text"]),
            (b2, "It would be worth", f"${bt['end_value']:,.0f}", T["gold"]),
            (b3, "Profit", f"${bt['gain']:+,.0f}", gc),
            (b4, "Return", f"{bt['gain_pct']:+.1f}%", gc)]:
            col.markdown(f'<div class="card" style="text-align:center;">'
                         f'<div style="font-size:10px;color:{T["text3"]};text-transform:uppercase;">{lbl_}</div>'
                         f'<div style="font-size:19px;font-weight:700;color:{c_};margin-top:5px;">{val_}</div>'
                         f'</div>', unsafe_allow_html=True)
        st.caption(f"{bt['n_buys']} automatic buys over {bt['years']} years. This is DCA discipline made visible.")
    else:
        st.caption("Not enough history for this ETF/period combination.")

    st.divider()

    # ---- Scenario 2: swap one holding ----
    st.markdown("##### \U0001f501 What if I had bought ___ instead of ___?")
    st.caption("Replays your ACTUAL recorded trades with one ticker swapped, same dates and dollar amounts.")
    if lab_trades:
        held_now = sorted(set(t["ticker"] for t in lab_trades))
        sw1, sw2 = st.columns(2)
        with sw1: swap_from = st.selectbox("Swap out (from your real trades):", held_now, key="lab_swf")
        with sw2: swap_to   = st.selectbox("Swap in:", [t for t in CATALOG if t != swap_from], key="lab_swt")
        if st.button("Run swap backtest", use_container_width=True, key="lab_swap_btn"):
            need = tuple(set(held_now) | {swap_to})
            try:    px_all = load_prices(need)
            except Exception: px_all = prices
            sw = backtest_swap(lab_trades, swap_from, swap_to, px_all)
            d_c = T["green"] if sw["difference"] >= 0 else T["red"]
            verdict = (f"{swap_to} would have made you ${sw['difference']:,.2f} MORE"
                       if sw["difference"] >= 0 else
                       f"{swap_to} would have made you ${abs(sw['difference']):,.2f} LESS \u2014 your pick won")
            s1, s2, s3 = st.columns(3)
            s1.markdown(f'<div class="card" style="text-align:center;"><div style="font-size:10px;color:{T["text3"]};">YOUR REAL PORTFOLIO</div>'
                        f'<div style="font-size:19px;font-weight:700;color:{T["gold"]};margin-top:5px;">${sw["real_value"]:,.2f}</div></div>',
                        unsafe_allow_html=True)
            s2.markdown(f'<div class="card" style="text-align:center;"><div style="font-size:10px;color:{T["text3"]};">WITH {swap_to} INSTEAD</div>'
                        f'<div style="font-size:19px;font-weight:700;color:{T["text"]};margin-top:5px;">${sw["swap_value"]:,.2f}</div></div>',
                        unsafe_allow_html=True)
            s3.markdown(f'<div class="card" style="text-align:center;"><div style="font-size:10px;color:{T["text3"]};">DIFFERENCE</div>'
                        f'<div style="font-size:19px;font-weight:700;color:{d_c};margin-top:5px;">${sw["difference"]:+,.2f}</div></div>',
                        unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:13px;color:{d_c};margin-top:6px;">\U0001f52c {verdict}</div>',
                        unsafe_allow_html=True)
            st.caption("Hindsight is educational, not predictive \u2014 use this to understand behavior differences, not to chase what already ran.")
    else:
        st.info("Record trades in MY PORTFOLIO first \u2014 the swap test replays your actual history.")

    st.divider()

    # ---- Compound Money Machine ----
    st.markdown(f'##### \u2699\ufe0f The Compound Money Machine', unsafe_allow_html=True)
    st.caption("Drag the sliders. Watch the curve bend. Exact monthly compounding math \u2014 the growth-rate scenarios use real historical CAGRs from your own board.")
    cm1, cm2, cm3 = st.columns(3)
    with cm1: mm_monthly = st.slider("Monthly investment ($)", 50, 2000, 300, 50)
    with cm2: mm_years   = st.slider("Years", 5, 45, 30, 5)
    with cm3: mm_start   = st.number_input("Starting amount ($)", min_value=0.0,
                                            value=float(sum(load_portfolio() and
                                                [tr["amount"] for tr in load_portfolio()] or [0])),
                                            step=100.0, key="mm_start")
    voo_hist = trailing_ann(prices["VOO"].dropna(), 10)/100 if "VOO" in prices.columns else 0.10
    scen = [("Conservative 6%", 0.06, T["text2"]), ("Historical S&P ~10%", 0.10, T["gold"]),
            (f"VOO 10-yr actual {voo_hist*100:.1f}%", voo_hist, T["green"]), ("Optimistic 13%", 0.13, "#00bfff")]
    mfig = go.Figure()
    end_vals = {}
    for name, rate, colr in scen:
        srs = compound_series(mm_monthly, mm_years, rate, mm_start)
        end_vals[name] = (srs.iloc[-1], colr)
        mfig.add_trace(go.Scatter(x=srs.index, y=srs.values, name=name, mode="lines",
                                  line=dict(width=2.4, color=colr)))
    invested_line = [mm_start + mm_monthly*12*y for y in np.linspace(0, mm_years, mm_years*12+1)]
    mfig.add_trace(go.Scatter(x=list(np.linspace(0, mm_years, mm_years*12+1)), y=invested_line,
                              name="Cash you put in", mode="lines",
                              line=dict(width=1.6, color=T["text3"], dash="dot")))
    mfig.update_layout(template="plotly_dark", height=430, paper_bgcolor=T["bg"], plot_bgcolor=T["bg"],
                       hovermode="x unified", xaxis_title="Years", yaxis_title="Portfolio value ($)",
                       legend=dict(orientation="h", y=-0.18), font=dict(family="Roboto Mono", size=11))
    mfig.update_xaxes(gridcolor=T["bg3"]); mfig.update_yaxes(gridcolor=T["bg3"], tickformat="$,.0f")
    st.plotly_chart(mfig, use_container_width=True)
    total_in_mm = mm_start + mm_monthly*12*mm_years
    mid_val = end_vals.get("Historical S&P ~10%", (0, ""))[0]
    st.markdown(f'<div style="font-size:13px;color:{T["text2"]};">'
                f'You contribute <b style="color:{T["text"]};">${total_in_mm:,.0f}</b> over {mm_years} years. '
                f'At the historical ~10%, compounding turns it into '
                f'<b style="color:{T["gold"]};">${mid_val:,.0f}</b> \u2014 '
                f'<b style="color:{T["green"]};">${mid_val-total_in_mm:,.0f}</b> of that is growth doing the work, not you.</div>',
                unsafe_allow_html=True)

# ================================================================ TAB: MY PROFILE
with tab_profile:
    st.markdown('<div class="lbl">Investor Profile \u2014 who you are shapes every recommendation</div>',
                unsafe_allow_html=True)
    prof = load_profile()

    if prof.get("type"):
        st.markdown(f'<div style="border:1px solid {T["gold"]};border-radius:10px;padding:20px 24px;background:{T["bg2"]};margin-bottom:14px;">'
                    f'<div style="font-size:10px;color:{T["text3"]};text-transform:uppercase;letter-spacing:2px;">Your investor type \u00b7 assessed {prof.get("taken_at","")}</div>'
                    f'<div style="font-family:Oswald;font-size:26px;font-weight:700;color:{T["gold"]};margin:6px 0;">{prof["type"]}</div>'
                    f'<div style="font-size:12.5px;color:{T["text2"]};line-height:1.7;">{prof["description"]}</div>'
                    f'<div style="font-size:11px;color:{T["text3"]};margin-top:8px;">Risk capacity score: {prof["score"]}/{prof["max"]} ({prof["pct"]}%) \u00b7 '
                    f'This profile is injected into the AI Advisor\u2019s context \u2014 every answer it gives is calibrated to who you are.</div>'
                    f'</div>', unsafe_allow_html=True)
        if st.button("Retake the quiz", key="retake_quiz"):
            save_profile({})
            st.rerun()
    else:
        st.markdown(f'<div style="font-size:12.5px;color:{T["text2"]};margin-bottom:14px;">'
                    f'Six questions, two minutes. Your answers create a persistent investor profile that '
                    f'personalizes the AI Advisor, recommendations, and risk warnings across the whole platform.</div>',
                    unsafe_allow_html=True)
        with st.form("profile_quiz"):
            answers = {}
            for i, (key, question, options) in enumerate(QUIZ):
                choice = st.radio(f"**{i+1}. {question}**", [o[0] for o in options],
                                  key=f"quiz_{key}", index=None)
                if choice is not None:
                    answers[key] = dict(options)[choice]
            submitted_quiz = st.form_submit_button("Get my investor profile", use_container_width=True)
            if submitted_quiz:
                if len(answers) < len(QUIZ):
                    st.warning("Answer all six questions to get your profile.")
                else:
                    result = score_quiz(answers)
                    save_profile(result)
                    st.rerun()

    # ---- Dividend tax estimator ----
    st.markdown(f'<div class="lbl">{gloss("Qualified dividend","Dividend Tax Estimator")} \u2014 what you\u2019d owe even without selling</div>',
                unsafe_allow_html=True)
    st.caption("Reinvested dividends in a TAXABLE account are still taxed the year they're paid \u2014 reinvesting doesn't defer them. "
               "(Selling shares for gains is a separate tax you only pay when you sell.)")
    tax_trades = load_portfolio()
    if tax_trades:
        tax_pnl = compute_pnl(tax_trades, prices, live_quotes=live_q)
        if not tax_pnl.empty:
            vals_by_t = tax_pnl.groupby("Ticker")["Cur. Value $"].sum().to_dict()
            div_info_t = get_dividend_info(tuple(vals_by_t.keys()))
            div_by_t = {t: v * div_info_t.get(t, 0)/100 for t, v in vals_by_t.items()}
            bracket = st.selectbox("Your annual taxable income bracket:",
                                   ["~$0-47k (student)", "$47k-100k", "$100k-500k", "$500k+"],
                                   index=0, key="tax_bracket")
            est = dividend_tax_estimate(div_by_t, bracket)
            tx1, tx2, tx3 = st.columns(3)
            tx1.markdown(f'<div class="card" style="text-align:center;"><div style="font-size:10px;color:{T["text3"]};">ANNUAL DIVIDENDS</div>'
                         f'<div style="font-size:20px;font-weight:700;color:{T["green"]};margin-top:5px;">${est["total_div"]:,.2f}</div></div>',
                         unsafe_allow_html=True)
            tx2.markdown(f'<div class="card" style="text-align:center;"><div style="font-size:10px;color:{T["text3"]};">EST. TAX OWED / YR</div>'
                         f'<div style="font-size:20px;font-weight:700;color:{T["orange"]};margin-top:5px;">${est["total_tax"]:,.2f}</div></div>',
                         unsafe_allow_html=True)
            keep_pct = (1 - est["total_tax"]/est["total_div"])*100 if est["total_div"] else 100
            tx3.markdown(f'<div class="card" style="text-align:center;"><div style="font-size:10px;color:{T["text3"]};">YOU KEEP</div>'
                         f'<div style="font-size:20px;font-weight:700;color:{T["text"]};margin-top:5px;">{keep_pct:.1f}%</div></div>',
                         unsafe_allow_html=True)
            if est["rows"]:
                st.dataframe(pd.DataFrame(est["rows"]), hide_index=True, use_container_width=True)
            if bracket == "~$0-47k (student)":
                st.markdown(f'<div style="font-size:12px;color:{T["green"]};">'
                            f'\u2705 Good news: at student income levels, QUALIFIED dividends are taxed at 0%. '
                            f'Your only drag is the small ordinary-income slice (mostly from VXUS\u2019s foreign dividends). '
                            f'A Roth IRA would shelter even that \u2014 and locks in tax-free growth for 40 years.</div>',
                            unsafe_allow_html=True)
            st.caption("Estimates only \u2014 assumes typical qualified-dividend percentages per fund type. Not tax advice; consult a tax professional for filings.")
    else:
        st.info("Record your trades in MY PORTFOLIO to see your dividend tax picture.")

# ================================================================ TAB 4: AI ADVISOR
with tab_ai:
    st.markdown('<div class="lbl">AI Investment Advisor — knows your portfolio, market data, and 70+ ETFs</div>',
                unsafe_allow_html=True)
    ai_key = st.session_state.get("ai_key","")
    if not ai_key:
        st.info("Enter your Anthropic API key in the sidebar. Get one free at console.anthropic.com.")
    else:
        # ---- Past Conversations panel ----
        with st.expander("📚 Past Conversations", expanded=False):
            load_past_conversations.clear()
            past_convs = load_past_conversations()
            sb_ready   = _get_sb() is not None
            if not sb_ready:
                st.caption("Connect Supabase (SUPABASE_URL + SUPABASE_KEY in Streamlit secrets) to persist conversations.")
            elif not past_convs:
                st.caption("No saved conversations yet. Start chatting and your history will appear here.")
            else:
                for conv in past_convs:
                    date     = (conv.get("updated_at") or conv.get("created_at",""))[:10]
                    title    = conv.get("title","Untitled")[:55]
                    msg_cnt  = len(conv.get("messages",[]))
                    pc1, pc2, pc3 = st.columns([3, 1, 1])
                    with pc1:
                        if st.button(f"{date} — {title} ({msg_cnt} msgs)",
                                     key=f"view_{conv['id']}", help="Click to view"):
                            st.session_state.ai_messages  = conv.get("messages", [])
                            st.session_state.conv_id      = conv["id"]
                            st.session_state.conv_title   = conv.get("title","Untitled")
                            st.session_state.viewing_past = conv["id"]
                            st.rerun()
                    with pc2:
                        if st.button("Continue", key=f"cont_{conv['id']}"):
                            st.session_state.ai_messages  = conv.get("messages", [])
                            st.session_state.conv_id      = conv["id"]
                            st.session_state.conv_title   = conv.get("title","Untitled")
                            st.session_state.viewing_past = None
                            st.rerun()
                    with pc3:
                        if st.button("🗑", key=f"del_{conv['id']}", help="Delete"):
                            delete_conversation(conv["id"])
                            if st.session_state.conv_id == conv["id"]:
                                st.session_state.ai_messages  = []
                                st.session_state.conv_id      = str(dt.datetime.now().timestamp())
                                st.session_state.conv_title   = "New conversation"
                            st.rerun()

        # ---- New chat button ----
        nc1, nc2 = st.columns([1, 4])
        with nc1:
            if st.button("🆕 New chat", use_container_width=True):
                if st.session_state.ai_messages:
                    save_conversation(st.session_state.conv_id,
                                      st.session_state.conv_title,
                                      st.session_state.ai_messages)
                st.session_state.ai_messages  = []
                st.session_state.conv_id      = str(dt.datetime.now().timestamp())
                st.session_state.conv_title   = "New conversation"
                st.session_state.viewing_past = None
                st.rerun()
        with nc2:
            if st.session_state.ai_messages:
                st.markdown(f'<div style="color:{T["text2"]};font-size:12px;padding-top:8px;">'
                            f'💬 <b>{st.session_state.conv_title}</b> '
                            f'({len(st.session_state.ai_messages)} messages)</div>',
                            unsafe_allow_html=True)
        st.divider()

        # ---- Build context ----
        dfm_ai    = compute_metrics(prices, "VOO")
        sigs_ai   = compute_signals(prices[[t for t in sel if t in prices.columns]])
        trades_ai = load_portfolio()
        pnl_ai    = compute_pnl(trades_ai, prices, live_quotes=live_q) if trades_ai else pd.DataFrame()
        fg_ai     = get_fear_greed()
        macro_ai  = get_macro_snapshot()

        pf_sum = "No investments recorded yet."
        if not pnl_ai.empty:
            ti  = pnl_ai["Invested $"].sum()
            tc  = pnl_ai["Cur. Value $"].sum()
            pf_sum = (f"Total invested: ${ti:,.0f}, current value: ${tc:,.0f}, "
                      f"gain: ${tc-ti:+,.0f} ({(tc/ti-1)*100:+.1f}%)\n"
                      + "\n".join(f"  {r['Ticker']}: invested ${r['Invested $']:.0f}, "
                                   f"now ${r['Cur. Value $']:.0f} ({r['Return %']:+.1f}%, ann {r['Ann. %']:+.1f}%)"
                                   for _, r in pnl_ai.iterrows()))

        m_snap = []
        for _, r in dfm_ai.iterrows():
            t   = r["Ticker"]
            sig = sigs_ai.get(t, {})
            m_snap.append(
                f"  {t} ({'HELD' if t in OWNED else 'watchlist'}): "
                f"${r['Price']:.2f}, 1Y {r['1Y TR %']:+.1f}%, 5Y {r['5Y Ann %']:+.1f}%/yr, "
                f"Sharpe {r['Sharpe']:.2f}, MaxDD {r['Max DD %']:.0f}%, "
                f"Corr→VOO {r['Corr→VOO']:.2f}"
                + (f", RSI {sig['rsi']}" if sig else "")
                + (", Golden X" if sig.get("golden") else
                   ", Death X" if sig.get("golden") is False else ""))

        top_opp = dfm_ai[~dfm_ai["Ticker"].isin(OWNED)].dropna(subset=["Sharpe"]).nlargest(5,"Sharpe")
        opp_l   = [f"  {r['Ticker']} ({r['Category']}): 5Y {r['5Y Ann %']:+.1f}%/yr, Sharpe {r['Sharpe']:.2f}"
                   for _, r in top_opp.iterrows()]
        macro_str = ", ".join(f"{k}={v['current']}" for k,v in macro_ai.items()) if macro_ai else "unavailable"
        held_cats   = set(CATALOG.get(t,{}).get("cat","") for t in OWNED)
        all_cats    = {"core","growth","tech","semis","dividend","value","factor","sector","intl","smallmid","realasset","bond","thematic"}
        missing_str = ", ".join(CAT_LABEL.get(c,c) for c in all_cats-held_cats)
        memory_ctx  = build_memory_context(st.session_state.conv_id)
        prof_ai     = load_profile()
        profile_ctx = ""
        if prof_ai.get("type"):
            profile_ctx = (f"INVESTOR PROFILE (from their quiz, {prof_ai.get('taken_at','')}): "
                           f"{prof_ai['type']} \u2014 {prof_ai['description']} "
                           f"Risk capacity {prof_ai['pct']}%. Calibrate ALL advice to this profile: "
                           f"risk warnings, allocation suggestions, and tone.")

        sys_prompt = (
            "You are an expert ETF investment advisor for a 20-year-old F-1 visa student "
            "with a 30-40 year investing horizon. You have real-time data and memory of prior conversations.\n\n"
            "PHILOSOPHY: Long-term buy-and-hold. VOO ~50%. Moderate-high risk. Never sells.\n\n"
            f"HELD ETFs: {', '.join(OWNED)}\n"
            f"PORTFOLIO P&L:\n{pf_sum}\n\n"
            f"CURRENT METRICS:\n" + "\n".join(m_snap) + "\n\n"
            f"MARKET SENTIMENT: {fg_ai['value']}/100 \u2014 {fg_ai['label']}\n"
            f"MACRO: {macro_str}\n\n"
            f"TOP NON-HELD OPPS:\n" + "\n".join(opp_l) + "\n\n"
            f"MISSING CATEGORIES: {missing_str}\n\n"
            f"{profile_ctx}\n\n"
            f"{memory_ctx}\n\n"
            "INSTRUCTIONS: Be direct, data-backed, beginner-friendly. Give real tickers. "
            "Reference prior conversations naturally when relevant. "
            "You are not a licensed financial advisor."
        )

        # ---- Starter questions ----
        if not st.session_state.ai_messages:
            st.markdown(f'<div style="font-size:11.5px;color:{T["text2"]};margin-bottom:10px;">Suggested questions:</div>',
                        unsafe_allow_html=True)
            starters = [
                "What should I invest in right now for highest long-term returns?",
                "Based on current macro conditions, how should I adjust my portfolio?",
                "What does the Fear & Greed index mean for my holdings today?",
                "What ETFs would best diversify my current portfolio?",
                "How does SMH's volatility compare to VOO and is it worth holding?",
                "What's the ideal allocation for someone my age with my goals?",
            ]
            sc = st.columns(2)
            for i, q in enumerate(starters):
                with sc[i%2]:
                    if st.button(q, key=f"s_{i}"):
                        st.session_state.conv_title = q[:60]
                        st.session_state.ai_messages.append({"role":"user","content":q})
                        st.rerun()

        # ---- Render messages ----
        for msg in st.session_state.ai_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # ---- Chat input ----
        if prompt := st.chat_input("Ask about your portfolio, ETFs, macro, what to buy…"):
            if not st.session_state.ai_messages:
                st.session_state.conv_title = prompt[:60]
            st.session_state.ai_messages.append({"role":"user","content":prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                try:
                    import anthropic as _ant
                    client    = _ant.Anthropic(api_key=ai_key)
                    holder    = st.empty()
                    full_resp = ""
                    with client.messages.stream(
                        model="claude-sonnet-4-6", max_tokens=1400,
                        system=sys_prompt,
                        messages=[{"role":m["role"],"content":m["content"]}
                                  for m in st.session_state.ai_messages[-14:]]
                    ) as stream:
                        for chunk in stream.text_stream:
                            full_resp += chunk
                            holder.markdown(full_resp+"◌")
                    holder.markdown(full_resp)
                    st.session_state.ai_messages.append({"role":"assistant","content":full_resp})
                    save_conversation(st.session_state.conv_id,
                                      st.session_state.conv_title,
                                      st.session_state.ai_messages)
                    load_past_conversations.clear()
                except ImportError:
                    st.error("Run: pip install anthropic")
                except Exception as e:
                    err = str(e)
                    if "credit" in err.lower() or "balance" in err.lower():
                        st.error("Out of Anthropic credits. Go to console.anthropic.com → Plans & Billing to add credits.")
                    elif "invalid_api_key" in err.lower() or "authentication" in err.lower():
                        st.error("Invalid API key — check it in the sidebar.")
                    else:
                        st.error(f"AI error: {err}")

        st.markdown(f'<div class="disclaim">Conversations auto-save to Supabase after each reply. ' +
                    f'Prior sessions inform AI memory. Educational only, not financial advice.</div>',
                    unsafe_allow_html=True)


# ================================================================ TAB 5: CHART
with tab_chart:
    st.markdown('<div class="lbl">Total Return Chart</div>', unsafe_allow_html=True)
    rl = st.radio("Range:", list(RANGES.keys()), index=6, horizontal=True,
                  label_visibility="collapsed")
    mode, p, interval = RANGES[rl]
    if mode == "intraday":
        with st.spinner(f"Loading {rl} intraday data\u2026"):
            try: plot_df = load_intraday(sel, p, interval)
            except Exception as e: st.error(f"Intraday fetch: {e}"); plot_df = pd.DataFrame()
    else:
        plot_df = prices[prices.index >= prices.index[-1]-pd.Timedelta(days=p)]

    palette = [T["gold"],T["orange"],T["green"],"#4f8ef7","#a78bfa","#2dd4bf",
               "#fb923c","#e879f9","#60a5fa","#f87171"]
    fig = go.Figure()
    for i, t in enumerate(sel):
        if t not in plot_df.columns: continue
        s = plot_df[t].dropna()
        if s.empty: continue
        norm = s/s.iloc[0]*100-100
        fig.add_trace(go.Scatter(x=s.index, y=norm, name=t, mode="lines",
            line=dict(width=2.2, color=palette[i%len(palette)])))
    fig.add_hline(y=0, line_dash="dot", line_color=T["text3"], line_width=1)
    fig.update_layout(title=f"Total return \u2014 {rl} (rebased to 0%)",
        template="plotly_dark", height=540, hovermode="x unified",
        paper_bgcolor=T["bg"], plot_bgcolor=T["bg"],
        yaxis_title="Total return %", legend=dict(orientation="h",y=-0.15),
        font=dict(family="Roboto Mono"))
    fig.update_xaxes(gridcolor=T["bg3"]); fig.update_yaxes(gridcolor=T["bg3"])
    st.plotly_chart(fig, use_container_width=True)
    st.caption("1D/1W = intraday bars. 1M+ = daily total-return closes (dividends reinvested).")

# ================================================================ FOOTER
st.markdown(f'<div class="disclaim">ETF Investor Bro v4 \u00b7 Built with yfinance \u00b7 pandas \u00b7 '
            f'plotly \u00b7 streamlit \u2014 all open-source. '
            f'Expense ratios verified ~June 2026. Technical signals are indicators, not predictions. '
            f'Monte Carlo uses historical volatility \u2014 not a forecast. Educational only, not financial advice.</div>',
            unsafe_allow_html=True)