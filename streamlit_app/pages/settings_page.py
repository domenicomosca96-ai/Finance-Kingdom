"""Settings / Admin — Connectivity tests, environment validation, diagnostics."""

import streamlit as st


def render():
    st.title("Settings & Admin")
    st.caption("System diagnostics, connectivity tests, and environment validation")

    tab1, tab2, tab3, tab4 = st.tabs(["Connectivity", "Signal Weighting", "Environment", "Database"])

    with tab1:
        _render_connectivity()

    with tab2:
        _render_signal_weighting()

    with tab3:
        _render_environment()

    with tab4:
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
                        st.error("GEMINI_API_KEY is not set. Add it in Streamlit secrets.")
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

                        try:
                            conn.execute(text("SELECT 'test'::vector(3)"))
                            pgvector_ok = True
                        except Exception:
                            pgvector_ok = False

                    st.success("Database connected.")
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

    st.divider()
    st.subheader("Setup Checklist")
    st.markdown("""
**To get AlphaEdge fully working, you need:**

1. **Gemini API Key** — Get one free at [ai.google.dev](https://ai.google.dev)
   - Add `GEMINI_API_KEY` to your Streamlit secrets
   - Free tier supports `gemini-2.5-flash` (default model)

2. **Neon.tech Database** — Free PostgreSQL at [neon.tech](https://neon.tech)
   - Create a project, copy the connection string
   - Add `DATABASE_URL` to your Streamlit secrets
   - Format: `postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require`

3. **Streamlit Secrets** — In your app dashboard, click "Settings" > "Secrets":
   ```toml
   GEMINI_API_KEY = "AIzaSy..."
   DATABASE_URL = "postgresql://neondb_owner:YOUR_PASSWORD@ep-xxx.eu-central-1.aws.neon.tech/neondb?sslmode=require"
   ```

4. **Initialize DB** — Go to Database tab > click "Initialize / Create Tables"
5. **Bootstrap KB** — Go to Knowledge Base page > click "Bootstrap Built-in Documents"
""")


