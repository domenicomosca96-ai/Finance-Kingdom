"""Knowledge Base — Upload, ingest, browse collections."""

import streamlit as st
from pathlib import Path


UPLOAD_DIR = Path(__file__).parent.parent.parent / "data" / "uploads"
KNOWLEDGE_DIR = Path(__file__).parent.parent.parent / "data" / "knowledge"


def render():
    st.title("Knowledge Base")
    st.caption("Manage documents for RAG retrieval — PDFs and Markdown")

    tab1, tab2, tab3 = st.tabs(["Upload & Ingest", "Collections", "Bootstrap"])

    with tab1:
        _render_upload()

    with tab2:
        _render_collections()

    with tab3:
        _render_bootstrap()


def _render_upload():
    st.subheader("Upload Documents")

    uploaded_files = st.file_uploader(
        "Upload PDF or Markdown files",
        type=["pdf", "md", "txt"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        saved = []
        for f in uploaded_files:
            dest = UPLOAD_DIR / f.name
            dest.write_bytes(f.getbuffer())
            saved.append(f.name)
        st.success(f"Saved {len(saved)} file(s): {', '.join(saved)}")

        if st.button("Ingest uploaded files", type="primary"):
            with st.spinner("Ingesting documents into knowledge base..."):
                try:
                    from streamlit_app.services.bootstrap import run_bootstrap
                    result = run_bootstrap(force=False)
                    st.success(f"Ingestion complete: {result['new_chunks']} new chunks, {result['skipped']} skipped")
                    if result["errors"]:
                        for e in result["errors"]:
                            st.error(e)
                    _clear_caches()
                except Exception as e:
                    st.error(f"Ingestion failed: {str(e)}")

    st.divider()

    # Show existing files
    st.subheader("Uploaded Files")
    _show_dir_files(UPLOAD_DIR, "uploads")

    st.subheader("Knowledge Files (built-in)")
    _show_dir_files(KNOWLEDGE_DIR, "knowledge")


def _show_dir_files(directory: Path, label: str):
    if directory.exists():
        files = sorted(directory.glob("*.*"))
        if files:
            for f in files:
                size_kb = f.stat().st_size / 1024
                st.text(f"  {f.name} ({size_kb:.1f} KB)")
        else:
            st.info(f"No files in {label}/")
    else:
        st.info(f"Directory {label}/ does not exist yet.")


def _render_collections():
    st.subheader("Document Collections")

    try:
        from core.models.database import engine
        from sqlalchemy import text

        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT collection, count(*), count(DISTINCT source) "
                "FROM document_chunks GROUP BY collection ORDER BY collection"
            ))
            rows = result.fetchall()

        if rows:
            for coll, chunk_count, source_count in rows:
                with st.expander(f"{coll.replace('_', ' ').title()} — {chunk_count} chunks, {source_count} sources"):
                    # Show sources in this collection
                    with engine.connect() as conn:
                        sources = conn.execute(text(
                            "SELECT DISTINCT source, count(*) FROM document_chunks "
                            "WHERE collection = :c GROUP BY source ORDER BY source"
                        ), {"c": coll}).fetchall()
                    for src, cnt in sources:
                        st.text(f"  {src}: {cnt} chunks")
        else:
            st.info("No collections found. Bootstrap the knowledge base first.")

    except Exception as e:
        st.warning(f"Cannot connect to database: {str(e)}")
        st.info("Configure DATABASE_URL in your .env file and ensure PostgreSQL is running.")


def _render_bootstrap():
    st.subheader("Bootstrap Knowledge Base")
    st.markdown(
        "This will scan `data/knowledge/` and `data/uploads/` for Markdown and PDF files, "
        "chunk them, compute Gemini embeddings, and store in pgvector with deduplication."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Bootstrap (skip existing)", type="primary", use_container_width=True):
            _do_bootstrap(force=False)
    with col2:
        if st.button("Force Re-ingest All", use_container_width=True):
            _do_bootstrap(force=True)


def _do_bootstrap(force: bool):
    with st.status("Running bootstrap...", expanded=True) as status:
        try:
            from streamlit_app.services.bootstrap import run_bootstrap
            result = run_bootstrap(force=force)

            st.write(f"New chunks: {result['new_chunks']}")
            st.write(f"Skipped (unchanged): {result['skipped']}")

            if result.get("files"):
                for f in result["files"]:
                    icon = "[OK]" if f.get("status") == "ingested" else "[--]"
                    chunks = f.get("chunks", "")
                    st.write(f"  {icon} {f['name']} -> {f.get('collection', '?')} ({chunks} chunks)" if chunks else f"  {icon} {f['name']} (skipped)")

            if result.get("collections"):
                st.write("\nCollection totals:")
                for coll, count in result["collections"].items():
                    st.write(f"  {coll}: {count} chunks")

            if result["errors"]:
                for e in result["errors"]:
                    st.error(e)

            status.update(label="Bootstrap complete", state="complete")
            _clear_caches()
        except Exception as e:
            status.update(label=f"Error: {str(e)}", state="error")
            st.error(str(e))


def _clear_caches():
    """Clear relevant Streamlit caches after data changes."""
    try:
        st.cache_data.clear()
    except Exception:
        pass
