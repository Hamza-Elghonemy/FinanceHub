# streamlit_app.py
# Financial Insights Hub — formatted & fixed
# Palette: purple/teal gradient + light theme CSS

from __future__ import annotations
import io
import hashlib
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Optional click support
try:
    from streamlit_plotly_events import plotly_events
    CLICK_ENABLED = True
except Exception:
    CLICK_ENABLED = False

# -----------------------------
# App & Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Financial Insights Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Theme state (kept as light-only per your comment)
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# -----------------------------
# Color palette (purple/teal set)
# -----------------------------
DELOITTE_PRIMARY = "#667eea"
DELOITTE_SECONDARY = "#764ba2"
DELOITTE_ACCENT = "#f093fb"
COLORWAY = [
    "#667eea", "#764ba2", "#f093fb",
    "#f5576c", "#11998e", "#38ef7d",
    "#a8edea", "#fed6e3"
]

# -----------------------------
# Enhanced CSS Styling
# -----------------------------
def apply_custom_css():
    theme = st.session_state.theme

    if theme == "light":
        st.markdown("""
        <style>
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --accent-color: #f093fb;
            --bg-primary: #FFFFFF;
            --bg-secondary: #F8FAFC;
            --bg-tertiary: #F1F5F9;
            --text-primary: #1E293B;
            --text-secondary: #64748B;
            --text-muted: #94A3B8;
            --border-color: #E2E8F0;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --accent-color: #f093fb;
            --bg-primary: #0F172A;
            --bg-secondary: #1E293B;
            --bg-tertiary: #334155;
            --text-primary: #F1F5F9;
            --text-secondary: #CBD5E1;
            --text-muted: #94A3B8;
            --border-color: #475569;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        }
        </style>
        """, unsafe_allow_html=True)

    # Global UI
    st.markdown("""
    <style>
    .stApp {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"]{
        background: var(--bg-primary) !important;
        border-right: 2px solid var(--border-color) !important;
    }

    /* Header block */
    .main-header {
        background: var(--bg-primary);
        border: 2px solid var(--border-color);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: var(--text-primary);
        text-align: center;
        box-shadow: var(--shadow-lg);
    }
    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        color: var(--text-primary);
    }
    .main-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        color: var(--text-secondary);
    }

    /* Cards */
    .metric-card {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }
    .metric-card h3 {
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card .value {
        color: var(--text-primary);
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
    }
    .metric-card .delta { font-size: 0.9rem; font-weight: 600; margin-top: .5rem; }
    .delta.positive { color: #10B981; }
    .delta.negative { color: #EF4444; }

    /* Chart container */
    .chart-container {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
        position: relative;
    }
    .chart-container::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        border-radius: 16px 16px 0 0;
    }
    .chart-title {
        color: var(--text-primary);
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0 0 1.0rem 0;
        display: flex;
        align-items: center;
        gap: .5rem;
    }

    /* Dataframe styling */
    .stDataFrame { border-radius: 16px !important; overflow: hidden !important; box-shadow: var(--shadow-lg) !important; border: 1px solid var(--border-color) !important; }
    .stDataFrame table { background: var(--bg-primary) !important; }
    .stDataFrame thead th {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
        color: white !important; font-weight: 700 !important; padding: 1rem !important;
        border: none !important; font-size: .95rem !important; letter-spacing: .5px !important;
    }
    .stDataFrame tbody td {
        background: var(--bg-primary) !important; color: var(--text-primary) !important;
        padding: 1rem !important; border-bottom: 1px solid var(--border-color) !important;
    }
    .stDataFrame tbody tr:hover { background: var(--bg-tertiary) !important; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
        color: white !important; border: none !important; border-radius: 12px !important;
        padding: .75rem 2rem !important; font-weight: 600 !important;
        box-shadow: var(--shadow) !important; transition: all .3s ease !important;
    }
    .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: var(--shadow-lg) !important; }

    /* Inputs */
    .stSelectbox > div > div {
        background: var(--bg-primary) !important; border: 2px solid var(--border-color) !important;
        border-radius: 12px !important; color: var(--text-primary) !important;
        font-size: 1.05rem !important; padding: .5rem .75rem !important; min-height: 3rem !important;
    }
    .stSelectbox label { font-size: 1rem !important; font-weight: 600 !important; color: var(--text-primary) !important; }

    /* Metric container tweaks */
    [data-testid="metric-container"] {
        background: var(--bg-primary); border: 1px solid var(--border-color);
        padding: 1rem; border-radius: 12px; box-shadow: var(--shadow);
    }

    /* Insight box */
    .insight-box {
        background: linear-gradient(135deg, var(--primary-color)20, var(--secondary-color)20);
        border: 1px solid var(--border-color);
        border-radius: 16px; padding: 1.5rem; margin: 1rem 0; border-left: 4px solid var(--primary-color);
    }
    .insight-text { color: var(--text-primary); font-size: 1.05rem; font-weight: 500; margin: 0; }

    /* General text */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, div, span { color: var(--text-primary) !important; }
    .stCaption { color: var(--text-secondary) !important; }
    </style>
    """, unsafe_allow_html=True)

