"""Database engine, session, and initialization.

Supports both local PostgreSQL and cloud providers (Neon.tech, Supabase).
Handles postgres:// vs postgresql:// URL schemes and SSL requirements.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from core.config import settings
from core.models import Base


def _fix_db_url(url: str) -> str:
    """Fix common DB URL issues for cloud providers."""
    # Neon/Supabase may provide postgres:// but SQLAlchemy needs postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    # Add sslmode for cloud providers if not present
    if ("neon.tech" in url or "supabase" in url) and "sslmode" not in url:
        separator = "&" if "?" in url else "?"
        url += f"{separator}sslmode=require"
    return url


_db_url = _fix_db_url(settings.DATABASE_URL)
engine = create_engine(_db_url, echo=False, pool_size=5, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> Session:
    """Get a database session."""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def init_db():
    """Create all tables + enable pgvector extension."""
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)
