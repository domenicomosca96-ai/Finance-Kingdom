"""Dashboard — System overview, latest analyses, knowledge stats, watchlist summary."""

import streamlit as st
from datetime import datetime, date


def render():
    st.title("Dashboard")
    st.caption(f"System overview — {date.today().strftime('%B %d, %Y')}")

    # ── Status metrics row ──
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        db_ok = _check_db()
        st.metric("Database", "Online" if db_ok else "Offline")
    with col2:
        gemini_ok = _check_gemini()
        st.metric("Gemini API", "Connected" if gemini_ok else "Not configured")
    with col3:
        kb_stats = _get_kb_stats()
        st.metric("Knowledge Chunks", kb_stats.get("total", 0))
    with col4:
        trade_count = _get_trade_count()
        st.metric("Trade Ideas (30d)", trade_count)

    st.divider()

    # ── Two-column layout ──
    left, right = st.columns([2, 1])

    with left:
        st.subheader("Latest Analyses")
        ideas = _get_recent_ideas()
        if ideas:
            for idea in ideas:
                _render_idea_card(idea)
        else:
            st.info("No analyses yet. Go to **Analysis** to run your first watchlist scan.")

        st.subheader("Watchlist Overview")
        from core.config.watchlist import WATCHLIST
        for cat, tickers in WATCHLIST.items():
            with st.expander(f"{cat} ({len(tickers)} tickers)"):
                cols = st.columns(4)
                for i, (sym, name) in enumerate(tickers.items()):
                    cols[i % 4].markdown(f"`{sym}` {name}")

    with right:
        st.subheader("Knowledge Base")
        if kb_stats.get("collections"):
            for coll, count in kb_stats["collections"].items():
                st.markdown(f"**{coll.replace('_', ' ').title()}** — {count} chunks")
        else:
            st.info("Knowledge base empty. Go to **Knowledge Base** to bootstrap.")

        st.subheader("System Health")
        _render_health()


def _render_idea_card(idea):
    """Render a single trade idea as an expander card."""
    score_color = "score-high" if idea.probability_pct >= 72 else "score-medium" if idea.probability_pct >= 58 else "score-low"
    direction_icon = "LONG" if idea.direction == "long" else "SHORT" if idea.direction == "short" else "NEUTRAL"

    with st.expander(f"{idea.ticker} — {direction_icon} — {idea.probability_pct:.1f}%", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric("Macro", f"{idea.raw_macro:.0f}")
        c2.metric("Theme", f"{idea.raw_theme:.0f}")
        c3.metric("PAM", f"{idea.raw_pam:.0f}")

        if idea.thesis:
            st.markdown(f"**Thesis:** {idea.thesis[:300]}")
        if idea.option_strategy:
            st.markdown(f"**Options:** {idea.option_strategy}")
        st.caption(f"Created: {idea.created_at.strftime('%Y-%m-%d %H:%M') if idea.created_at else 'N/A'}")


@st.cache_data(ttl=60)
def _check_db() -> bool:
    try:
        from core.models.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@st.cache_data(ttl=300)
def _check_gemini() -> bool:
    from core.config import settings
    return bool(settings.GEMINI_API_KEY)


@st.cache_data(ttl=30)
def _get_kb_stats() -> dict:
    try:
        from core.models.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT collection, count(*) FROM document_chunks GROUP BY collection ORDER BY collection"
            ))
            collections = {row[0]: row[1] for row in result}
            total = sum(collections.values())
        return {"total": total, "collections": collections}
    except Exception:
        return {"total": 0, "collections": {}}


@st.cache_data(ttl=30)
def _get_trade_count() -> int:
    try:
        from core.models.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT count(*) FROM trade_ideas WHERE dt >= current_date - interval '30 days'"
            ))
            return result.scalar() or 0
    except Exception:
        return 0


def _get_recent_ideas():
    try:
        from core.models.database import SessionLocal
        from core.models import TradeIdea
        with SessionLocal() as db:
            return db.query(TradeIdea).order_by(TradeIdea.created_at.desc()).limit(10).all()
    except Exception:
        return []


def _render_health():
    from core.config import settings
    checks = {
        "GEMINI_API_KEY": bool(settings.GEMINI_API_KEY),
        "DATABASE_URL": bool(settings.DATABASE_URL),
        "Database": _check_db(),
    }
    for name, ok in checks.items():
        icon = "OK" if ok else "MISSING"
        st.markdown(f"{'[OK]' if ok else '[!!]'} {name}: **{icon}**")
