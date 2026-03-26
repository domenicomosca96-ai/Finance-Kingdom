# AlphaEdge v3 — Handoff Document

## What the App Does

AlphaEdge is a personal AI investment operating system for swing trading and macro/liquidity-driven analysis. It combines:

1. **Deterministic PAM Engine** — Piranha Profits methodology for pattern detection (UC1, UR2, DR2, DC1), flow state analysis, momentum classification, and accumulation/distribution rotation
2. **Gemini 3 AI Layer** — 4-step chain-of-thought pipeline for macro synthesis, thesis generation, score validation, and investment memo formatting
3. **Options Strategy Mapper** — Bang Van's complete strategy selection matrix across IV regimes
4. **Position Sizing** — Kelly criterion + Piranha Profits 2% risk rules
5. **Knowledge Base** — RAG retrieval over custom documents using pgvector embeddings
6. **Trade Journal** — Track entries, exits, P/L for calibration

## Architecture Summary

```
Single Streamlit app (app.py)
├── 6 UI pages (dashboard, pam, analysis, knowledge, journal, settings)
├── Core engine (pure Python, no LLM)
│   ├── PAM engine (market_data.py — 400+ lines of deterministic logic)
│   ├── Scoring (logistic sigmoid + Kelly criterion)
│   └── Options mapper (16 strategies from Bang Van matrix)
├── AI layer (Gemini 3, server-side only)
│   ├── 4-step chain (context > analyst > critic > formatter)
│   └── Embeddings (text-embedding-004, 768 dim)
├── Database (PostgreSQL + pgvector)
│   ├── 6 tables (document_chunks, daily_bars, pam_signals, trade_ideas, journal, analysis_jobs)
│   └── Hash-based deduplication for document ingestion
└── Knowledge base (6 built-in markdown files)
```

## Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | **Yes** | Google Gemini API key (get from aistudio.google.com/apikey) |
| `DATABASE_URL` | **Yes** | PostgreSQL connection string with pgvector |
| `GEMINI_MODEL` | No | Default: `gemini-2.5-flash` |
| `PORTFOLIO_SIZE` | No | Default: `100000` |

See `.env.example` for all optional parameters.

## Exact Run Command (Local)

```bash
# Prerequisites: Python 3.11+, PostgreSQL 16 with pgvector

# Setup
cp .env.example .env
# Edit .env: set GEMINI_API_KEY and DATABASE_URL

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
streamlit run app.py
```

## Exact Run Command (Docker)

```bash
cp .env.example .env
# Edit .env: set GEMINI_API_KEY

docker compose up -d
# App at http://localhost:8501
```

## Exact Deploy Steps

### Streamlit Community Cloud
1. Push repo to GitHub
2. Go to share.streamlit.io > New app > Select repo > Main file: `app.py`
3. Add secrets: `GEMINI_API_KEY`, `DATABASE_URL` (external PostgreSQL required — use Supabase or Neon free tier)
4. Deploy

### Railway
1. New project from GitHub repo
2. Add PostgreSQL service, run `CREATE EXTENSION vector;`
3. Set env vars: `GEMINI_API_KEY`, `DATABASE_URL=${{Postgres.DATABASE_URL}}`
4. Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`

## Smoke Tests

After deployment, verify in this order:

1. **Settings > Test Gemini Connection** — Should return "Connected"
2. **Settings > Test Database** — Should show PostgreSQL version + pgvector OK
3. **Settings > Initialize Database** — Creates all 6 tables
4. **Settings > Test Embeddings** — Should return 768-dim vector
5. **Knowledge Base > Bootstrap** — Should ingest 6 markdown files (~30-40 chunks)
6. **PAM Engine > AAPL** — Should return flow state, momentum, pattern analysis
7. **Analysis > NVDA** — Full 4-step Gemini chain + scoring + options
8. **Journal > New Entry** — Should persist to database
9. **Dashboard** — Should show stats and recent analyses

## Post-Deploy Checks

- [ ] All 6 Streamlit pages load without errors
- [ ] Gemini API responds (Settings page test)
- [ ] Database is accessible and tables exist
- [ ] Knowledge base has been bootstrapped
- [ ] PAM engine returns valid results for at least 3 tickers
- [ ] Full analysis pipeline completes end-to-end
- [ ] Journal entries persist across page reloads
- [ ] No API keys visible in browser (check Network tab)

## Known Limitations

1. **yfinance rate limits** — Heavy usage may hit Yahoo Finance rate limits. Use `@st.cache_data` (already implemented) to mitigate.
2. **IV Rank is a proxy** — yfinance doesn't provide historical IV; the IV rank is estimated from realized volatility.
3. **No real-time data** — Uses EOD (end-of-day) data from yfinance. Not suitable for intraday trading.
4. **Gemini latency** — The 4-step chain makes 4 sequential API calls. Full analysis takes 15-30 seconds per watchlist.
5. **pgvector required** — The embedding/RAG pipeline requires PostgreSQL with pgvector. Cannot use SQLite.
6. **Single-user** — No authentication or multi-user support. Designed as a personal tool.
7. **Streamlit session state** — Long-running analyses may timeout on Streamlit Cloud (free tier has resource limits).

## Next Recommended Improvements

1. Add `@st.cache_data` with TTL to PAM engine calls for same-day ticker re-analysis
2. Add charting (plotly) for PAM visualization with swing points and SMA overlays
3. Add export functionality (PDF/CSV) for analysis results
4. Add watchlist management (save/load watchlists)
5. Add alerts/notifications when PAM patterns are detected
6. Consider Gemini context caching for knowledge base (reduce embedding costs)
7. Add authentication if deploying publicly
