# AlphaEdge v3 — Deployment Guide

## Option 1: Docker Compose (Recommended for Self-Hosted)

```bash
# 1. Clone
git clone https://github.com/domenicomosca96-ai/Finance-Kingdom.git
cd Finance-Kingdom

# 2. Configure
cp .env.example .env
# Edit .env — set GEMINI_API_KEY

# 3. Launch
docker compose up -d

# 4. Verify
open http://localhost:8501
```

The Docker Compose setup includes:
- PostgreSQL 16 with pgvector (auto-configured)
- Streamlit app (auto-builds)
- Persistent data volume

To stop: `docker compose down`
To reset database: `docker compose down -v`

---

## Option 2: Streamlit Community Cloud

### Prerequisites
- GitHub repository (public or connected to Streamlit Cloud)
- Gemini API key
- External PostgreSQL with pgvector (e.g., Supabase, Neon, Railway)

### Steps

1. **Push code to GitHub** (already done if you're reading this)

2. **Set up external PostgreSQL**
   - **Supabase** (free tier): Create project > Enable pgvector extension > Get connection string
   - **Neon** (free tier): Create database > Enable pgvector > Get connection string

3. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repo
   - Set main file: `app.py`
   - Add secrets in Streamlit Cloud dashboard:

   ```toml
   # In Streamlit Cloud > Settings > Secrets
   GEMINI_API_KEY = "your-key-here"
   DATABASE_URL = "postgresql://user:pass@host:5432/dbname"
   ```

4. **Post-deploy**
   - Open the app
   - Go to Settings > Initialize Database
   - Go to Knowledge Base > Bootstrap

### Important Notes for Streamlit Cloud
- The app uses `st.secrets` fallback (environment variables work too)
- pgvector must be enabled on your external PostgreSQL
- File uploads are ephemeral — use the bootstrap for persistent knowledge

---

## Option 3: Railway

### Steps

1. **Create Railway project**
   - Go to [railway.app](https://railway.app)
   - New Project > Deploy from GitHub repo

2. **Add PostgreSQL**
   - Add Service > Database > PostgreSQL
   - In the PostgreSQL service, run: `CREATE EXTENSION vector;`

3. **Configure environment variables**
   ```
   GEMINI_API_KEY=your-key-here
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   GEMINI_MODEL=gemini-2.5-flash
   ```

4. **Set start command**
   ```
   streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
   ```

5. **Deploy** — Railway auto-builds from Dockerfile or requirements.txt

### Railway Notes
- Railway provides `$PORT` — Streamlit must bind to it
- PostgreSQL plugin auto-provides `DATABASE_URL`
- You may need to install pgvector manually:
  ```sql
  CREATE EXTENSION IF NOT EXISTS vector;
  ```

---

## Post-Deployment Checklist

After deploying on any platform:

1. [ ] Open the app URL
2. [ ] Go to **Settings** > Test Gemini Connection — should show "Connected"
3. [ ] Go to **Settings** > Test Database — should show PostgreSQL version
4. [ ] Go to **Settings** > Initialize Database — creates all tables
5. [ ] Go to **Knowledge Base** > Bootstrap — ingests built-in knowledge
6. [ ] Go to **PAM Engine** > Run analysis on AAPL — verifies yfinance + PAM
7. [ ] Go to **Analysis** > Run with NVDA — verifies full Gemini pipeline
8. [ ] Go to **Journal** > Create test entry — verifies persistence

---

## Cost Estimates

| Service | Cost |
|---------|------|
| Gemini API (50 analyses/day) | ~$5-15/month |
| PostgreSQL (Supabase free) | $0 |
| Streamlit Cloud (free tier) | $0 |
| Railway (Starter) | ~$5/month |
| Docker self-hosted | Your server cost |

---

## Troubleshooting

### "pgvector extension not found"
```sql
-- Connect to your database and run:
CREATE EXTENSION IF NOT EXISTS vector;
```

### "GEMINI_API_KEY not set"
- Verify the key is in `.env` (local) or Secrets (cloud)
- Restart the app after changing environment variables

### "Insufficient data for TICKER"
- yfinance needs at least 60 trading days of data
- Check if the ticker symbol is correct
- Some tickers may not have options data (IV rank will show N/A)

### Database connection timeout
- Check DATABASE_URL format: `postgresql://user:pass@host:5432/dbname`
- Ensure PostgreSQL is accessible from your deployment environment
- For Streamlit Cloud, the database must be publicly accessible (or use Supabase/Neon)
