"""Settings / Admin — Connectivity tests, environment validation, diagnostics."""

import streamlit as st


def render():
    st.title("Settings & Admin")
    st.caption("System diagnostics, connectivity tests, and environment validation")

    tab1, tab2, tab3 = st.tabs(["Connectivity", "Environment", "Database"])

    with tab1:
        _render_connectivity()

    with tab2:
        _render_environment()

    with tab3:
        _render_database()


def _render_connectivity():
    st.subheader("Connectivity Tests")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Gemini API**")
        if st.button("Test Gemini Connection", type="primary"):
            with st.spinner("Testing Gemini API..."):
                try:
                    from google import genai
                    from core.config import settings

                    if not settings.GEMINI_API_KEY:
                        st.error("GEMINI_API_KEY is not set in environment variables.")
                    else:
                        client = genai.Client(api_key=settings.GEMINI_API_KEY)
                        response = client.models.generate_content(
                            model=settings.MODEL,
                            contents="Say 'AlphaEdge connection verified' in exactly those words.",
                        )
                        st.success(f"Gemini connected. Model: {settings.MODEL}")
                        st.code(response.text[:200])
                except Exception as e:
                    st.error(f"Gemini connection failed: {str(e)}")

    with col2:
        st.markdown("**Database (PostgreSQL)**")
        if st.button("Test Database Connection"):
            with st.spinner("Testing database..."):
                try:
                    from core.models.database import engine
                    from sqlalchemy import text

                    with engine.connect() as conn:
                        result = conn.execute(text("SELECT version()"))
                        version = result.scalar()

                        # Check pgvector
                        try:
                            conn.execute(text("SELECT 'test'::vector(3)"))
                            pgvector_ok = True
                        except Exception:
                            pgvector_ok = False

                    st.success(f"Database connected.")
                    st.code(version[:100] if version else "Unknown version")
                    if pgvector_ok:
                        st.success("pgvector extension: OK")
                    else:
                        st.warning("pgvector extension: NOT available (run: CREATE EXTENSION vector)")
                except Exception as e:
                    st.error(f"Database connection failed: {str(e)}")

    st.divider()

    st.markdown("**Embedding Test**")
    if st.button("Test Gemini Embeddings"):
        with st.spinner("Testing embedding generation..."):
            try:
                from google import genai
                from google.genai import types
                from core.config import settings
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                result = client.models.embed_content(
                    model=settings.EMBEDDING_MODEL,
                    contents="AlphaEdge test embedding",
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
                )
                emb = result.embeddings[0].values
                st.success(f"Embedding OK — dimension: {len(emb)}")
                st.code(f"First 5 values: {emb[:5]}")
            except Exception as e:
                st.error(f"Embedding test failed: {str(e)}")


def _render_environment():
    st.subheader("Environment Variables")

    from core.config import settings

    env_vars = {
        "GEMINI_API_KEY": "***" + settings.GEMINI_API_KEY[-4:] if len(settings.GEMINI_API_KEY) > 4 else ("SET" if settings.GEMINI_API_KEY else "NOT SET"),
        "GEMINI_MODEL": settings.MODEL,
        "EMBEDDING_MODEL": settings.EMBEDDING_MODEL,
        "EMBEDDING_DIM": str(settings.EMBEDDING_DIM),
        "DATABASE_URL": settings.DATABASE_URL[:50] + "..." if len(settings.DATABASE_URL) > 50 else settings.DATABASE_URL,
        "SCORE_THRESHOLD": str(settings.SCORE_THRESHOLD),
        "LOGISTIC_K": str(settings.LOGISTIC_K),
        "LOGISTIC_C": str(settings.LOGISTIC_C),
        "W_MACRO / W_THEME / W_PAM": f"{settings.W_MACRO} / {settings.W_THEME} / {settings.W_PAM}",
        "KELLY_FRACTION": str(settings.KELLY_FRACTION),
        "MAX_RISK_PER_TRADE": f"{settings.MAX_RISK_PER_TRADE_PCT}%",
        "MAX_PORTFOLIO_HEAT": f"{settings.MAX_PORTFOLIO_HEAT_PCT}%",
        "PORTFOLIO_SIZE": f"${settings.PORTFOLIO_SIZE:,.0f}",
    }

    for name, value in env_vars.items():
        c1, c2 = st.columns([1, 2])
        c1.markdown(f"**{name}**")
        c2.code(value)

    st.divider()
    st.subheader("Scoring Test")

    with st.form("scoring_test"):
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            test_macro = st.number_input("Macro Score", 0.0, 100.0, 65.0)
        with sc2:
            test_theme = st.number_input("Theme Score", 0.0, 100.0, 70.0)
        with sc3:
            test_pam = st.number_input("PAM Score", 0.0, 100.0, 75.0)

        if st.form_submit_button("Test Logistic Scoring"):
            from core.scoring import compute_score
            result = compute_score(test_macro, test_theme, test_pam)
            r1, r2, r3 = st.columns(3)
            r1.metric("Raw Composite", f"{result.raw_composite:.1f}")
            r2.metric("Probability", f"{result.probability_pct:.1f}%")
            r3.metric("Confidence Tier", result.confidence_tier.upper())


def _render_database():
    st.subheader("Database Management")

    if st.button("Initialize / Create Tables"):
        with st.spinner("Creating tables..."):
            try:
                from core.models.database import init_db
                init_db()
                st.success("Database tables created successfully (pgvector extension enabled).")
            except Exception as e:
                st.error(f"Table creation failed: {str(e)}")

    st.divider()

    st.markdown("**Table Row Counts**")
    try:
        from core.models.database import engine
        from sqlalchemy import text

        tables = ["document_chunks", "daily_bars", "pam_signals", "trade_ideas", "journal", "analysis_jobs"]
        with engine.connect() as conn:
            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT count(*) FROM {table}"))
                    count = result.scalar()
                    st.text(f"  {table}: {count} rows")
                except Exception:
                    st.text(f"  {table}: (table not found)")
    except Exception as e:
        st.warning(f"Cannot connect: {str(e)}")
