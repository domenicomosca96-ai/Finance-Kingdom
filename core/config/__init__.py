"""Centralized configuration — supports both .env (local) and st.secrets (Streamlit Cloud)."""

import os
from dotenv import load_dotenv

load_dotenv()


def _get(key: str, default: str = "") -> str:
    """Get config value from st.secrets first, then env vars, then default."""
    # 1. Streamlit Cloud secrets (highest priority)
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    # 2. Environment variable
    return os.getenv(key, default)


class Settings:
    # Gemini API (required — server-side only)
    GEMINI_API_KEY: str = _get("GEMINI_API_KEY")

    # Postgres (required for full functionality)
    DATABASE_URL: str = _get(
        "DATABASE_URL",
        "postgresql://alpha:alpha@localhost:5432/alphaedge",
    )

    # Scoring (logistic sigmoid)
    SCORE_THRESHOLD: float = float(_get("SCORE_THRESHOLD", "65"))
    LOGISTIC_K: float = float(_get("LOGISTIC_K", "0.08"))
    LOGISTIC_C: float = float(_get("LOGISTIC_C", "55"))

    # Weights (Macro=GLI+Intermarket 45%, Theme=Sectors+Fundamentals 35%, PAM=PriceAction+Elliott 20%)
    W_MACRO: float = float(_get("W_MACRO", "0.45"))
    W_THEME: float = float(_get("W_THEME", "0.35"))
    W_PAM: float = float(_get("W_PAM", "0.20"))

    # Risk Management
    KELLY_FRACTION: float = float(_get("KELLY_FRACTION", "0.25"))
    MAX_POSITION_PCT: float = float(_get("MAX_POSITION_PCT", "5.0"))
    MAX_RISK_PER_TRADE_PCT: float = float(_get("MAX_RISK_PER_TRADE_PCT", "2.0"))
    MAX_PORTFOLIO_HEAT_PCT: float = float(_get("MAX_PORTFOLIO_HEAT_PCT", "6.0"))
    PORTFOLIO_SIZE: float = float(_get("PORTFOLIO_SIZE", "100000"))

    # Gemini model (gemini-2.5-pro for highest quality financial analysis)
    MODEL: str = _get("GEMINI_MODEL", "gemini-2.5-pro")
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    EMBEDDING_DIM: int = 768


settings = Settings()
