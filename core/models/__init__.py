"""
SQLAlchemy models — Postgres + pgvector.

Tables:
  document_chunks   — RAG vector store
  daily_bars        — OHLCV market data cache
  pam_signals       — Deterministic PAM engine outputs
  trade_ideas       — AI-generated trade ideas with scores
  journal           — Trade journal for feedback loop
  analysis_jobs     — Job tracking
"""

from datetime import datetime, date
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, Text, Date, DateTime,
    JSON, ForeignKey, Index, UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector
from core.config import settings
import enum

Base = declarative_base()


# ═══════════════════════════════════════════════════════════
#  ENUMS
# ═══════════════════════════════════════════════════════════

class CollectionType(str, enum.Enum):
    MACRO_LIQUIDITY = "macro_liquidity"
    TRADING_METHODS = "trading_methods"
    PAM_STRUCTURES = "pam_structures"
    TECH_REPORTS = "tech_reports"
    WATCHLIST_SETUPS = "watchlist_setups"


class Direction(str, enum.Enum):
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"


class FlowState(str, enum.Enum):
    POSITIVE = "positive_flow"
    NEGATIVE = "negative_flow"
    TRANSITION_UP = "transition_up"
    TRANSITION_DOWN = "transition_down"
    RANGING = "ranging"


class PAMPattern(str, enum.Enum):
    UC1 = "UC1"
    UC2 = "UC2"
    UR1 = "UR1"
    UR2 = "UR2"
    DC1 = "DC1"
    DC2 = "DC2"
    DR1 = "DR1"
    DR2 = "DR2"
    NONE = "NONE"


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


# ═══════════════════════════════════════════════════════════
#  DOCUMENT CHUNKS (pgvector RAG store)
# ═══════════════════════════════════════════════════════════

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    collection = Column(String(50), nullable=False, index=True)
    source = Column(String(500), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    content_text = Column(Text)  # full extracted text for Gemini context injection
    embedding = Column(Vector(settings.EMBEDDING_DIM), nullable=False)
    metadata_ = Column("metadata", JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_chunks_embedding", "embedding", postgresql_using="ivfflat",
              postgresql_with={"lists": 100},
              postgresql_ops={"embedding": "vector_cosine_ops"}),
    )


# ═══════════════════════════════════════════════════════════
#  DAILY BARS (OHLCV cache)
# ═══════════════════════════════════════════════════════════

class DailyBar(Base):
    __tablename__ = "daily_bars"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    dt = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    sma_20 = Column(Float)
    sma_50 = Column(Float)
    sma_150 = Column(Float)
    ema_20 = Column(Float)
    ema_50 = Column(Float)
    atr_14 = Column(Float)
    rsi_14 = Column(Float)

    __table_args__ = (
        UniqueConstraint("ticker", "dt", name="uq_ticker_date"),
    )


# ═══════════════════════════════════════════════════════════
#  PAM SIGNALS (deterministic engine output)
# ═══════════════════════════════════════════════════════════

class PAMSignal(Base):
    __tablename__ = "pam_signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    dt = Column(Date, nullable=False)

    flow_state = Column(String(30), nullable=False)
    above_sma50 = Column(Boolean, nullable=False)
    hh_hl_count = Column(Integer, default=0)
    lh_ll_count = Column(Integer, default=0)

    pattern = Column(String(10), default="NONE")
    pattern_confidence = Column(Float, default=0.0)
    trigger_level = Column(Float)
    stop_level = Column(Float)
    target_level = Column(Float)

    flush_detected = Column(Boolean, default=False)
    flush_direction = Column(String(10))
    momentum_angle_deg = Column(Float)
    is_wave = Column(Boolean, default=False)
    is_flush = Column(Boolean, default=False)

    rotation_segment = Column(String(5))
    micro_score = Column(Float, default=50.0)

    metadata_ = Column("metadata", JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("ticker", "dt", name="uq_pam_ticker_date"),
    )


# ═══════════════════════════════════════════════════════════
#  TRADE IDEAS (AI-generated)
# ═══════════════════════════════════════════════════════════

class TradeIdea(Base):
    __tablename__ = "trade_ideas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(50), ForeignKey("analysis_jobs.job_id"), index=True)
    ticker = Column(String(20), nullable=False, index=True)
    dt = Column(Date, nullable=False)

    raw_macro = Column(Float, default=50.0)
    raw_theme = Column(Float, default=50.0)
    raw_pam = Column(Float, default=50.0)
    raw_composite = Column(Float, default=50.0)
    probability_pct = Column(Float, default=50.0)

    direction = Column(String(10), default="neutral")
    trade_type = Column(String(10), default="stock")  # stock, options, both
    actionable = Column(Boolean, default=False)
    thesis = Column(Text)
    swing_plan = Column(Text)
    entry_price = Column(Float)
    stop_loss = Column(Float)
    target_price = Column(Float)

    option_strategy = Column(String(50))
    option_legs = Column(JSON)
    option_rationale = Column(Text)
    payoff_matrix = Column(JSON)

    kelly_fraction = Column(Float)
    suggested_capital = Column(Float)
    suggested_contracts = Column(Integer)
    max_risk_dollars = Column(Float)

    invalidation = Column(Text)
    catalysts = Column(JSON, default=[])
    llm_raw_output = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════
#  JOURNAL
# ═══════════════════════════════════════════════════════════

class JournalEntry(Base):
    __tablename__ = "journal"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_idea_id = Column(Integer, ForeignKey("trade_ideas.id"), nullable=True)
    ticker = Column(String(20), nullable=False)
    direction = Column(String(10), nullable=False)
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    target_price = Column(Float, nullable=False)
    strategy = Column(String(100))
    ai_score = Column(Float)
    conviction = Column(String(20), default="medium")
    notes = Column(Text)

    exit_price = Column(Float)
    pnl = Column(Float)
    pnl_pct = Column(Float)
    status = Column(String(20), default="open")

    macro_score_at_entry = Column(Float)
    theme_score_at_entry = Column(Float)
    pam_score_at_entry = Column(Float)

    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime)


# ═══════════════════════════════════════════════════════════
#  ANALYSIS JOBS
# ═══════════════════════════════════════════════════════════

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    job_id = Column(String(50), primary_key=True)
    tickers = Column(JSON, nullable=False)
    status = Column(String(20), default="pending")
    macro_context = Column(Text)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    ideas = relationship("TradeIdea", backref="job", lazy="selectin")
