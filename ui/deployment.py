# streamlit_app.py
# Financial Insights Hub — Enhanced with Real Data & AI Integration
# Palette: purple/teal gradient + light/dark theme CSS

from __future__ import annotations
import io
import json
import subprocess
import sys
import hashlib
from datetime import datetime
from pathlib import Path
from profatibility_viewer import render_profitability_from_json
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

# Theme state management
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Initialize session state for programmatic selections
if "selected_sector" not in st.session_state:
    st.session_state.selected_sector = None
if "selected_company" not in st.session_state:
    st.session_state.selected_company = None

# -----------------------------
# Color palette (purple/teal set)
# -----------------------------
DELOITTE_PRIMARY = "#86BC25"
DELOITTE_SECONDARY = "#cef6ce"
DELOITTE_ACCENT = "#f093fb"
COLORWAY = [
    "#667eea", "#764ba2", "#f093fb",
    "#f5576c", "#11998e", "#38ef7d",
    "#a8edea", "#fed6e3"
]

# -----------------------------
# Enhanced CSS Styling with Dark Theme
# -----------------------------
def apply_custom_css():
    theme = st.session_state.theme

    if theme == "light":
        st.markdown("""
        <style>
        :root {
            --primary-color: #86BC25;
            --secondary-color: #cef6ce;
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
            --secondary-color: #cef6ce;
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

    # Enhanced CSS with AI insights styling
    st.markdown("""
    <style>
    /* Global app background and text colors */
    .stApp {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
    }

    /* Main content area */
    .main .block-container {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important; /* scoped */
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--bg-primary) !important;
        border-right: 2px solid var(--border-color) !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stSidebar"] > div {
        background: var(--bg-primary) !important;
    }

    /* Sidebar text colors (scoped to sidebar only) */
    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }

    /* Theme toggle button in sidebar */
    .theme-toggle-sidebar {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        font-size: 16px !important;
        cursor: pointer !important;
        box-shadow: var(--shadow) !important;
        margin: 10px auto !important;
        display: block !important;
    }

    .theme-toggle-sidebar:hover {
        transform: scale(1.1) !important;
        box-shadow: var(--shadow-lg) !important;
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
        color: var(--text-primary) !important;
    }
    .main-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        color: var(--text-secondary) !important;
    }

    /* Enhanced metric cards */
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
        color: var(--text-primary);
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
        color: var(--text-secondary) !important;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card .value {
        color: var(--text-primary) !important;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
    }
    .metric-card .delta { 
        font-size: 0.9rem; 
        font-weight: 600; 
        margin-top: .5rem; 
    }
    .delta.positive { color: #10B981 !important; }
    .delta.negative { color: #EF4444 !important; }

    /* AI Insight boxes - fixed gradient tokens using color-mix() */
    .ai-insight-box {
        background: linear-gradient(
            135deg,
            color-mix(in srgb, var(--primary-color) 15%, transparent),
            color-mix(in srgb, var(--secondary-color) 15%, transparent)
        );
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid var(--primary-color);
        position: relative;
        color: var(--text-primary) !important;
    }
    
    .ai-insight-box::before {
        content: "🤖 AI";
        position: absolute;
        top: 0.5rem;
        right: 1rem;
        background: var(--primary-color);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: 600;
    }

    .ai-insight-box * {
        color: var(--text-primary) !important;
    }

    /* Chart container */
    .chart-container {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
        position: relative;
        color: var(--text-primary);
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
        color: var(--text-primary) !important;
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0 0 1.0rem 0;
        display: flex;
        align-items: center;
        gap: .5rem;
    }

    /* Dataframe styling */
    .stDataFrame { 
        border-radius: 16px !important; 
        overflow: hidden !important; 
        box-shadow: var(--shadow-lg) !important; 
        border: 1px solid var(--border-color) !important; 
    }
    .stDataFrame table { 
        background: var(--bg-primary) !important; 
    }
    .stDataFrame thead th {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
        color: white !important; 
        font-weight: 700 !important; 
        padding: 1rem !important;
        border: none !important; 
        font-size: .95rem !important; 
        letter-spacing: .5px !important;
    }
    .stDataFrame tbody td {
        background: var(--bg-primary) !important; 
        color: var(--text-primary) !important;
        padding: 1rem !important; 
        border-bottom: 1px solid var(--border-color) !important;
    }
    .stDataFrame tbody tr:hover { 
        background: var(--bg-tertiary) !important; 
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
        color: white !important; 
        border: none !important; 
        border-radius: 12px !important;
        padding: .75rem 2rem !important; 
        font-weight: 600 !important;
        box-shadow: var(--shadow) !important; 
        transition: all .3s ease !important;
    }
    .stButton > button:hover { 
        transform: translateY(-2px) !important; 
        box-shadow: var(--shadow-lg) !important; 
    }

    /* Generate AI Insights button */
    .generate-button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        box-shadow: var(--shadow) !important;
        transition: all 0.3s ease !important;
        margin: 1rem 0 !important;
    }
    
    .generate-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
    }

    /* Input styling */
    .stSelectbox > div > div {
        background: var(--bg-primary) !important; 
        border: 2px solid var(--border-color) !important;
        border-radius: 12px !important; 
        color: var(--text-primary) !important;
        font-size: 1rem !important; 
        padding: .6rem .9rem !important; 
        min-height: 2.75rem !important;
    }
    .stSelectbox label { 
        font-size: 1rem !important; 
        font-weight: 600 !important; 
        color: var(--text-primary) !important;  /* FIXED (was #0000) */
    }

    /* --- Streamlit selectbox text visibility fixes --- */
    .stSelectbox [data-baseweb="select"] > div {
      color: var(--text-primary) !important;
      background: var(--bg-primary) !important;
      
        padding-top: 0.1rem !important;
        padding-bottom: 0.1rem !important;
    }
    .stSelectbox [data-baseweb="select"] input {
      color: var(--text-primary) !important;
      -webkit-text-fill-color: var(--text-primary) !important;

      
        padding-top: 0.1rem !important;
        padding-bottom: 0.1rem !important;
    }
    .stSelectbox [data-baseweb="select"] div[aria-hidden="true"] {
      color: var(--text-secondary) !important; /* placeholder */
    }
    .stSelectbox svg {
      fill: var(--text-primary) !important;
      color: var(--text-primary) !important;
      opacity: .85;
    }
    /* Dropdown menu (options list) */
    div[role="listbox"] [role="option"] {
      color: var(--text-primary) !important;
      background: var(--bg-primary) !important;
    }

    /* Multiselect styling */
    .stMultiSelect > div > div {
        background: var(--bg-primary) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }
    .stMultiSelect label {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }
    /* Apply the same BaseWeb fixes for multiselect */
    .stMultiSelect [data-baseweb="select"] > div {
      color: var(--text-primary) !important;
      background: var(--bg-primary) !important;
    }
    .stMultiSelect [data-baseweb="select"] input {
      color: var(--text-primary) !important;
      -webkit-text-fill-color: var(--text-primary) !important;
    }
    .stMultiSelect [data-baseweb="select"] div[aria-hidden="true"] {
      color: var(--text-secondary) !important;
    }
    .stMultiSelect svg {
      fill: var(--text-primary) !important;
      color: var(--text-primary) !important;
    }

    /* Metric container tweaks */
    [data-testid="metric-container"] {
        background: var(--bg-primary); 
        border: 1px solid var(--border-color);
        padding: 1rem; 
        border-radius: 12px; 
        box-shadow: var(--shadow);
        color: var(--text-primary);
    }

    /* Insight box - fixed gradient tokens */
    .insight-box {
        background: linear-gradient(
            135deg,
            color-mix(in srgb, var(--primary-color) 20%, transparent),
            color-mix(in srgb, var(--secondary-color) 20%, transparent)
        );
        border: 1px solid var(--border-color);
        border-radius: 16px; 
        padding: 1.5rem; 
        margin: 1rem 0; 
        border-left: 4px solid var(--primary-color);
        color: var(--text-primary);
    }
    .insight-text { 
        color: var(--text-primary) !important; 
        font-size: 1.05rem; 
        font-weight: 500; 
        margin: 0; 
    }

    /* Keep captions secondary */
    .stCaption, .stCaption * { 
        color: var(--text-secondary) !important; 
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
    }

    .streamlit-expanderContent {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
    }

    /* Company selection cards */
    .company-card {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        cursor: pointer;
        color: var(--text-primary) !important;
    }
    .company-card:hover {
        border-color: var(--primary-color);
        transform: translateY(-2px);
        box-shadow: var(--shadow);
    }

    /* Fix for plotly charts toolbar color */
    .js-plotly-plot .plotly .modebar {
        color: var(--text-primary) !important;
    }

    /* Divider color */
    hr {
        border-color: var(--border-color) !important;
    }

    /* Navigation buttons specific styling */
    .stColumns > div > div > button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-weight: 600 !important;
        box-shadow: var(--shadow) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }

    .stColumns > div > div > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    </style>
    """, unsafe_allow_html=True)

apply_custom_css()


# -----------------------------
# Enhanced Data Loading Functions with Real JSON Data
# -----------------------------
@st.cache_data(show_spinner=True)
def load_real_financial_data() -> tuple[pd.DataFrame, dict[str, dict[str, str]]]:
    """Load financial data from the combined JSON file with proper structure parsing."""
    try:
        # Get the project root directory
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        data_file = project_root / "data" / "combined_financial_data_yearly_ratios.json"
        
        if not data_file.exists():
            st.error(f"Data file not found: {data_file}")
            return pd.DataFrame(), {}
        
        with open(data_file, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        
        # Define sector mapping based on your actual data structure
        sector_map = {
            "Healthcare": {
                "Abbott Laboratories": "ABT",
                "CVS Health": "CVS", 
                "Johnson & Johnson": "JNJ",
                "Pfizer": "PFE",
                "UnitedHealth": "UNH"
            },
            "Tech": {
                "Apple": "AAPL",
                "Google": "GOOGL",
                "IBM": "IBM",
                "Meta": "META",
                "Microsoft": "MSFT"
            }
        }
        
        # Convert your nested JSON structure to DataFrame
        rows = []
        
        for sector_name, sector_data in all_data.items():
            if sector_data:  # sector_data is a list
                for company_block in sector_data:
                    for ticker, company_data_list in company_block.items():
                        # Find company name from ticker
                        company_name = None
                        for comp_name, comp_ticker in sector_map.get(sector_name, {}).items():
                            if comp_ticker == ticker:
                                company_name = comp_name
                                break
                        
                        if not company_name:
                            company_name = ticker  # Use ticker as fallback
                        
                        # Process each year's data
                        for year_data in company_data_list:
                            for year_str, quarters_data in year_data.items():
                                if year_str == "ratios":
                                    continue  # Skip ratios for now
                                
                                try:
                                    year = int(year_str)
                                except (ValueError, TypeError):
                                    continue
                                
                                # quarters_data is a list of quarter objects
                                if isinstance(quarters_data, list):
                                    for quarter_block in quarters_data:
                                        for quarter_str, quarter_data in quarter_block.items():
                                            try:
                                                quarter = int(quarter_str)
                                            except (ValueError, TypeError):
                                                continue
                                            
                                            # Extract financial data from nested structure
                                            profitability = quarter_data.get('profitability', {})
                                            balance_sheet = quarter_data.get('balance_sheet', {})
                                            cash_flow = quarter_data.get('cash_flow', {})
                                            
                                            # Create row with actual data from your JSON
                                            row = {
                                                'sector': sector_name,
                                                'company': company_name,
                                                'ticker': ticker,
                                                'Year': year,
                                                'Quarter': quarter,
                                                'period_end': f"{year}-{quarter*3:02d}-30",  # Approximate quarter end
                                                
                                                # Profitability metrics
                                                'revenue': profitability.get('revenue', 0),
                                                'gross_profit': profitability.get('gross_profit', 0),
                                                'operating_income': profitability.get('operating_income', 0),
                                                'net_income': profitability.get('net_income', 0),
                                                
                                                # Balance sheet metrics
                                                'cash': balance_sheet.get('cash_and_equivalents', 0),
                                                'total_assets': balance_sheet.get('total_assets', 0),
                                                'total_liabilities': balance_sheet.get('total_liabilities', 0),
                                                'equity': balance_sheet.get('shareholders_equity', 0),
                                                'current_assets': balance_sheet.get('current_assets', 0),
                                                'current_liabilities': balance_sheet.get('current_liabilities', 0),
                                                
                                                # Cash flow metrics
                                                'cfo': cash_flow.get('operating_cash_flow', 0),
                                                'capex': cash_flow.get('capex', 0),
                                                'fcf': cash_flow.get('free_cash_flow', 0),
                                            }
                                            
                                            # Calculate derived metrics
                                            if row['revenue'] > 0:
                                                row['gross_margin'] = row['gross_profit'] / row['revenue']
                                                row['operating_margin'] = row['operating_income'] / row['revenue']
                                                row['net_margin'] = row['net_income'] / row['revenue']
                                                row['fcf_margin'] = row['fcf'] / row['revenue']
                                            else:
                                                row['gross_margin'] = 0
                                                row['operating_margin'] = 0
                                                row['net_margin'] = 0
                                                row['fcf_margin'] = 0
                                            
                                            if row['current_liabilities'] > 0:
                                                row['current_ratio'] = row['current_assets'] / row['current_liabilities']
                                            else:
                                                row['current_ratio'] = 0
                                            
                                            if row['equity'] > 0:
                                                row['debt_to_equity'] = row['total_liabilities'] / row['equity']
                                                row['roe'] = row['net_income'] / row['equity']
                                            else:
                                                row['debt_to_equity'] = 0
                                                row['roe'] = 0
                                            
                                            # Calculate COGS and earnings quality
                                            row['cogs'] = row['revenue'] - row['gross_profit']
                                            if row['net_income'] > 0:
                                                row['earnings_quality'] = row['cfo'] / row['net_income']
                                            else:
                                                row['earnings_quality'] = 0
                                            
                                            rows.append(row)
        
        if not rows:
            st.error("No valid data found in the JSON file.")
            return pd.DataFrame(), sector_map
        
        df = pd.DataFrame(rows)
        
        # Convert numeric columns
        numeric_cols = [
            'revenue', 'gross_profit', 'operating_income', 'net_income', 'cogs',
            'cash', 'total_assets', 'total_liabilities', 'equity',
            'current_assets', 'current_liabilities',
            'cfo', 'capex', 'fcf',
            'gross_margin', 'operating_margin', 'net_margin', 'fcf_margin',
            'current_ratio', 'debt_to_equity', 'roe', 'earnings_quality'
        ]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        st.success(f"✅ Loaded {len(df)} records from real financial data")
        return df.sort_values(['sector', 'company', 'Year', 'Quarter']), sector_map
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(), {}

# -----------------------------
# AI Insights Integration
# -----------------------------
def generate_ai_insights(ticker: str, analysis_type: str, analysis_scope: str) -> dict | None:
    """Call the LLM analysis script with interactive input simulation."""
    try:
        # Get the path to llm_calling.py in src directory
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        llm_script = project_root / "src" / "llm_calling.py"
        
        if not llm_script.exists():
            st.error(f"llm_calling.py not found at: {llm_script}")
            return None
        
        # Map analysis types to metrics for your LLM script
        metric_mapping = {
            "Profitability": "Profitability",
            "Financial Standing": "Balance Sheet",
            "Cash Flow": "Cash Flow",
        }
        
        # Determine sector based on ticker
        sector_mapping = {
            "AAPL": "Tech", "GOOGL": "Tech", "IBM": "Tech", "META": "Tech", "MSFT": "Tech",
            "JNJ": "Healthcare", "PFE": "Healthcare", "UNH": "Healthcare", "CVS": "Healthcare", "ABT": "Healthcare"
        }

        scope_mapping = {
            "Sector-wide Analysis": "Sector",
            "Company Analysis": "Company",
            "Company vs Sector": "Company vs Sector",
        }

        sector = sector_mapping.get(ticker, "Tech")
        metric = metric_mapping.get(analysis_type, "Profitability")
        scope = scope_mapping.get(analysis_scope,"Company vs Sector")
        
        # Create input simulation for the interactive script
        input_data = f"{sector}\n{ticker}\n{metric}\n{scope}\n"

        # Execute the script with simulated input
        with st.spinner(f"🤖 Generating {analysis_type} insights for {ticker}..."):
            result = subprocess.run(
                [sys.executable, str(llm_script)],
                input=input_data,
                capture_output=True,
                text=True,
                cwd=str(project_root),
                timeout=120
            )
        
        if result.returncode == 0:
            st.success(f"✅ {analysis_type} analysis completed for {ticker}")
            
            # Try to load the generated JSON file
            output_file = project_root / "output" / f"{ticker}_{metric}_{scope}_analysis.json"
            
            if output_file.exists():
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Try to parse as JSON, if it fails return as text
                        try:
                            return json.loads(content)
                        except json.JSONDecodeError:
                            return {"analysis": content, "type": "text"}
                except Exception as e:
                    st.error(f"Error reading output file: {e}")
                    return None
            else:
                st.info("Analysis completed but output file not found yet.")
                return {"status": "completed", "message": "Analysis generated successfully"}
        else:
            error_msg = result.stderr if result.stderr else "Unknown error occurred"
            st.error(f"❌ Error generating insights: {error_msg}")
            return None
            
    except subprocess.TimeoutExpired:
        st.error("⏱️ Analysis timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"❌ Error running analysis: {str(e)}")
        return None

# -----------------------------
# Utility Functions (Enhanced)
# -----------------------------



def add_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """Add calculated ratios - now using real data"""
    return df  # Ratios already calculated in load_real_financial_data

@st.cache_data
def mock_valuation(df_scope: pd.DataFrame) -> pd.DataFrame:
    """Generate valuation metrics for companies"""
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
        font=dict(color="#1E293B" if st.session_state.theme == "light" else "#F1F5F9", size=13),
        legend=dict(title=None, orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    grid_color = "#E2E8F0" if st.session_state.theme == "light" else "#475569"
    axis_color = "#64748B" if st.session_state.theme == "light" else "#CBD5E1"
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
# Display AI Insights Function
# -----------------------------
# -----------------------------
# AI Insights normalizer + display (visual, not raw JSON)
# -----------------------------

def _normalize_ai_insights(data):
    """
    Normalize AI payloads into:
    [
      {"quarter":"YYYY-Q#", "required_fields":{"revenue":float, "sector_avg":float}, "insights":"..."},
      ...
    ]
    """
    def _num(x):
        try:
            return float(x)
        except Exception:
            return None

    def _fmt_quarter(q):
        # Accept "2024-4" or "2024-Q4" etc → "2024-Q4"
        q = str(q)
        if "-Q" in q:
            y, qn = q.split("-Q", 1)
            return f"{y}-Q{qn}"
        if "-" in q:
            y, qn = q.split("-", 1)
            return f"{y}-Q{int(qn)}" if qn.isdigit() else q
        return q

    # If already a list in our target shape, keep it
    if isinstance(data, list) and data and isinstance(data[0], dict) and "required_fields" in data[0]:
        # make sure the numbers and quarter format are clean
        out = []
        for item in data:
            rf = item.get("required_fields", {}) or {}
            out.append({
                "quarter": _fmt_quarter(item.get("quarter")),
                "required_fields": {
                    "revenue": _num(rf.get("revenue")),
                    "sector_avg": _num(rf.get("sector_avg")),
                },
                "insights": item.get("insights", "") or item.get("analysis", "") or ""
            })
        return [x for x in out if x["required_fields"]["revenue"] is not None and x["required_fields"]["sector_avg"] is not None]

    # Dict with "quarters": [...]
    if isinstance(data, dict) and isinstance(data.get("quarters"), list):
        out = []
        for q in data["quarters"]:
            if not isinstance(q, dict):
                continue
            rf = q.get("required_fields", {}) or {}
            revenue = _num(q.get("revenue") or q.get("Revenue") or q.get("metrics", {}).get("revenue") or rf.get("revenue"))
            sector_avg = _num(q.get("sector_avg") or q.get("Sector_Avg") or q.get("metrics", {}).get("sector_avg") or rf.get("sector_avg"))
            quarter = _fmt_quarter(q.get("quarter") or q.get("period") or q.get("label"))
            insights = q.get("insight") or q.get("insights") or q.get("analysis") or q.get("commentary") or ""
            if quarter and revenue is not None and sector_avg is not None:
                out.append({"quarter": quarter,
                            "required_fields": {"revenue": revenue, "sector_avg": sector_avg},
                            "insights": insights})
        # sort if possible
        try:
            out.sort(key=lambda x: (x["quarter"].split("-")[0], int(x["quarter"].split("-")[1].replace("Q",""))))
        except Exception:
            pass
        return out if out else None

    # Dict keyed by quarter {"2024-4": {...}}
    if isinstance(data, dict) and any("-" in str(k) for k in data.keys()):
        out = []
        for quarter_key, payload in data.items():
            if not isinstance(payload, dict):
                continue
            rf = payload.get("required_fields", {}) or {}
            revenue = _num(payload.get("revenue") or payload.get("Revenue") or payload.get("metrics", {}).get("revenue") or rf.get("revenue"))
            sector_avg = _num(payload.get("sector_avg") or payload.get("Sector_Avg") or payload.get("metrics", {}).get("sector_avg") or rf.get("sector_avg"))
            quarter = _fmt_quarter(quarter_key)
            insights = payload.get("insight") or payload.get("insights") or payload.get("analysis") or payload.get("commentary") or ""
            if revenue is not None and sector_avg is not None:
                out.append({"quarter": quarter,
                            "required_fields": {"revenue": revenue, "sector_avg": sector_avg},
                            "insights": insights})
        try:
            out.sort(key=lambda x: (x["quarter"].split("-")[0], int(x["quarter"].split("-")[1].replace("Q",""))))
        except Exception:
            pass
        return out if out else None

    return None



def display_ai_insights(insights_data, company_name, ticker, analysis_type):
    """Display AI insights in a professional UI format for multiple JSON formats"""
    if not insights_data:
        st.info("No AI insights available yet.")
        return
    
    # Parse JSON if it's a string
    if isinstance(insights_data, str):
        try:
            insights_data = json.loads(insights_data)
        except json.JSONDecodeError:
            st.error("Invalid JSON format in insights data")
            return
    
    # Determine the type of analysis based on JSON structure
    if isinstance(insights_data, dict):
        if "quarters" in insights_data and "company" in insights_data:
            # Company Analysis Format
            display_company_analysis(insights_data, company_name, ticker, analysis_type)
        elif "companies" in insights_data and "sector_comparison" in insights_data:
            # Sector Analysis Format
            display_sector_analysis(insights_data, company_name, ticker, analysis_type)
        else:
            # Legacy format
            display_legacy_format(insights_data, company_name, ticker, analysis_type)
    elif isinstance(insights_data, list):
        # Original quarterly format
        display_quarterly_format(insights_data, company_name, ticker, analysis_type)
    else:
        st.error("Unrecognized data format")

def display_company_analysis(insights_data, company_name, ticker, analysis_type):
    """Display Company Analysis format (quarters with company_insights only)"""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, var(--primary-color)10, var(--secondary-color)10); 
                border-radius: 16px; padding: 2rem; margin: 1.5rem 0; 
                border-left: 6px solid var(--primary-color);">
        <h2 style="color: var(--text-primary); margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;">
            🤖 AI {analysis_type} Analysis: Company Focus
            <span style="background: var(--primary-color); color: white; padding: 0.25rem 0.75rem; 
                       border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                {company_name} ({ticker})
            </span>
        </h2>
        <p style="color: var(--text-secondary); margin: 0;">
            Quarterly company-specific performance analysis and insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    quarters_data = insights_data.get("quarters", [])
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📊 Overview", "📈 Quarterly Analysis"])
    
    with tab1:
        # Overview metrics from KPIs (ignore averages)
        st.markdown("### Executive Summary")
        
        if quarters_data:
            total_quarters = len(quarters_data)
            
            # Extract key metrics from latest quarter (ignore averages)
            latest_quarter = quarters_data[0] if quarters_data else {}
            latest_kpis = latest_quarter.get("kpis", {})
            
            # Filter out average metrics and get company-specific values
            company_kpis = {k: v for k, v in latest_kpis.items() if "Average" not in k}
            
            # Display KPIs in columns
            if company_kpis:
                kpi_items = list(company_kpis.items())
                cols = st.columns(min(4, len(kpi_items)))
                
                for i, (kpi_name, kpi_value) in enumerate(kpi_items):
                    with cols[i % 4]:
                        # Format value based on type
                        if isinstance(kpi_value, (int, float)):
                            if "Ratio" in kpi_name or "Growth" in kpi_name:
                                display_value = fmt_ratio(kpi_value)
                            elif "Margin" in kpi_name:
                                display_value = fmt_pct(kpi_value)
                            elif "Cash Flow" in kpi_name or "Income" in kpi_name:
                                display_value = fmt_money(kpi_value)
                            else:
                                display_value = fmt_ratio(kpi_value)
                        else:
                            display_value = str(kpi_value)
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>{kpi_name}</h3>
                            <div class="value">{display_value}</div>
                            <div class="delta neutral">Q{len(quarters_data)} 2023</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Performance trend chart using available metrics
            st.markdown("### Performance Trend")
            if quarters_data:
                # Extract chart data from quarters
                chart_data = []
                for quarter in quarters_data:
                    quarter_name = quarter.get("quarter", "")
                    charts = quarter.get("charts", {})
                    kpis = quarter.get("kpis", {})
                    
                    # Combine chart metrics and KPIs for plotting
                    quarter_metrics = {"quarter": quarter_name}
                    
                    # Add chart metrics
                    for chart_name, chart_data_inner in charts.items():
                        metrics = chart_data_inner.get("metrics", {})
                        quarter_metrics.update(metrics)
                    
                    # Add non-average KPIs
                    for k, v in kpis.items():
                        if "Average" not in k and isinstance(v, (int, float)):
                            quarter_metrics[k] = v
                    
                    chart_data.append(quarter_metrics)
                
                if chart_data:
                    # Create chart based on available metrics
                    df_chart = pd.DataFrame(chart_data)
                    if len(df_chart) > 1:
                        # Select numeric columns for plotting
                        numeric_cols = df_chart.select_dtypes(include=[np.number]).columns.tolist()
                        if numeric_cols:
                            # Plot first few numeric metrics
                            fig = go.Figure()
                            colors = COLORWAY
                            
                            for i, col in enumerate(numeric_cols[:4]):  # Limit to 4 metrics
                                fig.add_trace(go.Scatter(
                                    x=df_chart["quarter"],
                                    y=df_chart[col],
                                    mode='lines+markers',
                                    name=col.replace("_", " ").title(),
                                    line=dict(color=colors[i % len(colors)], width=3),
                                    marker=dict(size=8)
                                ))
                            
                            fig = style_fig(fig)
                            fig.update_layout(
                                height=400,
                                title=f"{analysis_type} Metrics Trend",
                                xaxis_title="Quarter",
                                yaxis_title="Value"
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Quarterly breakdown using company_insights only
        st.markdown("### Quarterly Analysis")
        
        for i, quarter_data in enumerate(quarters_data):
            quarter = quarter_data.get("quarter", f"Quarter {i+1}")
            kpis = quarter_data.get("kpis", {})
            company_insights = quarter_data.get("insights", {}).get("company_insights", "No insights available")
            
            # Filter out average KPIs
            company_kpis = {k: v for k, v in kpis.items() if "Average" not in k}
            
            with st.expander(f"📊 {quarter} - Detailed Analysis", expanded=(i < 2)):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Display company KPIs
                    for kpi_name, kpi_value in company_kpis.items():
                        if isinstance(kpi_value, (int, float)):
                            if "Ratio" in kpi_name or "Growth" in kpi_name:
                                display_value = fmt_ratio(kpi_value)
                            elif "Margin" in kpi_name:
                                display_value = fmt_pct(kpi_value)
                            elif "Cash Flow" in kpi_name or "Income" in kpi_name:
                                display_value = fmt_money(kpi_value)
                            else:
                                display_value = fmt_ratio(kpi_value)
                        else:
                            display_value = str(kpi_value)
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>{kpi_name}</h3>
                            <div class="value">{display_value}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="ai-insight-box">
                        <h4 style="color: var(--text-primary); margin: 0 0 1rem 0;">💡 Company Insights</h4>
                        <p style="color: var(--text-primary); line-height: 1.6; margin: 0;">
                            {company_insights}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

def display_sector_analysis(insights_data, company_name, ticker, analysis_type):
    """Display Sector Analysis format (use all data in JSON)"""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, var(--primary-color)10, var(--secondary-color)10); 
                border-radius: 16px; padding: 2rem; margin: 1.5rem 0; 
                border-left: 6px solid var(--primary-color);">
        <h2 style="color: var(--text-primary); margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;">
            🤖 AI {analysis_type} Analysis: Sector Overview
            <span style="background: var(--primary-color); color: white; padding: 0.25rem 0.75rem; 
                       border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                {insights_data.get("sector_comparison", {}).get("sector", "Healthcare")} Sector
            </span>
        </h2>
        <p style="color: var(--text-secondary); margin: 0;">
            Comprehensive sector analysis with company comparisons and rankings
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for sector analysis
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Sector Overview", "🏢 Company Profiles", "📈 Rankings", "💡 Insights"])
    
    companies_data = insights_data.get("companies", [])
    sector_comparison = insights_data.get("sector_comparison", {})
    
    with tab1:
        # Sector overview
        st.markdown("### Sector Performance Summary")
        
        if companies_data:
            # Calculate sector averages
            total_companies = len(companies_data)
            
            # Aggregate metrics
            total_revenue = sum([comp.get("annual", {}).get("profitability", {}).get("revenue", 0) for comp in companies_data])
            total_net_income = sum([comp.get("annual", {}).get("profitability", {}).get("net_income", 0) for comp in companies_data])
            avg_profit_margin = sum([comp.get("annual", {}).get("ratios", {}).get("ProfitMargin", 0) for comp in companies_data]) / total_companies
            avg_roe = sum([comp.get("annual", {}).get("ratios", {}).get("ReturnOnEquity", 0) for comp in companies_data]) / total_companies
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Total Revenue</h3>
                    <div class="value">{fmt_money(total_revenue)}</div>
                    <div class="delta neutral">Sector Total</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Total Net Income</h3>
                    <div class="value">{fmt_money(total_net_income)}</div>
                    <div class="delta neutral">Sector Total</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Avg Profit Margin</h3>
                    <div class="value">{fmt_pct(avg_profit_margin)}</div>
                    <div class="delta neutral">Sector Average</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Avg ROE</h3>
                    <div class="value">{fmt_pct(avg_roe)}</div>
                    <div class="delta neutral">Sector Average</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Sector composition chart
        if companies_data:
            st.markdown("### Sector Composition by Revenue")
            
            revenue_data = []
            for company in companies_data:
                comp_info = company.get("company_info", {})
                annual = company.get("annual", {})
                revenue = annual.get("profitability", {}).get("revenue", 0)
                
                revenue_data.append({
                    "Company": comp_info.get("symbol", "N/A"),
                    "Revenue": revenue
                })
            
            df_revenue = pd.DataFrame(revenue_data)
            fig = px.pie(df_revenue, values="Revenue", names="Company", 
                        title="Revenue Distribution by Company")
            fig = style_fig(fig)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Company profiles
        st.markdown("### Company Performance Profiles")
        
        for company in companies_data:
            comp_info = company.get("company_info", {})
            annual = company.get("annual", {})
            kpis = company.get("kpis", {})
            insights = company.get("insights", {})
            
            symbol = comp_info.get("symbol", "N/A")
            name = comp_info.get("name", "Unknown Company")
            
            with st.expander(f"🏢 {name} ({symbol})", expanded=(symbol == ticker)):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Key metrics
                    profitability = annual.get("profitability", {})
                    balance_sheet = annual.get("balance_sheet", {})
                    ratios = annual.get("ratios", {})
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Revenue</h3>
                        <div class="value">{fmt_money(profitability.get("revenue", 0))}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Net Income</h3>
                        <div class="value">{fmt_money(profitability.get("net_income", 0))}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Profit Margin</h3>
                        <div class="value">{fmt_pct(ratios.get("ProfitMargin", 0))}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Company insights
                    st.markdown("#### Key Insights")
                    for insight_type, insight_text in insights.items():
                        st.markdown(f"""
                        <div style="background: var(--bg-tertiary); border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
                            <div style="color: var(--primary-color); font-weight: 600; margin-bottom: 0.5rem;">
                                {insight_type.replace('_', ' ').title()}
                            </div>
                            <div style="color: var(--text-primary); font-size: 0.9rem;">
                                {insight_text}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    
    with tab3:
        # Rankings from sector comparison
        st.markdown("### Sector Rankings")
        
        rankings = sector_comparison.get("rankings", {})
        
        for metric_name, ranking_data in rankings.items():
            st.markdown(f"#### {metric_name.replace('_', ' ').replace('.', ' ').title()}")
            
            if ranking_data and len(ranking_data) > 0:
                # Debug: Show the structure of ranking_data
                st.write("Debug - Ranking data structure:", ranking_data[:2] if len(ranking_data) > 1 else ranking_data)
                
                # Extract companies and values with better error handling
                companies = []
                values = []
                
                for item in ranking_data:
                    # Try different possible keys for company and value
                    try:
                        company = item.get("company") or item.get("Company") or ""
                        value = item.get("value") or item.get("Value") or 0
                        
                        if company and isinstance(value, (int, float)):
                            companies.append(company)
                            values.append(value)
                    except Exception as e:
                        st.write(f"Error processing ranking item: {e}")  # Debugging line
                
                if companies and values:
                    # Highlight the current company
                    colors = [COLORWAY[0] if comp == ticker else COLORWAY[1] for comp in companies]
                    
                    fig = go.Figure(data=[go.Bar(x=companies, y=values, marker_color=colors)])
                    fig = style_fig(fig)
                    fig.update_layout(
                        height=300,
                        title=f"{metric_name.replace('_', ' ').title()} Rankings",
                        xaxis_title="Company",
                        yaxis_title="Value"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show ranking table
                    ranking_df = pd.DataFrame(ranking_data)
                    print(ranking_df)
                    ranking_df.index = range(1, len(ranking_df) + 1)
                    ranking_df.index.name = "Rank"
                    st.dataframe(ranking_df, use_container_width=True)
    
    with tab4:
        # Consolidated insights
        st.markdown("### Sector Insights Summary")
        
        # Extract insights from all companies
        for company in companies_data:
            comp_info = company.get("company_info", {})
            insights = company.get("insights", {})
            symbol = comp_info.get("symbol", "N/A")
            name = comp_info.get("name", "Unknown")
            
            if insights:
                st.markdown(f"""
                <div style="background: var(--bg-primary); border: 1px solid var(--border-color); 
                            border-radius: 12px; padding: 1.5rem; margin: 1rem 0; 
                            border-left: 4px solid {'var(--primary-color)' if symbol == ticker else 'var(--border-color)'};">
                    <div style="color: var(--primary-color); font-weight: 600; margin-bottom: 1rem; font-size: 1.1rem;">
                        {name} ({symbol})
                    </div>
                """, unsafe_allow_html=True)
                
                for insight_type, insight_text in insights.items():
                    st.markdown(f"""
                    <div style="margin-bottom: 0.5rem;">
                        <strong style="color: var(--text-secondary);">{insight_type.replace('_', ' ').title()}:</strong>
                        <span style="color: var(--text-primary);"> {insight_text}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)

def display_quarterly_format(insights_data, company_name, ticker, analysis_type):
    """Display original quarterly format (your existing implementation)"""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, var(--primary-color)10, var(--secondary-color)10); 
                border-radius: 16px; padding: 2rem; margin: 1.5rem 0; 
                border-left: 6px solid var(--primary-color);">
        <h2 style="color: var(--text-primary); margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;">
            🤖 AI Financial Analysis: {analysis_type}
            <span style="background: var(--primary-color); color: white; padding: 0.25rem 0.75rem; 
                       border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                {company_name} ({ticker})
            </span>
        </h2>
        <p style="color: var(--text-secondary); margin: 0;">
            Comprehensive quarterly analysis with sector comparisons and strategic insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Quarterly Analysis", "🎯 Key Metrics", "💡 Strategic Insights"])
    
    with tab1:
        # Overview metrics
        st.markdown("### Executive Summary")
        
        # Calculate overview metrics
        total_quarters = len(insights_data)
        avg_revenue = sum([item['required_fields']['revenue'] for item in insights_data]) / total_quarters
        avg_sector = sum([item['required_fields']['sector_avg'] for item in insights_data]) / total_quarters
        outperformance = ((avg_revenue - avg_sector) / avg_sector) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Analysis Period</h3>
                <div class="value">{total_quarters}</div>
                <div class="delta neutral">Quarters Analyzed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Avg Revenue</h3>
                <div class="value">{fmt_money(avg_revenue)}</div>
                <div class="delta neutral">Per Quarter</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Sector Average</h3>
                <div class="value">{fmt_money(avg_sector)}</div>
                <div class="delta neutral">Per Quarter</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            performance_class = "positive" if outperformance > 0 else "negative" if outperformance < 0 else "neutral"
            st.markdown(f"""
            <div class="metric-card">
                <h3>Outperformance</h3>
                <div class="value">{outperformance:+.1f}%</div>
                <div class="delta {performance_class}">vs Sector</div>
            </div>
            """, unsafe_allow_html=True)

        # Revenue trend chart
        st.markdown("### Revenue Performance Trend")
        
        # Prepare data for plotting
        quarters = [item['quarter'] for item in insights_data]
        revenues = [item['required_fields']['revenue'] for item in insights_data]
        sector_avgs = [item['required_fields']['sector_avg'] for item in insights_data]
        
        # Sort by quarter
        quarter_data = list(zip(quarters, revenues, sector_avgs))
        quarter_data.sort(key=lambda x: (x[0].split('-')[0], x[0].split('-')[1]))
        quarters, revenues, sector_avgs = zip(*quarter_data)
        
        # Create comparison chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=quarters,
            y=revenues,
            mode='lines+markers',
            name=f'{company_name} Revenue',
            line=dict(color=COLORWAY[0], width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=quarters,
            y=sector_avgs,
            mode='lines+markers',
            name='Sector Average',
            line=dict(color=COLORWAY[1], width=3, dash='dash'),
            marker=dict(size=8)
        ))
        
        fig = style_fig(fig)
        fig.update_layout(
            height=400,
            title="Revenue Performance vs Sector Average",
            xaxis_title="Quarter",
            yaxis_title="Revenue ($)",
            yaxis=dict(tickformat='$,.0f')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Quarterly breakdown using company_insights only
        st.markdown("### Quarterly Analysis")
        
        for i, quarter_data in enumerate(sorted(insights_data, key=lambda x: (x['quarter'].split('-')[0], x['quarter'].split('-')[1]), reverse=True)):
            quarter = quarter_data['quarter']
            revenue = quarter_data['required_fields']['revenue']
            sector_avg = quarter_data['required_fields']['sector_avg']
            insights = quarter_data['insights']
            
            performance = ((revenue - sector_avg) / sector_avg) * 100
            performance_icon = "📈" if performance > 0 else "📉" if performance < 0 else "➡️"
            performance_class = "positive" if performance > 0 else "negative" if performance < 0 else "neutral"
            
            with st.expander(f"{performance_icon} {quarter} - {fmt_money(revenue)} ({performance:+.1f}% vs sector)", expanded=(i < 2)):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Revenue</h3>
                        <div class="value">{fmt_money(revenue)}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Sector Average</h3>
                        <div class="value">{fmt_money(sector_avg)}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Performance</h3>
                        <div class="value">{performance:+.1f}%</div>
                        <div class="delta {performance_class}">vs Sector</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="ai-insight-box">
                        <h4 style="color: var(--text-primary); margin: 0 0 1rem 0;">💡 AI Strategic Analysis</h4>
                        <p style="color: var(--text-primary); line-height: 1.6; margin: 0;">
                            {insights}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab3:
        # Key metrics analysis
        st.markdown("### Performance Metrics Analysis")
        
        # Performance distribution
        performances = [((item['required_fields']['revenue'] - item['required_fields']['sector_avg']) / 
                       item['required_fields']['sector_avg']) * 100 for item in insights_data]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Performance distribution chart
            fig = go.Figure(data=[go.Histogram(x=performances, nbinsx=8, name="Performance Distribution")])
            fig.update_traces(marker_color=COLORWAY[0])
            fig = style_fig(fig)
            fig.update_layout(
                height=300,
                title="Performance Distribution (%)",
                xaxis_title="Outperformance vs Sector (%)",
                yaxis_title="Frequency"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Revenue growth analysis
            revenues_sorted = [item['required_fields']['revenue'] for item in sorted(insights_data, key=lambda x: (x['quarter'].split('-')[0], x['quarter'].split('-')[1]))]
            growth_rates = []
            for i in range(1, len(revenues_sorted)):
                growth = ((revenues_sorted[i] - revenues_sorted[i-1]) / revenues_sorted[i-1]) * 100
                growth_rates.append(growth)
            
            if growth_rates:
                fig = go.Figure(data=[go.Bar(x=list(range(len(growth_rates))), y=growth_rates, name="QoQ Growth")])
                fig.update_traces(marker_color=COLORWAY[2])
                fig = style_fig(fig)
                fig.update_layout(
                    height=300,
                    title="Quarter-over-Quarter Growth (%)",
                    xaxis_title="Quarter Sequence",
                    yaxis_title="Growth Rate (%)"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_performance = sum(performances) / len(performances)
            st.markdown(f"""
            <div class="metric-card">
                <h3>Avg Outperformance</h3>
                <div class="value">{avg_performance:+.1f}%</div>
                <div class="delta neutral">vs Sector</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            consistency = len([p for p in performances if p > 0]) / len(performances) * 100
            st.markdown(f"""
            <div class="metric-card">
                <h3>Consistency</h3>
                <div class="value">{consistency:.0f}%</div>
                <div class="delta neutral">Quarters Above Sector</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            max_performance = max(performances)
            st.markdown(f"""
            <div class="metric-card">
                <h3>Peak Performance</h3>
                <div class="value">{max_performance:+.1f}%</div>
                <div class="delta positive">Best Quarter</div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        # Strategic insights summary
        st.markdown("### Strategic Insights & Recommendations")
        
        # Extract key themes from all insights
        all_insights = " ".join([item['insights'] for item in insights_data])
        
        # Common themes analysis (simple keyword extraction)
        themes = {
            "Growth Drivers": ["growth", "strong", "robust", "success", "expansion", "innovation"],
            "Challenges": ["challenge", "risk", "pressure", "competition", "headwind", "disruption"],
            "Strategic Focus": ["strategy", "investment", "focus", "R&D", "partnership", "market"],
            "Market Position": ["position", "advantage", "leadership", "ecosystem", "brand", "loyalty"]
        }
        
        theme_insights = {}
        for theme, keywords in themes.items():
            relevance = sum([all_insights.lower().count(keyword) for keyword in keywords])
            theme_insights[theme] = relevance
        
        # Display strategic themes
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Key Strategic Themes")
            for theme, relevance in sorted(theme_insights.items(), key=lambda x: x[1], reverse=True):
                bar_width = min(100, (relevance / max(theme_insights.values())) * 100) if max(theme_insights.values()) > 0 else 0
                st.markdown(f"""
                <div style="margin: 1rem 0;">
                    <div style="color: var(--text-primary); font-weight: 600; margin-bottom: 0.5rem;">
                        {theme} ({relevance} mentions)
                    </div>
                    <div style="background: var(--border-color); border-radius: 10px; height: 10px;">
                        <div style="background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)); 
                                    width: {bar_width}%; height: 100%; border-radius: 10px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Recent Quarter Highlights")
            # Show insights from the most recent 2 quarters
            recent_quarters = sorted(insights_data, key=lambda x: (x['quarter'].split('-')[0], x['quarter'].split('-')[1]), reverse=True)[:2]
            
            for quarter_data in recent_quarters:
                quarter = quarter_data['quarter']
                insights = quarter_data['insights']
                # Extract first sentence as highlight
                highlight = insights.split('.')[0] + '.' if '.' in insights else insights[:100] + '...'
                
                st.markdown(f"""
                <div style="background: var(--bg-primary); border: 1px solid var(--border-color); 
                            border-radius: 12px; padding: 1rem; margin: 0.5rem 0;">
                    <div style="color: var(--primary-color); font-weight: 600; margin-bottom: 0.5rem;">
                        {quarter}
                    </div>
                    <div style="color: var(--text-primary); font-size: 0.9rem; line-height: 1.5;">
                        {highlight}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Action items and recommendations
        st.markdown("#### AI-Generated Action Items")
        action_items = [
            "📊 Continue monitoring quarterly performance against sector benchmarks",
            "🎯 Focus on maintaining competitive advantages identified in the analysis",
            "⚠️ Address potential risks highlighted across multiple quarters",
            "🚀 Leverage identified growth drivers for strategic planning",
            "🔍 Deep-dive into quarters with exceptional performance for best practices"
        ]
        
        for item in action_items:
            st.markdown(f"""
            <div style="background: var(--bg-primary); border-left: 4px solid var(--primary-color); 
                        padding: 1rem; margin: 0.5rem 0; border-radius: 0 8px 8px 0;">
                <div style="color: var(--text-primary);">{item}</div>
            </div>
            """, unsafe_allow_html=True)

def display_legacy_format(insights_data, company_name, ticker, analysis_type):
    """Display legacy format (fallback)"""
    st.markdown('<div class="ai-insight-box">', unsafe_allow_html=True)
    st.markdown("#### 🤖 AI Analysis Results")
    if isinstance(insights_data, dict):
        for key, value in insights_data.items():
            if key not in ['type', 'status', 'message']:
                st.markdown(f"**{key.replace('_', ' ').title()}:**")
                if isinstance(value, (list, dict)):
                    st.json(value)
                else:
                    st.write(value)
    else:
        st.write(str(insights_data))
    st.markdown('</div>', unsafe_allow_html=True)
# -----------------------------
# Load Data (Updated to use real data)
# -----------------------------
@st.cache_data
def load_data():
    panel, sector_map = load_real_financial_data()
    return add_ratios(panel), sector_map

with st.spinner("🔄 Loading real financial data..."):
    PANEL, SECTOR_MAP = load_data()

if PANEL.empty:
    st.error("❌ No financial data available. Please check your data files and try again.")
    st.info("💡 To fix this issue:")
    st.markdown("""
    1. Ensure `combined_financial_data_yearly_ratios.json` exists in the `data/` directory
    2. Verify the JSON structure matches the expected format
    3. Check file permissions and encoding
    """)
    st.stop()

# -----------------------------
# Header with Theme Toggle
# -----------------------------
st.markdown("""
<div class="main-header">
    <h1>Financial Insights Hub</h1>
    <p>AI-Powered Financial Analytics & Business Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Show data source information
data_info = st.expander("ℹ️ Data Source Information")
with data_info:
    st.write(f"**Companies loaded:** {len(PANEL['company'].unique())}")
    st.write(f"**Sectors:** {', '.join(PANEL['sector'].unique())}")
    st.write(f"**Year range:** {PANEL['Year'].min()} - {PANEL['Year'].max()}")
    st.write(f"**Quarter range:** Q{PANEL['Quarter'].min()} - Q{PANEL['Quarter'].max()}")
    st.write(f"**Total records:** {len(PANEL)}")
    
    # Show sample of companies by sector
    for sector in PANEL['sector'].unique():
        companies = PANEL[PANEL['sector'] == sector]['company'].unique()
        st.write(f"**{sector}:** {', '.join(companies)}")


# -----------------------------
# Sidebar Controls (Enhanced)
# -----------------------------
with st.sidebar:
    # Theme toggle at the top of sidebar
    st.markdown("### Theme")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:  # Center the button
        if st.button(
            "🌓" if st.session_state.theme == "light" else "☀️",
            help="Toggle light/dark theme",
            key="theme_toggle_sidebar",
            use_container_width=True
        ):
            st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
            st.rerun()
    
    st.caption(f"Current: *{st.session_state.theme.title()} Mode*")
    
    st.divider()

    st.markdown("### Data Filters")
    
    # Handle programmatic sector changes
    sectors = sorted(SECTOR_MAP.keys())
    if st.session_state.selected_sector and st.session_state.selected_sector in sectors:
        sector_index = sectors.index(st.session_state.selected_sector)
    else:
        sector_index = 0
    
    sector = st.selectbox("Sector", sectors, index=sector_index, key="sector_select")
    
    # Handle programmatic company changes
    companies = ["All"] + list(SECTOR_MAP[sector].keys())
    if st.session_state.selected_company and st.session_state.selected_company in companies:
        company_index = companies.index(st.session_state.selected_company)
    else:
        company_index = 0
    
    company = st.selectbox("Company", companies, index=company_index, key="company_select")
# -----------------------------
# Navigation (Enhanced with AI Insights)
# -----------------------------
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboards"

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📊 Dashboards", use_container_width=True):
        st.session_state.current_page = "Dashboards"
with col2:
    if st.button("🧾 Data Table", use_container_width=True):
        st.session_state.current_page = "Data Table"
with col3:
    if st.button("📈 Insights", use_container_width=True):
        st.session_state.current_page = "Insights"
with col4:
    if st.button("🤖 AI Analysis", use_container_width=True):
        st.session_state.current_page = "AI Analysis"

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
# PAGE 1 — DASHBOARDS (Existing code remains mostly the same)
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
# PAGE 2 — DATA TABLE (Enhanced)
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
            file_name=f"financial_data_{sector}{company}{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No data available for the selected criteria.")

# =====================================================
# PAGE 3 — INSIGHTS (Enhanced)
# =====================================================
elif st.session_state.current_page == "Insights":
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

# =====================================================
# PAGE 4 — AI ANALYSIS
# =====================================================
else:
    st.markdown(f"## 🤖 AI-Powered Financial Analysis — {SC_LABEL}")
    
    if company == "All":
        st.warning("⚠️ Please select a specific company to generate AI insights.")
        
        # Show available companies for AI analysis with improved selection
        st.markdown("### Available Companies for Analysis")
        for sector_name, companies_dict in SECTOR_MAP.items():
            with st.expander(f"📊 {sector_name} Sector"):
                for comp_name, ticker in companies_dict.items():
                    if st.button(
                        f"🔍 Analyze {comp_name} ({ticker})",
                        key=f"analyze_{ticker}",
                        use_container_width=True
                    ):
                        st.session_state.selected_sector = sector_name
                        st.session_state.selected_company = comp_name
                        st.session_state.current_page = "AI Analysis"
                        st.rerun()
    else:
        # Get ticker for the selected company
        ticker = SECTOR_MAP[sector][company]
        
        st.markdown(f"### AI Analysis for **{company}** ({ticker})")
        
        # Analysis type selection
        col1, col2, col3, col4 = st.columns(4) 
        
        with col1:
            analysis_type = st.selectbox(
                "Analysis Type",
                ["Profitability", "Financial Standing", "Cash Flow"],
                help="Select the type of financial analysis to generate"
            )
        with col2:
            analysis_scope = st.selectbox(
                "Analysis Scope",
                ["Sector-wide Analysis", "Company Analysis", "Company vs Sector"],
                key="analysis_scope"
            )
        with col3:  
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            generate_clicked = st.button(
                "🤖 Generate AI Insights",
                use_container_width=True,
                help=f"Generate {analysis_type} insights for {company}"
            )
        
        with col4:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            # Demo button to show sample data
            demo_clicked = st.button(
                "📋 Load Demo Data",
                use_container_width=True,
                help="Load sample AI insights for demonstration"
            )
        
        # Demo data loader
        if demo_clicked:
            demo_insights = [
                {"quarter":"2023-Q4","required_fields":{"revenue":119575000000,"sector_avg":100000000000},"insights":"In Q4 2023, AAPL reported a revenue of $119.58 billion, significantly outperforming the sector average of $100 billion. This strong performance can be attributed to robust demand for its flagship products, particularly the iPhone and services segment. AAPL's ability to maintain a premium pricing strategy while expanding its ecosystem has solidified its market position. However, potential risks include supply chain disruptions and increasing competition in the tech sector, which could impact future revenue growth. Looking ahead, AAPL's focus on innovation and expansion into new markets will be critical in sustaining this momentum."},
                {"quarter":"2023-Q3","required_fields":{"revenue":89498000000,"sector_avg":80000000000},"insights":"AAPL's revenue for Q3 2023 was $89.50 billion, exceeding the sector average of $80 billion. This quarter saw a rebound in consumer spending, particularly in the services and wearables categories. AAPL's strategic investments in AI and augmented reality are expected to drive future growth. However, the company faces challenges from macroeconomic factors such as inflation and potential regulatory scrutiny. Maintaining its competitive edge will require continuous innovation and effective cost management."},
                {"quarter":"2023-Q2","required_fields":{"revenue":81797000000,"sector_avg":75000000000},"insights":"In Q2 2023, AAPL generated $81.80 billion in revenue, surpassing the sector average of $75 billion. The growth was driven by strong sales in its services segment and a resurgence in hardware sales. AAPL's ability to leverage its ecosystem to enhance customer loyalty is a significant strength. However, the company must navigate potential headwinds from global economic uncertainties and supply chain challenges. Future revenue growth will depend on AAPL's agility in responding to market dynamics and consumer preferences."},
                {"quarter":"2023-Q1","required_fields":{"revenue":94836000000,"sector_avg":85000000000},"insights":"AAPL's revenue for Q1 2023 reached $94.84 billion, outpacing the sector average of $85 billion. This strong performance reflects AAPL's successful holiday season sales and the continued popularity of its product lineup. The company's focus on enhancing its services revenue stream is a positive indicator for future growth. However, AAPL must remain vigilant against competitive pressures and potential market saturation. Strategic investments in emerging technologies and new product categories will be essential for sustaining growth."},
                {"quarter":"2024-Q4","required_fields":{"revenue":124300000000,"sector_avg":110000000000},"insights":"In Q4 2024, AAPL reported a revenue of $124.30 billion, significantly above the sector average of $110 billion. This growth can be attributed to the successful launch of new products and services as well as an expanding customer base. AAPL's commitment to sustainability and innovation positions it well for future growth. However, the company must address potential risks related to supply chain disruptions and geopolitical tensions. Continued investment in R&D and strategic partnerships will be crucial for maintaining its competitive advantage."},
                {"quarter":"2024-Q3","required_fields":{"revenue":94930000000,"sector_avg":90000000000},"insights":"AAPL's revenue for Q3 2024 was $94.93 billion, slightly above the sector average of $90 billion. This performance reflects strong demand for its products and services, particularly in emerging markets. AAPL's focus on enhancing customer experience through innovative features and services is a key strength. However, the company faces challenges from increasing competition and potential regulatory scrutiny. To sustain growth, AAPL must continue to innovate and adapt to changing market conditions."},
                {"quarter":"2024-Q2","required_fields":{"revenue":85777000000,"sector_avg":80000000000},"insights":"In Q2 2024, AAPL achieved a revenue of $85.78 billion, exceeding the sector average of $80 billion. This growth was driven by strong sales in its services and wearables segments. AAPL's ability to leverage its brand loyalty and ecosystem is a significant advantage. However, the company must remain cautious of potential economic headwinds and competitive pressures. Strategic investments in new technologies and market expansion will be essential for sustaining revenue growth."},
                {"quarter":"2024-Q1","required_fields":{"revenue":90753000000,"sector_avg":85000000000},"insights":"AAPL's revenue for Q1 2024 reached $90.75 billion, above the sector average of $85 billion. This strong performance reflects robust demand for its flagship products and services. AAPL's focus on innovation and customer engagement is a key driver of its success. However, the company must navigate potential risks related to supply chain disruptions and market volatility. Continued investment in R&D and strategic partnerships will be critical for maintaining its competitive edge."},
                {"quarter":"2025-Q2","required_fields":{"revenue":94036000000,"sector_avg":90000000000},"insights":"In Q2 2025, AAPL reported a revenue of $94.04 billion, surpassing the sector average of $90 billion. This growth can be attributed to strong sales in its services and hardware segments. AAPL's commitment to innovation and customer satisfaction remains a key strength. However, the company must remain vigilant against competitive pressures and potential market saturation. Strategic investments in emerging technologies and new product categories will be essential for sustaining growth."},
                {"quarter":"2025-Q1","required_fields":{"revenue":95359000000,"sector_avg":91000000000},"insights":"AAPL's revenue for Q1 2025 reached $95.36 billion, exceeding the sector average of $91 billion. This strong performance reflects AAPL's successful product launches and expanding customer base. The company's focus on enhancing its services revenue stream is a positive indicator for future growth. However, AAPL must navigate potential headwinds from global economic uncertainties and supply chain challenges. Continued investment in R&D and strategic partnerships will be crucial for maintaining its competitive advantage."}
            ]
            st.session_state[f"insights_{ticker}_{analysis_type}"] = demo_insights
            st.success("✅ Demo AI insights loaded successfully!")
        
        if generate_clicked:
            insights = generate_ai_insights(ticker, analysis_type,analysis_scope)
            if insights:
                st.session_state[f"insights_{ticker}_{analysis_type}_{analysis_scope}"] = insights

        insights_key = f"insights_{ticker}_{analysis_type}_{analysis_scope}"
        if insights_key in st.session_state:
            insights = st.session_state[insights_key]
            display_ai_insights(insights, company, ticker, analysis_type)
            
            # Export tools
            st.markdown("### 📥 Export Analysis")
            col1, col2 = st.columns(2)
            with col1:
                json_str = json.dumps(insights, indent=2)
                st.download_button(
                    label="💾 Download JSON",
                    data=json_str,
                    file_name=f"{ticker}_{analysis_type}_{analysis_scope}_insights_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            with col2:
                if st.button("🔄 Clear Analysis", use_container_width=True):
                    del st.session_state[insights_key]
                    st.rerun()
        else:
            st.info(f"💡 Click 'Generate AI Insights' to analyze {company}'s {analysis_type.lower()} performance, or 'Load Demo Data' to preview.")
            
            # Preview: recent financial rows
            if not df_scope.empty:
                st.markdown("#### 📊 Recent Financials Preview")
                recent_data = df_scope.tail(4)
                if analysis_type == "Profitability":
                    display_cols = ['Year', 'Quarter', 'revenue', 'gross_margin', 'operating_margin', 'net_margin']
                elif analysis_type == "Financial Standing":
                    display_cols = ['Year', 'Quarter', 'total_assets', 'equity', 'current_ratio', 'debt_to_equity']
                elif analysis_type == "Cash Flow":
                    display_cols = ['Year', 'Quarter', 'cfo', 'capex', 'fcf', 'fcf_margin']
                else:
                    display_cols = ['Year', 'Quarter', 'roe', 'current_ratio', 'debt_to_equity', 'earnings_quality']

                display_data = recent_data[display_cols].copy()

                # format types
                for col in ['revenue','total_assets','equity','cfo','capex','fcf']:
                    if col in display_data.columns:
                        display_data[col] = display_data[col].apply(fmt_money)
                for col in [c for c in display_cols if 'margin' in c]:
                    if col in display_data.columns:
                        display_data[col] = display_data[col].apply(fmt_pct)
                for col in [c for c in display_cols if 'ratio' in c or c in ['debt_to_equity','roe','earnings_quality']]:
                    if col in display_data.columns:
                        display_data[col] = display_data[col].apply(lambda x: fmt_ratio(x) if pd.notna(x) else "-")

                st.dataframe(display_data, use_container_width=True, hide_index=True)
