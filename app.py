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
# ═══════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0a0e14; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #1e2530;
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

    /* Hide Streamlit branding but keep header for sidebar toggle */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### AlphaEdge")
    st.caption("AI Investment Advisor v3")
    st.divider()

    page = st.radio(
        "Navigation",
        ["Dashboard", "PAM Engine", "Analysis", "Knowledge Base", "Journal", "Settings"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("Powered by Gemini 3 + PAM Engine")
    st.caption("Server-side AI only — no client exposure")


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
