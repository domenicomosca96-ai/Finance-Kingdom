"""
Bootstrap — Load knowledge into Postgres/pgvector with deduplication.

Uses Gemini text-embedding-004 for embeddings.
"""

import sys
import hashlib
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.orm import Session
from core.config import settings
from core.models.database import init_db, engine
from core.models import DocumentChunk
from streamlit_app.services.retrieval import embed_batch

KNOWLEDGE_DIR = Path(__file__).parent.parent.parent / "data" / "knowledge"
UPLOAD_DIR = Path(__file__).parent.parent.parent / "data" / "uploads"

COLLECTION_MAP = {
    "liquidity": "macro_liquidity", "macro": "macro_liquidity", "howell": "macro_liquidity",
    "fed": "macro_liquidity",
    "trading": "trading_methods", "khoo": "trading_methods", "bang": "trading_methods",
    "method": "trading_methods", "option": "trading_methods", "strategy": "trading_methods",
    "pam": "pam_structures", "manipulation": "pam_structures", "smc": "pam_structures",
    "accumulation": "pam_structures", "distribution": "pam_structures", "rotation": "pam_structures",
    "momentum": "pam_structures", "reversal": "pam_structures", "ur2": "pam_structures",
    "dr2": "pam_structures", "uc1": "pam_structures",
    "tech": "tech_reports", "semiconductor": "tech_reports", "nvidia": "tech_reports",
    "equity": "tech_reports", "playbook": "tech_reports",
}


def _chunk_text(text_content: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]:
    """Simple recursive character text splitter without langchain dependency."""
    if len(text_content) <= chunk_size:
        return [text_content] if text_content.strip() else []

    chunks = []
    start = 0
    while start < len(text_content):
        end = start + chunk_size
        if end < len(text_content):
            # Try to break at paragraph, then sentence, then word
            for sep in ["\n\n", "\n", ". ", " "]:
                idx = text_content.rfind(sep, start + chunk_size // 2, end)
                if idx > start:
                    end = idx + len(sep)
                    break
        chunk = text_content[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap if end < len(text_content) else len(text_content)

    return chunks


def resolve_collection(filename: str) -> str:
    name_lower = filename.lower()
    for pattern, collection in COLLECTION_MAP.items():
        if pattern in name_lower:
            return collection
    return "tech_reports"


def content_hash(text_content: str) -> str:
    return hashlib.sha256(text_content.encode("utf-8")).hexdigest()[:16]


def is_already_ingested(db: Session, source: str, file_hash: str) -> bool:
    result = db.execute(
        text("SELECT count(*) FROM document_chunks WHERE source = :s AND metadata->>'hash' = :h"),
        {"s": source, "h": file_hash},
    )
    return result.scalar() > 0


def delete_source(db: Session, source: str):
    db.execute(text("DELETE FROM document_chunks WHERE source = :s"), {"s": source})
    db.commit()


def ingest_text(db: Session, text_content: str, source: str, collection: str, force: bool = False) -> int:
    """Chunk, embed, and insert with dedup."""
    file_hash = content_hash(text_content)

    if not force and is_already_ingested(db, source, file_hash):
        return -1

    delete_source(db, source)
    chunks = _chunk_text(text_content)
    if not chunks:
        return 0

    embeddings = embed_batch(chunks)

    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        db.add(DocumentChunk(
            collection=collection,
            source=source,
            chunk_index=i,
            content=chunk,
            content_text=text_content if i == 0 else None,
            embedding=emb,
            metadata_={"hash": file_hash, "total_chunks": len(chunks)},
        ))
    db.commit()
    return len(chunks)


def run_bootstrap(force: bool = False) -> dict:
    """Run knowledge base bootstrap. Returns status dict."""
    init_db()

    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    results = {"new_chunks": 0, "skipped": 0, "errors": [], "files": []}

    with Session(engine) as db:
        # Markdown files
        md_files = sorted(KNOWLEDGE_DIR.glob("*.md"))
        for f in md_files:
            try:
                text_content = f.read_text(encoding="utf-8")
                collection = resolve_collection(f.name)
                n = ingest_text(db, text_content, f.name, collection, force)
                if n == -1:
                    results["skipped"] += 1
                    results["files"].append({"name": f.name, "status": "skipped", "collection": collection})
                else:
                    results["new_chunks"] += n
                    results["files"].append({"name": f.name, "status": "ingested", "chunks": n, "collection": collection})
            except Exception as e:
                results["errors"].append(f"{f.name}: {str(e)}")

        # PDF files in uploads
        pdf_files = sorted(UPLOAD_DIR.glob("*.pdf"))
        if pdf_files:
            try:
                import fitz
                for f in pdf_files:
                    try:
                        doc = fitz.open(str(f))
                        text_content = "\n\n".join(p.get_text("text") for p in doc if p.get_text("text").strip())
                        doc.close()
                        if not text_content.strip():
                            results["errors"].append(f"{f.name}: no text extracted")
                            continue
                        collection = resolve_collection(f.name)
                        n = ingest_text(db, text_content, f.name, collection, force)
                        if n == -1:
                            results["skipped"] += 1
                            results["files"].append({"name": f.name, "status": "skipped", "collection": collection})
                        else:
                            results["new_chunks"] += n
                            results["files"].append({"name": f.name, "status": "ingested", "chunks": n, "collection": collection})
                    except Exception as e:
                        results["errors"].append(f"{f.name}: {str(e)}")
            except ImportError:
                results["errors"].append("PyMuPDF not installed — PDF ingestion skipped")

        # Markdown in uploads
        md_uploads = sorted(UPLOAD_DIR.glob("*.md"))
        for f in md_uploads:
            try:
                text_content = f.read_text(encoding="utf-8")
                collection = resolve_collection(f.name)
                n = ingest_text(db, text_content, f.name, collection, force)
                if n == -1:
                    results["skipped"] += 1
                    results["files"].append({"name": f.name, "status": "skipped", "collection": collection})
                else:
                    results["new_chunks"] += n
                    results["files"].append({"name": f.name, "status": "ingested", "chunks": n, "collection": collection})
            except Exception as e:
                results["errors"].append(f"{f.name}: {str(e)}")

        # Collection stats
        try:
            result = db.execute(text(
                "SELECT collection, count(*) FROM document_chunks GROUP BY collection ORDER BY collection"
            ))
            results["collections"] = {row[0]: row[1] for row in result}
        except Exception:
            results["collections"] = {}

    return results