apply_custom_css()

# -----------------------------
# Data Functions
# -----------------------------
@st.cache_data(show_spinner=True)
def fetch_yfinance_quarterlies(tickers: list[str]) -> dict[str, pd.DataFrame]:
    try:
        import yfinance as yf
    except Exception:
        return {}
    out = {}
    for t in tickers:
        try:
            tk = yf.Ticker(t)
            q_inc = tk.quarterly_financials
            q_bal = tk.quarterly_balance_sheet
            q_cf  = tk.quarterly_cashflow

            def tidy(df: pd.DataFrame):
                if df is None or df.empty:
                    return pd.DataFrame()
                df = df.copy()
                df.index = df.index.astype(str)
                df = df.T.reset_index().rename(columns={"index": "period_end"})
                df["period_end"] = pd.to_datetime(df["period_end"])
                df["Year"] = df["period_end"].dt.year
                df["Quarter"] = df["period_end"].dt.quarter
                return df

            inc, bal, cf = tidy(q_inc), tidy(q_bal), tidy(q_cf)
            dfs = [d for d in [inc, bal, cf] if not d.empty]
            if not dfs:
                continue
            df = dfs[0]
            for d in dfs[1:]:
                df = pd.merge(df, d, on=["period_end", "Year", "Quarter"], how="outer")

            rename = {
                "Total Revenue": "revenue", "Cost Of Revenue": "cogs", "Gross Profit": "gross_profit",
                "Operating Income": "operating_income", "Net Income": "net_income",
                "Total Assets": "total_assets", "Total Liab": "total_liabilities",
                "Total Stockholder Equity": "equity", "Total Current Assets": "current_assets",
                "Total Current Liabilities": "current_liabilities", "Operating Cash Flow": "cfo",
                "Capital Expenditure": "capex", "Free Cash Flow": "fcf",
                "Cash And Cash Equivalents": "cash"
            }
            for k, v in rename.items():
                if k in df.columns:
                    df.rename(columns={k: v}, inplace=True)
            if "fcf" not in df.columns and {"cfo", "capex"}.issubset(df.columns):
                df["fcf"] = df["cfo"] + df["capex"]
            out[t] = df.sort_values(["Year", "Quarter"])
        except Exception:
            continue
    return out

def _sector_map() -> dict[str, dict[str, str]]:
    return {
        "Technology": {"Apple": "AAPL", "Microsoft": "MSFT", "NVIDIA": "NVDA"},
        "Finance": {"JPMorgan": "JPM", "Bank of America": "BAC", "Wells Fargo": "WFC"},
        "Healthcare": {"Johnson & Johnson": "JNJ", "Pfizer": "PFE", "UnitedHealth": "UNH"},
    }

@st.cache_data(show_spinner=False)
def mock_financials(sector_map: dict[str, dict[str, str]]) -> pd.DataFrame:
    rng = np.random.default_rng(5)
    periods = pd.period_range("2019Q1", "2024Q4", freq="Q")
    rows = []
    for sector, comps in sector_map.items():
        for company, ticker in comps.items():
            base_rev = rng.uniform(5e9, 45e9)
            g = rng.uniform(0.01, 0.05)
            for p in periods:
                y, q = p.year, p.quarter
                t = (y - periods[0].year) * 4 + (q - 1)
                revenue = base_rev * ((1 + g) ** t) * rng.uniform(0.95, 1.06)
                cogs = revenue * rng.uniform(0.45, 0.60)
                gp = revenue - cogs
                opex = revenue * rng.uniform(0.18, 0.28)
                opinc = gp - opex
                netinc = opinc * rng.uniform(0.6, 0.85)

                assets = revenue * 3 * rng.uniform(0.85, 1.15)
                liab = assets * rng.uniform(0.45, 0.65)
                equity = assets - liab
                curr_assets = assets * rng.uniform(0.35, 0.55)
                curr_liab = liab * rng.uniform(0.35, 0.55)

                cfo = netinc * rng.uniform(0.8, 1.4)
                capex = -revenue * rng.uniform(0.03, 0.07)
                fcf = cfo + capex
                cash = revenue * rng.uniform(0.05, 0.10)

                rows.append(dict(
                    sector=sector, company=company, ticker=ticker, Year=y, Quarter=q,
                    period_end=pd.to_datetime(f"{y}Q{q}"),
                    revenue=revenue, cogs=cogs, gross_profit=gp,
                    operating_income=opinc, net_income=netinc,
                    total_assets=assets, total_liabilities=liab, equity=equity,
                    current_assets=curr_assets, current_liabilities=curr_liab,
                    cfo=cfo, capex=capex, fcf=fcf, cash=cash
                ))
    return pd.DataFrame(rows).sort_values(["sector", "company", "Year", "Quarter"])

