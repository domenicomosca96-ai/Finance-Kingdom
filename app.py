"""
AlphaEdge — AI Investment Advisor
Streamlit Application Entry Point

A professional AI swing trading operating system combining:
- Deterministic PAM engine (Piranha Profits methodology)
- Gemini 3 AI analysis (server-side only)
- Options strategy mapping (Bang Van matrix)
- Position sizing (Kelly criterion + risk rules)
"""

import streamlit as st

st.set_page_config(
    page_title="AlphaEdge — AI Investment Advisor",
    page_icon="$",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════
#  CUSTOM CSS — Professional dark terminal aesthetic
#  NOTE: Do NOT hide header — it contains the sidebar toggle
# ═══════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0a0e14; }

    /* Sidebar — always visible, min width */
    [data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #1e2530;
        min-width: 280px;
    }

    /* Sidebar navigation items */
    [data-testid="stSidebar"] .stRadio > label {
        font-size: 1rem;
    }
    [data-testid="stSidebar"] .stRadio > div > label {
        padding: 8px 12px;
        border-radius: 6px;
        margin-bottom: 2px;
    }
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background-color: #1a2332;
    }

    /* Cards / containers */
    [data-testid="stExpander"] {
        background-color: #111820;
        border: 1px solid #1e2530;
        border-radius: 8px;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }

    /* Headers */
    h1, h2, h3 { color: #e6edf3; }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #111820;
        border-radius: 8px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
        color: #8b949e;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a2332;
        color: #22c55e;
    }

    /* Success/error colors */
    .score-high { color: #22c55e; font-weight: bold; }
    .score-medium { color: #f59e0b; font-weight: bold; }
    .score-low { color: #ef4444; font-weight: bold; }

    /* Table styling */
    .dataframe { font-size: 0.85rem; }

    /* Only hide Streamlit footer — keep header for sidebar toggle */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════

PAGES = {
    "Dashboard": "Dashboard — Overview",
    "Watchlist": "Watchlist — Control Center",
    "Analysis": "Analysis — AI Trade Ideas",
    "PAM Engine": "PAM Engine — Price Action",
    "PAM Library": "PAM Library — Setup Catalog",
    "Knowledge Base": "Knowledge Base — Documents",
    "Journal": "Journal — Trade Log",
    "Settings": "Settings — Config & Weights",
}

with st.sidebar:
    st.markdown("## AlphaEdge")
    st.markdown("**AI Investment Advisor**")
    st.divider()

    page = st.radio(
        "Navigate to:",
        list(PAGES.keys()),
        format_func=lambda x: PAGES[x],
        index=0,
    )

    st.divider()
    st.markdown("**Quick Actions**")
    if st.button("Run Analysis", type="primary", use_container_width=True, key="sidebar_run"):
        page = "Analysis"
        st.session_state["_force_page"] = "Analysis"
        st.rerun()

    st.divider()
    st.caption("Powered by Gemini 2.5 Pro + PAM Engine")
    st.caption("6-layer signal hierarchy | 9-insight regime framework")

# Handle forced page navigation from sidebar button
if "_force_page" in st.session_state:
    page = st.session_state.pop("_force_page")


# ═══════════════════════════════════════════════════════════
#  PAGE ROUTER
# ═══════════════════════════════════════════════════════════

if page == "Dashboard":
    from streamlit_app.pages.dashboard import render
    render()
elif page == "Watchlist":
    from streamlit_app.pages.watchlist_manager import render
    render()
elif page == "Analysis":
    from streamlit_app.pages.analysis import render
    render()
elif page == "PAM Engine":
    from streamlit_app.pages.pam_engine import render
    render()
elif page == "PAM Library":
    from streamlit_app.pages.pam_library import render
    render()
elif page == "Knowledge Base":
    from streamlit_app.pages.knowledge_base import render
    render()
elif page == "Journal":
    from streamlit_app.pages.journal import render
    render()
elif page == "Settings":
    from streamlit_app.pages.settings_page import render
    render()
