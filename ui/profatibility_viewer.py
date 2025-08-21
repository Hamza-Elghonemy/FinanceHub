# ---- ai_profitability_views.py ----
import json
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Deloitte-ish palette (kept consistent with your app)
DELOITTE_PRIMARY = "#86BC25"
DELOITTE_BLACK   = "#111111"
DELOITTE_BLUE    = "#009FDA"
COLORWAY = [DELOITTE_PRIMARY, "#2E2E2E", DELOITTE_BLUE, "#6C757D", "#8E8E8E"]

def _style_fig(fig):
    # uses your theme if you already set CSS variables (safe defaults otherwise)
    plot_bg = "rgba(255,255,255,1)"
    paper_bg = "rgba(255,255,255,1)"
    try:
        theme = st.session_state.get("theme", "light")
        plot_bg = "rgba(255,255,255,1)" if theme == "light" else "rgba(14,17,22,1)"
        paper_bg = "rgba(255,255,255,1)" if theme == "light" else "rgba(11,14,18,1)"
        font_color = "#111" if theme == "light" else "#EAEAEA"
        grid = "#E6E9ED" if theme == "light" else "#20252b"
        axis = "#2E2E2E" if theme == "light" else "#cfd2d6"
    except Exception:
        font_color = "#111"; grid = "#E6E9ED"; axis = "#2E2E2E"

    fig.update_layout(
        colorway=COLORWAY,
        hovermode="x unified",
        margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor=plot_bg, paper_bgcolor=paper_bg,
        font=dict(color=font_color, size=13),
        legend=dict(title=None, orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    fig.update_xaxes(showgrid=True, gridcolor=grid, linecolor=axis, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=grid, linecolor=axis, zeroline=False)
    return fig

def _fmt_money(x):
    if x is None or pd.isna(x): return "-"
    x = float(x)
    a = abs(x)
    if a >= 1e12: return f"${x/1e12:.2f}T"
    if a >= 1e9:  return f"${x/1e9:.2f}B"
    if a >= 1e6:  return f"${x/1e6:.2f}M"
    return f"${x:,.0f}"

def _fmt_pct(x, decimals=1):
    return "-" if (x is None or pd.isna(x)) else f"{x*100:.{decimals}f}%"

# ------------------------------------------------------------------
# LOADERS
# ------------------------------------------------------------------
def load_company_json(path_or_dict):
    """Load company JSON (quarters list with kpis/insights)."""
    data = path_or_dict
    if not isinstance(path_or_dict, dict):
        data = json.loads(Path(path_or_dict).read_text(encoding="utf-8"))
    assert "quarters" in data, "Company JSON must contain 'quarters'."
    return data

def load_sector_json(path_or_dict):
    """Load sector JSON (companies list with annual/kpis/insights)."""
    data = path_or_dict
    if not isinstance(path_or_dict, dict):
        txt = Path(path_or_dict).read_text(encoding="utf-8")
        # some files might start without outer {} – patch if needed
        data = json.loads(txt if txt.strip().startswith("{") else "{"+txt.strip().strip(",")+"}")
    assert "companies" in data, "Sector JSON must contain 'companies'."
    return data

# ------------------------------------------------------------------
# SMALL BUILDERS
# ------------------------------------------------------------------
def _kpi_tile(title, value, sub=None):
    sub = sub or ""
    st.markdown(
        f"""
        <div class="metric-card" style="background:var(--block-bg,#fff);border:1px solid var(--border,rgba(0,0,0,.08));border-radius:16px;padding:1rem;">
          <h3 style="margin:0 0 .35rem 0;color:var(--text-color,#111);font:600 12px/1.1 system-ui;letter-spacing:.4px;text-transform:uppercase;">{title}</h3>
          <div class="value" style="font:800 28px/1 system-ui;color:var(--text-color,#111)">{value}</div>
          <div class="delta neutral" style="color:var(--muted,#666);font-weight:600;margin-top:.25rem">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _kpi_compare_chart(name, value, avg, is_pct=False, height=220):
    df = pd.DataFrame({
        "Label": [name, "Average"],
        "Value": [value, avg]
    })
    yfmt = ".0%" if is_pct else "$,.0f"
    fig = px.bar(
        df, x="Label", y="Value",
        text="Value",
    )
    fig.update_traces(texttemplate="%{y:"+yfmt+"}", textposition="outside")
    fig.update_layout(height=height, xaxis_title=None, yaxis=dict(tickformat=yfmt))
    return _style_fig(fig)

# ------------------------------------------------------------------
# VIEWS
# ------------------------------------------------------------------
def render_company_only(company_json, company_name="Company", ticker="TCKR"):
    """
    Show KPIs WITHOUT averages + charts using the per-quarter 'charts' data.
    Insights section uses **company_insights** only.
    """
    data = load_company_json(company_json)
    quarters = data.get("quarters", [])
    if not quarters:
        st.info("No quarters in company file."); return

    # Latest quarter (keep order as given if already sorted)
    latest = quarters[-1]
    k = latest.get("kpis", {})
    ins = latest.get("insights", {})
    c1,c2,c3,c4 = st.columns(4)

    with c1: _kpi_tile("Net Income", _fmt_money(k.get("Net Income")))
    with c2: _kpi_tile("Operating Margin %", _fmt_pct(k.get("Operating Margin %")))
    with c3: _kpi_tile("ROE", _fmt_pct(k.get("Return on Equity (ROE)")))
    with c4:
        # Optional: Revenue (from chart metrics this quarter)
        rev = latest.get("charts",{}).get("Revenue & Gross Profit",{}).get("metrics",{}).get("Revenue")
        _kpi_tile("Revenue", _fmt_money(rev))

    # Build across-quarter time series from charts.metrics
    def _safe_get(q, block, metric):
        return q.get("charts",{}).get(block,{}).get("metrics",{}).get(metric)

    ts = []
    for q in quarters:
        qlbl = q.get("quarter")
        ts.append({
            "Quarter": qlbl,
            "Revenue": _safe_get(q, "Revenue & Gross Profit", "Revenue"),
            "Gross Profit": _safe_get(q, "Revenue & Gross Profit", "Gross Profit"),
            "Operating Income": _safe_get(q, "Revenue, Operating Income, Net Income", "Operating Income"),
            "Net Income": _safe_get(q, "Revenue, Operating Income, Net Income", "Net Income"),
        })
    ts = pd.DataFrame(ts).dropna(how="all", subset=["Revenue","Gross Profit","Operating Income","Net Income"])

    # Trend: Revenue & GP
    st.markdown('<div class="card"><div class="section-title">Revenue & Gross Profit (Trend)</div>', unsafe_allow_html=True)
    lf = ts.melt("Quarter", ["Revenue","Gross Profit"], var_name="Metric", value_name="Value")
    fig1 = px.line(lf, x="Quarter", y="Value", color="Metric", markers=True)
    fig1.update_traces(marker=dict(size=6), line=dict(width=3),
                       hovertemplate="<b>%{x}</b><br>%{legendgroup}: %{y:$,.0f}<extra></extra>")
    st.plotly_chart(_style_fig(fig1).update_layout(height=380, xaxis_title=None, yaxis=dict(tickformat="$,.0f")), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bars: Revenue → Operating Income → Net Income (latest through time)
    st.markdown('<div class="card"><div class="section-title">Revenue vs Operating Income vs Net Income</div>', unsafe_allow_html=True)
    bf = ts.melt("Quarter", ["Revenue","Operating Income","Net Income"], var_name="Metric", value_name="Value")
    fig2 = px.bar(bf, x="Quarter", y="Value", color="Metric", barmode="group")
    fig2.update_traces(hovertemplate="<b>%{x}</b><br>%{legendgroup}: %{y:$,.0f}<extra></extra>")
    st.plotly_chart(_style_fig(fig2).update_layout(height=380, xaxis_title=None, yaxis=dict(tickformat="$,.0f")), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Insight — company_insights ONLY
    st.markdown(f"""
    <div class="ai-insight-box" style="background:linear-gradient(135deg,var(--primary-color, {DELOITTE_PRIMARY})10, var(--secondary-color, {DELOITTE_BLUE})10); border-radius:16px; padding:1.25rem; border-left:6px solid var(--primary-color,{DELOITTE_PRIMARY});">
      <h4 style="margin:0 0 .5rem 0;">💡 {company_name} ({ticker}) — Company Insight</h4>
      <p style="margin:0; line-height:1.6;">{ins.get('company_insights','')}</p>
    </div>
    """, unsafe_allow_html=True)

def render_company_vs_sector(company_json, company_name="Company", ticker="TCKR"):
    """
    Ignore JSON charts. For each KPI show a **paired bar** (Value vs Average).
    Insights section uses **comparative_insights** only.
    """
    data = load_company_json(company_json)
    quarters = data.get("quarters", [])
    if not quarters:
        st.info("No quarters in company file."); return
    latest = quarters[-1]
    k = latest.get("kpis", {})
    ins = latest.get("insights", {})

    # Build compare tiles
    st.markdown("#### KPI vs Sector Average")
    cg1, cg2, cg3 = st.columns(3)
    with cg1:
        fig = _kpi_compare_chart("Net Income", k.get("Net Income"), k.get("Net Income Average"), is_pct=False)
        st.plotly_chart(fig, use_container_width=True)
    with cg2:
        fig = _kpi_compare_chart("Operating Margin %", k.get("Operating Margin %"), k.get("Operating Margin % Average"), is_pct=True)
        st.plotly_chart(fig, use_container_width=True)
    with cg3:
        fig = _kpi_compare_chart("ROE", k.get("Return on Equity (ROE)"), k.get("Return on Equity (ROE) Average"), is_pct=True)
        st.plotly_chart(fig, use_container_width=True)

    # Insight — comparative_insights ONLY
    st.markdown(f"""
    <div class="ai-insight-box" style="background:linear-gradient(135deg,var(--primary-color,{DELOITTE_PRIMARY})10, var(--secondary-color,{DELOITTE_BLUE})10); border-radius:16px; padding:1.25rem; border-left:6px solid var(--primary-color,{DELOITTE_PRIMARY});">
      <h4 style="margin:0 0 .5rem 0;">🤝 {company_name} vs Sector</h4>
      <p style="margin:0; line-height:1.6;">{ins.get('comparative_insights','')}</p>
    </div>
    """, unsafe_allow_html=True)

def render_sector_analysis(sector_json, focus_symbol="JNJ"):
    """
    Parse JNJ_Profitability_Sector_analysis.json and visualize cross-company metrics.
    Shows: Net Income, Operating Margin %, ROE, and FCF across all companies,
    plus textual insights for the focus company.
    """
    data = load_sector_json(sector_json)
    companies = data.get("companies", [])
    if not companies:
        st.info("No companies found in sector file."); return

    # Build one row per company with a few key fields
    rows = []
    for c in companies:
        info = c.get("company_info", {})
        sym  = info.get("symbol")
        name = info.get("name", sym)
        ann  = c.get("annual", {})
        prof = ann.get("profitability", {})
        kpis = c.get("kpis", {})
        ratios = ann.get("ratios", {})
        rows.append(dict(
            Symbol=sym,
            Company=name,
            Revenue=prof.get("revenue"),
            NetIncome=(kpis.get("Net Income",{}) or {}).get("value", prof.get("net_income")),
            OpMargin=kpis.get("Operating Margin %", ratios.get("ProfitMargin")),
            ROE=kpis.get("Return on Equity (ROE)", ratios.get("ReturnOnEquity")),
            FCF=(kpis.get("Free Cash Flow",{}) or {}).get("value"),
            FCFMargin=kpis.get("FCF Margin", None),
        ))
    df = pd.DataFrame(rows).dropna(subset=["Company"])

    # === Charts
    st.markdown("#### Sector Snapshot")
    c1,c2 = st.columns(2)
    with c1:
        fig = px.bar(df.sort_values("NetIncome", ascending=False), x="Company", y="NetIncome", title="Net Income")
        fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:$,.0f}<extra></extra>")
        st.plotly_chart(_style_fig(fig).update_layout(height=360, xaxis_title=None, yaxis=dict(tickformat="$,.0f")), use_container_width=True)
    with c2:
        fig = px.bar(df.sort_values("OpMargin", ascending=False), x="Company", y="OpMargin", title="Operating Margin %")
        fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:.1%}<extra></extra>")
        st.plotly_chart(_style_fig(fig).update_layout(height=360, xaxis_title=None, yaxis_tickformat=".0%"), use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        fig = px.bar(df.sort_values("ROE", ascending=False), x="Company", y="ROE", title="Return on Equity (ROE)")
        fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:.1%}<extra></extra>")
        st.plotly_chart(_style_fig(fig).update_layout(height=360, xaxis_title=None, yaxis_tickformat=".0%"), use_container_width=True)
    with c4:
        base = "FCFMargin" if df["FCFMargin"].notna().any() else "FCF"
        ttl = "FCF Margin" if base == "FCFMargin" else "Free Cash Flow"
        yfmt = ".0%" if base == "FCFMargin" else "$,.0f"
        fig = px.bar(df.sort_values(base, ascending=False), x="Company", y=base, title=ttl)
        fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:"+yfmt+"}<extra></extra>")
        st.plotly_chart(_style_fig(fig).update_layout(height=360, xaxis_title=None, yaxis=dict(tickformat=yfmt)), use_container_width=True)

    # === Focus company insights (profitability/standing/cash_flow/ratios)
    focus = next((c for c in companies if c.get("company_info",{}).get("symbol")==focus_symbol), None)
    if focus:
        info = focus.get("company_info", {})
        ins  = focus.get("insights", {})
        st.markdown(f"""
        <div class="ai-insight-box" style="background:linear-gradient(135deg,var(--primary-color,{DELOITTE_PRIMARY})10,var(--secondary-color,{DELOITTE_BLUE})10); border-radius:16px; padding:1.25rem; border-left:6px solid var(--primary-color,{DELOITTE_PRIMARY}); margin-top:.5rem;">
          <h4 style="margin:.25rem 0 .75rem 0;">🔎 {info.get('name', focus_symbol)} ({focus_symbol}) — Insights</h4>
          <ul style="margin:0; padding-left:1.2rem; line-height:1.6;">
            <li><strong>Profitability:</strong> {ins.get('profitability','–')}</li>
            <li><strong>Financial Standing:</strong> {ins.get('financial_standing','–')}</li>
            <li><strong>Cash Flow:</strong> {ins.get('cash_flow','–')}</li>
            <li><strong>Ratios:</strong> {ins.get('ratios','–')}</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------
# EXAMPLE USAGE in your app
# ------------------------------------------------------------------
def render_profitability_from_json(mode: str):
    """
    mode ∈ {"company_only", "company_vs_sector", "sector"}.
    Change file paths to your actual locations.
    """
    company_file = "/mnt/data/JNJ_Profitability_Company_analysis.json"
    sector_file  = "/mnt/data/JNJ_Profitability_Sector_analysis.json"

    if mode == "company_only":
        render_company_only(company_file, company_name="Johnson & Johnson", ticker="JNJ")

    elif mode == "company_vs_sector":
        render_company_vs_sector(company_file, company_name="Johnson & Johnson", ticker="JNJ")

    else:  # "sector"
        render_sector_analysis(sector_file, focus_symbol="JNJ")
