"""
AlphaEdge — AI Investment Advisor
Streamlit Application Entry Point

A professional AI swing trading operating system combining:
- Deterministic PAM engine (Piranha Profits methodology)
- Gemini AI analysis (server-side only)
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
#  CUSTOM CSS — Professional dark design
#  NOTE: Do NOT hide header — it contains the sidebar toggle
# ═══════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0a0e14;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #0a0e14 100%);
        border-right: 1px solid #22c55e20;
        min-width: 280px;
    }
    [data-testid="stSidebar"] .stRadio > div > label {
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 4px;
        transition: background-color 0.2s;
    }
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background-color: #22c55e15;
    }

    /* Expander cards */
    [data-testid="stExpander"] {
        background-color: #111820;
        border: 1px solid #1e2530;
        border-radius: 10px;
    }

    /* Metrics — green accent */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #e6edf3;
    }
    [data-testid="stMetricDelta"] svg { display: none; }

    /* Headers */
    h1 { color: #e6edf3; font-weight: 800; }
    h2 { color: #c9d1d9; font-weight: 700; }
    h3 { color: #8b949e; font-weight: 600; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #111820;
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 18px;
        color: #8b949e;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #22c55e20;
        color: #22c55e;
        font-weight: 600;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 20px;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
    }

    /* Score colors */
    .score-high { color: #22c55e; font-weight: bold; }
    .score-medium { color: #f59e0b; font-weight: bold; }
    .score-low { color: #ef4444; font-weight: bold; }

    /* Dividers */
    hr { border-color: #1e2530 !important; }

    /* Info/warning/error boxes */
    [data-testid="stAlert"] {
        border-radius: 8px;
    }

    /* Multiselect chips */
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background-color: #22c55e30;
        border-radius: 6px;
    }

    /* Table styling */
    .dataframe { font-size: 0.85rem; }

    /* Only hide footer — keep header for sidebar toggle */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════

PAGES = {
    "Dashboard": "Dashboard — Overview",
    "Analysis": "Analysis — AI Trade Ideas",
    "PAM Engine": "PAM Engine — Price Action",
    "Knowledge Base": "Knowledge Base — Documents",
    "Journal": "Journal — Trade Log",
    "Settings": "Settings — Config & Weights",
}

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 5px 0;">
        <span style="font-size: 2rem; font-weight: 800; color: #22c55e;">AlphaEdge</span><br/>
        <span style="font-size: 0.85rem; color: #8b949e;">AI Investment Advisor</span>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navigate to:",
        list(PAGES.keys()),
        format_func=lambda x: PAGES[x],
        index=0,
    )

    st.divider()
    if st.button("Run Analysis", type="primary", use_container_width=True, key="sidebar_run"):
        st.session_state["_force_page"] = "Analysis"
        st.rerun()

    st.divider()
    st.caption("Powered by Gemini 2.5 Flash + PAM Engine")
    st.caption("6-layer hierarchy | 9-insight regime framework")

# Handle forced page navigation from sidebar button
if "_force_page" in st.session_state:
    page = st.session_state.pop("_force_page")


# ═══════════════════════════════════════════════════════════
#  PAGE ROUTER
# ═══════════════════════════════════════════════════════════

if page == "Dashboard":
    from streamlit_app.pages.dashboard import render
    render()
elif page == "PAM Engine":
    from streamlit_app.pages.pam_engine import render
    render()
elif page == "Analysis":
    from streamlit_app.pages.analysis import render
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
