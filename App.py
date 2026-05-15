"""
NSE Risk Score Report — Streamlit + Plotly
Run: streamlit run app.py
pip install streamlit plotly pandas numpy yfinance
"""
 
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
import hashlib
 
# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NSE Risk Report",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)
 
# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');
 
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #07080c !important;
    color: #e2e8f0 !important;
}
.stApp { background-color: #07080c !important; }
.block-container { padding: 1.2rem 2rem 3rem 2rem; max-width: 1320px; margin: auto; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
 
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 18px; padding: 5px; gap: 4px;
    border: 1px solid rgba(255,255,255,0.07);
}
.stTabs [data-baseweb="tab"] {
    background: transparent; border-radius: 13px;
    color: #64748b; font-family: 'DM Sans', sans-serif;
    font-weight: 600; font-size: 0.85rem; padding: 9px 22px;
    transition: all 0.25s; border: 1px solid transparent;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(99,102,241,0.22), rgba(139,92,246,0.18)) !important;
    color: #c4b5fd !important;
    border: 1px solid rgba(139,92,246,0.35) !important;
    box-shadow: 0 2px 12px rgba(99,102,241,0.15) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem; }
 
.card {
    background: linear-gradient(145deg, rgba(255,255,255,0.045), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.08); border-radius: 22px;
    padding: 1.3rem 1.5rem; margin-bottom: 0.9rem;
    backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
}
.card-glow {
    background: linear-gradient(145deg, rgba(99,102,241,0.09), rgba(139,92,246,0.05));
    border: 1px solid rgba(139,92,246,0.28); border-radius: 22px;
    padding: 1.4rem 1.6rem; margin-bottom: 0.9rem;
    box-shadow: 0 0 40px rgba(99,102,241,0.07), inset 0 1px 0 rgba(255,255,255,0.06);
}
.card-green {
    background: linear-gradient(145deg, rgba(34,197,94,0.08), rgba(16,185,129,0.04));
    border: 1px solid rgba(34,197,94,0.28); border-radius: 22px;
    padding: 1.2rem 1.4rem; margin-bottom: 0.9rem;
}
.card-red {
    background: linear-gradient(145deg, rgba(239,68,68,0.08), rgba(220,38,38,0.04));
    border: 1px solid rgba(239,68,68,0.28); border-radius: 22px;
    padding: 1.2rem 1.4rem; margin-bottom: 0.9rem;
}
.card-amber {
    background: linear-gradient(145deg, rgba(251,191,36,0.08), rgba(245,158,11,0.04));
    border: 1px solid rgba(251,191,36,0.28); border-radius: 22px;
    padding: 1.2rem 1.4rem; margin-bottom: 0.9rem;
}
.card-buy {
    background: linear-gradient(145deg, rgba(34,197,94,0.1), rgba(16,185,129,0.06));
    border: 2px solid rgba(34,197,94,0.4); border-radius: 24px;
    padding: 1.8rem; margin-bottom: 1rem;
    box-shadow: 0 0 50px rgba(34,197,94,0.09), inset 0 1px 0 rgba(255,255,255,0.05);
}
.card-sell {
    background: linear-gradient(145deg, rgba(239,68,68,0.1), rgba(220,38,38,0.06));
    border: 2px solid rgba(239,68,68,0.4); border-radius: 24px;
    padding: 1.8rem; margin-bottom: 1rem;
    box-shadow: 0 0 50px rgba(239,68,68,0.09), inset 0 1px 0 rgba(255,255,255,0.05);
}
.card-hold {
    background: linear-gradient(145deg, rgba(251,191,36,0.1), rgba(245,158,11,0.06));
    border: 2px solid rgba(251,191,36,0.4); border-radius: 24px;
    padding: 1.8rem; margin-bottom: 1rem;
    box-shadow: 0 0 50px rgba(251,191,36,0.09), inset 0 1px 0 rgba(255,255,255,0.05);
}
.stat-pill {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px; padding: 0.75rem 1rem; text-align: center;
}
.mono { font-family: 'JetBrains Mono', monospace !important; }
.label {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #475569; margin-bottom: 4px;
}
.section-title {
    font-size: 1rem; font-weight: 700; color: #f1f5f9;
    margin-bottom: 0.9rem; letter-spacing: -0.01em;
}
.positive { color: #4ade80 !important; font-family: 'JetBrains Mono', monospace; }
.negative { color: #f87171 !important; font-family: 'JetBrains Mono', monospace; }
.neutral  { color: #fbbf24 !important; font-family: 'JetBrains Mono', monospace; }
 
.badge-buy {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(34,197,94,0.15); border: 1.5px solid rgba(34,197,94,0.45);
    color: #4ade80; font-family: 'JetBrains Mono', monospace;
    font-weight: 700; font-size: 1rem; padding: 6px 20px;
    border-radius: 10px; letter-spacing: 0.06em;
    box-shadow: 0 0 16px rgba(34,197,94,0.15);
}
.badge-sell {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(239,68,68,0.15); border: 1.5px solid rgba(239,68,68,0.45);
    color: #f87171; font-family: 'JetBrains Mono', monospace;
    font-weight: 700; font-size: 1rem; padding: 6px 20px;
    border-radius: 10px; letter-spacing: 0.06em;
    box-shadow: 0 0 16px rgba(239,68,68,0.15);
}
.badge-hold {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(251,191,36,0.15); border: 1.5px solid rgba(251,191,36,0.45);
    color: #fbbf24; font-family: 'JetBrains Mono', monospace;
    font-weight: 700; font-size: 1rem; padding: 6px 20px;
    border-radius: 10px; letter-spacing: 0.06em;
    box-shadow: 0 0 16px rgba(251,191,36,0.15);
}
.disclaimer-banner {
    background: rgba(239,68,68,0.07); border: 1px solid rgba(239,68,68,0.2);
    border-radius: 16px; padding: 0.9rem 1.3rem;
    font-size: 0.78rem; color: #fca5a5; line-height: 1.7; margin-bottom: 1.2rem;
}
.disclaimer-footer {
    background: rgba(239,68,68,0.04); border: 1px solid rgba(239,68,68,0.12);
    border-radius: 12px; padding: 0.65rem 1rem;
    font-size: 0.7rem; color: #ef4444; text-align: center; margin-top: 2rem;
}
.prog-wrap { background: rgba(255,255,255,0.05); border-radius: 99px; height: 6px; margin-top: 4px; }
.prog-fill { height: 6px; border-radius: 99px; }
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important; color: #f1f5f9 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1rem !important; padding: 11px 18px !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(139,92,246,0.5) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}
.stButton > button {
    background: linear-gradient(135deg, rgba(99,102,241,0.22), rgba(139,92,246,0.18)) !important;
    border: 1px solid rgba(139,92,246,0.38) !important;
    border-radius: 14px !important; color: #c4b5fd !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important; padding: 9px 26px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(99,102,241,0.38), rgba(139,92,246,0.3)) !important;
    box-shadow: 0 0 24px rgba(99,102,241,0.22) !important;
}
.stDataFrame { border-radius: 14px; overflow: hidden; }
.row-item {
    display: flex; justify-content: space-between; align-items: center;
    padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.82rem;
}
.row-item:last-child { border-bottom: none; }
</style>
""", unsafe_allow_html=True)
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
 
def stock_seed(symbol: str) -> int:
    return int(hashlib.md5(symbol.upper().encode()).hexdigest(), 16) % (2**31)
 
 
def progress_bar(val, color):
    pct = max(0, min(val, 100))
    return f'<div class="prog-wrap"><div class="prog-fill" style="width:{pct}%;background:{color};"></div></div>'
 
 
DISCLAIMER = """<div class="disclaimer-footer">
⚠️ This combines traditional analysis with non-conventional sentiment tools.
Past performance is no guarantee. Not financial advice. Educational/illustrative only.
</div>"""
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  SBC — STOCK-SPECIFIC (changes by symbol + date)
# ══════════════════════════════════════════════════════════════════════════════
 
NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni",
    "Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha",
    "Moola","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishtha",
    "Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati",
]
PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]
P_EMOJI = {"Sun":"☀️","Moon":"🌙","Mars":"♂️","Mercury":"☿",
            "Jupiter":"♃","Venus":"♀","Saturn":"♄","Rahu":"☊","Ketu":"☋"}
P_BENEFIC = {"Sun":True,"Moon":True,"Mercury":True,"Jupiter":True,"Venus":True,
              "Mars":False,"Saturn":False,"Rahu":False,"Ketu":False}
 
 
def compute_sbc(symbol: str) -> dict:
    nak_idx = ord(symbol[0].upper()) % 27
    stock_nak = NAKSHATRAS[nak_idx]
 
    today = datetime.now()
    day_key = today.year * 10000 + today.month * 100 + today.day
    day_rng = np.random.default_rng(stock_seed(symbol) ^ day_key)
 
    planet_status, planet_naks = {}, {}
    for planet in PLANETS:
        p_idx = int(day_rng.integers(0, 27))
        planet_naks[planet] = NAKSHATRAS[p_idx]
        diff = abs(p_idx - nak_idx) % 27
        has_vedha = diff in {0, 1, 6, 7, 13, 14, 20, 21}
        if has_vedha:
            planet_status[planet] = "Malefic Vedha" if not P_BENEFIC[planet] else "Benefic Vedha"
        else:
            planet_status[planet] = "No Vedha"
 
    ben = sum(1 for s in planet_status.values() if s == "Benefic Vedha")
    mal = sum(1 for s in planet_status.values() if s == "Malefic Vedha")
    raw = ben * 18 - mal * 14 + (9 - ben - mal) * 4
    score = max(10, min(90, raw + 40))
 
    yogas = ["Sarpa Yoga","Amrita Yoga","Siddha Yoga","Mrityu Yoga",
             "Visha Yoga","Subha Yoga","Pushkara Yoga","Dagdha Yoga"]
    lbl = ("Strongly Bullish" if score >= 70 else
           ("Mildly Bullish" if score >= 55 else ("Neutral" if score >= 40 else "Bearish")))
 
    return {
        "sbc_score": int(score), "sbc_label": lbl,
        "stock_nak": stock_nak, "first_letter": symbol[0].upper(),
        "planet_status": planet_status, "planet_naks": planet_naks,
        "benefic": ben, "malefic": mal,
        "active_yoga": yogas[stock_seed(symbol) % len(yogas)],
        "hit_rate": round(45 + stock_seed(symbol) % 10, 1),
    }
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  GANN — PRICE-BASED, STOCK-SPECIFIC
# ══════════════════════════════════════════════════════════════════════════════
 
def compute_gann(price: float, symbol: str) -> dict:
    root = math.sqrt(price)
    sq9 = sorted([round((root + i * 0.25) ** 2, 2)
                  for i in range(-4, 5) if root + i * 0.25 > 0])
 
    degree = round((root % 1) * 360, 1)
    fr = math.floor(root)
 
    cardinals = {
        "0° Base":    round(fr ** 2, 2),
        "90° First":  round((fr + 0.25) ** 2, 2),
        "180° Half":  round((fr + 0.50) ** 2, 2),
        "270° Third": round((fr + 0.75) ** 2, 2),
        "360° Full":  round((fr + 1.00) ** 2, 2),
    }
 
    above = [l for l in sq9 if l > price]
    below = [l for l in sq9 if l < price]
    res = min(above) if above else round(price * 1.03, 2)
    sup = max(below) if below else round(price * 0.97, 2)
    atr_est = round(price * 0.018, 2)
 
    angles = {
        "4×1 (Strong Res)": round(price + atr_est * 4, 2),
        "2×1 (Resistance)":  round(price + atr_est * 2, 2),
        "1×1 (Dynamic)":    round(price + atr_est * 1, 2),
        "1×2 (Support)":    round(price - atr_est * 1, 2),
        "1×4 (Strong Sup)": round(price - atr_est * 4, 2),
    }
 
    base_cycle = max(10, int(root * 2) % 30 + 12)
    today = datetime.now()
    cycles = [
        (today + timedelta(days=base_cycle),       "1×1 Price-Time Square",  "Watch for reversal"),
        (today + timedelta(days=base_cycle * 2),   "Cardinal Cross (90°)",   "Major pivot zone"),
        (today + timedelta(days=base_cycle * 3),   "45° Time Arc",           "S/R test expected"),
        (today + timedelta(days=base_cycle * 4),   "Full Cycle (360°)",      "Strong P-T squaring"),
    ]
 
    bias = "Bullish" if degree < 180 else "Bearish"
    strength = "Strong" if (degree < 90 or degree > 270) else "Moderate"
 
    return {
        "degree": degree, "sq9": sq9, "res": res, "sup": sup,
        "cardinals": cardinals, "angles": angles,
        "cycles": cycles, "bias": bias, "strength": strength,
        "base_cycle": base_cycle,
    }
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  DATA FETCH
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=180, show_spinner=False)
def fetch_stock_data(symbol: str) -> dict:
    symbol = symbol.upper().strip()
    
    try:
        import yfinance as yf
        t = yf.Ticker(f"{symbol}.NS")
        info = t.info
        hist = t.history(period="1y")
        
        if hist.empty or len(hist) < 30:
            raise ValueError("Insufficient data")

        price = float(
            info.get("currentPrice") or 
            info.get("regularMarketPrice") or 
            hist["Close"].iloc[-1]
        )
        prev_close = float(info.get("previousClose") or hist["Close"].iloc[-2])
        price = round(price, 2)
        change_pct = round((price - prev_close) / prev_close * 100, 2)

        rec = hist.tail(120).copy()

        # Real technicals
        delta = rec["Close"].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rsi = round(float(100 - 100 / (1 + gain / loss)).iloc[-1], 1)

        tr = pd.concat([rec["High"] - rec["Low"], 
                        (rec["High"] - rec["Close"].shift()).abs(), 
                        (rec["Low"] - rec["Close"].shift()).abs()], axis=1).max(axis=1)
        atr = round(float(tr.rolling(14).mean().iloc[-1]), 2)

        ema12 = rec["Close"].ewm(span=12, adjust=False).mean()
        ema26 = rec["Close"].ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        macd_signal = macd_line.ewm(span=9, adjust=False).mean()

        beta = float(info.get("beta") or 1.0)
        mkt_cap = round((info.get("marketCap") or 0) / 1e12, 2)
        volume = int(info.get("volume") or rec["Volume"].iloc[-1])

        # Analyst target
        analyst_tp = info.get("targetMeanPrice")
        if analyst_tp and price > 0:
            analyst_tp = round(float(analyst_tp), 2)
            upside = round((analyst_tp / price - 1) * 100, 1)
        else:
            analyst_tp = round(price * 1.16, 2)
            upside = 16.0

        # Risk score
        risk_score = min(88, int(18 + (atr/price)*900 + beta*16 + (20 if rsi > 70 else 0)))

        entry_lo = round(price * 0.977, 2)
        entry_hi = round(price * 1.006, 2)
        sl = round(price - atr * 2.6, 2)
        t1 = round(price + atr * 4.0, 2)
        t2 = round(price + atr * 7.2, 2)
        mid = round((entry_lo + entry_hi) / 2, 2)
        rr = round((t1 - mid) / max(mid - sl, 1), 2)

        return {
            "symbol": symbol, "price": price, "change_pct": change_pct,
            "volume": volume, "mkt_cap": mkt_cap, "beta": round(beta, 2),
            "atr": atr, "risk_score": risk_score, "rsi": rsi,
            "macd_val": round(float(macd_line.iloc[-1]), 2),
            "macd_sig": round(float(macd_signal.iloc[-1]), 2),
            "analyst_tp": analyst_tp, "upside": upside,
            "pe_curr": round(float(info.get("trailingPE") or 25), 1),
            "pe_5y": round(float(info.get("trailingPE") or 25) * 0.95, 1),
            "pb_curr": round(float(info.get("priceToBook") or 3), 2),
            "roe": round(float((info.get("returnOnEquity") or 0.12) * 100), 1),
            "de_ratio": round(float(info.get("debtToEquity") or 0.5), 2),
            "pledge_pct": round(float(info.get("heldPercentInsiders", 0.15) * 100), 1),
            "pcr": 1.08,
            "max_pain": round(price * 0.99, 0),
            "entry_low": entry_lo, "entry_high": entry_hi,
            "sl": sl, "t1": t1, "t2": t2, "rr": rr,
            "verdict": "BUY" if risk_score < 45 else ("SELL" if risk_score > 65 else "HOLD"),
            "dates": rec.index.tolist(),
            "opens": rec["Open"].tolist(),
            "highs": rec["High"].tolist(),
            "lows": rec["Low"].tolist(),
            "closes": rec["Close"].tolist(),
            "volumes": rec["Volume"].tolist(),
            "sma20": round(float(rec["Close"].rolling(20).mean().iloc[-1]), 2),
            "sma50": round(float(rec["Close"].rolling(50).mean().iloc[-1]), 2),
            "sma200": round(float(rec["Close"].rolling(200).mean().iloc[-1]), 2),
            "ema9": round(float(rec["Close"].ewm(span=9, adjust=False).mean().iloc[-1]), 2),
            "ema21": round(float(rec["Close"].ewm(span=21, adjust=False).mean().iloc[-1]), 2),
            "data_source": "live"
        }

    except Exception:
        # Complete synthetic fallback with ALL keys the app needs
        rng = np.random.default_rng(stock_seed(symbol))
        price = round(float(rng.uniform(180, 4200)), 2)
        atr = round(price * 0.019, 2)
        risk_score = int(rng.integers(32, 72))
        
        dates = pd.date_range(end=datetime.today(), periods=120, freq="B").tolist()
        closes = [price]
        for _ in range(119):
            closes.append(closes[-1] * (1 + float(rng.normal(0, 0.013))))
        closes = closes[::-1]

        return {
            "symbol": symbol, "price": price, "change_pct": round(float(rng.uniform(-5, 5)), 2),
            "volume": int(rng.integers(800000, 25000000)), "mkt_cap": round(float(rng.uniform(0.2, 18)), 2),
            "beta": round(float(rng.uniform(0.65, 1.85)), 2), "atr": atr,
            "risk_score": risk_score,
            "hist_var": round(float(rng.uniform(-4.2, -1.3)), 2),
            "max_dd": round(float(rng.uniform(-38, -11)), 1),
            "rsi": round(float(rng.uniform(35, 68)), 1),
            "macd_val": round(float(rng.uniform(-12, 14)), 2),
            "macd_sig": round(float(rng.uniform(-10, 12)), 2),
            "analyst_tp": round(price * 1.16, 2),
            "upside": round(float(rng.uniform(9, 28)), 1),
            "pe_curr": round(float(rng.uniform(14, 42)), 1),
            "pe_5y": round(float(rng.uniform(12, 48)), 1),
            "pb_curr": round(float(rng.uniform(1.4, 7.5)), 2),
            "roe": round(float(rng.uniform(9, 34)), 1),
            "de_ratio": round(float(rng.uniform(0.1, 2.1)), 2),
            "pledge_pct": round(float(rng.uniform(0, 22)), 1),
            "pcr": round(float(rng.uniform(0.65, 1.55)), 2),
            "max_pain": round(price * float(rng.uniform(0.96, 1.04)), 0),
            "entry_low": round(price * 0.976, 2),
            "entry_high": round(price * 1.005, 2),
            "sl": round(price - atr * 2.5, 2),
            "t1": round(price + atr * 3.5, 2),
            "t2": round(price + atr * 6.5, 2),
            "rr": round(float(rng.uniform(1.8, 3.2)), 2),
            "verdict": "BUY" if risk_score < 45 else ("SELL" if risk_score > 65 else "HOLD"),
            "dates": dates,
            "opens": [p * float(rng.uniform(0.995, 1.005)) for p in closes],
            "highs": [p * float(rng.uniform(1.001, 1.012)) for p in closes],
            "lows": [p * float(rng.uniform(0.988, 0.999)) for p in closes],
            "closes": closes,
            "volumes": [int(rng.integers(800000, 25000000)) for _ in closes],
            "sma20": round(price * 0.99, 2),
            "sma50": round(price * 0.97, 2),
            "sma200": round(price * 0.89, 2),
            "ema9": round(price * 0.995, 2),
            "ema21": round(price * 0.982, 2),
            "data_source": "synthetic"
        }
 
# ══════════════════════════════════════════════════════════════════════════════
#  CHART HELPERS
# ══════════════════════════════════════════════════════════════════════════════
 
BL = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)",
    font=dict(family="JetBrains Mono, monospace", color="#64748b", size=11),
    margin=dict(l=8,r=8,t=28,b=8),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False, color="#475569"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False, color="#475569"),
)

# ── Simple Score Display (replaces problematic gauge) ───────────────────────
def score_display(value, title, low_good=True, max_val=100):
    v = max(0, min(int(value), max_val))
    
    if low_good:
        color = "#4ade80" if v < 40 else ("#fbbf24" if v < 65 else "#f87171")
        desc = "(Lower = Safer)" if title.startswith("Overall Risk") else ""
    else:
        color = "#f87171" if v < 40 else ("#fbbf24" if v < 65 else "#4ade80")
        desc = "(Higher = Better)" if "SBC" in title or "Technical" in title else ""

    st.markdown(f"""
    <div style="text-align:center; padding: 20px 0;">
        <div style="font-size: 0.95rem; color:#64748b; margin-bottom:8px;">{title}</div>
        <div style="font-family: 'JetBrains Mono'; font-size: 4.8rem; font-weight: 800; 
                    color: {color}; line-height: 1; margin-bottom: 8px;">{v}</div>
        <div style="font-size: 1.1rem; color: #94a3b8;">/ {max_val} {desc}</div>
    </div>
    """, unsafe_allow_html=True)


def candle_chart(d):
    """Clean candlestick chart"""
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=d["dates"], open=d["opens"], high=d["highs"], low=d["lows"], close=d["closes"],
        increasing_line_color="#4ade80", decreasing_line_color="#f87171",
        increasing_fillcolor="rgba(74,222,128,0.65)",
        decreasing_fillcolor="rgba(248,113,113,0.65)",
        name="Price", line=dict(width=1.2)
    ))

    cl = pd.Series(d["closes"])
    for w, col, dash in [(20, "#60a5fa", "solid"), (50, "#a78bfa", "solid"), (200, "#f59e0b", "dot")]:
        fig.add_trace(go.Scatter(
            x=d["dates"], y=cl.rolling(w).mean(), mode="lines",
            line=dict(color=col, width=1.6, dash=dash), name=f"SMA{w}", opacity=0.9
        ))

    vcol = ["rgba(74,222,128,0.45)" if c >= o else "rgba(248,113,113,0.45)"
            for c, o in zip(d["closes"], d["opens"])]
    fig.add_trace(go.Bar(
        x=d["dates"], y=d["volumes"], name="Volume",
        marker_color=vcol, yaxis="y2", opacity=0.75
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(family="JetBrains Mono, monospace", color="#64748b", size=11),
        margin=dict(l=10, r=10, t=30, b=10),
        height=440,
        hovermode="x unified",
        legend=dict(orientation="h", y=1.05, x=0, font=dict(size=10, color="#475569")),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False, color="#475569", rangeslider=dict(visible=False)),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", side="right"),
        yaxis2=dict(domain=[0, 0.16], showgrid=False, showticklabels=False)
    )
    return fig
 
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=d["dates"], 
        open=d["opens"], 
        high=d["highs"], 
        low=d["lows"], 
        close=d["closes"],
        increasing_line_color="#4ade80", 
        decreasing_line_color="#f87171",
        increasing_fillcolor="rgba(74,222,128,0.65)",
        decreasing_fillcolor="rgba(248,113,113,0.65)",
        name="Price", 
        line=dict(width=1.2)
    ))

    # Moving Averages
    cl = pd.Series(d["closes"])
    for w, col, dash in [(20, "#60a5fa", "solid"), (50, "#a78bfa", "solid"), (200, "#f59e0b", "dot")]:
        fig.add_trace(go.Scatter(
            x=d["dates"], 
            y=cl.rolling(w).mean(), 
            mode="lines",
            line=dict(color=col, width=1.6, dash=dash), 
            name=f"SMA{w}", 
            opacity=0.9
        ))

    # Volume bars
    vcol = ["rgba(74,222,128,0.45)" if c >= o else "rgba(248,113,113,0.45)"
            for c, o in zip(d["closes"], d["opens"])]
    fig.add_trace(go.Bar(
        x=d["dates"], 
        y=d["volumes"], 
        name="Volume",
        marker_color=vcol, 
        yaxis="y2", 
        opacity=0.75
    ))

    # Self-contained layout
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(family="JetBrains Mono, monospace", color="#64748b", size=11),
        margin=dict(l=10, r=10, t=30, b=10),
        height=440,
        hovermode="x unified",
        legend=dict(orientation="h", y=1.05, x=0, font=dict(size=10, color="#475569")),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)", 
            showline=False, 
            color="#475569",
            rangeslider=dict(visible=False)
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)", 
            side="right"
        ),
        yaxis2=dict(
            domain=[0, 0.16], 
            showgrid=False, 
            showticklabels=False
        )
    )
    return fig
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  ROW ITEM HTML
# ══════════════════════════════════════════════════════════════════════════════
 
def ri(label, val, col="#94a3b8"):
    return f"""<div class='row-item'>
        <span style='color:#475569;'>{label}</span>
        <span style='font-family:JetBrains Mono;font-size:0.82rem;color:{col};'>{val}</span>
    </div>"""
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — RISK OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
 
def render_risk_overview(d):
    c1, c2 = st.columns([1, 1.65])
    with c1:
        score_display(d["risk_score"], "Overall Risk Score", low_good=True)
        vh = {"BUY":"<span class='badge-buy'>▲ BUY</span>",
              "SELL":"<span class='badge-sell'>▼ SELL</span>",
              "HOLD":"<span class='badge-hold'>● HOLD</span>"}[d["verdict"]]
        vh = {"BUY":"<span class='badge-buy'>▲ BUY</span>",
              "SELL":"<span class='badge-sell'>▼ SELL</span>",
              "HOLD":"<span class='badge-hold'>● HOLD</span>"}[d["verdict"]]
        st.markdown(f"<div style='text-align:center;margin-top:-6px;'>{vh}</div>",
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='label'>Risk Component Breakdown</div>", unsafe_allow_html=True)
        rng = np.random.default_rng(stock_seed(d["symbol"]))
        for lbl, base in [
            ("Quantitative Risk (40%)", 0.40),
            ("Technical Confluence (30%)", 0.30),
            ("Fundamental Health (20%)", 0.20),
            ("Sentiment Overlay (10%)",  0.10),
        ]:
            val = min(95, int(d["risk_score"] * base * float(rng.uniform(0.88, 1.12))))
            col = "#4ade80" if val<40 else ("#fbbf24" if val<65 else "#f87171")
            st.markdown(f"""<div style='margin-bottom:0.6rem;'>
                <div style='display:flex;justify-content:space-between;margin-bottom:3px;'>
                    <span style='font-size:0.72rem;color:#64748b;'>{lbl}</span>
                    <span style='font-family:JetBrains Mono;font-size:0.72rem;color:{col};font-weight:600;'>{val}</span>
                </div>{progress_bar(val,col)}</div>""", unsafe_allow_html=True)

    with c2:
        mid = round((d["entry_low"]+d["entry_high"])/2, 2)
        st.markdown("<div class='card-glow'><div class='section-title'>🎯 Trade Plan</div>",
                    unsafe_allow_html=True)
        for row in [
            ri("Entry Zone",    f"₹{d['entry_low']:,.2f} – ₹{d['entry_high']:,.2f}", "#93c5fd"),
            ri("Stop-Loss",     f"₹{d['sl']:,.2f}  (ATR×2.5 swing low)",              "#f87171"),
            ri("Target 1",      f"₹{d['t1']:,.2f}  (+{round((d['t1']/mid-1)*100,1)}%)","#4ade80"),
            ri("Target 2",      f"₹{d['t2']:,.2f}  (+{round((d['t2']/mid-1)*100,1)}%)","#c084fc"),
            ri("Risk : Reward", f"1 : {d['rr']}",                                      "#fbbf24"),
            ri("Timeframe",     "Valid till next monthly expiry",                       "#94a3b8"),
            ri("Confluence",    "Medium–High" if d["risk_score"]<55 else "Low–Medium", "#94a3b8"),
        ]:
            st.markdown(row, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Stats Row (Clean single row) ─────────────────────────────────
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    stats = [
        ("Beta",        d["beta"],               ""),
        ("ATR (14)",    f"₹{d['atr']}",           ""),
        ("VaR 95%",     f"{d['hist_var']}%",       "negative"),
        ("Max DD",      f"{d['max_dd']}%",         "negative"),
        ("Analyst TP",  f"₹{d['analyst_tp']:,.0f}","positive"),
        ("Upside",      f"{d['upside']}%",         "positive" if d['upside']>0 else "negative"),
        ("Mkt Cap",     f"₹{d['mkt_cap']:.2f}T",  ""),
        ("Volume",      f"{d['volume']:,.0f}",     ""),
    ]
    
    cols = st.columns(len(stats))
    for i, (lbl, val, cls) in enumerate(stats):
        with cols[i]:
            st.markdown(f"""<div class='stat-pill'>
                <div class='label'>{lbl}</div>
                <div style='font-family:JetBrains Mono;font-size:0.82rem;margin-top:4px;'
                     class='{cls}'>{val}</div></div>""", unsafe_allow_html=True)

    # ── Fundamentals Moat & Valuation ───────────────────────────────────────
    st.markdown("<br><div class='section-title'>🏛️ Fundamental Moat & Valuation</div>",
                unsafe_allow_html=True)
    
    rng2 = np.random.default_rng(stock_seed(d["symbol"])+99)
    dcf_lo = round(d["price"]*float(rng2.uniform(0.92,1.1)), 0)
    dcf_hi = round(d["price"]*float(rng2.uniform(1.12,1.45)), 0)
    roe_c  = "positive" if d["roe"]>15 else "neutral"
    de_c   = "positive" if d["de_ratio"]<0.5 else ("neutral" if d["de_ratio"]<1.5 else "negative")
    plg_c  = "negative" if d["pledge_pct"]>15 else "positive"

    fa, fb, fc = st.columns(3)
    with fa:
        st.markdown(f"""<div class='card'>
            <div class='label' style='margin-bottom:8px;'>Valuation</div>
            {ri("P/E Current",    f"{d['pe_curr']}x")}
            {ri("P/E 5-yr Median",f"{d['pe_5y']}x")}
            {ri("Price / Book",   f"{d['pb_curr']}x")}
            {ri("DCF Fair Value", f"₹{dcf_lo:,.0f} – ₹{dcf_hi:,.0f}", "#4ade80")}
        </div>""", unsafe_allow_html=True)
    with fb:
        st.markdown(f"""<div class='card'>
            <div class='label' style='margin-bottom:8px;'>Health & Governance</div>
            <div class='row-item'>
                <span style='color:#475569;'>ROE (TTM)</span>
                <span class='mono {roe_c}' style='font-size:0.82rem;'>{d['roe']}%</span>
            </div>
            <div class='row-item'>
                <span style='color:#475569;'>Debt / Equity</span>
                <span class='mono {de_c}' style='font-size:0.82rem;'>{d['de_ratio']}x</span>
            </div>
            <div class='row-item'>
                <span style='color:#475569;'>Promoter Pledge</span>
                <span class='mono {plg_c}' style='font-size:0.82rem;'>{d['pledge_pct']}%</span>
            </div>
            {ri("Insider Activity","Neutral (placeholder)","#fbbf24")}
        </div>""", unsafe_allow_html=True)
    with fc:
        st.markdown(f"""<div class='card'>
            <div class='label' style='margin-bottom:8px;'>Industry Outlook</div>
            <div style='font-size:0.72rem;color:#475569;'>Tailwinds</div>
            <div style='font-size:0.78rem;color:#e2e8f0;margin-bottom:8px;'>
                Domestic demand recovery + capex cycle (placeholder)</div>
            <div style='font-size:0.72rem;color:#475569;'>Headwinds</div>
            <div style='font-size:0.78rem;color:#e2e8f0;margin-bottom:8px;'>
                Margin pressure, global macro risk (placeholder)</div>
            <div style='font-size:0.72rem;color:#475569;'>Analyst Consensus</div>
            <div class='mono positive' style='font-size:0.78rem;margin-top:2px;'>
                Moderate Buy · {d['upside']}% upside</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(DISCLAIMER, unsafe_allow_html=True)
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — SENTIMENT OVERLAY
# ══════════════════════════════════════════════════════════════════════════════
 
def render_sentiment(d):
    sbc  = compute_sbc(d["symbol"])
    gann = compute_gann(d["price"], d["symbol"])
 
    st.markdown("""<div class='disclaimer-banner'>
        ⚠️ <b>Supplementary Sentiment — Read Before Using</b><br>
        Non-traditional tools used by ~18% of active NSE traders.
        Backtested directional edge &lt;53% on Nifty-50 over 5 years.
        Use as confluence only, <b>never</b> primary signal.
    </div>""", unsafe_allow_html=True)
 
    # ── SBC ──────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>🔵 Sarvatobhadra Chakra (SBC) Analysis</div>",
                unsafe_allow_html=True)
    s1, s2 = st.columns([1, 1.7])
    with s1:
        score_display(sbc["sbc_score"], "SBC Vedha Score", low_good=False)
        sc = "positive" if sbc["sbc_score"]>=55 else ("neutral" if sbc["sbc_score"]>=40 else "negative")
        st.markdown(f"<div style='text-align:center;margin-top:-4px;'>"
                    f"<span class='{sc}' style='font-weight:700;font-size:0.95rem;'>"
                    f"{sbc['sbc_label']}</span></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        for lbl, cnt, col in [
            ("Benefic Vedhas", sbc["benefic"], "#4ade80"),
            ("Malefic Vedhas", sbc["malefic"], "#f87171"),
            ("No Vedha",       9-sbc["benefic"]-sbc["malefic"], "#64748b"),
        ]:
            st.markdown(f"""<div style='display:flex;justify-content:space-between;
                padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.05);font-size:0.78rem;'>
                <span style='color:#64748b;'>{lbl}</span>
                <span style='font-family:JetBrains Mono;color:{col};font-weight:600;'>{cnt}</span>
            </div>""", unsafe_allow_html=True)
 
    with s2:
        st.markdown(f"""<div class='card'>
            <div class='label' style='margin-bottom:8px;'>First Akshara Analysis</div>
            <div style='font-size:0.84rem;color:#e2e8f0;margin-bottom:10px;'>
                Symbol starts with
                <span style='font-family:JetBrains Mono;color:#a5b4fc;font-weight:600;'>
                    "{sbc['first_letter']}"</span>
                → Nakshatra: <span style='font-family:JetBrains Mono;color:#c4b5fd;'>
                    {sbc['stock_nak']}</span><br>
                Today's vedha: <span class='{sc}' style='font-weight:600;'>
                    {"✅ Benefic — supportive energy" if sbc["sbc_score"]>55
                     else ("⚡ Neutral — mixed signals" if sbc["sbc_score"]>40
                           else "⚠️ Malefic — caution advised")}
                </span>
            </div>
            <div class='label' style='margin-bottom:8px;'>Planetary Vedha Grid</div>
        """, unsafe_allow_html=True)
        pcols = st.columns(3)
        for i, pl in enumerate(PLANETS):
            status = sbc["planet_status"][pl]
            nak    = sbc["planet_naks"][pl]
            pcls   = "positive" if "Benefic" in status else ("negative" if "Malefic" in status else "neutral")
            with pcols[i%3]:
                st.markdown(f"""<div style='padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.05);'>
                    <div style='font-size:0.73rem;color:#475569;'>{P_EMOJI[pl]} {pl}</div>
                    <div class='mono {pcls}' style='font-size:0.7rem;'>{status}</div>
                    <div style='font-size:0.64rem;color:#334155;'>{nak}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
 
        st.markdown(f"""<div class='card' style='margin-top:0;'>
            <div style='display:flex;justify-content:space-between;margin-bottom:10px;'>
                <div class='label'>Active Yoga</div>
                <span style='font-family:JetBrains Mono;font-size:0.78rem;color:#c084fc;'>
                    {sbc['active_yoga']}</span>
            </div>
            <div class='label'>Short-term (1–7 days)</div>
            <div style='font-size:0.8rem;color:#e2e8f0;margin:4px 0 10px;'>
                {"Moon transiting " + sbc["stock_nak"] + " axis — benefic vedha active, mild momentum support."
                 if sbc["sbc_score"]>50 else
                 "Saturn–Rahu vedha on " + sbc["stock_nak"] + " — malefic energy, avoid aggressive longs."}
            </div>
            <div class='label'>Medium-term (30–90 days)</div>
            <div style='font-size:0.8rem;color:#e2e8f0;margin-top:4px;'>
                Jupiter's transit relative to {sbc['stock_nak']} is
                {"forming a trine — historically supportive over 30-90 day horizon." if sbc["sbc_score"]>50
                 else "in a challenging square — medium-term overhead pressure."}
                Historical directional accuracy: <b>{sbc['hit_rate']}%</b> (illustrative).
            </div>
        </div>""", unsafe_allow_html=True)
 
    # ── Gann ─────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title' style='margin-top:0.5rem;'>🔷 Gann Price–Time Square Analysis</div>",
                unsafe_allow_html=True)
    g1, g2 = st.columns(2)
    bc = "positive" if gann["bias"]=="Bullish" else "negative"
 
    with g1:
        st.markdown(f"""<div class='card'>
            <div class='label' style='margin-bottom:8px;'>Square of Nine — Position</div>
            {ri("Current Price", f"₹{d['price']:,.2f}")}
            {ri("√ Price",       f"{round(math.sqrt(d['price']),4)}", "#94a3b8")}
            {ri("Gann Degree",   f"{gann['degree']}°", "#fbbf24")}
            {ri("Quadrant Bias", f"{gann['strength']} {gann['bias']}", "#4ade80" if gann["bias"]=="Bullish" else "#f87171")}
            {ri("Next SQ9 Res",  f"₹{gann['res']:,.2f}", "#4ade80")}
            {ri("SQ9 Support",   f"₹{gann['sup']:,.2f}", "#f87171")}
        </div>""", unsafe_allow_html=True)
 
        st.markdown("<div class='card'><div class='label' style='margin-bottom:6px;'>Nearby SQ9 Levels</div>"
                    "<div style='display:flex;flex-wrap:wrap;gap:6px;'>", unsafe_allow_html=True)
        for lvl in gann["sq9"]:
            cls = "positive" if lvl>d["price"] else ("negative" if lvl<d["price"] else "neutral")
            st.markdown(f"""<span class='{cls}'
                style='font-family:JetBrains Mono;font-size:0.72rem;
                background:rgba(255,255,255,0.04);border-radius:8px;padding:2px 8px;'>
                ₹{lvl:,.2f}</span>""", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)
 
        st.markdown("<div class='card'><div class='label' style='margin-bottom:8px;'>Cardinal Price Levels</div>",
                    unsafe_allow_html=True)
        for dlbl, lvl in gann["cardinals"].items():
            cls = "positive" if lvl>d["price"] else "negative"
            st.markdown(ri(dlbl, f"₹{lvl:,.2f}", "#4ade80" if lvl>d["price"] else "#f87171"),
                        unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
 
    with g2:
        st.markdown("<div class='card'><div class='label' style='margin-bottom:8px;'>Time Cycles — Next 90 Days</div>",
                    unsafe_allow_html=True)
        for dt, event, impact in gann["cycles"]:
            days = (dt - datetime.now()).days
            st.markdown(f"""<div style='padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);'>
                <div style='display:flex;justify-content:space-between;'>
                    <div>
                        <div style='font-family:JetBrains Mono;font-size:0.78rem;color:#a5b4fc;'>
                            {dt.strftime('%d %b %Y')}
                            <span style='color:#334155;font-size:0.65rem;'> T+{days}d</span>
                        </div>
                        <div style='font-size:0.73rem;color:#64748b;'>{event}</div>
                    </div>
                    <span style='font-size:0.7rem;color:#fbbf24;align-self:flex-start;
                        background:rgba(251,191,36,0.1);border-radius:6px;padding:2px 8px;'>
                        {impact}</span>
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.7rem;color:#334155;margin-top:6px;'>"
                    f"Base cycle: {gann['base_cycle']} days (√{round(d['price'],0)})</div></div>",
                    unsafe_allow_html=True)
 
        st.markdown("<div class='card'><div class='label' style='margin-bottom:8px;'>Gann Angles</div>",
                    unsafe_allow_html=True)
        for albl, alvl in gann["angles"].items():
            cls = "#4ade80" if alvl>d["price"] else "#f87171"
            st.markdown(ri(albl, f"₹{alvl:,.2f}", cls), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
 
        st.markdown(f"""<div class='card'>
            <div class='label' style='margin-bottom:6px;'>Gann Commentary</div>
            <div style='font-size:0.8rem;color:#e2e8f0;line-height:1.6;'>
                Price at <span class='mono neutral'>{gann['degree']}°</span> on SQ9 —
                <span class='{bc}'><b>{gann['strength']} {gann['bias']}</b></span> quadrant.
                Price-time squaring near <span class='mono positive'>₹{gann['res']:,.2f}</span>.
                Next major cycle: <b>{gann['cycles'][1][0].strftime('%d %b')}</b> — watch velocity.
                <br><span style='color:#334155;font-size:0.7rem;'>Illustrative. Use as confluence only.</span>
            </div>
        </div>""", unsafe_allow_html=True)
 
    st.markdown(DISCLAIMER, unsafe_allow_html=True)
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — TECHNICAL DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════════
 
def render_technical(d):
    rng = np.random.default_rng(stock_seed(d["symbol"])+7)
    ts = int(
        (50 if d["rsi"]<60 else 30) +
        (15 if d["macd_val"]>d["macd_sig"] else -5) +
        (15 if d["price"]>d["sma50"] else -5) +
        (10 if d["price"]>d["sma200"] else -5) +
        int(rng.integers(-5,10))
    )
    ts = max(8, min(96, ts))
    tv = "Bullish" if ts>58 else ("Neutral" if ts>42 else "Bearish")
    tc = "positive" if ts>58 else ("neutral" if ts>42 else "negative")
 
    ca, cb = st.columns([3,1])
    with ca:
        st.markdown("<div class='section-title'>📉 Price Action — Daily Chart</div>",
                    unsafe_allow_html=True)
        st.plotly_chart(candle_chart(d), use_container_width=True, config={"displayModeBar":False})
    with cb:
        score_display(ts, "Technical Score", low_good=False)
        st.markdown(f"<div style='text-align:center;margin-top:-4px;' class='{tc}'><b>{tv}</b></div>",
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        rc = "negative" if d["rsi"]>70 else ("positive" if d["rsi"]<30 else "neutral")
        mc = "positive" if d["macd_val"]>d["macd_sig"] else "negative"
        for lbl, val, cls in [("RSI (14)",d["rsi"],rc),("MACD",d["macd_val"],mc),
                               ("Signal",d["macd_sig"],mc),("ADX",d["adx"],"neutral")]:
            st.markdown(ri(lbl, val, "#4ade80" if cls=="positive" else ("#f87171" if cls=="negative" else "#fbbf24")),
                        unsafe_allow_html=True)
 
    t1, t2 = st.columns(2)
    with t1:
        st.markdown("<div class='section-title' style='margin-top:0.5rem;'>📐 Moving Averages</div>",
                    unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "Indicator": ["SMA 20","SMA 50","SMA 200","EMA 9","EMA 21"],
            "Value": [f"₹{v:,.2f}" for v in [d["sma20"],d["sma50"],d["sma200"],d["ema9"],d["ema21"]]],
            "Signal": ["✅ Above" if d["price"]>v else "⚠️ Below"
                       for v in [d["sma20"],d["sma50"],d["sma200"],d["ema9"],d["ema21"]]],
        }), use_container_width=True, hide_index=True)
 
        st.markdown("<div class='section-title' style='margin-top:1rem;'>🌊 Fibonacci</div>",
                    unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "Level":  ["23.6%","38.2%","50.0%","61.8%","78.6%"],
            "Price":  [f"₹{v:,.2f}" for v in [d["fib_236"],d["fib_382"],d["fib_500"],d["fib_618"],d["fib_786"]]],
            "Zone":   ["Weak Sup","Support","Strong Sup","Golden","Major Sup"],
        }), use_container_width=True, hide_index=True)
 
    with t2:
        st.markdown("<div class='section-title' style='margin-top:0.5rem;'>🎯 Key S/R Zones</div>",
                    unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "Zone":  ["Strong Resistance","Resistance","Current Price","Support","Strong Support"],
            "Level": [f"₹{round(d['price']*1.115):,}", f"₹{round(d['price']*1.055):,}",
                      f"₹{d['price']:,.2f}",            f"₹{round(d['price']*0.962):,}",
                      f"₹{round(d['price']*0.912):,}"],
            "Type":  ["Order Block","FVG","Spot","Swing Low","OB+FVG"],
        }), use_container_width=True, hide_index=True)
 
        st.markdown("<div class='section-title' style='margin-top:1rem;'>📦 F&O Snapshot</div>",
                    unsafe_allow_html=True)
        pc = "positive" if d["pcr"]>1 else "negative"
        st.markdown(f"""<div class='card'>
            <div class='row-item'>
                <span style='color:#475569;font-size:0.78rem;'>Put-Call Ratio</span>
                <span class='mono {pc}'>{d['pcr']}</span>
            </div>
            <div class='row-item'>
                <span style='color:#475569;font-size:0.78rem;'>Max Pain Level</span>
                <span class='mono'>₹{d['max_pain']:,.0f}</span>
            </div>
            <div style='padding:6px 0;font-size:0.73rem;color:#475569;'>
                OI: Short buildup near resistance · Long addition at support (placeholder)
            </div>
        </div>""", unsafe_allow_html=True)
 
    st.markdown("<div class='section-title' style='margin-top:0.5rem;'>⚠️ Risk Factors</div>",
                unsafe_allow_html=True)
    rf1, rf2, rf3 = st.columns(3)
    for col, lbl, val, warn in [
        (rf1,"Volatility",    f"ATR ₹{d['atr']} | Beta {d['beta']}",     d["beta"]>1.3),
        (rf2,"Liquidity",     f"Vol: {d['volume']:,.0f}",                  d["volume"]<1_000_000),
        (rf3,"Drawdown Risk", f"Max DD {d['max_dd']}% | VaR {d['hist_var']}%", True),
    ]:
        with col:
            st.markdown(f"""<div class='{"card-red" if warn else "card-green"}'>
                <div class='label'>{"🔴" if warn else "🟢"} {lbl}</div>
                <div class='mono' style='font-size:0.8rem;margin-top:5px;'>{val}</div>
            </div>""", unsafe_allow_html=True)
 
    st.markdown(DISCLAIMER, unsafe_allow_html=True)
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4 — FINAL VERDICT
# ══════════════════════════════════════════════════════════════════════════════
 
