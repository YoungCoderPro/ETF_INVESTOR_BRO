#!/usr/bin/env python3
"""
================================================================================
 ETF COMMAND CENTER v3  —  personal investing dashboard
================================================================================
 Run:    python -m streamlit run etf_app.py
 Mobile: open http://<your-network-url>:8501 on any device on the same WiFi
 Deploy: push to GitHub -> share.streamlit.io (free public URL, no VS Code needed)
================================================================================
"""
import datetime as dt, json, os, numpy as np, pandas as pd
import streamlit as st
import plotly.graph_objects as go
from pathlib import Path
import yfinance as yf
from PIL import Image as _PIL_Image

# ================================================================ CONSTANTS
OWNED   = ["VOO", "VGT", "SMH", "VXUS", "SCHG"]
RF      = 0.02
PORTFOLIO_FILE = Path(__file__).parent / "portfolio.json"

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

CAT_LABEL = {"core":"US Core","growth":"Growth","tech":"Tech","semis":"Semis",
    "dividend":"Dividend","value":"Value","factor":"Factor","sector":"Sector",
    "intl":"International","smallmid":"Small/Mid","realasset":"Real Asset",
    "bond":"Bond","thematic":"Thematic","custom":"Custom"}
MEGACAP_WATCH = ["NVDA","AAPL","MSFT","AMZN","GOOGL","META","TSLA"]
RANGES = {"1D":("intraday","1d","5m"),"1W":("intraday","5d","15m"),
          "1M":("daily",30,None),"1Y":("daily",365,None),
          "3Y":("daily",3*365,None),"5Y":("daily",5*365,None),"10Y/MAX":("daily",10*365,None)}

# ================================================================ DATA LAYER

@st.cache_data(ttl=60*60*6, show_spinner=False)
def load_prices(tickers: tuple, days: int = 3650) -> pd.DataFrame:
    end = dt.date.today()
    start = end - dt.timedelta(days=days + 15)
    df = yf.download(list(tickers), start=start, end=end, auto_adjust=True, progress=False)["Close"]
    if isinstance(df, pd.Series):
        df = df.to_frame(name=tickers[0])
    return df.dropna(how="all")

@st.cache_data(ttl=60*5, show_spinner=False)
def load_intraday(tickers: tuple, period: str, interval: str) -> pd.DataFrame:
    df = yf.download(list(tickers), period=period, interval=interval, auto_adjust=True, progress=False)["Close"]
    if isinstance(df, pd.Series):
        df = df.to_frame(name=tickers[0])
    return df.dropna(how="all")

def trailing_ann(s: pd.Series, years: int):
    cut = s.index[-1] - pd.DateOffset(years=years)
    sub = s[s.index >= cut].dropna()
    if len(sub) < 2: return np.nan
    r = sub.iloc[-1] / sub.iloc[0] - 1
    return ((1 + r) ** (1 / years) - 1) * 100

def compute_metrics(prices: pd.DataFrame, bench: str = "VOO") -> pd.DataFrame:
    rows, bench_ret, bench_y5 = [], None, np.nan
    if bench in prices.columns:
        bench_ret = prices[bench].pct_change().dropna()
        bench_y5  = trailing_ann(prices[bench].dropna(), 5)
    for t in prices.columns:
        s = prices[t].dropna()
        if len(s) < 30: continue
        rets = s.pct_change().dropna()
        yrs  = (s.index[-1] - s.index[0]).days / 365.25
        cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / max(yrs, 0.1)) - 1
        vol  = float(rets.std()) * np.sqrt(252)
        down = float(rets[rets < 0].std()) * np.sqrt(252)
        cum  = (1 + rets).cumprod()
        mdd  = float(((cum - cum.cummax()) / cum.cummax()).min())
        corr = np.nan
        if bench_ret is not None and t != bench:
            al = pd.concat([rets, bench_ret], axis=1, sort=False).dropna()
            corr = float(al.iloc[:,0].corr(al.iloc[:,1])) if len(al) > 2 else np.nan
        elif t == bench:
            corr = 1.0
        y5 = trailing_ann(s, 5)
        meta = CATALOG.get(t, dict(name=t, cat="custom", role="Custom", er=np.nan))
        rows.append(dict(
            Ticker=t, Name=meta["name"], Category=CAT_LABEL.get(meta["cat"],""),
            Held="✅" if t in OWNED else "",
            Price=round(float(s.iloc[-1]), 2), ER=meta["er"],
            **{"1Y TR %": round(trailing_ann(s,1),1), "3Y Ann %": round(trailing_ann(s,3),1),
               "5Y Ann %": round(y5,1),              "10Y Ann %": round(trailing_ann(s,10),1)},
            **{"Vol %": round(vol*100,1),
               "Sharpe": round((cagr-RF)/vol, 2) if vol > 0 else np.nan,
               "Sortino": round((cagr-RF)/down, 2) if down > 0 else np.nan,
               "Max DD %": round(mdd*100,1),
               "Corr→VOO": round(corr,2) if pd.notna(corr) else np.nan,
               "vs S&P 5Y": round(y5-bench_y5,1) if pd.notna(y5) and pd.notna(bench_y5) else np.nan}))
    return pd.DataFrame(rows)

def compute_rsi(s: pd.Series, period: int = 14) -> pd.Series:
    delta = s.diff()
    gain  = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    loss  = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def compute_signals(prices: pd.DataFrame) -> dict:
    out = {}
    for t in prices.columns:
        s = prices[t].dropna()
        if len(s) < 55: continue
        rsi     = compute_rsi(s)
        ma50    = s.rolling(50).mean()
        ma200   = s.rolling(200).mean() if len(s) >= 200 else None
        price   = float(s.iloc[-1])
        hi52    = float(s[-252:].max()) if len(s)>=252 else float(s.max())
        lo52    = float(s[-252:].min()) if len(s)>=252 else float(s.min())
        golden  = bool(float(ma50.iloc[-1]) > float(ma200.iloc[-1])) if ma200 is not None else None
        ret_1m  = (s.iloc[-1]/s.iloc[-22]-1)*100 if len(s)>=22 else np.nan
        ret_3m  = (s.iloc[-1]/s.iloc[-66]-1)*100 if len(s)>=66 else np.nan
        out[t]  = dict(rsi=round(float(rsi.iloc[-1]),1), price=price,
                       ma50=round(float(ma50.iloc[-1]),2),
                       ma200=round(float(ma200.iloc[-1]),2) if ma200 is not None else None,
                       hi52=hi52, lo52=lo52,
                       pct_from_hi=round((price-hi52)/hi52*100,1),
                       pct_from_lo=round((price-lo52)/lo52*100,1),
                       golden=golden, ret_1m=round(float(ret_1m),1),
                       ret_3m=round(float(ret_3m),1))
    return out

@st.cache_data(ttl=60*60, show_spinner=False)
def get_news(tickers: tuple) -> list:
    articles = []
    for t in tickers:
        try:
            raw = yf.Ticker(t).news or []
            for item in raw[:4]:
                content = item.get("content", {})
                if content:
                    title = content.get("title","")
                    url   = (content.get("canonicalUrl") or {}).get("url","")
                    pub   = (content.get("provider") or {}).get("displayName","")
                    ptime = content.get("pubDate","")
                else:
                    title = item.get("title","")
                    url   = item.get("link","")
                    pub   = item.get("publisher","")
                    ptime = str(item.get("providerPublishTime",""))
                if title:
                    articles.append(dict(ticker=t, title=title, url=url, publisher=pub, time=ptime))
        except Exception:
            pass
    articles.sort(key=lambda x: x.get("time",""), reverse=True)
    return articles[:25]

