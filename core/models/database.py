"""Database engine, session, and initialization."""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from core.config import settings
from core.models import Base

engine = create_engine(settings.DATABASE_URL, echo=False, pool_size=5, pool_pre_ping=True)
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
