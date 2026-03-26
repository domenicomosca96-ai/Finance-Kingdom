# AlphaEdge v3 — AI Investment Advisor

A professional AI swing trading operating system combining deterministic technical analysis (Piranha Profits PAM methodology) with Gemini 3 AI for macro/liquidity synthesis, thesis generation, and investment memo creation.

## Features

- **PAM Engine** — Deterministic Price Action & Momentum detection (UC1, UR2, DR2, DC1 patterns, flow state, rotation segments)
- **AI Analysis** — 4-step Gemini chain (Context Builder > Analyst > Critic > Formatter) for rigorous trade idea generation
- **Options Mapping** — Complete Bang Van strategy matrix (16 strategies across IV regimes)
- **Position Sizing** — Kelly criterion + Piranha Profits 2% risk rule
- **Knowledge Base** — RAG with pgvector, PDF/Markdown ingestion, hash-based deduplication
- **Trade Journal** — Track entries, exits, P/L, and calibrate AI accuracy over time
- **Professional UI** — Dark terminal-style Streamlit interface

## Architecture

```
app.py                          # Streamlit entry point
streamlit_app/
  pages/                        # 6 UI sections
    dashboard.py, pam_engine.py, analysis.py,
    knowledge_base.py, journal.py, settings_page.py
  services/                     # Gemini chain, retrieval, bootstrap
    gemini_chain.py, retrieval.py, bootstrap.py
core/
  config/                       # Environment settings
  models/                       # SQLAlchemy ORM + database session
  pam/                          # Deterministic PAM engine (809 lines)
  scoring/                      # Logistic scoring + Kelly sizing
  options/                      # Bang Van options strategy mapper
data/
  knowledge/                    # Built-in markdown knowledge base
  uploads/                      # User-uploaded PDFs/docs
```

### Deterministic vs AI Responsibilities

| Layer | Responsibility |
|-------|---------------|
| **Deterministic (PAM)** | Pattern detection, flow state, momentum, scoring inputs, options rules, sizing, invalidation |
| **AI (Gemini)** | Macro/liquidity synthesis, thesis generation, summarizing documents, ranking ideas, investment memos |

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 16 with pgvector extension
- Gemini API key ([Get one here](https://aistudio.google.com/apikey))

### Local Setup

```bash
# 1. Clone and enter
git clone https://github.com/domenicomosca96-ai/Finance-Kingdom.git
cd Finance-Kingdom

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — add GEMINI_API_KEY and DATABASE_URL

# 5. Start PostgreSQL (if not running)
# Option A: Docker
docker run -d --name alphaedge-db \
  -e POSTGRES_USER=alpha -e POSTGRES_PASSWORD=alpha -e POSTGRES_DB=alphaedge \
  -p 5432:5432 pgvector/pgvector:pg16

# 6. Run the app
streamlit run app.py
```

### Docker Compose (recommended)

```bash
cp .env.example .env
# Edit .env — add GEMINI_API_KEY

docker compose up -d
# App available at http://localhost:8501
```

### First Run Checklist
1. Open http://localhost:8501
2. Go to **Settings** > Test Gemini Connection
3. Go to **Settings** > Initialize Database
4. Go to **Knowledge Base** > Bootstrap
5. Go to **PAM Engine** > Test with a ticker (e.g., NVDA)
6. Go to **Analysis** > Run your first watchlist

## Security

- Gemini API key is server-side only (never exposed to browser)
- All AI calls happen in Python backend
- Secrets managed via environment variables
- No client-side API key exposure

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | — | Google Gemini API key |
| `DATABASE_URL` | Yes | `postgresql://alpha:alpha@localhost:5432/alphaedge` | PostgreSQL connection |
| `GEMINI_MODEL` | No | `gemini-2.5-flash` | Gemini model to use |
| `PORTFOLIO_SIZE` | No | `100000` | Portfolio size for sizing |
| `MAX_RISK_PER_TRADE_PCT` | No | `2.0` | Max risk per trade |

See `.env.example` for all options.

## Deployment

See [DEPLOY.md](DEPLOY.md) for detailed deployment instructions for:
- Streamlit Community Cloud
- Railway
- Docker (self-hosted)

## Knowledge Base

Built-in documents (in `data/knowledge/`):
- `liquidity-framework.md` — Howell liquidity phases, Fed, DXY
- `trading-methodology.md` — Adam Khoo trend rules, risk management
- `pam-structures.md` — PAM institutional patterns
- `bang-van-options-strategies.md` — Options strategy matrix
- `accumulation-distribution-rotation.md` — A/B/C/D rotation model
- `equity-tech-playbook.md` — AI/semis sector analysis

Upload your own PDFs and Markdown files via the Knowledge Base page.

## License

Private — personal use only.