@st.cache_data(ttl=60*60*4, show_spinner=False)
def get_suggestions(owned: tuple, n: int = 5) -> list:
    candidates = [t for t in list(CATALOG)[:40] if t not in owned]
    try:
        px = yf.download(candidates, period="3mo", auto_adjust=True, progress=False)["Close"]
        if isinstance(px, pd.Series): px = px.to_frame(name=candidates[0])
        res = []
        for t in px.columns:
            s = px[t].dropna()
            if len(s) < 20: continue
            rets = s.pct_change().dropna()
            r1m  = (s.iloc[-1]/s.iloc[-22]-1)*100 if len(s)>=22 else np.nan
            vol  = float(rets.std()) * np.sqrt(252) * 100
            sharpe = (r1m - 0.5) / vol if vol > 0 and pd.notna(r1m) else -99
            res.append(dict(ticker=t, ret_1m=round(r1m,1), sharpe_3m=round(sharpe,2)))
        res.sort(key=lambda x: -x["sharpe_3m"])
        return res[:n]
    except Exception:
        return []

@st.cache_data(ttl=60*60*6, show_spinner=False)
def validate_ticker(ticker: str):
    ticker = ticker.strip().upper()
    if not ticker or not ticker.replace(".","").replace("-","").isalnum(): return None
    try:
        fi = yf.Ticker(ticker).fast_info
        p  = fi.get("lastPrice") or fi.get("last_price")
        return {"ticker": ticker, "price": float(p)} if p else None
    except Exception: return None

@st.cache_data(ttl=60*60*24, show_spinner=False)
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

def monte_carlo(s: pd.Series, n_years=10, n_paths=2000, monthly_add=100.0) -> dict:
    rets  = s.pct_change().dropna()
    mu, sigma = float(rets.mean()), float(rets.std())
    start_val = float(s.iloc[-1])
    finals = []
    rng = np.random.default_rng(42)
    for _ in range(n_paths):
        val = start_val
        for day in range(n_years * 252):
            val = val * np.exp(rng.normal(mu - 0.5*sigma**2, sigma))
            if monthly_add > 0 and day % 21 == 0:
                val += monthly_add
        finals.append(val)
    finals.sort()
    n = len(finals)
    return dict(p10=finals[int(n*.10)], p25=finals[int(n*.25)], p50=finals[int(n*.50)],
                p75=finals[int(n*.75)], p90=finals[int(n*.90)], current=start_val)

# ================================================================ PORTFOLIO — SUPABASE + LOCAL FALLBACK

def _get_sb():
    """Return a Supabase client if credentials are configured, else None."""
    try:
        from supabase import create_client
        url = (st.secrets.get("SUPABASE_URL","") if hasattr(st,"secrets") else "") \
              or os.environ.get("SUPABASE_URL","")
        key = (st.secrets.get("SUPABASE_KEY","") if hasattr(st,"secrets") else "") \
              or os.environ.get("SUPABASE_KEY","")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None

def load_portfolio() -> list:
    """Load trades from Supabase if available, else local JSON."""
    sb = _get_sb()
    if sb:
        try:
            rows = sb.table("portfolio_trades").select("*").execute().data or []
            return [{"id": r["id"], "ticker": r["ticker"],
                     "date": str(r["date_bought"]), "amount": r["amount_usd"],
                     "note": r.get("note","")} for r in rows]
        except Exception:
            pass
    # local fallback
    try:
        return json.loads(PORTFOLIO_FILE.read_text()) if PORTFOLIO_FILE.exists() else []
    except Exception:
        return []

def save_portfolio(trades: list):
    """Sync all trades to Supabase (full replace) and keep local JSON as backup."""
    sb = _get_sb()
    if sb:
        try:
            # Delete all existing rows then re-insert (simple full-sync for a small personal list)
            existing = sb.table("portfolio_trades").select("id").execute().data or []
            if existing:
                ids = [r["id"] for r in existing]
                sb.table("portfolio_trades").delete().in_("id", ids).execute()
            if trades:
                rows = [{"id": t.get("id", str(dt.datetime.now().timestamp())),
                         "ticker": t["ticker"], "date_bought": t["date"],
                         "amount_usd": float(t["amount"]), "note": t.get("note","")}
                        for t in trades]
                sb.table("portfolio_trades").insert(rows).execute()
        except Exception:
            pass
    # always write local backup too
    try:
        PORTFOLIO_FILE.write_text(json.dumps(trades, indent=2))
    except Exception:
        pass