def _render_signal_weighting():
    st.subheader("How AlphaEdge Weights Signals")

    from core.config import settings

    st.markdown("""
**AlphaEdge uses a 6-layer signal hierarchy mapped to 3 computational pillars:**

The 6 strategic layers are compressed into 3 scorable dimensions, then combined
using configurable weights and mapped through a logistic sigmoid to produce a
final trade probability.
""")

    st.markdown("### Signal Hierarchy (6 Layers)")
    st.markdown("""
| Layer | Weight | What it decides |
|-------|--------|----------------|
| **Global Liquidity** (Howell GLI) | 35% | Risk-on vs risk-off. Country allocation. |
| **Sector Trends / Leadership** | 25% | Where to concentrate risk. |
| **PAM / Price Action** | 15% | When to enter, where to invalidate. |
| **Intermarket Confirmation** | 10% | DXY, MOVE, yield curve, breadth, credit spreads. |
| **Fundamentals** | 10% | Quality filter, narrative coherence. |
| **Elliott Wave** | 5% | Maturity/asymmetry map only, never a trigger. |
""")

    st.markdown("### How Layers Map to Scoring Pillars")
    w1, w2, w3 = st.columns(3)
    w1.metric("Macro Pillar", f"{settings.W_MACRO * 100:.0f}%",
              help="Global Liquidity 35% + Intermarket 10% = 45%")
    w2.metric("Theme Pillar", f"{settings.W_THEME * 100:.0f}%",
              help="Sector Trends 25% + Fundamentals 10% = 35%")
    w3.metric("PAM Pillar", f"{settings.W_PAM * 100:.0f}%",
              help="Price Action 15% + Elliott 5% = 20%")

    st.markdown(f"""
### Core Principle: LIQUIDITY > INFLATION > DOLLAR

1. **Liquidity** decides if you are risk-on or risk-off
2. **Inflation** decides what TYPE of risk-on/risk-off (demand-pull vs supply-shock vs debt-deflation)
3. **DXY** decides how favorable the global regime is (with nuance — WHY is DXY strong matters)

### Three-Layer Regime Classification

Each analysis first classifies the macro environment:

| Layer | Options | Meaning |
|-------|---------|---------|
| Liquidity | Accelerating / Flat / Decelerating | From Howell GLI + regional divergence |
| Inflation | Benign disinflation / Sweet-spot / Overheating / Stagflation / Debt-deflation | Type matters more than level |
| Dollar | Bullish / Neutral / Bearish | With conditional logic based on WHY |

### Financial Conditions Triangle

```
Yields DOWN + DXY DOWN + Commodities Stable  = SWEET SPOT (full risk-on)
Yields UP   + DXY DOWN + Commodities UP      = REFLATION (commodities lead)
Yields UP   + DXY UP   + Commodities UP      = STAGFLATION (gold/BTC only)
Yields DOWN + DXY UP   + Commodities DOWN     = DEFLATION SCARE (duration up)
```

### Duration Bucket Framework

| Bucket | Assets | Favored when |
|--------|--------|-------------|
| Short duration / collateral | Cash, T-bills | Liquidity decelerating |
| Medium duration defensives | Quality bonds | Deflation scare |
| Long duration growth | Tech, growth | Liquidity accelerating + conditions easing |
| Monetary hedges | Gold, BTC | Fiscal dominance, monetary inflation |
| Cyclical reflation | Commodities, energy | China easing, bearish DXY |

### Scoring Formula

```
composite = (Macro x {settings.W_MACRO}) + (Theme x {settings.W_THEME}) + (PAM x {settings.W_PAM})
probability = 100 / (1 + exp(-{settings.LOGISTIC_K} * (composite - {settings.LOGISTIC_C})))
```

### Confidence Tiers & Trade Types
| Tier | Probability | Trade Type |
|------|------------|------------|
| **HIGH** | >= 72% | Full position + Options eligible |
| **MEDIUM** | >= 58% | Reduced stock position only |
| **LOW** | >= 45% | Watchlist only |
| **NO TRADE** | < 45% | Skip |

### Customizing Weights
Environment variables or Streamlit secrets:
- `W_MACRO` = {settings.W_MACRO} (GLI + Intermarket)
- `W_THEME` = {settings.W_THEME} (Sectors + Fundamentals)
- `W_PAM` = {settings.W_PAM} (Price Action + Elliott)
""")

    st.divider()
    st.subheader("Interactive Weight Tester")
    with st.form("weight_test"):
        wc1, wc2, wc3 = st.columns(3)
        with wc1:
            tw_macro = st.slider("Macro Weight", 0.0, 1.0, settings.W_MACRO, 0.05)
        with wc2:
            tw_theme = st.slider("Theme Weight", 0.0, 1.0, settings.W_THEME, 0.05)
        with wc3:
            tw_pam = st.slider("PAM Weight", 0.0, 1.0, settings.W_PAM, 0.05)

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            test_macro = st.number_input("Test Macro Score", 0.0, 100.0, 65.0)
        with sc2:
            test_theme = st.number_input("Test Theme Score", 0.0, 100.0, 70.0)
        with sc3:
            test_pam = st.number_input("Test PAM Score", 0.0, 100.0, 75.0)

        if st.form_submit_button("Calculate"):
            import math
            total_w = tw_macro + tw_theme + tw_pam
            if total_w == 0:
                st.error("Weights cannot all be zero.")
            else:
                nw_macro = tw_macro / total_w
                nw_theme = tw_theme / total_w
                nw_pam = tw_pam / total_w
                composite = test_macro * nw_macro + test_theme * nw_theme + test_pam * nw_pam
                prob = 100.0 / (1.0 + math.exp(-settings.LOGISTIC_K * (composite - settings.LOGISTIC_C)))

                r1, r2, r3 = st.columns(3)
                r1.metric("Composite", f"{composite:.1f}")
                r2.metric("Probability", f"{prob:.1f}%")
                tier = "HIGH" if prob >= 72 else "MEDIUM" if prob >= 58 else "LOW" if prob >= 45 else "NO TRADE"
                r3.metric("Tier", tier)
                st.info(f"Normalized weights: Macro={nw_macro:.2f}, Theme={nw_theme:.2f}, PAM={nw_pam:.2f}")


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
