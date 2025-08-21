import streamlit as st
import json
from typing import Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go
from model_integration import ModelOutputIntegrator

def display_ai_insights_panel(ticker: str, analysis_type: str = 'all'):
    """Display comprehensive AI insights panel"""
    
    integrator = ModelOutputIntegrator()
    analysis = integrator.load_company_analysis(ticker)
    
    if not analysis:
        st.info("No AI analysis available for this company")
        return
    
    # Create tabs for different analysis types
    tabs = st.tabs(["📊 Summary", "💰 Profitability", "🏦 Balance Sheet", "💸 Cash Flow", "📈 vs Sector"])
    
    with tabs[0]:  # Summary
        st.markdown("### AI-Powered Financial Summary")
        
        # Overall health score
        scores = []
        if 'profitability' in analysis:
            prof_score = analysis['profitability'].get('overall_score', 50)
            scores.append(prof_score)
        if 'balance_sheet' in analysis:
            bs_score = analysis['balance_sheet'].get('overall_score', 50)
            scores.append(bs_score)
        if 'cash_flow' in analysis:
            cf_score = analysis['cash_flow'].get('overall_score', 50)
            scores.append(cf_score)
        
        if scores:
            overall_score = sum(scores) / len(scores)
            
            # Health score gauge
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = overall_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Financial Health Score"},
                delta = {'reference': 70},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"}],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90}
                }
            ))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Key highlights
        st.markdown("### Key Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Strengths")
            strengths = []
            for key, data in analysis.items():
                if isinstance(data, dict) and 'strengths' in data:
                    strengths.extend(data['strengths'][:2])  # Top 2 from each category
            
            for strength in strengths[:4]:  # Max 4 strengths
                st.markdown(f"✅ {strength}")
        
        with col2:
            st.markdown("#### Areas for Improvement")
            concerns = []
            for key, data in analysis.items():
                if isinstance(data, dict) and 'concerns' in data:
                    concerns.extend(data['concerns'][:2])
            
            for concern in concerns[:4]:  # Max 4 concerns
                st.markdown(f"⚠️ {concern}")
    
    with tabs[1]:  # Profitability
        if 'profitability' in analysis:
            prof_data = analysis['profitability']
            st.markdown("### Profitability Analysis")
            
            # Display profitability metrics
            if 'metrics' in prof_data:
                metrics = prof_data['metrics']
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if 'gross_margin' in metrics:
                        st.metric("Gross Margin", f"{metrics['gross_margin']:.1%}")
                with col2:
                    if 'operating_margin' in metrics:
                        st.metric("Operating Margin", f"{metrics['operating_margin']:.1%}")
                with col3:
                    if 'net_margin' in metrics:
                        st.metric("Net Margin", f"{metrics['net_margin']:.1%}")
            
            # Trend analysis
            if 'trend_analysis' in prof_data:
                st.markdown("#### Trend Analysis")
                trend = prof_data['trend_analysis']
                st.write(trend.get('summary', 'No trend analysis available'))
        else:
            st.info("No profitability analysis available")
    
    with tabs[2]:  # Balance Sheet
        if 'balance_sheet' in analysis:
            bs_data = analysis['balance_sheet']
            st.markdown("### Balance Sheet Analysis")
            
            # Liquidity and leverage metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Liquidity")
                if 'liquidity_metrics' in bs_data:
                    liq = bs_data['liquidity_metrics']
                    if 'current_ratio' in liq:
                        st.metric("Current Ratio", f"{liq['current_ratio']:.2f}")
                    if 'quick_ratio' in liq:
                        st.metric("Quick Ratio", f"{liq['quick_ratio']:.2f}")
            
            with col2:
                st.markdown("#### Leverage")
                if 'leverage_metrics' in bs_data:
                    lev = bs_data['leverage_metrics']
                    if 'debt_to_equity' in lev:
                        st.metric("Debt-to-Equity", f"{lev['debt_to_equity']:.2f}")
                    if 'debt_to_assets' in lev:
                        st.metric("Debt-to-Assets", f"{lev['debt_to_assets']:.2f}")
        else:
            st.info("No balance sheet analysis available")
    
    with tabs[3]:  # Cash Flow
        if 'cash_flow' in analysis:
            cf_data = analysis['cash_flow']
            st.markdown("### Cash Flow Analysis")
            
            # Cash flow metrics
            if 'metrics' in cf_data:
                metrics = cf_data['metrics']
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if 'operating_cash_flow' in metrics:
                        st.metric("Operating CF", f"${metrics['operating_cash_flow']/1e9:.1f}B")
                with col2:
                    if 'free_cash_flow' in metrics:
                        st.metric("Free Cash Flow", f"${metrics['free_cash_flow']/1e9:.1f}B")
                with col3:
                    if 'fcf_margin' in metrics:
                        st.metric("FCF Margin", f"{metrics['fcf_margin']:.1%}")
            
            # Quality analysis
            if 'quality_analysis' in cf_data:
                st.markdown("#### Cash Flow Quality")
                quality = cf_data['quality_analysis']
                st.write(quality.get('assessment', 'No quality analysis available'))
        else:
            st.info("No cash flow analysis available")
    
    with tabs[4]:  # vs Sector
        sector_keys = [k for k in analysis.keys() if 'vs_sector' in k]
        if sector_keys:
            st.markdown("### Sector Comparison")
            
            for key in sector_keys:
                sector_data = analysis[key]
                analysis_name = key.replace('_vs_sector', '').replace('_', ' ').title()
                
                st.markdown(f"#### {analysis_name}")
                if 'peer_comparison' in sector_data:
                    peer_comp = sector_data['peer_comparison']
                    st.write(peer_comp.get('summary', 'No peer comparison available'))
                
                # Ranking if available
                if 'ranking' in sector_data:
                    ranking = sector_data['ranking']
                    st.metric("Sector Ranking", f"{ranking.get('position', 'N/A')}/{ranking.get('total_companies', 'N/A')}")
        else:
            st.info("No sector comparison data available")

def create_performance_indicator(value: float, metric_type: str) -> str:
    """Create a visual performance indicator"""
    integrator = ModelOutputIntegrator()
    assessment = integrator.get_metric_assessment(value, metric_type)
    
    color_map = {
        'excellent': '🟢',
        'good': '🟡', 
        'neutral': '🟠',
        'warning': '🟠',
        'bad': '🔴'
    }
    
    return f"{color_map.get(assessment['class'], '⚪')} {assessment['description']}"