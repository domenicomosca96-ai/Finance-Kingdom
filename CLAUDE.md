# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
streamlit run app.py          # start locally (port 8501)
docker compose up -d          # start with bundled PostgreSQL
```

No test suite or linter is configured. The `tests/` directory is empty.

## Environment

Copy `.env.example` to `.env` and set:
- `GEMINI_API_KEY` — Google Gemini API key (server-side only, never exposed to browser)
- `DATABASE_URL` — PostgreSQL connection string (default: `postgresql://alpha:alpha@localhost:5432/alphaedge`)

On Streamlit Cloud, configure the same keys under **Settings → Secrets** (the config layer reads `st.secrets` first, then env vars — see `core/config/__init__.py`).

## Architecture

Single-file Streamlit entry point (`app.py`) routes to eight page modules. Business logic lives entirely in `core/`; UI in `streamlit_app/`.

```
core/
  config/__init__.py       # Settings class — all tuneable params (weights, thresholds, model)
  config/watchlist.py      # 108-ticker watchlist with sensitivity tags + metadata helpers
  models/__init__.py       # SQLAlchemy ORM (9 tables); init via core/models/database.py
  pam/                     # Deterministic PAM engine (Piranha Profits methodology)
    market_data.py         # yfinance OHLCV + indicators (SMA/EMA/ATR/RSI, swing detection)
    setup_library.py       # Pattern detection: UC1/UC2/UR2/UR1/DC1/DC2/DR2/DR1 + scoring
  options/options_mapper.py  # Bang Van strategy matrix → leg construction + payoff
  scoring/__init__.py      # Logistic probability transform + fractional Kelly sizing

streamlit_app/
  services/
    gemini_chain.py        # 4-step Gemini chain: Context Builder → Analyst → Critic → Formatter
    bootstrap.py           # Ingest markdown from data/knowledge/ → chunk → embed → pgvector
    retrieval.py           # pgvector cosine search; multi-collection RAG retrieval
  pages/                   # 8 UI pages (dashboard, watchlist_manager, analysis, pam_engine,
                           #   pam_library, knowledge_base, journal, settings_page)

data/knowledge/            # 9 markdown files loaded into pgvector at startup
```

### Analysis Pipeline (core flow in `streamlit_app/pages/analysis.py`)

1. Run PAM engine per ticker → `FullPAMResult` (pattern, flow_state, micro_score, levels)
2. RAG retrieval → top-k chunks from `document_chunks` via pgvector
3. Gemini 4-step chain (all server-side) → macro/theme scores + trade thesis JSON
4. Composite score: `0.45 × macro + 0.35 × theme + 0.20 × pam` → logistic probability
5. Kelly sizing with hard caps: 2% per-trade risk, 6% portfolio heat, 5% max position
6. Persist `TradeIdea` to PostgreSQL; surface in UI

### Signal Weights (configurable via env or Settings page)

| Layer | Weight | Env var |
|-------|--------|---------|
| Global Liquidity (Howell GLI) | 35% | `W_MACRO` covers layers 1+4 |
| Sector Trends | 25% | `W_THEME` |
| PAM / Price Action | 15% | `W_PAM` |
| Intermarket | 10% | — |
| Fundamentals | 10% | — |
| Elliott Wave | 5% | — |

`W_MACRO` defaults to 0.45, `W_THEME` to 0.35, `W_PAM` to 0.20 (sum = 1.0).

### Database

PostgreSQL 16 + pgvector extension. Key tables:
- `document_chunks` — RAG vectors (768-dim, IVFFlat index, cosine distance)
- `daily_bars` — OHLCV cache (unique on ticker + dt)
- `pam_signals` — deterministic engine output per ticker/date
- `trade_ideas` — AI-generated trade recommendations with scores + sizing
- `watchlist_items` — user watchlist with asset class, tier, options flags, sensitivity tags

Schema is created automatically by `core/models/database.py:init_db()` on first run.

### Gemini Models

- Analysis: `gemini-2.5-flash` (default free tier; override via `GEMINI_MODEL` env var)
- Embeddings: `text-embedding-004` (768 dimensions, hardcoded in `core/config/__init__.py`)

Free-tier API key has **zero quota** for `gemini-2.5-pro` — use `gemini-2.5-flash` unless a paid key is configured.

## Key Conventions

- **PAM patterns** are uppercase strings: `UC1`, `UR2`, `DC1`, `DR2`, etc. The `NONE` sentinel means no valid pattern detected.
- **Confidence tiers**: `high` (≥72%), `medium` (58–72%), `low` (45–58%), `no_trade` (<45%). Options are only recommended when probability ≥ 72% AND `options_liquid = true`.
- **Knowledge base** markdown files in `data/knowledge/` are the LLM's primary reasoning source. Add new files there and re-bootstrap to extend the model's domain knowledge. Collections: `macro_liquidity`, `trading_methods`, `pam_structures`, `tech_reports`, `watchlist_setups`.
- **Secrets**: `GEMINI_API_KEY` must never reach the browser — all Gemini calls are in Python backend only.