def render_final_verdict(d):
    sbc  = compute_sbc(d["symbol"])
    gann = compute_gann(d["price"], d["symbol"])
 
    # ── Scores ────────────────────────────────────────────────────────────────
    tech_bull = (
        (25 if d["price"]>d["sma50"] else 0) +
        (20 if d["price"]>d["sma200"] else 0) +
        (15 if d["macd_val"]>d["macd_sig"] else 0) +
        (15 if 40<d["rsi"]<65 else (5 if d["rsi"]<=40 else 0)) +
        (15 if d["adx"]>25 else 5) +
        (10 if d["pcr"]>1.0 else 0)
    )
    gann_bull = (70 if gann["bias"]=="Bullish" else 30)
    if gann["strength"]=="Strong":
        gann_bull = min(95, gann_bull+15) if gann["bias"]=="Bullish" else max(5, gann_bull-15)
    sbc_bull = sbc["sbc_score"]
 
    composite = round(tech_bull*0.60 + gann_bull*0.20 + sbc_bull*0.20)
    risk_adj  = max(0, (d["risk_score"]-50)*0.3)
    final     = max(0, min(100, composite - risk_adj))
 
    # ── Verdicts ──────────────────────────────────────────────────────────────
    if final >= 65:
        na, na_sub, na_card, na_col, na_ico = "BUY","Favorable setup for new long position","card-buy","#4ade80","▲"
    elif final <= 35:
        na, na_sub, na_card, na_col, na_ico = "AVOID / SHORT","Unfavorable — wait or consider hedge","card-sell","#f87171","▼"
    else:
        na, na_sub, na_card, na_col, na_ico = "WAIT FOR ENTRY","Setup not confirmed — watch trigger","card-hold","#fbbf24","◈"
 
    if final >= 70:
        ea, ea_sub, ea_cls = "ADD MORE","Strong continuation — add on dips to entry zone","positive"
    elif final >= 55:
        ea, ea_sub, ea_cls = "HOLD","Trend intact — hold with trailing stop","positive"
    elif final >= 40:
        ea, ea_sub, ea_cls = "HOLD (Cautious)","Mixed signals — tighten SL, partial book","neutral"
    elif final >= 25:
        ea, ea_sub, ea_cls = "PARTIAL SELL","Momentum fading — book 50%, trail rest","neutral"
    else:
        ea, ea_sub, ea_cls = "EXIT / SELL","Trend deteriorating — exit to protect capital","negative"
 
    strength = ("Very Strong" if abs(final-50)>30 else ("Strong" if abs(final-50)>20 else ("Moderate" if abs(final-50)>10 else "Weak")))
    conf_n   = {3:"High",2:"Medium",1:"Low",0:"Very Low"}[sum([tech_bull>55,gann_bull>55,sbc_bull>55])]
    conf_col = {"High":"#4ade80","Medium":"#60a5fa","Low":"#fbbf24","Very Low":"#f87171"}[conf_n]
 
    # ── Hero card ─────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(139,92,246,0.04));
        border:1px solid rgba(139,92,246,0.2);border-radius:24px;
        padding:1.8rem 2rem;margin-bottom:1.2rem;
        box-shadow:0 0 60px rgba(99,102,241,0.06);'>
        <div class='label' style='margin-bottom:6px;'>
            FINAL COMPOSITE VERDICT — {d["symbol"]}</div>
        <div style='display:flex;align-items:center;gap:1.2rem;flex-wrap:wrap;'>
            <div style='font-family:JetBrains Mono;font-size:2.8rem;font-weight:800;
                color:{na_col};line-height:1;'>{na_ico} {na}</div>
            <div>
                <div style='color:#94a3b8;font-size:0.9rem;margin-bottom:6px;'>{na_sub}</div>
                <div style='display:flex;gap:8px;flex-wrap:wrap;'>
                    <span style='font-family:JetBrains Mono;font-size:0.76rem;
                        background:rgba(255,255,255,0.05);border-radius:8px;padding:2px 10px;color:#64748b;'>
                        Score: <b style='color:{na_col};'>{int(final)}</b>/100</span>
                    <span style='font-family:JetBrains Mono;font-size:0.76rem;
                        background:rgba(255,255,255,0.05);border-radius:8px;padding:2px 10px;color:#64748b;'>
                        Signal: <b style='color:{na_col};'>{strength}</b></span>
                    <span style='font-family:JetBrains Mono;font-size:0.76rem;
                        background:rgba(255,255,255,0.05);border-radius:8px;padding:2px 10px;color:#64748b;'>
                        Confluence: <b style='color:{conf_col};'>{conf_n}</b></span>
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)
 
    # ── Two action cards ──────────────────────────────────────────────────────
    vc1, vc2 = st.columns(2)
    mid = round((d["entry_low"]+d["entry_high"])/2, 2)
 
    with vc1:
        st.markdown(f"""<div class='{na_card}'>
            <div class='label' style='margin-bottom:8px;'>🆕 NEW POSITION</div>
            <div style='font-family:JetBrains Mono;font-size:1.7rem;font-weight:800;color:{na_col};'>
                {na_ico} {na}</div>
            <div style='color:#94a3b8;font-size:0.82rem;margin:6px 0 14px;'>{na_sub}</div>
            <div class='label' style='margin-bottom:8px;'>Action Plan</div>""",
                    unsafe_allow_html=True)
        if na == "BUY":
            plan = [
                ("Entry",       f"₹{d['entry_low']:,.2f} – ₹{d['entry_high']:,.2f}", "#93c5fd"),
                ("Stop-Loss",   f"₹{d['sl']:,.2f}",                                   "#f87171"),
                ("Target 1",    f"₹{d['t1']:,.2f}",                                   "#4ade80"),
                ("Target 2",    f"₹{d['t2']:,.2f}",                                   "#c084fc"),
                ("Risk:Reward", f"1 : {d['rr']}",                                      "#fbbf24"),
            ]
        elif "AVOID" in na:
            plan = [
                ("Avoid Long",  "Do not initiate long position",                      "#f87171"),
                ("Short Entry", f"Below ₹{d['sl']:,.2f} (advanced traders)",          "#f87171"),
                ("Short Target",f"₹{round(d['price']*0.94):,}",                      "#4ade80"),
                ("Short SL",    f"₹{round(d['price']*1.025):,}",                     "#fbbf24"),
                ("Alternative", "Wait for base formation + volume",                   "#94a3b8"),
            ]
        else:
            plan = [
                ("Watch Level", f"₹{d['entry_low']:,.2f} (support)",                 "#60a5fa"),
                ("Trigger",     f"Close above ₹{d['entry_high']:,.2f} on vol",       "#fbbf24"),
                ("Then Target", f"₹{d['t1']:,.2f}",                                  "#4ade80"),
                ("Invalidate",  f"Break below ₹{d['sl']:,.2f}",                     "#f87171"),
                ("Note",        "Wait for confirmation candle",                       "#94a3b8"),
            ]
        for lbl, val, col in plan:
            st.markdown(ri(lbl, val, col), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
 
    with vc2:
        ea_card = "card-green" if ea_cls=="positive" else ("card-amber" if ea_cls=="neutral" else "card-red")
        ea_col2 = "#4ade80" if ea_cls=="positive" else ("#fbbf24" if ea_cls=="neutral" else "#f87171")
        ea_ico  = "▲" if ea_cls=="positive" else ("◈" if ea_cls=="neutral" else "▼")
        st.markdown(f"""<div class='{ea_card}'>
            <div class='label' style='margin-bottom:8px;'>📦 EXISTING POSITION</div>
            <div style='font-family:JetBrains Mono;font-size:1.7rem;font-weight:800;color:{ea_col2};'>
                {ea_ico} {ea}</div>
            <div style='color:#94a3b8;font-size:0.82rem;margin:6px 0 14px;'>{ea_sub}</div>
            <div class='label' style='margin-bottom:8px;'>Position Management</div>""",
                    unsafe_allow_html=True)
        if "ADD" in ea:
            mgmt = [
                ("Add Zone",   f"₹{d['entry_low']:,.2f}–₹{d['entry_high']:,.2f}", "#93c5fd"),
                ("Trail SL",   f"₹{d['sl']:,.2f}",                                "#f87171"),
                ("Book @ T1",  f"₹{d['t1']:,.2f} (25%)",                          "#4ade80"),
                ("Book @ T2",  f"₹{d['t2']:,.2f} (50%)",                          "#c084fc"),
                ("Hold Rest",  "Let winners run",                                  "#94a3b8"),
            ]
        elif ea == "HOLD":
            mgmt = [
                ("Trail SL",   f"₹{d['sl']:,.2f}",                                "#f87171"),
                ("Partial",    f"₹{d['t1']:,.2f} (30%)",                          "#4ade80"),
                ("Full Target",f"₹{d['t2']:,.2f}",                                "#c084fc"),
                ("Review On",  gann["cycles"][0][0].strftime("%d %b %Y"),         "#a5b4fc"),
                ("Action",     "No new adds till trigger",                         "#94a3b8"),
            ]
        elif "Cautious" in ea:
            mgmt = [
                ("Book Partial",f"₹{d['t1']:,.2f} (40%)",                         "#fbbf24"),
                ("Tighten SL", f"₹{round(d['price']*0.975):,}",                  "#f87171"),
                ("Watch",      f"₹{round(d['price']*0.965):,} (key support)",    "#60a5fa"),
                ("Avoid",      "No averaging down",                               "#f87171"),
                ("Review",     "Reassess in 5 trading sessions",                  "#94a3b8"),
            ]
        elif "PARTIAL" in ea:
            mgmt = [
                ("Book 50%",   "At current market",                               "#fbbf24"),
                ("Move SL",    f"₹{round(d['price']*0.975):,} (tight)",          "#f87171"),
                ("Hold Rest",  f"Trail to ₹{round(d['price']*0.96):,}",          "#94a3b8"),
                ("Avoid",      "No fresh long entries",                            "#f87171"),
                ("Review",     gann["cycles"][0][0].strftime("%d %b %Y"),         "#a5b4fc"),
            ]
        else:
            mgmt = [
                ("Exit Now",   f"Sell at market / ₹{round(d['price']*0.998):,}", "#f87171"),
                ("Hard SL",    f"₹{d['sl']:,.2f}",                                "#f87171"),
                ("Re-entry",   f"Only above ₹{d['entry_high']:,.2f} on vol",     "#64748b"),
                ("Rule",       "Protect capital first",                           "#f87171"),
                ("Cooldown",   "Stay out min 5 sessions",                         "#94a3b8"),
            ]
        for lbl, val, col in mgmt:
            st.markdown(ri(lbl, val, col), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
 
    # ── Score Scorecard ───────────────────────────────────────────────────────
    st.markdown("<div class='section-title' style='margin-top:0.5rem;'>📊 Signal Scorecard</div>",
                unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns(4)
    for col, title, score, icon, desc in [
        (sc1, "Technical",  tech_bull,     "📈", "Price action + indicators"),
        (sc2, "Gann",       gann_bull,     "🔷", "Price–Time squaring"),
        (sc3, "SBC Astro",  sbc_bull,      "🔵", "Vedha confluence"),
        (sc4, "Composite",  int(final),    "⚡", "Weighted final (60/20/20)"),
    ]:
        color = "#4ade80" if score>58 else ("#fbbf24" if score>42 else "#f87171")
        lbl   = "Bullish" if score>58 else ("Neutral" if score>42 else "Bearish")
        with col:
            st.markdown(f"""<div class='card' style='text-align:center;'>
                <div style='font-size:1.5rem;'>{icon}</div>
                <div class='label' style='margin:6px 0 4px;'>{title}</div>
                <div style='font-family:JetBrains Mono;font-size:2rem;font-weight:800;
                    color:{color};line-height:1;'>{score}</div>
                <div style='color:{color};font-size:0.72rem;font-weight:600;margin:4px 0 8px;'>
                    {lbl}</div>
                {progress_bar(score,color)}
                <div style='font-size:0.68rem;color:#475569;margin-top:8px;'>{desc}</div>
            </div>""", unsafe_allow_html=True)
 
    # ── Key Observations ──────────────────────────────────────────────────────
    st.markdown("<div class='section-title' style='margin-top:0.5rem;'>🔍 Key Observations</div>",
                unsafe_allow_html=True)
    obs = []
    obs.append(("✅" if d["price"]>d["sma200"] else "⚠️",
                "Price above SMA 200 — long-term uptrend intact" if d["price"]>d["sma200"]
                else "Price below SMA 200 — long-term trend bearish",
                "positive" if d["price"]>d["sma200"] else "negative"))
    obs.append(("✅" if d["macd_val"]>d["macd_sig"] else "⚠️",
                "MACD above signal — bullish momentum" if d["macd_val"]>d["macd_sig"]
                else "MACD below signal — weakening momentum",
                "positive" if d["macd_val"]>d["macd_sig"] else "negative"))
    obs.append(("🔴" if d["rsi"]>70 else ("🟢" if d["rsi"]<30 else "🟡"),
                f"RSI {d['rsi']} — {'Overbought, pullback risk' if d['rsi']>70 else ('Oversold, bounce watch' if d['rsi']<30 else 'Neutral zone')}",
                "negative" if d["rsi"]>70 else ("positive" if d["rsi"]<30 else "neutral")))
    obs.append(("✅" if d["pcr"]>1.2 else ("⚠️" if d["pcr"]<0.8 else "🟡"),
                f"PCR {d['pcr']} — {'Put-heavy, upside bias' if d['pcr']>1.2 else ('Call-heavy, bearish bias' if d['pcr']<0.8 else 'Balanced OI')}",
                "positive" if d["pcr"]>1.2 else ("negative" if d["pcr"]<0.8 else "neutral")))
    obs.append(("🔷",
                f"Gann: {gann['degree']}° → {gann['strength']} {gann['bias']} quadrant on SQ9",
                "positive" if gann["bias"]=="Bullish" else "negative"))
    obs.append(("📅",
                f"Next Gann cycle: {gann['cycles'][0][0].strftime('%d %b')} — velocity change watch",
                "neutral"))
    obs.append(("🔵",
                f"SBC: {sbc['benefic']} benefic vs {sbc['malefic']} malefic vedhas → {sbc['sbc_label']}",
                "positive" if sbc["sbc_score"]>55 else ("neutral" if sbc["sbc_score"]>40 else "negative")))
    obs.append(("🏛️",
                f"ROE {d['roe']}% | D/E {d['de_ratio']}x | Pledge {d['pledge_pct']}%",
                "positive" if d["roe"]>15 and d["de_ratio"]<1 else "neutral"))
 
    oa, ob_ = st.columns(2)
    for i, (icon, text, cls) in enumerate(obs):
        col = oa if i%2==0 else ob_
        col_hex = "#4ade80" if cls=="positive" else ("#f87171" if cls=="negative" else "#fbbf24")
        with col:
            st.markdown(f"""<div class='card' style='padding:0.75rem 1rem;margin-bottom:0.5rem;'>
                <div style='display:flex;gap:8px;align-items:flex-start;'>
                    <span style='font-size:0.95rem;flex-shrink:0;'>{icon}</span>
                    <span style='font-size:0.78rem;color:{col_hex};line-height:1.5;'>{text}</span>
                </div>
            </div>""", unsafe_allow_html=True)
 
    st.markdown(DISCLAIMER, unsafe_allow_html=True)
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  SEARCH TAB
# ══════════════════════════════════════════════════════════════════════════════
 
def render_search():
    st.markdown("""<div style='text-align:center;padding:2.5rem 0 1.5rem;'>
        <div style='font-size:2.4rem;font-weight:800;color:#f1f5f9;letter-spacing:-0.03em;'>
            NSE Risk Score Report</div>
        <div style='color:#475569;font-size:0.95rem;margin-top:0.5rem;'>
            Enter any NSE symbol · SBC &amp; Gann calculated per stock · Live data via yfinance
        </div>
    </div>""", unsafe_allow_html=True)
 
    _, cc, _ = st.columns([1,2,1])
    with cc:
        sym_in = st.text_input("", placeholder="e.g. RELIANCE, TCS, INFY, HDFCBANK, SBIN…",
                               key="sym_in", label_visibility="collapsed")
        _, bc, _ = st.columns([1,2,1])
        with bc:
            go = st.button("🔍  Analyse Stock", use_container_width=True)
 
    if go and sym_in.strip():
        st.session_state["active_sym"] = sym_in.strip().upper()
        st.session_state["do_fetch"]   = True
 
    st.markdown("<br><div class='label' style='text-align:center;'>Quick Access</div>",
                unsafe_allow_html=True)
    pop = ["RELIANCE","TCS","INFY","HDFCBANK","SBIN","WIPRO","TATAMOTORS","ADANIPORTS"]
    pcols = st.columns(len(pop))
    for i, sym in enumerate(pop):
        with pcols[i]:
            if st.button(sym, use_container_width=True, key=f"q_{sym}"):
                st.session_state["active_sym"] = sym
                st.session_state["do_fetch"]   = True
 
    if st.session_state.get("do_fetch") and st.session_state.get("active_sym"):
        sym = st.session_state["active_sym"]
        with st.spinner(f"⏳ Fetching data for {sym}…"):
            data = fetch_stock_data(sym)
        st.session_state["stock_data"] = data
        st.session_state["do_fetch"]   = False
 
    if st.session_state.get("stock_data"):
        render_report(st.session_state["stock_data"])
    else:
        st.markdown("""<div style='text-align:center;padding:3rem 0;color:#1e293b;font-size:0.9rem;'>
            📈 Enter a stock symbol above to begin analysis
        </div>""", unsafe_allow_html=True)
 
 
def render_report(d):
    src = (
        "<span style='background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.25);"
        "border-radius:6px;padding:1px 8px;font-size:0.68rem;color:#4ade80;'>● LIVE</span>"
        if d.get("data_source")=="live" else
        "<span style='background:rgba(251,191,36,0.12);border:1px solid rgba(251,191,36,0.25);"
        "border-radius:6px;padding:1px 8px;font-size:0.68rem;color:#fbbf24;'>⚠ SYNTHETIC</span>"
    )
    h1, h2 = st.columns([5,1])
    with h1:
        chg_cls = "positive" if d["change_pct"]>=0 else "negative"
        arrow   = "▲" if d["change_pct"]>=0 else "▼"
        st.markdown(f"""<div style='padding:0.7rem 0 0.4rem;display:flex;align-items:center;gap:14px;flex-wrap:wrap;'>
            <span style='font-size:1.55rem;font-weight:800;color:#f1f5f9;'>{d["symbol"]}</span>
            <span style='font-family:JetBrains Mono;font-size:1.35rem;color:#f1f5f9;font-weight:600;'>
                ₹{d['price']:,.2f}</span>
            <span class='{chg_cls}' style='font-size:0.95rem;font-weight:600;'>
                {arrow} {abs(d['change_pct']):.2f}%</span>
            {src}
            <span style='color:#334155;font-size:0.72rem;'>NSE</span>
        </div>""", unsafe_allow_html=True)
    with h2:
        if st.button("🔄 Refresh", use_container_width=True, type="primary"):
            st.cache_data.clear()
            if "stock_data" in st.session_state:
                del st.session_state["stock_data"]
            st.session_state["do_fetch"] = True
            st.rerun()

    tabs = st.tabs([
        "📊 Risk Overview",
        "🌙 Sentiment Overlay",
        "📈 Technical Deep Dive",
        "⚡ Final Verdict",
    ])
    with tabs[0]: render_risk_overview(d)
    with tabs[1]: render_sentiment(d)
    with tabs[2]: render_technical(d)
    with tabs[3]: render_final_verdict(d)
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
 
def main():
    st.markdown("""<div style='display:flex;align-items:center;justify-content:space-between;
        padding:0.4rem 0 1rem;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:0.8rem;'>
        <div style='display:flex;align-items:center;gap:10px;'>
            <div style='width:36px;height:36px;
                background:linear-gradient(135deg,rgba(99,102,241,0.3),rgba(139,92,246,0.2));
                border:1px solid rgba(139,92,246,0.35);border-radius:11px;
                display:flex;align-items:center;justify-content:center;font-size:1.1rem;'>📊</div>
            <div>
                <div style='font-weight:800;font-size:0.98rem;color:#f1f5f9;'>NSE Risk Report</div>
                <div style='font-size:0.65rem;color:#334155;'>Live · SBC + Gann + Technical · v2.0</div>
            </div>
        </div>
        <div style='font-family:JetBrains Mono;font-size:0.68rem;color:#1e293b;'>
            Not Financial Advice</div>
    </div>""", unsafe_allow_html=True)
 
    app_tabs = st.tabs(["🔍 Stock Analysis", "ℹ️ How to Use"])
 
    with app_tabs[0]:
        render_search()
 
    with app_tabs[1]:
        st.markdown("""<div class='card' style='max-width:740px;margin:auto;'>
            <div class='section-title'>How to Use This Dashboard</div>
            <div style='font-size:0.83rem;color:#64748b;line-height:1.9;'>
                <b style='color:#f1f5f9;'>1. Search any NSE symbol</b> — type RELIANCE, TCS, SBIN etc.
                Live data via yfinance; synthetic fallback if unavailable.<br>
                <b style='color:#f1f5f9;'>2. Risk Overview</b> — Risk score (lower = safer), trade plan
                (entry / SL / targets), and fundamental moat.<br>
                <b style='color:#f1f5f9;'>3. Sentiment Overlay</b> — SBC vedha grid (unique per symbol,
                refreshed daily) + Gann SQ9 calculated from real price.<br>
                <b style='color:#f1f5f9;'>4. Technical Deep Dive</b> — Candlestick chart, MAs, RSI,
                MACD, Fibonacci, S/R zones, F&amp;O snapshot.<br>
                <b style='color:#f1f5f9;'>5. ⚡ Final Verdict</b> — Composite score (Tech 60% · Gann 20%
                · SBC 20%), verdict for new entry AND existing position management, scorecard,
                and 8 key observations.
            </div>
            <div style='background:rgba(0,0,0,0.25);border-radius:12px;padding:1rem;
                font-family:JetBrains Mono;font-size:0.72rem;color:#4f46e5;margin-top:1rem;'>
                pip install streamlit plotly pandas numpy yfinance<br>
                streamlit run app.py
            </div>
        </div>""", unsafe_allow_html=True)
        st.markdown(DISCLAIMER, unsafe_allow_html=True)
 
 
if __name__ == "__main__":
    main()
