"""
Policy & Regulatory Feedback Intelligence System
Decision-Support Dashboard for Public Consultation Analysis.
Runs locally with zero external telemetry or cloud dependencies.
"""

import os
import sqlite3
import pandas as pd
import streamlit as st

from app.ui_components import (
    render_header,
    render_overview_tab,
    render_clauses_tab,
    render_sentiment_tab,
    render_campaigns_tab,
    render_insights_tab,
    render_data_tab,
    render_evaluation_tab
)

# ==============================================================================
# Page Configuration
# ==============================================================================
st.set_page_config(
    page_title="Policy & Regulatory Feedback Intelligence System",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# Custom CSS for Modern, Accessible Dark Theme
# ==============================================================================
st.markdown("""
<style>
    /* Global font & background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .main {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Top Header Banner */
    .gov-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    }
    
    .gov-title {
        font-size: 25px;
        font-weight: 800;
        margin: 0;
        line-height: 1.3;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .gov-icon {
        font-size: 26px;
    }
    
    .gov-title-text {
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.01em;
    }
    
    .gov-summary {
        font-size: 13.5px;
        line-height: 1.5;
        color: #94A3B8;
        margin-top: 8px;
        margin-bottom: 0;
        max-width: 950px;
        word-wrap: break-word;
    }
    
    /* Navigation Bar Styling (State-Preserving Horizontal Tab Pills) */
    div[data-testid="stRadio"] {
        margin-bottom: 20px;
    }
    
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex;
        flex-direction: row;
        gap: 8px;
        background-color: #1E293B;
        padding: 8px 10px;
        border-radius: 12px;
        border: 1px solid #334155;
        overflow-x: auto;
        white-space: nowrap;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        height: 42px;
        padding: 0 18px;
        border-radius: 8px;
        background-color: transparent;
        border: none !important;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin: 0 !important;
        transition: all 0.2s ease-in-out;
    }

    /* Target the text explicitly so light/dark browser theme cannot make it black */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stRadio"] > div[role="radiogroup"] > label p,
    div[data-testid="stRadio"] > div[role="radiogroup"] > label span {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.01em !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
    }
    
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
        background-color: rgba(56, 189, 248, 0.15) !important;
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover p {
        color: #38BDF8 !important;
    }
    
    /* Selected / Active Tab Pill */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked),
    div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #0284C7 !important;
        box-shadow: 0 2px 10px rgba(2, 132, 199, 0.45);
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p,
    div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] p {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Hide standard circular radio inputs */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }

    div[data-testid="stRadio"] > div[role="radiogroup"] input[type="radio"] {
        display: none !important;
    }

    /* Fallback for native stTabs if present */
    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] span {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] span {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* KPI Metric Cards */
    .kpi-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px 14px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .kpi-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        font-weight: 600;
        margin-bottom: 4px;
    }
    
    .kpi-val {
        font-size: 26px;
        font-weight: 800;
        line-height: 1.2;
    }
    
    .kpi-sub {
        font-size: 11px;
        color: #64748B;
        margin-top: 4px;
    }
    
    /* Insight Banner */
    .insight-box {
        background: #1E293B;
        border-left: 4px solid #38BDF8;
        padding: 16px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    .insight-title {
        font-weight: 700;
        color: #38BDF8;
        font-size: 15px;
        margin-bottom: 6px;
    }
    
    .insight-body {
        color: #E2E8F0;
        font-size: 13.5px;
        line-height: 1.6;
    }
    
    /* Statute Box */
    .statute-box {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 16px;
        margin-top: 8px;
    }

    /* Dual summary cards */
    .summary-card-support {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid #059669;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 14px;
    }
    
    .summary-card-oppose {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid #DC2626;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 14px;
    }
    
    .summary-header {
        font-size: 14.5px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    
    .support-text { color: #34D399; }
    .oppose-text { color: #F87171; }
    
    /* Quote boxes */
    .quote-box {
        background: #0F172A;
        border-left: 3px solid #64748B;
        padding: 10px 12px;
        margin-bottom: 8px;
        font-size: 12.5px;
        color: #CBD5E1;
        font-style: italic;
    }
    
    /* Campaign boxes */
    .flag-reason-banner {
        background: rgba(251, 146, 60, 0.1);
        border: 1px solid #FB923C;
        border-radius: 8px;
        padding: 12px 16px;
        color: #FED7AA;
        font-size: 13px;
        margin-bottom: 14px;
    }
    
    .canonical-box {
        background: #1E293B;
        border: 1px solid #34D399;
        border-radius: 8px;
        padding: 12px 14px;
        font-size: 13px;
        color: #E2E8F0;
        line-height: 1.5;
    }
    
    .duplicate-box {
        background: #1E293B;
        border-left: 3px solid #FB923C;
        padding: 10px 12px;
        margin-bottom: 8px;
        font-size: 12.5px;
        color: #CBD5E1;
        line-height: 1.5;
    }
    
    /* Responsive tweaks */
    @media (max-width: 768px) {
        .gov-title { font-size: 20px; }
        .gov-summary { font-size: 12.5px; }
        .kpi-val { font-size: 22px; }
    }
</style>
""", unsafe_allow_html=True)

DB_PATH = os.path.join("data", "consultation.db")


# ==============================================================================
# Database Connection & Cached Data Loading
# ==============================================================================
@st.cache_resource
def get_connection():
    """Create thread-safe SQLite connection with math functions."""
    import math
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.create_function("ln", 1, lambda x: math.log(x) if x and x > 0 else 0.0)
    conn.create_function("log10", 1, lambda x: math.log10(x) if x and x > 0 else 0.0)
    return conn


@st.cache_data(ttl=60)
def load_overview_data():
    """Load core analytical views and summary totals."""
    conn = get_connection()
    df_raw = pd.read_sql_query("SELECT * FROM v_section_stance_raw", conn)
    df_adj = pd.read_sql_query("SELECT * FROM v_section_stance_adjusted", conn)
    df_controversy = pd.read_sql_query("SELECT * FROM v_controversy_ranking", conn)
    df_trends = pd.read_sql_query("SELECT * FROM v_weekly_trends", conn)
    df_campaigns = pd.read_sql_query("SELECT * FROM campaigns", conn)
    df_sections = pd.read_sql_query("SELECT * FROM sections", conn)
    
    cur = conn.cursor()
    total_comments = cur.execute("SELECT COUNT(*) FROM comments").fetchone()[0]
    total_campaign = cur.execute("SELECT COUNT(*) FROM comments WHERE is_campaign = 1").fetchone()[0]
    total_review = cur.execute("SELECT COUNT(*) FROM predictions WHERE needs_review = 1").fetchone()[0]
    
    pos_comments = cur.execute("SELECT COUNT(*) FROM comments WHERE true_stance = 'support'").fetchone()[0]
    neu_comments = cur.execute("SELECT COUNT(*) FROM comments WHERE true_stance = 'neutral'").fetchone()[0]
    neg_comments = cur.execute("SELECT COUNT(*) FROM comments WHERE true_stance = 'oppose'").fetchone()[0]

    return {
        "df_raw": df_raw,
        "df_adj": df_adj,
        "df_controversy": df_controversy,
        "df_trends": df_trends,
        "df_campaigns": df_campaigns,
        "df_sections": df_sections,
        "total_comments": total_comments,
        "total_campaign": total_campaign,
        "total_review": total_review,
        "pos_comments": pos_comments,
        "neu_comments": neu_comments,
        "neg_comments": neg_comments
    }


# ==============================================================================
# MAIN APPLICATION LAYOUT
# ==============================================================================
def main():
    # 1. Header (Task 1)
    render_header()
    
    # 2. Load Cached Analytical Data
    try:
        data = load_overview_data()
        conn = get_connection()
    except Exception as e:
        st.error(f"Error connecting to consultation database: {e}")
        return

    # 3. State-Preserving Navigation Tabs (Never resets on form submit or rerun)
    tab_options = [
        "📊 Overview",
        "📜 Clauses",
        "💬 Sentiment",
        "🛡️ Campaigns",
        "💡 Insights",
        "📁 Data & Export",
        "🎯 Evaluation"
    ]
    
    selected_tab = st.radio(
        "Navigation",
        options=tab_options,
        horizontal=True,
        key="active_nav_tab",
        label_visibility="collapsed"
    )

    # Tab 1: Overview
    if selected_tab == "📊 Overview":
        render_overview_tab(data)

    # Tab 2: Clauses
    elif selected_tab == "📜 Clauses":
        render_clauses_tab(data, conn)

    # Tab 3: Sentiment
    elif selected_tab == "💬 Sentiment":
        render_sentiment_tab(data, conn)

    # Tab 4: Campaign Detection
    elif selected_tab == "🛡️ Campaigns":
        render_campaigns_tab(data, conn)

    # Tab 5: Insights
    elif selected_tab == "💡 Insights":
        render_insights_tab(data)

    # Tab 6: Data & Export
    elif selected_tab == "📁 Data & Export":
        render_data_tab(conn, data)

    # Tab 7: Evaluation & Live Tester
    elif selected_tab == "🎯 Evaluation":
        render_evaluation_tab()


if __name__ == "__main__":
    main()
