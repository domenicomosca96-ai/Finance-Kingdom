"""
RAG Retrieval — pgvector semantic search with Gemini embeddings.

Uses Google's text-embedding-004 model for embeddings (768 dim).
All API calls are server-side only.
"""

from google import genai
from google.genai import types
from sqlalchemy import text
from sqlalchemy.orm import Session
from core.config import settings

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def embed_text(content: str) -> list[float]:
    """Generate embedding vector using Gemini text-embedding-004."""
    client = _get_client()
    result = client.models.embed_content(
        model=settings.EMBEDDING_MODEL,
        contents=content,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
    )
    return result.embeddings[0].values


def embed_query(content: str) -> list[float]:
    """Generate embedding for a search query."""
    client = _get_client()
    result = client.models.embed_content(
        model=settings.EMBEDDING_MODEL,
        contents=content,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    return result.embeddings[0].values


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Batch embedding for documents."""
    client = _get_client()
    embeddings = []
    for t in texts:
        result = client.models.embed_content(
            model=settings.EMBEDDING_MODEL,
            contents=t,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
        )
        embeddings.append(result.embeddings[0].values)
    return embeddings


def retrieve(
    db: Session,
    query: str,
    collections: list[str] | None = None,
    k: int = 8,
) -> list[dict]:
    """Semantic search over document_chunks using pgvector cosine distance."""
    query_vec = embed_query(query)
    vec_str = "[" + ",".join(str(v) for v in query_vec) + "]"

    where_clause = ""
    params = {"vec": vec_str, "k": k}
    if collections:
        placeholders = ",".join(f":c{i}" for i in range(len(collections)))
        where_clause = f"WHERE collection IN ({placeholders})"
        for i, c in enumerate(collections):
            params[f"c{i}"] = c

    sql = text(f"""
        SELECT id, collection, source, content, metadata,
               1 - (embedding <=> :vec::vector) AS similarity
        FROM document_chunks
        {where_clause}
        ORDER BY embedding <=> :vec::vector
        LIMIT :k
    """)

    result = db.execute(sql, params)
    rows = result.fetchall()

    return [
        {
            "id": r.id, "collection": r.collection, "source": r.source,
            "content": r.content, "metadata": r.metadata,
            "similarity": round(float(r.similarity), 4),
        }
        for r in rows
    ]


def multi_collection_retrieve(
    db: Session, query: str,
    collections: list[str], k_per_collection: int = 5,
) -> dict[str, list[dict]]:
    """Retrieve from each collection separately."""
    results = {}
    for coll in collections:
        results[coll] = retrieve(db, query, [coll], k_per_collection)
    return results


def format_retrieved_docs(docs_by_collection: dict) -> str:
    """Format for LLM context injection."""
    sections = []
    for coll, docs in docs_by_collection.items():
        if not docs:
            continue
        header = f"== {coll.upper().replace('_', ' ')} =="
        chunks = []
        for d in docs:
            chunks.append(f"[{d['source']}] (sim={d['similarity']})\n{d['content']}")
        sections.append(f"{header}\n\n" + "\n---\n".join(chunks))
    return "\n\n\n".join(sections)