@st.cache_data(show_spinner=True)
def build_panel() -> tuple[pd.DataFrame, dict[str, dict[str, str]]]:
    smap = _sector_map()
    live = fetch_yfinance_quarterlies([t for m in smap.values() for t in m.values()])
    frames = []
    for s, comps in smap.items():
        for c, t in comps.items():
            if t in live and not live[t].empty:
                df = live[t].copy()
                df["sector"] = s
                df["company"] = c
                keep = [
                    "sector", "company", "Year", "Quarter", "period_end", "revenue", "cogs", "gross_profit",
                    "operating_income", "net_income", "total_assets", "total_liabilities", "equity",
                    "current_assets", "current_liabilities", "cfo", "capex", "fcf", "cash"
                ]
                for k in keep:
                    if k not in df.columns:
                        df[k] = np.nan
                frames.append(df[keep])
    live_panel = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    mock = mock_financials(smap)
    if not live_panel.empty:
        key = ["sector", "company", "Year", "Quarter"]
        panel = mock.merge(live_panel, on=key, how="left", suffixes=("", "_live"))
        for col in [
            "period_end", "revenue", "cogs", "gross_profit", "operating_income", "net_income",
            "total_assets", "total_liabilities", "equity", "current_assets", "current_liabilities",
            "cfo", "capex", "fcf", "cash"
        ]:
            live_col = f"{col}_live"
            if live_col in panel.columns:
                panel[col] = panel[live_col].combine_first(panel[col])
                panel.drop(columns=[live_col], inplace=True)
    else:
        panel = mock
    return panel, smap

