"""Centralized configuration — environment variables + defaults."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Gemini API (required — server-side only)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Postgres (required)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://alpha:alpha@localhost:5432/alphaedge",
    )

    # Scoring (logistic sigmoid)
    SCORE_THRESHOLD: float = float(os.getenv("SCORE_THRESHOLD", "65"))
    LOGISTIC_K: float = float(os.getenv("LOGISTIC_K", "0.08"))
    LOGISTIC_C: float = float(os.getenv("LOGISTIC_C", "55"))

    # Weights
    W_MACRO: float = float(os.getenv("W_MACRO", "0.30"))
    W_THEME: float = float(os.getenv("W_THEME", "0.25"))
    W_PAM: float = float(os.getenv("W_PAM", "0.45"))

    # Risk Management
    KELLY_FRACTION: float = float(os.getenv("KELLY_FRACTION", "0.25"))
    MAX_POSITION_PCT: float = float(os.getenv("MAX_POSITION_PCT", "5.0"))
    MAX_RISK_PER_TRADE_PCT: float = float(os.getenv("MAX_RISK_PER_TRADE_PCT", "2.0"))
    MAX_PORTFOLIO_HEAT_PCT: float = float(os.getenv("MAX_PORTFOLIO_HEAT_PCT", "6.0"))
    PORTFOLIO_SIZE: float = float(os.getenv("PORTFOLIO_SIZE", "100000"))

    # Gemini model
    MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    EMBEDDING_DIM: int = 768  # Gemini text-embedding-004 dimension


settings = Settings()