def compute_pnl(trades: list, prices: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for trade in trades:
        t, amount = trade["ticker"], float(trade["amount"])
        if t not in prices.columns: continue
        s = prices[t].dropna()
        buy_dt  = pd.Timestamp(trade["date"])
        future  = s[s.index >= buy_dt]
        buy_px  = float(future.iloc[0]) if not future.empty else float(s.iloc[0])
        curr_px = float(s.iloc[-1])
        shares  = amount / buy_px
        curr_v  = shares * curr_px
        gain    = curr_v - amount
        pct     = gain / amount * 100
        days    = max((pd.Timestamp.today() - buy_dt).days, 1)
        try:
            if days < 14:
                ann = pct           # too early to annualize meaningfully
            else:
                raw = (curr_v / amount) ** (365.0 / days) - 1
                ann = float(np.clip(raw * 100, -99.9, 50000.0))
        except (OverflowError, ZeroDivisionError, ValueError):
            ann = pct
        rows.append({"ID": trade.get("id",""), "Ticker": t,
                     "Date": trade["date"], "Invested $": round(amount,2),
                     "Cur. Value $": round(curr_v,2), "Gain $": round(gain,2),
                     "Return %": round(pct,2), "Ann. %": round(ann,2),
                     "Days": days, "Note": trade.get("note","")})
    return pd.DataFrame(rows) if rows else pd.DataFrame()

# ================================================================ UI SETUP

_app_icon = _PIL_Image.open(Path(__file__).parent / "icon.png")
st.set_page_config(page_title="ETF Investor Bro", layout="wide", page_icon=_app_icon,
    initial_sidebar_state="expanded")
st.markdown("""
<link rel="manifest" href="https://raw.githubusercontent.com/YoungCoderPro/ETF-Investor/main/manifest.json">
<link rel="apple-touch-icon" href="https://raw.githubusercontent.com/YoungCoderPro/ETF-Investor/main/icon.png">
<link rel="shortcut icon" href="https://raw.githubusercontent.com/YoungCoderPro/ETF-Investor/main/icon.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="ETF Investor Bro">
<meta name="theme-color" content="#d4af37">
""", unsafe_allow_html=True)

THEME = dict(bg="#0d1f2d", bg2="#132233", bg3="#1f3b4d",
             gold="#d4af37", orange="#f5900a",
             green="#00e676", red="#ff5252",
             text="#dde8f0", text2="#7a9db5", text3="#3d6070")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&family=Oswald:wght@500;600;700&display=swap');
html,body,[class*="css"]{{font-family:'Roboto Mono',monospace;}}
.stApp{{background:{THEME['bg']} !important;}}
section[data-testid="stSidebar"]{{background:{THEME['bg2']};border-right:1px solid {THEME['bg3']};}}
.masthead{{display:flex;align-items:baseline;gap:14px;border-bottom:2px solid {THEME['gold']};
  padding-bottom:10px;margin-bottom:6px;}}
.masthead h1{{font-family:Oswald,sans-serif;font-weight:700;font-size:28px;letter-spacing:1px;
  color:{THEME['text']};margin:0;text-transform:uppercase;}}
.masthead .tag{{color:{THEME['text2']};font-size:11px;letter-spacing:1.5px;text-transform:uppercase;}}
.tape-wrap{{overflow:hidden;white-space:nowrap;background:{THEME['bg2']};
  border:1px solid {THEME['bg3']};border-radius:4px;padding:10px 0;margin:10px 0 18px;}}
.tape{{display:inline-block;animation:scroll-left 36s linear infinite;padding-left:100%;}}
.tape:hover{{animation-play-state:paused;}}
@keyframes scroll-left{{0%{{transform:translateX(0);}}100%{{transform:translateX(-100%);}}}}
.tape-item{{display:inline-block;margin-right:48px;font-size:14px;font-weight:500;}}
.tape-tk{{color:{THEME['text']};font-weight:700;}}
.up{{color:{THEME['green']};font-weight:600;}}.dn{{color:{THEME['red']};font-weight:600;}}
.term-label{{font-family:Oswald,sans-serif;font-size:12.5px;letter-spacing:2px;
  color:{THEME['gold']};text-transform:uppercase;margin:20px 0 10px;
  border-left:3px solid {THEME['gold']};padding-left:10px;}}
.board{{width:100%;border-collapse:collapse;font-size:13px;}}
.board th{{text-align:left;padding:9px 11px;color:{THEME['text2']};font-size:10px;letter-spacing:1px;
  text-transform:uppercase;border-bottom:1px solid {THEME['bg3']};background:{THEME['bg2']};position:sticky;top:0;}}
.board td{{padding:9px 11px;border-bottom:1px solid {THEME['bg3']};color:{THEME['text']};}}
.board tr:hover td{{background:{THEME['bg3']};}}
.row-held td:first-child{{border-left:3px solid {THEME['gold']};}}
.row-watch td:first-child{{border-left:3px solid #4f8ef7;}}
.tk-cell{{font-weight:700;font-size:14px;color:{THEME['text']};}}
.tk-name{{font-size:10px;color:{THEME['text3']};display:block;margin-top:1px;}}
.held-tag{{font-size:8.5px;background:rgba(212,175,55,.18);color:{THEME['gold']};
  padding:1px 6px;border-radius:3px;margin-left:5px;letter-spacing:.5px;}}
.sharpe-bg{{background:{THEME['bg3']};border-radius:2px;height:12px;width:65px;
  display:inline-block;vertical-align:middle;overflow:hidden;margin-right:5px;}}
.sharpe-fill{{height:100%;background:linear-gradient(90deg,{THEME['bg3']},{THEME['gold']});}}
.card{{background:{THEME['bg2']};border:1px solid {THEME['bg3']};border-radius:8px;padding:16px 18px;margin-bottom:12px;}}
.signal-ok{{color:{THEME['green']};font-weight:600;}}
.signal-warn{{color:{THEME['orange']};font-weight:600;}}
.signal-bad{{color:{THEME['red']};font-weight:600;}}
.news-item{{border-left:3px solid {THEME['orange']};padding:8px 12px;margin-bottom:8px;
  background:{THEME['bg2']};border-radius:0 6px 6px 0;}}
.news-tk{{font-size:10px;font-weight:700;color:{THEME['gold']};}}
.news-title{{font-size:13px;color:{THEME['text']};line-height:1.4;}}
.news-meta{{font-size:10.5px;color:{THEME['text3']};margin-top:3px;}}
.pf-pos{{color:{THEME['green']};font-weight:600;}}
.pf-neg{{color:{THEME['red']};font-weight:600;}}
.suggest-card{{background:{THEME['bg3']};border:1px solid {THEME['gold']};border-radius:8px;
  padding:14px 16px;text-align:center;}}
.suggest-tk{{font-family:Oswald;font-size:20px;font-weight:700;color:{THEME['gold']};}}
.suggest-name{{font-size:10.5px;color:{THEME['text2']};margin-top:2px;}}
.suggest-ret{{font-size:14px;font-weight:600;margin-top:6px;}}
.disclaim{{color:{THEME['text3']};font-size:10.5px;line-height:1.6;
  border-top:1px solid {THEME['bg3']};padding-top:14px;margin-top:24px;}}
</style>""", unsafe_allow_html=True)

# ================================================================ SESSION STATE
for k, v in [("selected", list(OWNED)), ("selected_etf", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ================================================================ SIDEBAR
with st.sidebar:
    st.markdown(f'<div style="font-family:Oswald;font-size:16px;color:{THEME["gold"]};'
                f'letter-spacing:1px;text-transform:uppercase;margin-bottom:12px;">⚙ Controls</div>',
                unsafe_allow_html=True)
    st.markdown("**Your holdings:**")
    st.markdown(" ".join(f'<code style="background:{THEME["bg3"]};color:{THEME["gold"]};'
                         f'padding:2px 6px;border-radius:3px;">{t}</code>' for t in OWNED),
                unsafe_allow_html=True)
    st.markdown("---")
    addable = [f"{t} — {CATALOG[t]['name']}" for t in CATALOG if t not in st.session_state.selected]
    to_add  = st.multiselect("Add from database:", addable, label_visibility="visible")
    for label in to_add:
        tk = label.split(" — ")[0]
        if tk not in st.session_state.selected:
            st.session_state.selected.append(tk)
    removable = [t for t in st.session_state.selected if t not in OWNED]
    if removable:
        to_rem = st.multiselect("Remove watchlist:", removable)
        st.session_state.selected = [t for t in st.session_state.selected if t not in to_rem]
    st.markdown("---")
    # ---- AI key (used by AI Advisor tab) ----
    ai_key_default = (st.secrets.get("ANTHROPIC_KEY","") if hasattr(st,"secrets") else
                      os.environ.get("ANTHROPIC_KEY",""))
    if "ai_key" not in st.session_state:
        st.session_state.ai_key = ai_key_default
    if not st.session_state.ai_key:
        st.markdown(f'<div style="font-size:10.5px;color:{THEME["gold"]};">🤖 AI Advisor key</div>',
                    unsafe_allow_html=True)
        typed = st.text_input("Anthropic API key:", type="password",
                              placeholder="sk-ant-...", label_visibility="collapsed")
        if typed:
            st.session_state.ai_key = typed
            st.rerun()
        st.caption("Get a free key at console.anthropic.com to enable the AI Advisor tab.")
    else:
        st.markdown(f'<div style="font-size:10.5px;color:{THEME["green"]};">🤖 AI Advisor: ready</div>',
                    unsafe_allow_html=True)
        if st.button("Clear AI key", use_container_width=False):
            st.session_state.ai_key = ""; st.rerun()
    st.markdown("---")
    new_tk = st.text_input("Add any ticker:", placeholder="JEPI, COIN, SPLG…")
    if st.button("➕ Add", use_container_width=True) and new_tk:
        info = validate_ticker(new_tk)
        if info is None: st.error(f"'{new_tk.upper()}' not found on Yahoo Finance.")
        elif info["ticker"] in st.session_state.selected: st.info("Already added.")
        else:
            st.session_state.selected.append(info["ticker"])
            if info["ticker"] not in CATALOG:
                CATALOG[info["ticker"]] = dict(name=info["ticker"], cat="custom",
                    role="Custom", er=float("nan"))
            st.success(f"Added {info['ticker']} @ ${info['price']:.2f}")
    st.markdown("---")
    st.markdown(f'<div style="font-size:10.5px;color:{THEME["text3"]};line-height:1.7;">'
                f'📱 <b>Mobile:</b> same WiFi → use the Network URL shown in your terminal<br>'
                f'🌐 <b>Public URL:</b> push to GitHub → share.streamlit.io (free)<br>'
                f'🔄 Data: prices 6h · intraday 5min · news 1h</div>', unsafe_allow_html=True)

sel = tuple(dict.fromkeys(st.session_state.selected))

# ================================================================ FETCH PRICES
with st.spinner(f"Fetching live total-return data for {len(sel)} ETFs…"):
    try:
        prices = load_prices(sel, days=3650)
    except Exception as e:
        st.error(f"Data fetch failed: {e}"); st.stop()

# ================================================================ MASTHEAD + TAPE
st.markdown(f'<div class="masthead"><h1>📈 ETF Command Center</h1>'
            f'<span class="tag">Live Total-Return Terminal · Dividends Reinvested · {dt.date.today()}</span>'
            f'</div>', unsafe_allow_html=True)

tape_html = ""
for t in sel:
    if t not in prices.columns: continue
    s = prices[t].dropna()
    if len(s) < 2: continue
    chg = (s.iloc[-1]/s.iloc[-2]-1)*100
    cls = "up" if chg>=0 else "dn"
    arr = "▲" if chg>=0 else "▼"
    tape_html += (f'<span class="tape-item"><span class="tape-tk">{t}</span> '
                  f'${s.iloc[-1]:.2f} <span class="{cls}">{arr} {chg:+.2f}%</span></span>')
st.markdown(f'<div class="tape-wrap"><div class="tape">{tape_html*3}</div></div>',
            unsafe_allow_html=True)

# ================================================================ TABS
tab_board, tab_pf, tab_pulse, tab_ai, tab_chart = st.tabs([
    "📋  BOARD", "💼  MY PORTFOLIO", "📰  MARKET PULSE", "🤖  AI ADVISOR", "📈  CHART"])

# ================================================================ TAB 1: BOARD
with tab_board:
    st.markdown('<div class="term-label">Performance Board — Total Return</div>', unsafe_allow_html=True)
    dfm   = compute_metrics(prices, "VOO")
    order = {t:i for i,t in enumerate(sel)}
    dfm   = dfm.sort_values("Ticker", key=lambda c: c.map(lambda t: order.get(t,99)))

    def cell(v, suffix="%", dp=1):
        if pd.isna(v): return f'<span style="color:{THEME["text3"]}">n/a</span>'
        cls, sign = ("up", "+") if v >= 0 else ("dn", "")
        return f'<span class="{cls}">{sign}{v:.{dp}f}{suffix}</span>'


    rows_html2 = ""
    for _, r in dfm.iterrows():
        held     = r["Ticker"] in OWNED
        held_tag = '<span class="held-tag">HELD</span>' if held else ""
        er_str   = f'{r["ER"]:.2f}%' if pd.notna(r["ER"]) else "—"
        sh       = r["Sharpe"]
        sh_html  = (f'<span class="sharpe-bg"><span class="sharpe-fill" style="width:'
                    f'{max(min(sh/2.0,1),0)*100:.0f}%"></span></span>{sh:.2f}') if pd.notna(sh) else "n/a"
        corr_col = r["Corr\u2192VOO"]
        corr_str = "n/a" if pd.isna(corr_col) else f"{float(corr_col):.2f}"
        rows_html2 += (f'<tr class="{"row-held" if held else "row-watch"}">'
            f'<td><span class="tk-cell">{r["Ticker"]}</span>{held_tag}'
            f'<span class="tk-name">{r["Category"]}</span></td>'
            f'<td>${r["Price"]:.2f}</td><td>{er_str}</td>'
            f'<td>{cell(r["1Y TR %"])}</td><td>{cell(r["3Y Ann %"])}</td>'
            f'<td>{cell(r["5Y Ann %"])}</td><td>{cell(r["10Y Ann %"])}</td>'
            f'<td>{r["Vol %"]:.1f}%</td><td>{sh_html}</td>'
            f'<td class="dn">{r["Max DD %"]:.0f}%</td>'
            f'<td>{corr_str}</td>'
            f'<td>{cell(r["vs S&P 5Y"], suffix=" pts")}</td></tr>')

    st.markdown(f'''<div style="overflow-x:auto;border:1px solid {THEME['bg3']};border-radius:6px;">
    <table class="board"><thead><tr><th>ETF</th><th>Price</th><th>Expense</th>
    <th>1Y TR</th><th>3Y Ann</th><th>5Y Ann</th><th>10Y Ann</th><th>Vol</th>
    <th>Sharpe†</th><th>Max DD</th><th>Corr→VOO</th><th>vs S&P 5Y</th></tr></thead>
    <tbody>{rows_html2}</tbody></table></div>''', unsafe_allow_html=True)
    st.caption("Total returns (dividends reinvested). †Sharpe = 2% risk-free rate. Past performance ≠ future results.")

    # clickable buttons
    st.markdown('<div class="term-label">Click a ticker for deep dive</div>', unsafe_allow_html=True)
    cols = st.columns(len(sel))
    for i, t in enumerate(sel):
        with cols[i]:
            active = st.session_state.selected_etf == t
            lbl    = f"{'▶ ' if active else ''}{t}"
            if st.button(lbl, key=f"btn_{t}"):
                st.session_state.selected_etf = None if active else t
                st.rerun()

    pick = st.session_state.selected_etf
    if pick and pick in sel:
        meta   = CATALOG.get(pick, dict(name=pick, cat="custom", role="Custom", er=float("nan")))
        er_str = f'{meta["er"]:.2f}%' if pd.notna(meta["er"]) else "—"
        held_s = f'&middot; <span style="color:{THEME["gold"]}">HELD</span>' if pick in OWNED else ""
        st.markdown(f'''<div style="border:1px solid {THEME['gold']};border-radius:8px;
        padding:16px 20px;background:{THEME['bg2']};margin:12px 0 16px;">
        <span style="font-family:Oswald;font-size:22px;font-weight:700;color:{THEME['text']};
        letter-spacing:1px;">{pick}</span>
        <span style="color:{THEME['gold']};font-size:13px;margin-left:12px;">{meta['name']}</span>
        <span style="color:{THEME['text3']};font-size:11px;margin-left:10px;">
          {CAT_LABEL.get(meta['cat'],'')} &middot; ER {er_str} {held_s}</span></div>''',
            unsafe_allow_html=True)
        with st.spinner(f"Loading {pick} composition…"):
            ov = get_fund_overview(pick)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"##### 📌 Top holdings")
            th = ov["top_holdings"]
            if th is not None and not th.empty:
                td = th.copy()
                if "Holding Percent" in td.columns:
                    td = td.rename(columns={"Holding Percent":"Weight %"})
                    td["Weight %"] = (td["Weight %"]*100).round(2)
                st.dataframe(td, width='stretch')
                if "Holding Percent" in th.columns:
                    olap = th[th.index.isin(MEGACAP_WATCH)]
                    if not olap.empty:
                        pct_t = float(olap["Holding Percent"].sum())*100
                        st.markdown(f"**🔴 Mag-7 overlap: ~{pct_t:.1f}%**")
                        for tkr, row_h in olap.iterrows():
                            w = float(row_h["Holding Percent"])*100
                            bw = int(w*3)
                            st.markdown(f'<span style="font-family:monospace;font-size:12px;'
                                f'color:{THEME["text2"]};">{tkr:6s}</span>'
                                f'<span style="display:inline-block;width:{bw}px;height:10px;'
                                f'background:{THEME["gold"]};border-radius:2px;margin:0 8px;vertical-align:middle;"></span>'
                                f'<span style="color:{THEME["gold"]};font-size:12px;">{w:.1f}%</span>',
                                unsafe_allow_html=True)
                    else:
                        st.caption("No Mag-7 names in disclosed top holdings.")
            else:
                st.caption("Top holdings not available (commodities, bond funds, smaller ETFs).")
        with c2:
            st.markdown("##### 🏭 Sector weights")
            sw = ov["sector_weights"]
            if sw:
                sw_c = {k.replace("_"," ").title(): round(v*100,1) for k,v in sw.items() if v and v>0.001}
                sw_s = dict(sorted(sw_c.items(), key=lambda x: -x[1]))
                sfig = go.Figure(go.Bar(x=list(sw_s.values()), y=list(sw_s.keys()),
                    orientation="h",
                    marker=dict(color=list(sw_s.values()), colorscale=[[0,THEME["bg3"]],[1,THEME["gold"]]],
                                showscale=False),
                    text=[f"{v:.1f}%" for v in sw_s.values()], textposition="outside",
                    textfont=dict(color=THEME["text2"], size=11)))
                sfig.update_layout(template="plotly_dark", height=max(240,28*len(sw_s)),
                    margin=dict(l=10,r=60,t=10,b=10), paper_bgcolor=THEME["bg2"],
                    xaxis_title="% of fund", font=dict(family="Roboto Mono",size=11),
                    xaxis=dict(gridcolor=THEME["bg3"]))
                st.plotly_chart(sfig, width='stretch')
            else:
                st.caption("Sector breakdown not available.")
            if pick in prices.columns and "VOO" in prices.columns and pick != "VOO":
                al  = pd.concat([prices[pick].pct_change().dropna(),
                                  prices["VOO"].pct_change().dropna()], axis=1, sort=False).dropna()
                if len(al) > 2:
                    cv  = float(al.iloc[:,0].corr(al.iloc[:,1]))
                    bc  = THEME["red"] if cv>.9 else THEME["orange"] if cv>.6 else THEME["green"]
                    msg = ("Very high — little diversification benefit." if cv>.9 else
                           "Moderate — meaningful overlap with the market." if cv>.6 else
                           "Low — a genuine diversifier from US equities.")
                    st.markdown(f'<div style="border:1px solid {bc};border-radius:6px;'
                        f'padding:12px 16px;margin-top:10px;background:{THEME["bg"]};">'
                        f'<span style="color:{bc};font-family:Oswald;font-size:18px;font-weight:700;">'
                        f'Corr→VOO: {cv:.2f}</span>'
                        f'<div style="color:{THEME["text2"]};font-size:11.5px;margin-top:5px;">{msg}</div>'
                        f'</div>', unsafe_allow_html=True)
        if ov.get("description"):
            st.markdown("##### 📄 About")
            d = ov["description"]
            st.markdown(f'<div style="color:{THEME["text2"]};font-size:12px;line-height:1.7;">'
                        f'{d[:700]}{"…" if len(d)>700 else ""}</div>', unsafe_allow_html=True)
    else:
        if not pick:
            st.markdown(f'<div style="color:{THEME["text3"]};font-size:12px;padding:12px 0;">'
                        f'Select a ticker above to see top holdings, sector breakdown, and Mag-7 overlap.</div>',
                        unsafe_allow_html=True)

    # concentration donut
    st.markdown('<div class="term-label">Portfolio Concentration</div>', unsafe_allow_html=True)
    cats = {}
    for t in sel:
        c = CAT_LABEL.get(CATALOG.get(t,{}).get("cat",""), "Other")
        cats[c] = cats.get(c,0)+1
    cfig = go.Figure(go.Pie(labels=list(cats.keys()), values=list(cats.values()), hole=0.5,
        marker=dict(colors=[THEME["gold"],THEME["orange"],THEME["green"],"#4f8ef7",
                            THEME["text2"],"#a78bfa","#2dd4bf","#f87171"])))
    cfig.update_layout(template="plotly_dark", height=360, paper_bgcolor=THEME["bg"],
        title="Selected ETFs by category", font=dict(family="Roboto Mono"))
    st.plotly_chart(cfig, width='stretch')
    techish = sum(1 for t in sel if CATALOG.get(t,{}).get("cat") in ("tech","semis","growth"))
    if techish/max(len(sel),1) > 0.5:
        st.warning(f"⚠️ {techish}/{len(sel)} selected ETFs are tech/growth/semis — high concentration risk.")

# ================================================================ TAB 2: MY PORTFOLIO
with tab_pf:
    st.markdown('<div class="term-label">My Investment Tracker</div>', unsafe_allow_html=True)
    trades = load_portfolio()

    with st.expander("➕ Add a new investment", expanded=len(trades)==0):
        with st.form("add_trade", clear_on_submit=True):
            fc1, fc2, fc3, fc4 = st.columns([1,1,1,2])
            with fc1:
                pf_tk = st.text_input("Ticker", placeholder="VOO")
            with fc2:
                pf_dt = st.date_input("Date bought", value=dt.date.today())
            with fc3:
                pf_am = st.number_input("$ Amount", min_value=1.0, value=100.0, step=10.0)
            with fc4:
                pf_nt = st.text_input("Note (optional)", placeholder="First buy, DCA, etc.")
            submitted = st.form_submit_button("Record investment", use_container_width=True)
            if submitted and pf_tk:
                tk_up = pf_tk.strip().upper()
                trades.append({"id": str(dt.datetime.now().timestamp()),
                               "ticker": tk_up, "date": str(pf_dt),
                               "amount": float(pf_am), "note": pf_nt})
                save_portfolio(trades)
                if tk_up not in CATALOG:
                    CATALOG[tk_up] = dict(name=tk_up, cat="custom", role="Custom", er=float("nan"))
                st.success(f"Recorded ${pf_am:.0f} in {tk_up} on {pf_dt}.")
                st.rerun()

    if trades:
        all_tickers = tuple(set(t["ticker"] for t in trades) | set(sel))
        try:
            pf_prices = load_prices(all_tickers)
        except Exception:
            pf_prices = prices
        pnl_df = compute_pnl(trades, pf_prices)

        if not pnl_df.empty:
            total_in  = pnl_df["Invested $"].sum()
            total_cur = pnl_df["Cur. Value $"].sum()
            total_g   = total_cur - total_in
            total_pct = total_g / total_in * 100

            m1, m2, m3, m4 = st.columns(4)
            def metric_card(col, label, val, sub=None, color=None):
                sub_html = (f'<div style="font-size:11px;color:{THEME["text3"]};margin-top:2px;">{sub}</div>'
                            if sub else "")
                col.markdown(f'<div class="card"><div style="font-size:10px;color:{THEME["text3"]};'
                    f'text-transform:uppercase;letter-spacing:1px;">{label}</div>'
                    f'<div style="font-size:22px;font-weight:600;color:{color or THEME["text"]};'
                    f'margin-top:4px;">{val}</div>{sub_html}</div>', unsafe_allow_html=True)
            metric_card(m1, "Total invested",  f"${total_in:,.0f}")
            metric_card(m2, "Current value",   f"${total_cur:,.0f}")
            metric_card(m3, "Total gain/loss",
                        f'{"+" if total_g>=0 else ""}${total_g:,.0f}',
                        color=THEME["green"] if total_g>=0 else THEME["red"])
            metric_card(m4, "Total return",
                        f'{"+" if total_pct>=0 else ""}{total_pct:.1f}%',
                        color=THEME["green"] if total_pct>=0 else THEME["red"])

            # Styled table
            rows_pf = ""
            for _, r in pnl_df.iterrows():
                pos   = r["Gain $"] >= 0
                gc    = THEME["green"] if pos else THEME["red"]
                sign  = "+" if pos else ""
                rows_pf += (f'<tr><td style="font-weight:700;color:{THEME["text"]};">{r["Ticker"]}</td>'
                    f'<td>{r["Date"]}</td>'
                    f'<td>${r["Invested $"]:,.2f}</td>'
                    f'<td>${r["Cur. Value $"]:,.2f}</td>'
                    f'<td style="color:{gc};font-weight:600;">{sign}${r["Gain $"]:,.2f}</td>'
                    f'<td style="color:{gc};font-weight:600;">{sign}{r["Return %"]:.1f}%</td>'
                    f'<td style="color:{gc};">{sign}{r["Ann. %"]:.1f}%</td>'
                    f'<td style="color:{THEME["text3"]};">{r["Days"]}d</td>'
                    f'<td style="color:{THEME["text3"]};font-size:11px;">{r["Note"]}</td>'
                    f'<td></td></tr>')
            st.markdown(f'''<div style="overflow-x:auto;border:1px solid {THEME["bg3"]};border-radius:6px;margin-top:16px;">
            <table class="board"><thead><tr><th>Ticker</th><th>Date</th><th>Invested</th>
            <th>Value Now</th><th>Gain $</th><th>Return %</th><th>Ann. %</th>
            <th>Held</th><th>Note</th><th></th></tr></thead>
            <tbody>{rows_pf}</tbody></table></div>''', unsafe_allow_html=True)

            # Per-ticker breakdown bar
            st.markdown('<div class="term-label">Allocation by ticker</div>', unsafe_allow_html=True)
            tk_summary = pnl_df.groupby("Ticker").agg({"Invested $":"sum","Cur. Value $":"sum"}).reset_index()
            bfig = go.Figure()
            bfig.add_bar(x=tk_summary["Ticker"], y=tk_summary["Invested $"],
                        name="Invested", marker_color=THEME["bg3"])
            bfig.add_bar(x=tk_summary["Ticker"], y=tk_summary["Cur. Value $"],
                        name="Current value", marker_color=THEME["gold"])
            bfig.update_layout(template="plotly_dark", barmode="group", height=320,
                paper_bgcolor=THEME["bg"], font=dict(family="Roboto Mono"),
                legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(bfig, width='stretch')

            # Delete a trade
            ids = [(f'{r["Ticker"]} {r["Date"]} ${r["Invested $"]:.0f}', r["ID"])
                   for _, r in pnl_df.iterrows()]
            del_label = st.selectbox("Delete a trade:", ["—"] + [i[0] for i in ids])
            if del_label != "—":
                del_id = next(i[1] for i in ids if i[0] == del_label)
                if st.button("🗑 Delete selected trade"):
                    trades = [t for t in trades if t.get("id") != del_id]
                    save_portfolio(trades); st.rerun()
        else:
            st.info("No price data found for your recorded trades. Check ticker names.")

        # Monte Carlo projections
        st.markdown('<div class="term-label">10-Year Projection (Monte Carlo)</div>', unsafe_allow_html=True)
        st.caption("Probabilistic simulation based on historical daily volatility — not a forecast. "
                   "2,000 simulated paths, log-normal returns.")
        proj_tk  = st.selectbox("Project ticker:", [t for t in sel if t in prices.columns])
        monthly  = st.number_input("Monthly contribution ($)", min_value=0.0, value=100.0, step=50.0)
        if proj_tk and proj_tk in prices.columns:
            mc = monte_carlo(prices[proj_tk].dropna(), n_years=10, n_paths=2000, monthly_add=monthly)
            p1,p2,p3,p4,p5 = st.columns(5)
            for col, lbl, val, clr in [
                (p1,"Pessimistic\n(10th)",mc["p10"],THEME["red"]),
                (p2,"Conservative\n(25th)",mc["p25"],THEME["orange"]),
                (p3,"Median\n(50th)",mc["p50"],THEME["gold"]),
                (p4,"Optimistic\n(75th)",mc["p75"],THEME["green"]),
                (p5,"Best case\n(90th)",mc["p90"],"#00bfff")]:
                col.markdown(f'<div class="card" style="text-align:center;">'
                    f'<div style="font-size:10px;color:{THEME["text3"]};">{lbl.replace(chr(10),"<br>")}</div>'
                    f'<div style="font-size:20px;font-weight:700;color:{clr};margin-top:6px;">'
                    f'${val:,.0f}</div>'
                    f'<div style="font-size:10px;color:{THEME["text3"]};margin-top:3px;">'
                    f'{val/mc["current"]:.1f}× current</div></div>', unsafe_allow_html=True)
    else:
        st.info("No investments recorded yet. Use the form above to add your first position.")

# ================================================================ TAB 3: MARKET PULSE
with tab_pulse:
    st.markdown('<div class="term-label">Weekly Picks — Top momentum from the database</div>',
                unsafe_allow_html=True)
    with st.spinner("Scanning database for top-momentum ETFs…"):
        sugg = get_suggestions(sel)
    if sugg:
        scols = st.columns(min(len(sugg), 5))
        for i, s_item in enumerate(sugg[:5]):
            tk   = s_item["ticker"]
            meta = CATALOG.get(tk, dict(name=tk, cat="custom", role="Custom"))
            clr  = THEME["green"] if s_item["ret_1m"]>=0 else THEME["red"]
            with scols[i]:
                st.markdown(f'<div class="suggest-card">'
                    f'<div class="suggest-tk">{tk}</div>'
                    f'<div class="suggest-name">{meta["name"]}</div>'
                    f'<div class="suggest-ret" style="color:{clr};">'
                    f'{"+" if s_item["ret_1m"]>=0 else ""}{s_item["ret_1m"]:.1f}% (1M)</div>'
                    f'<div style="font-size:10px;color:{THEME["text3"]};margin-top:4px;">'
                    f'Sharpe(3M) {s_item["sharpe_3m"]:.2f}</div></div>', unsafe_allow_html=True)
    else:
        st.caption("Could not fetch suggestion data right now.")
    st.caption("Based on 1-month risk-adjusted return (Sharpe) across the 70+ ETF database. "
               "Not a recommendation — momentum can reverse.")

    # Technical signals for held ETFs
    st.markdown('<div class="term-label">Technical Signals — Your Holdings</div>', unsafe_allow_html=True)
    sigs = compute_signals(prices[[t for t in OWNED if t in prices.columns]])
    if sigs:
        for t, sg in sigs.items():
            rsi    = sg["rsi"]
            rsi_cls = "signal-bad" if rsi>70 else "signal-ok" if rsi<30 else "signal-warn"
            rsi_lbl = "Overbought" if rsi>70 else "Oversold" if rsi<30 else "Neutral"
            gc_str  = ("✅ Golden cross (MA50>MA200 — bullish)" if sg.get("golden") is True else
                       "⚠️ Death cross (MA50<MA200 — bearish)" if sg.get("golden") is False else "—")
            st.markdown(f'''<div class="card" style="margin-bottom:10px;">
            <span style="font-family:Oswald;font-size:17px;font-weight:700;color:{THEME["gold"]};">{t}</span>
            <span style="color:{THEME["text2"]};font-size:11px;margin-left:10px;">${sg["price"]:.2f}</span>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:10px;">
              <div><div style="font-size:10px;color:{THEME["text3"]};">RSI (14)</div>
                <div class="{rsi_cls}" style="font-size:16px;">{rsi} — {rsi_lbl}</div></div>
              <div><div style="font-size:10px;color:{THEME["text3"]};">vs 52-wk High</div>
                <div style="color:{""+THEME["red"] if sg["pct_from_hi"]<-20 else THEME["orange"] if sg["pct_from_hi"]<-5 else THEME["green"]};font-size:16px;font-weight:600;">{sg["pct_from_hi"]:+.1f}%</div></div>
              <div><div style="font-size:10px;color:{THEME["text3"]};">MA Crossover</div>
                <div style="font-size:13px;color:{THEME["text2"]};">{gc_str}</div></div>
              <div><div style="font-size:10px;color:{THEME["text3"]};">1M Return</div>
                <div class="{"up" if sg["ret_1m"]>=0 else "dn"}" style="font-size:16px;">{sg["ret_1m"]:+.1f}%</div></div>
              <div><div style="font-size:10px;color:{THEME["text3"]};">3M Return</div>
                <div class="{"up" if sg["ret_3m"]>=0 else "dn"}" style="font-size:16px;">{sg["ret_3m"]:+.1f}%</div></div>
              <div><div style="font-size:10px;color:{THEME["text3"]};">MA50</div>
                <div style="font-size:14px;color:{THEME["text2"]};">${sg["ma50"]:,.2f}</div></div>
            </div></div>''', unsafe_allow_html=True)
    st.caption("RSI < 30 = historically oversold / potential buy zone. RSI > 70 = potentially overbought. "
               "These are technical indicators, not predictions.")

    # News
    st.markdown('<div class="term-label">Latest News — Your Holdings</div>', unsafe_allow_html=True)
    with st.spinner("Fetching latest news…"):
        news = get_news(tuple(OWNED))
    if news:
        for art in news:
            link_html = (f'<a href="{art["url"]}" target="_blank" '
                         f'style="color:{THEME["text"]};text-decoration:none;">{art["title"]}</a>'
                         if art.get("url") else art["title"])
            st.markdown(f'<div class="news-item">'
                f'<span class="news-tk">{art["ticker"]}</span>'
                f'<div class="news-title">{link_html}</div>'
                f'<div class="news-meta">{art.get("publisher","")} · {art.get("time","")[:10]}</div>'
                f'</div>', unsafe_allow_html=True)
    else:
        st.caption("No news available right now — Yahoo Finance news coverage varies by ETF.")

# ================================================================ TAB 4: CHART
# ================================================================ TAB 4: AI ADVISOR
with tab_ai:
    st.markdown('<div class="term-label">AI Investment Advisor</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:{THEME["text2"]};font-size:12.5px;line-height:1.7;margin-bottom:16px;">'
                f'Powered by Claude (Anthropic). Knows your portfolio, current metrics, RSI signals, '
                f'and 70+ ETF performance data. Ask it anything about investing.</div>',
                unsafe_allow_html=True)

    ai_key = st.session_state.get("ai_key","")
    if not ai_key:
        st.info("Enter your Anthropic API key in the sidebar to activate the AI Advisor. "
                "Get one free at console.anthropic.com — $5 of free credit, more than enough.")
    else:
        # ---- Build rich context for the AI ----
        dfm_ai = compute_metrics(prices, "VOO")
        sigs_ai = compute_signals(prices[[t for t in sel if t in prices.columns]])
        trades_ai = load_portfolio()
        pnl_ai_df = compute_pnl(trades_ai, prices) if trades_ai else pd.DataFrame()

        # Summarise portfolio
        pf_summary = "No investments recorded yet."
        if not pnl_ai_df.empty:
            total_in  = pnl_ai_df["Invested $"].sum()
            total_cur = pnl_ai_df["Cur. Value $"].sum()
            rows_ai   = []
            for _, r in pnl_ai_df.iterrows():
                rows_ai.append(f"  {r['Ticker']}: invested ${r['Invested $']:.0f}, "
                               f"now ${r['Cur. Value $']:.0f} ({r['Return %']:+.1f}%, "
                               f"ann {r['Ann. %']:+.1f}%)")
            pf_summary = (f"Total invested: ${total_in:,.0f}, current value: ${total_cur:,.0f}, "
                         f"gain: ${total_cur-total_in:+,.0f} ({(total_cur/total_in-1)*100:+.1f}%)\n"
                         + "\n".join(rows_ai))

        # ETF metrics snapshot
        metrics_snap = []
        for _, r in dfm_ai.iterrows():
            t = r["Ticker"]
            sig = sigs_ai.get(t, {})
            rsi_str = f"RSI {sig.get('rsi','?')}" if sig else ""
            ma_str  = ("Golden cross" if sig.get("golden") else
                       "Death cross" if sig.get("golden") is False else "") if sig else ""
            metrics_snap.append(
                f"  {t} ({'HELD' if t in OWNED else 'watchlist'}): "
                f"price ${r['Price']:.2f}, 1Y TR {r['1Y TR %']:+.1f}%, "
                f"5Y ann {r['5Y Ann %']:+.1f}%, Sharpe {r['Sharpe']:.2f}, "
                f"MaxDD {r['Max DD %']:.0f}%, Corr→VOO {r['Corr→VOO']:.2f}"
                + (f", {rsi_str}" if rsi_str else "")
                + (f", {ma_str}" if ma_str else ""))

        # Find top non-held ETFs (basic momentum screen)
        top_opp = dfm_ai[~dfm_ai["Ticker"].isin(OWNED)].dropna(subset=["Sharpe"])
        top_opp = top_opp.nlargest(5, "Sharpe")
        opp_lines = []
        for _, r in top_opp.iterrows():
            opp_lines.append(f"  {r['Ticker']} ({r['Category']}): "
                             f"5Y {r['5Y Ann %']:+.1f}%/yr, Sharpe {r['Sharpe']:.2f}, "
                             f"MaxDD {r['Max DD %']:.0f}%, Corr→VOO {r['Corr→VOO']:.2f}")

        # Diversification gaps
        held_cats = set(CATALOG.get(t,{}).get("cat","") for t in OWNED)
        all_cats  = {"core","growth","tech","semis","dividend","value","factor",
                     "sector","intl","smallmid","realasset","bond","thematic"}
        missing   = all_cats - held_cats
        missing_str = ", ".join(CAT_LABEL.get(c,c) for c in missing)

        system_prompt = f"""You are an expert personal investment advisor with deep knowledge of ETFs, 
portfolio theory, and market dynamics. You are speaking with a 20-year-old F-1 visa student 
who is new to investing and has a long 30-40 year time horizon.

THEIR INVESTMENT PHILOSOPHY:
- Long-term buy-and-hold investor (not a trader)
- VOO always ~50% of portfolio
- Wants growth + diversification
- Risk tolerance: moderate-high (young, long horizon, can stomach drawdowns)
- Primary question they always want answered: "What should I be invested in for highest returns?"

CURRENT HELD ETFs: {', '.join(OWNED)}

PORTFOLIO P&L:
{pf_summary}

CURRENT METRICS FOR ALL SELECTED ETFs:
{chr(10).join(metrics_snap)}

TOP NON-HELD ETF OPPORTUNITIES (by Sharpe ratio, from the 70+ database):
{chr(10).join(opp_lines)}

MISSING DIVERSIFICATION CATEGORIES: {missing_str}

GUIDANCE:
- Be direct and specific. Give actual ticker recommendations with reasoning.
- Back up advice with the real metrics above.
- Explain concepts simply since they are a beginner.
- Acknowledge that past performance doesn't guarantee future results.
- When answering "what should I invest in?", consider: risk-adjusted returns (Sharpe), 
  correlation to VOO (diversification value), sector exposure gaps, and the user's long horizon.
- Distinguish between high-return-high-risk and high-return-moderate-risk options.
- You are NOT a licensed financial advisor; remind them of this when giving specific allocations.
- Keep responses focused and actionable, not overly long."""

        # ---- Chat UI ----
        if "ai_messages" not in st.session_state:
            st.session_state.ai_messages = []

        # Suggested starter questions
        starters = [
            "What should I invest in right now for the highest returns?",
            "How is my current portfolio performing? Any concerns?",
            "What are the most underrated ETFs I'm not holding?",
            "Should I add semiconductors (SMH) or spread into other sectors?",
            "What does my Sharpe ratio tell me, and how can I improve it?",
            "What's the best way to deploy $500 given my current holdings?",
        ]
        if not st.session_state.ai_messages:
            st.markdown(f'<div style="font-size:11.5px;color:{THEME["text2"]};margin-bottom:10px;">Suggested questions:</div>',
                        unsafe_allow_html=True)
            starter_cols = st.columns(2)
            for i, q in enumerate(starters):
                with starter_cols[i % 2]:
                    if st.button(q, key=f"starter_{i}",
                                 help="Click to send this question"):
                        st.session_state.ai_messages.append({"role":"user","content":q})
                        st.rerun()

        # Render conversation history
        for msg in st.session_state.ai_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input
        if prompt := st.chat_input("Ask about your portfolio, ETFs, market outlook…"):
            st.session_state.ai_messages.append({"role":"user","content":prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Call Claude
            with st.chat_message("assistant"):
                try:
                    import anthropic as _anthropic
                    client = _anthropic.Anthropic(api_key=ai_key)
                    # Keep last 10 turns to stay within context
                    history = st.session_state.ai_messages[-10:]
                    placeholder = st.empty()
                    full_response = ""
                    with client.messages.stream(
                        model="claude-sonnet-4-6",
                        max_tokens=1200,
                        system=system_prompt,
                        messages=[{"role":m["role"],"content":m["content"]} for m in history],
                    ) as stream:
                        for chunk in stream.text_stream:
                            full_response += chunk
                            placeholder.markdown(full_response + "▌")
                    placeholder.markdown(full_response)
                    st.session_state.ai_messages.append(
                        {"role":"assistant","content":full_response})
                except ImportError:
                    st.error("Run: pip install anthropic")
                except Exception as e:
                    err = str(e)
                    if "invalid_api_key" in err.lower() or "authentication" in err.lower():
                        st.error("Invalid API key. Check it in the sidebar.")
                    else:
                        st.error(f"AI error: {err}")

        if st.session_state.ai_messages:
            if st.button("🗑 Clear conversation"):
                st.session_state.ai_messages = []; st.rerun()

        st.markdown(f'<div class="disclaim">AI responses are educational and not financial advice. '
                    f'Claude is provided by Anthropic. Your API key is stored only in your '
                    f'browser session and never sent anywhere except Anthropic\'s API.</div>',
                    unsafe_allow_html=True)

# ================================================================ TAB 5: CHART
with tab_chart:
    st.markdown('<div class="term-label">Total Return Chart</div>', unsafe_allow_html=True)
    range_label = st.radio("Range:", list(RANGES.keys()), index=6, horizontal=True,
                           label_visibility="collapsed")
    mode, p, interval = RANGES[range_label]
    if mode == "intraday":
        with st.spinner(f"Loading {range_label} intraday data…"):
            try: plot_df = load_intraday(sel, p, interval)
            except Exception as e: st.error(f"Intraday fetch: {e}"); plot_df = pd.DataFrame()
    else:
        cutoff = prices.index[-1] - pd.Timedelta(days=p)
        plot_df = prices[prices.index >= cutoff]

    palette = [THEME["gold"], THEME["orange"], THEME["green"], "#4f8ef7",
               "#a78bfa", "#2dd4bf", "#fb923c", "#e879f9", "#60a5fa", "#f87171"]
    fig = go.Figure()
    for i, t in enumerate(sel):
        if t not in plot_df.columns: continue
        s = plot_df[t].dropna()
        if s.empty: continue
        norm = s / s.iloc[0] * 100 - 100
        fig.add_trace(go.Scatter(x=s.index, y=norm, name=t, mode="lines",
            line=dict(width=2.2, color=palette[i % len(palette)])))
    fig.add_hline(y=0, line_dash="dot", line_color=THEME["text3"], line_width=1)
    fig.update_layout(title=f"Total return — {range_label} (rebased to 0%)",
        template="plotly_dark", height=540, hovermode="x unified",
        paper_bgcolor=THEME["bg"], plot_bgcolor=THEME["bg"],
        yaxis_title="Total return %", legend=dict(orientation="h",y=-0.15),
        font=dict(family="Roboto Mono"))
    fig.update_xaxes(gridcolor=THEME["bg3"]); fig.update_yaxes(gridcolor=THEME["bg3"])
    st.plotly_chart(fig, width='stretch')
    st.caption("1D/1W = intraday bars. 1M+ = daily total-return closes with dividends reinvested. "
               "Younger funds (MAGS etc.) start from their own inception date.")

# ================================================================ FOOTER
st.markdown(f'<div class="disclaim">Built with yfinance · pandas · plotly · streamlit — all open-source. '
            f'Expense ratios verified ~June 2026. Technical signals (RSI, MA) are indicators, not predictions. '
            f'Portfolio projections use historical volatility via Monte Carlo — not forward-looking forecasts. '
            f'Educational tool only, not financial advice.</div>', unsafe_allow_html=True)