def add_ratios(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    x["gross_margin"] = x["gross_profit"] / x["revenue"]
    x["operating_margin"] = x["operating_income"] / x["revenue"]
    x["net_margin"] = x["net_income"] / x["revenue"]
    x["current_ratio"] = x["current_assets"] / x["current_liabilities"]
    x["debt_to_equity"] = x["total_liabilities"] / x["equity"]
    x["roe"] = x["net_income"] / x["equity"]
    x["fcf_margin"] = x["fcf"] / x["revenue"]
    x["earnings_quality"] = x["cfo"] / x["net_income"]
    return x

@st.cache_data
def mock_valuation(df_scope: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for comp in df_scope["company"].dropna().unique():
        seed = int(hashlib.md5(comp.encode()).hexdigest(), 16) % 10_000
        rng = np.random.default_rng(seed)
        rows.append(dict(
            company=comp,
            pe=rng.uniform(12, 35),
            peg=rng.uniform(0.8, 2.2),
            dividend_yield=rng.uniform(0.0, 0.03),
            pb=rng.uniform(2, 12),
        ))
    return pd.DataFrame(rows)

# -----------------------------
# Helpers
# -----------------------------
def fmt_money(x):
    if pd.isna(x):
        return "-"
    a = abs(x)
    if a >= 1e12: return f"${x/1e12:.2f}T"
    if a >= 1e9:  return f"${x/1e9:.2f}B"
    if a >= 1e6:  return f"${x/1e6:.2f}M"
    return f"${x:,.0f}"

def fmt_pct(x, decimals=1):
    return "-" if pd.isna(x) else f"{x*100:.{decimals}f}%"

def fmt_ratio(value, decimals=2, fallback="-"):
    if pd.isna(value):
        return fallback
    return f"{value:.{decimals}f}"

def pct_change(cur, prev):
    if pd.isna(cur) or pd.isna(prev) or prev == 0:
        return np.nan
    return (cur - prev) / prev

def sector_latest_df(sector_name):
    d = PANEL[PANEL["sector"] == sector_name].sort_values(["Year", "Quarter"])
    return d.groupby("company", as_index=False).tail(1)

def scope_agg_series(df, cols):
    g = df.groupby(["period_end"], as_index=False)[cols].sum()
    return g.sort_values("period_end")

def style_fig(fig):
    fig.update_layout(
        colorway=COLORWAY,
        hovermode="x unified",
        margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1E293B", size=13),
        legend=dict(title=None, orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    grid_color = "#E2E8F0"
    axis_color = "#64748B"
    fig.update_xaxes(showgrid=True, gridcolor=grid_color, linecolor=axis_color, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=grid_color, linecolor=axis_color, zeroline=False)
    return fig

def get_kpi_class(value, metric_type, benchmark=None):
    """Return a qualitative class for KPI styling."""
    if pd.isna(value):
        return "neutral"

    if metric_type in ("margin", "roe"):
        if value > 0.25: return "excellent"
        if value > 0.15: return "positive"
        if value > 0.05: return "neutral"
        if value > 0:   return "warning"
        return "negative"

    if metric_type == "ratio":  # current ratio
        if value > 2.5: return "excellent"
        if value > 2:   return "positive"
        if value > 1.5: return "neutral"
        if value > 1:   return "warning"
        return "negative"

    if metric_type == "debt_ratio":  # debt/equity (lower better)
        if value < 0.2: return "excellent"
        if value < 0.4: return "positive"
        if value < 0.7: return "neutral"
        if value < 1:   return "warning"
        return "negative"

    if metric_type == "growth":
        if value > 0.20: return "excellent"
        if value > 0.10: return "positive"
        if value > 0:    return "neutral"
        if value > -0.05:return "warning"
        return "negative"

    return "neutral"

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    panel, sector_map = build_panel()
    return add_ratios(panel), sector_map

with st.spinner("🔄 Loading financial data..."):
    PANEL, SECTOR_MAP = load_data()

# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div class="main-header">
    <h1>Financial Insights Hub</h1>
    <p>Advanced Financial Analytics & Business Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar Controls
# -----------------------------
with st.sidebar:
    st.markdown("### Controls")
    st.caption(f"Current Theme: **{st.session_state.theme.title()}**")

    st.divider()

    st.markdown("### Data Filters")
    sector = st.selectbox("Sector", sorted(SECTOR_MAP.keys()), key="sector_select")
    companies = ["All"] + list(SECTOR_MAP[sector].keys())
    company = st.selectbox("Company", companies, index=0, key="company_select")

# -----------------------------
# Navigation
# -----------------------------
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboards"

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Dashboards", use_container_width=True):
        st.session_state.current_page = "Dashboards"
with col2:
    if st.button("Data Table", use_container_width=True):
        st.session_state.current_page = "Data Table"
with col3:
    if st.button("Insights", use_container_width=True):
        st.session_state.current_page = "Insights"

st.divider()

# Scope definition
if company == "All":
    SC_LABEL = f"{sector} (Sector)"
    df_scope = PANEL[PANEL["sector"] == sector].copy()
else:
    SC_LABEL = f"{company} ({sector})"
    df_scope = PANEL[(PANEL["sector"] == sector) & (PANEL["company"] == company)].copy()

df_scope = df_scope.sort_values(["Year", "Quarter"])
if not df_scope.empty:
    latest = df_scope.tail(1).iloc[0]
else:
    latest = pd.Series(dtype="float64")

# =====================================================
# PAGE 1 — DASHBOARDS
# =====================================================
if st.session_state.current_page == "Dashboards":
    st.markdown(f"## Financial Dashboards — {SC_LABEL}")

    dashboard_type = st.selectbox(
        "Select Dashboard Type",
        ["Profitability", "Financial Standing", "Cash Flow", "Ratios & Valuation"],
        key="dashboard_type"
    )

    # ---------------- Profitability ----------------
    if dashboard_type == "Profitability":
        if not df_scope.empty:
            col1, col2, col3, col4 = st.columns(4)

            srt = df_scope.sort_values(["Year", "Quarter"])
            cur = srt["net_income"].iloc[-1] if len(srt) > 0 else np.nan
            prev_q = srt["net_income"].iloc[-2] if len(srt) > 1 else np.nan
            qoq = pct_change(cur, prev_q)
            opm = latest.get("operating_margin", np.nan)
            roe = latest.get("roe", np.nan)
            revenue = latest.get("revenue", np.nan)

            with col1:
                net_income_class = get_kpi_class(qoq, "growth")
                st.markdown(f"""
                <div class="metric-card {net_income_class}">
                    <h3>Net Income</h3>
                    <div class="value">{fmt_money(cur)}</div>
                    <div class="delta {'positive' if (qoq or 0) >= 0 else 'negative'}">
                        {f"{qoq*100:+.1f}% QoQ" if pd.notna(qoq) else "–"}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                opm_class = get_kpi_class(opm, "margin")
                st.markdown(f"""
                <div class="metric-card {opm_class}">
                    <h3>Operating Margin</h3>
                    <div class="value">{fmt_pct(opm)}</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                roe_class = get_kpi_class(roe, "roe")
                st.markdown(f"""
                <div class="metric-card {roe_class}">
                    <h3>ROE</h3>
                    <div class="value">{fmt_pct(roe)}</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div class="metric-card neutral">
                    <h3>Revenue</h3>
                    <div class="value">{fmt_money(revenue)}</div>
                </div>
                """, unsafe_allow_html=True)

        # Trend chart: Revenue & Gross Profit
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Revenue & Gross Profit Trend</div>', unsafe_allow_html=True)
        if not df_scope.empty:
            agg = scope_agg_series(df_scope, ["revenue", "gross_profit"])
            line_df = agg.melt(id_vars="period_end", value_vars=["revenue", "gross_profit"],
                               var_name="Metric", value_name="Value")
            fig1 = px.line(line_df, x="period_end", y="Value", color="Metric", markers=True)
            fig1.update_traces(marker=dict(size=6), line=dict(width=3))
            fig1 = style_fig(fig1)
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No data available for the selected scope.")
        st.markdown("</div>", unsafe_allow_html=True)

        # Peer comparison: Profit margin vs peers
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Profit Margin vs Sector Peers</div>', unsafe_allow_html=True)
        latest_sector = sector_latest_df(sector)
        if not latest_sector.empty:
            latest_sector["profit_margin"] = latest_sector["net_income"] / latest_sector["revenue"]
            med = latest_sector["profit_margin"].median()
            fig3 = px.bar(latest_sector.sort_values("profit_margin", ascending=False),
                          x="company", y="profit_margin")
            fig3.update_traces(hovertemplate="<b>%{x}</b><br>Profit Margin: %{y:.1%}<extra></extra>")
            # Median line (no position string to avoid invalid values)
            fig3.add_hline(y=med, line_dash="dash", line_color=DELOITTE_ACCENT,
                           annotation_text=f"Sector median {med:.1%}")
            fig3 = style_fig(fig3)
            fig3.update_layout(height=400, yaxis_tickformat=".0%")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No peer data available.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- Financial Standing ----------------
    elif dashboard_type == "Financial Standing":
        if not df_scope.empty:
            col1, col2, col3, col4 = st.columns(4)

            current_ratio = latest.get("current_ratio", np.nan)
            dte_proxy = latest.get("debt_to_equity", np.nan)
            equity_val = latest.get("equity", np.nan)
            assets_val = latest.get("total_assets", np.nan)

            with col1:
                cr_class = get_kpi_class(current_ratio, "ratio")
                st.markdown(f"""
                <div class="metric-card {cr_class}">
                    <h3>Current Ratio</h3>
                    <div class="value">{fmt_ratio(current_ratio)}</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                dte_class = get_kpi_class(dte_proxy, "debt_ratio")
                st.markdown(f"""
                <div class="metric-card {dte_class}">
                    <h3>Debt-to-Equity</h3>
                    <div class="value">{fmt_ratio(dte_proxy)}</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="metric-card neutral">
                    <h3>Total Equity</h3>
                    <div class="value">{fmt_money(equity_val)}</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div class="metric-card neutral">
                    <h3>Total Assets</h3>
                    <div class="value">{fmt_money(assets_val)}</div>
                </div>
                """, unsafe_allow_html=True)

        # Balance sheet components
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Balance Sheet Components</div>', unsafe_allow_html=True)
        if not df_scope.empty:
            bal = scope_agg_series(df_scope, ["total_assets", "total_liabilities", "equity"])
            balm = bal.melt("period_end", var_name="Component", value_name="Value")
            fig4 = px.bar(balm, x="period_end", y="Value", color="Component", barmode="stack")
            fig4 = style_fig(fig4)
            fig4.update_layout(height=400)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No data available for the selected scope.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- Cash Flow ----------------
    elif dashboard_type == "Cash Flow":
        if not df_scope.empty:
            col1, col2, col3, col4 = st.columns(4)

            srt = df_scope.sort_values(["Year", "Quarter"])
            fcf_cur = srt["fcf"].iloc[-1] if len(srt) > 0 else np.nan
            fcf_prev = srt["fcf"].iloc[-2] if len(srt) > 1 else np.nan
            fcf_change = pct_change(fcf_cur, fcf_prev)
            fcf_margin = latest.get("fcf_margin", np.nan)
            cfo_val = latest.get("cfo", np.nan)
            capex_val = latest.get("capex", np.nan)

            with col1:
                fcf_class = get_kpi_class(fcf_change, "growth")
                st.markdown(f"""
                <div class="metric-card {fcf_class}">
                    <h3>Free Cash Flow</h3>
                    <div class="value">{fmt_money(fcf_cur)}</div>
                    <div class="delta {'positive' if (fcf_change or 0) >= 0 else 'negative'}">
                        {f"{fcf_change*100:+.1f}%" if pd.notna(fcf_change) else "–"}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                fcf_margin_class = get_kpi_class(fcf_margin, "margin")
                st.markdown(f"""
                <div class="metric-card {fcf_margin_class}">
                    <h3>FCF Margin</h3>
                    <div class="value">{fmt_pct(fcf_margin)}</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="metric-card neutral">
                    <h3>Operating CF</h3>
                    <div class="value">{fmt_money(cfo_val)}</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div class="metric-card neutral">
                    <h3>CapEx</h3>
                    <div class="value">{fmt_money(capex_val)}</div>
                </div>
                """, unsafe_allow_html=True)

        # Cash flow trend
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Cash Flow Analysis</div>', unsafe_allow_html=True)
        if not df_scope.empty:
            ocf = scope_agg_series(df_scope, ["cfo", "fcf"])
            ocf_melted = ocf.melt("period_end", var_name="Cash Flow Type", value_name="Value")
            fig7 = px.line(ocf_melted, x="period_end", y="Value", color="Cash Flow Type", markers=True)
            fig7.update_traces(marker=dict(size=6), line=dict(width=3))
            fig7 = style_fig(fig7)
            fig7.update_layout(height=400)
            st.plotly_chart(fig7, use_container_width=True)
        else:
            st.info("No data available for the selected scope.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- Ratios & Valuation ----------------
    else:
        val = mock_valuation(PANEL[PANEL["sector"] == sector])
        latest_sector = sector_latest_df(sector)[["company", "roe"]].copy()
        val = val.merge(latest_sector, on="company", how="left")

        col1, col2, col3, col4 = st.columns(4)

        def pick_val(value_series, percent=False):
            if company != "All" and not val[val["company"] == company].empty:
                v = val[val["company"] == company][value_series].iloc[0]
            else:
                v = val[value_series].median()
            if pd.isna(v):
                return "–"
            return f"{v*100:.2f}%" if percent else f"{v:.2f}x"

        with col1:
            # P/E (qualitative banding)
            txt = pick_val("pe")
            try:
                pe_val = float(txt.replace("x", "")) if txt != "–" else np.nan
            except Exception:
                pe_val = np.nan
            if pd.notna(pe_val):
                if pe_val < 15: pe_class = "excellent"
                elif pe_val < 20: pe_class = "positive"
                elif pe_val < 25: pe_class = "neutral"
                elif pe_val < 35: pe_class = "warning"
                else: pe_class = "negative"
            else:
                pe_class = "neutral"
            st.markdown(f"""
            <div class="metric-card {pe_class}">
                <h3>P/E Ratio</h3>
                <div class="value">{txt}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            txt = pick_val("peg")
            try:
                peg_val = float(txt.replace("x", "")) if txt != "–" else np.nan
            except Exception:
                peg_val = np.nan
            if pd.notna(peg_val):
                if peg_val < 0.8: peg_class = "excellent"
                elif peg_val < 1.0: peg_class = "positive"
                elif peg_val < 1.5: peg_class = "neutral"
                elif peg_val < 2.0: peg_class = "warning"
                else: peg_class = "negative"
            else:
                peg_class = "neutral"
            st.markdown(f"""
            <div class="metric-card {peg_class}">
                <h3>PEG Ratio</h3>
                <div class="value">{txt}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            txt = pick_val("dividend_yield", percent=True)
            try:
                div_val = float(txt.replace("%", "")) if txt != "–" else np.nan
            except Exception:
                div_val = np.nan
            if pd.notna(div_val):
                if div_val > 4: div_class = "excellent"
                elif div_val > 2.5: div_class = "positive"
                elif div_val > 1: div_class = "neutral"
                elif div_val > 0.5: div_class = "warning"
                else: div_class = "negative"
            else:
                div_class = "neutral"
            st.markdown(f"""
            <div class="metric-card {div_class}">
                <h3>Dividend Yield</h3>
                <div class="value">{txt}</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            txt = pick_val("pb")
            try:
                pb_val = float(txt.replace("x", "")) if txt != "–" else np.nan
            except Exception:
                pb_val = np.nan
            if pd.notna(pb_val):
                if pb_val < 1.5: pb_class = "excellent"
                elif pb_val < 2.5: pb_class = "positive"
                elif pb_val < 4: pb_class = "neutral"
                elif pb_val < 6: pb_class = "warning"
                else: pb_class = "negative"
            else:
                pb_class = "neutral"
            st.markdown(f"""
            <div class="metric-card {pb_class}">
                <h3>P/B Ratio</h3>
                <div class="value">{txt}</div>
            </div>
            """, unsafe_allow_html=True)

        # Scatter: P/E vs ROE
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">P/E vs ROE Analysis</div>', unsafe_allow_html=True)
        fig11 = px.scatter(val, x="roe", y="pe", text="company", size_max=15)
        fig11.update_traces(textposition="top center", marker=dict(size=12))
        fig11 = style_fig(fig11)
        fig11.update_layout(height=400, xaxis_tickformat=".0%", xaxis_title="ROE", yaxis_title="P/E")
        st.plotly_chart(fig11, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# PAGE 2 — DATA TABLE
# =====================================================
elif st.session_state.current_page == "Data Table":
    st.markdown("## Financial Data Table")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        available_years = sorted(df_scope["Year"].unique()) if not df_scope.empty else []
        selected_year = st.selectbox("Filter by Year", options=["All Years"] + available_years, key="year_filter")
    with col2:
        available_quarters = sorted(df_scope["Quarter"].unique()) if not df_scope.empty else []
        selected_quarter = st.selectbox("Filter by Quarter", options=["All Quarters"] + [f"Q{q}" for q in available_quarters], key="quarter_filter")
    with col3:
        selected_columns = st.multiselect(
            "Select Columns",
            options=df_scope.columns.tolist() if not df_scope.empty else [],
            default=['company', 'Year', 'Quarter', 'revenue', 'net_income', 'total_assets', 'equity'],
            key="column_select"
        )
    with col4:
        pass

    display_df = df_scope.copy()
    if not df_scope.empty:
        if selected_year != "All Years":
            display_df = display_df[display_df["Year"] == selected_year]
        if selected_quarter != "All Quarters":
            quarter_num = int(selected_quarter[1])
            display_df = display_df[display_df["Quarter"] == quarter_num]
        if selected_columns:
            display_df = display_df[selected_columns]

    if not display_df.empty:
        monetary_cols = [
            'revenue', 'cogs', 'gross_profit', 'operating_income', 'net_income',
            'total_assets', 'total_liabilities', 'equity', 'current_assets',
            'current_liabilities', 'cfo', 'capex', 'fcf', 'cash'
        ]
        formatted_df = display_df.copy()
        for col in monetary_cols:
            if col in formatted_df.columns:
                formatted_df[col] = formatted_df[col].apply(lambda x: fmt_money(x) if pd.notna(x) else "-")

        st.dataframe(formatted_df, use_container_width=True, height=600, hide_index=True)

        st.info(
            f"Showing {len(display_df)} records "
            f"{'' if selected_year == 'All Years' else f'for {selected_year}'} "
            f"{'' if selected_quarter == 'All Quarters' else selected_quarter}"
        )

        # Export
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"financial_data_{sector}_{company}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No data available for the selected criteria.")

# =====================================================
# PAGE 3 — INSIGHTS
# =====================================================
else:  # Insights
    st.markdown("## Financial Insights & Analysis")

    col1, col2 = st.columns(2)
    with col1:
        insight_topic = st.selectbox(
            "Analysis Topic",
            ["Profitability", "Financial Standing", "Cash Flow", "Ratios & Valuation"],
            key="insight_topic"
        )
    with col2:
        analysis_scope = st.selectbox(
            "Analysis Scope",
            ["Sector-wide Analysis", "Company Analysis"],
            key="analysis_scope"
        )

    if insight_topic == "Profitability":
        st.markdown("### Profitability Insights")
        if analysis_scope == "Sector-wide Analysis":
            sector_data = sector_latest_df(sector)
            if not sector_data.empty:
                sector_data["profit_margin"] = sector_data["net_income"] / sector_data["revenue"]
                avg_margin = sector_data["profit_margin"].mean()
                best_performer = sector_data.loc[sector_data["profit_margin"].idxmax()]
                st.markdown(f"""
                <div class="insight-box">
                    <div class="insight-text">
                        <strong>Sector Analysis:</strong> The {sector} sector shows an average profit margin of
                        <strong>{avg_margin:.1%}</strong>. <strong>{best_performer['company']}</strong> leads with
                        <strong>{best_performer['profit_margin']:.1%}</strong> and net income of
                        <strong>{fmt_money(best_performer['net_income'])}</strong>.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("#### Profitability Rankings")
                st.dataframe(
                    sector_data[["company", "profit_margin", "net_income"]].sort_values("profit_margin", ascending=False),
                    use_container_width=True
                )
        else:
            if not df_scope.empty and company != "All":
                recent_data = df_scope.tail(4)
                if len(recent_data) > 1:
                    current_margin = recent_data["net_margin"].iloc[-1]
                    prev_margin = recent_data["net_margin"].iloc[-2]
                    margin_change = current_margin - prev_margin
                    sector_data = sector_latest_df(sector)
                    sector_avg = (sector_data["net_income"] / sector_data["revenue"]).mean()
                    performance = "outperforming" if current_margin > sector_avg else "underperforming"
                    trend = "improving" if margin_change > 0 else "declining"
                    st.markdown(f"""
                    <div class="insight-box">
                        <div class="insight-text">
                            <strong>Company Focus:</strong> <strong>{company}</strong> net margin is
                            <strong>{current_margin:.1%}</strong>, {performance} the sector average of
                            <strong>{sector_avg:.1%}</strong>. Trend is <strong>{trend}</strong>
                            ({'+' if margin_change > 0 else ''}{margin_change:.1%} vs previous quarter).
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    elif insight_topic == "Financial Standing":
        st.markdown("### Financial Standing Insights")
        if analysis_scope == "Sector-wide Analysis":
            sector_data = sector_latest_df(sector)
            if not sector_data.empty:
                avg_dte = (sector_data["total_liabilities"] / sector_data["equity"]).mean()
                avg_current_ratio = sector_data["current_ratio"].mean()
                strongest_balance = sector_data.loc[sector_data["equity"].idxmax()]
                st.markdown(f"""
                <div class="insight-box">
                    <div class="insight-text">
                        <strong>Balance Sheet Health:</strong> {sector} sector average D/E is <strong>{avg_dte:.2f}</strong>
                        and current ratio is <strong>{avg_current_ratio:.2f}</strong>. <strong>{strongest_balance['company']}</strong>
                        shows the highest equity at <strong>{fmt_money(strongest_balance['equity'])}</strong>.
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            if not df_scope.empty and company != "All":
                current_dte = latest.get("debt_to_equity", np.nan)
                current_ratio = latest.get("current_ratio", np.nan)
                dte_risk = "High" if current_dte > 2 else "Moderate" if current_dte > 1 else "Low"
                liquidity_health = "Strong" if current_ratio > 1.5 else "Adequate" if current_ratio > 1 else "Weak"
                st.markdown(f"""
                <div class="insight-box">
                    <div class="insight-text">
                        <strong>Financial Position:</strong> <strong>{company}</strong> shows
                        <strong>{dte_risk.lower()}</strong> leverage risk (D/E: {fmt_ratio(current_dte)}) and
                        <strong>{liquidity_health.lower()}</strong> liquidity (Current Ratio: {fmt_ratio(current_ratio)}).
                    </div>
                </div>
                """, unsafe_allow_html=True)

    elif insight_topic == "Cash Flow":
        st.markdown("### Cash Flow Insights")
        if analysis_scope == "Sector-wide Analysis":
            sector_data = sector_latest_df(sector)
            if not sector_data.empty:
                sector_data["fcf_margin"] = sector_data["fcf"] / sector_data["revenue"]
                avg_fcf_margin = sector_data["fcf_margin"].mean()
                best_cash_gen = sector_data.loc[sector_data["fcf"].idxmax()]
                st.markdown(f"""
                <div class="insight-box">
                    <div class="insight-text">
                        <strong>Cash Generation:</strong> {sector} sector average FCF margin is
                        <strong>{avg_fcf_margin:.1%}</strong>. <strong>{best_cash_gen['company']}</strong>
                        leads on absolute FCF at <strong>{fmt_money(best_cash_gen['fcf'])}</strong>.
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            if not df_scope.empty and company != "All":
                recent_fcf = df_scope.tail(4)["fcf"]
                if len(recent_fcf) > 1:
                    fcf_trend = "positive" if recent_fcf.iloc[-1] > recent_fcf.iloc[-2] else "negative"
                    avg_fcf = recent_fcf.mean()
                    st.markdown(f"""
                    <div class="insight-box">
                        <div class="insight-text">
                            <strong>Cash Flow Trend:</strong> <strong>{company}</strong> shows a
                            <strong>{fcf_trend}</strong> FCF trend with average quarterly FCF of
                            <strong>{fmt_money(avg_fcf)}</strong>.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    else:  # Ratios & Valuation
        st.markdown("### Valuation Insights")
        val = mock_valuation(PANEL[PANEL["sector"] == sector])
        if analysis_scope == "Sector-wide Analysis":
            avg_pe = val["pe"].mean()
            avg_pb = val["pb"].mean()
            st.markdown(f"""
            <div class="insight-box">
                <div class="insight-text">
                    <strong>Valuation Overview:</strong> {sector} trades at an average P/E of
                    <strong>{avg_pe:.1f}x</strong> and P/B of <strong>{avg_pb:.1f}x</strong>.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            if company != "All" and not val[val["company"] == company].empty:
                company_val = val[val["company"] == company].iloc[0]
                sector_pe_avg = val["pe"].mean()
                valuation_vs_peers = "premium" if company_val["pe"] > sector_pe_avg else "discount"
                st.markdown(f"""
                <div class="insight-box">
                    <div class="insight-text">
                        <strong>Valuation Position:</strong> <strong>{company}</strong> trades at a
                        <strong>{valuation_vs_peers}</strong> vs peers (P/E {company_val['pe']:.1f}x vs
                        sector {sector_pe_avg:.1f}x).
                    </div>
                </div>
                """, unsafe_allow_html=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-muted); font-size: 0.9rem; margin-top: 2rem;">
    Financial Insights Hub • Advanced Analytics Dashboard<br>
    Real-time data integration with comprehensive financial analysis
</div>
""", unsafe_allow_html=True)
st.markdown("""
<style>
/* Fix clipped text in selectboxes (and keep a comfy height) */
.stSelectbox [data-baseweb="select"]{
  min-height: 46px !important;          /* ~2.875rem */
}
.stSelectbox [data-baseweb="select"] > div { 
  align-items: center !important;        /* vertically center the text */
  padding-top: .55rem !important;
  padding-bottom: .55rem !important;
}

/* Make sure any text inside gets enough vertical room */
.stSelectbox [data-baseweb="select"] * {
  line-height: 1.35 !important;          /* prevents descender clipping */
}

/* If you keep your earlier selector, tame it a bit */
.stSelectbox > div > div {
  font-size: 1rem !important;            /* or 1.05rem */
  padding: .6rem .9rem !important;       /* reduce padding a touch */
  min-height: 2.75rem !important;        /* consistent with line-height */
}
</style>
""", unsafe_allow_html=True)

