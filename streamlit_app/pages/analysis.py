"""Analysis — Full watchlist analysis workflow with Gemini 3."""

import streamlit as st
import uuid
from datetime import date, datetime
from dataclasses import asdict


def render():
    st.title("Analysis")
    st.caption("Full AI-powered investment analysis — Gemini 3 + PAM Engine + Knowledge Base")

    # ── Input ──
    tickers_input = st.text_input(
        "Watchlist Tickers",
        value="NVDA, AAPL",
        placeholder="Comma-separated: NVDA, AAPL, MSFT, META",
    )
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

    col1, col2 = st.columns([1, 4])
    with col1:
        run_btn = st.button("Run Full Analysis", type="primary", use_container_width=True)

    if run_btn and tickers:
        _run_analysis(tickers)
    elif "analysis_results" in st.session_state:
        _display_results(st.session_state.analysis_results)


def _run_analysis(tickers: list[str]):
    from core.config import settings
    if not settings.GEMINI_API_KEY:
        st.error("GEMINI_API_KEY not configured. Go to Settings to verify.")
        return

    with st.status(f"Analyzing {', '.join(tickers)}...", expanded=True) as status:
        try:
            # Step 1: PAM Engine
            st.write("Step 1/5: Running PAM engine for each ticker...")
            from core.pam import run_full_pam
            pam_results = {}
            for t in tickers:
                try:
                    pam_results[t] = run_full_pam(t)
                    st.write(f"  [OK] {t} — micro_score: {pam_results[t].micro_score:.1f}")
                except Exception as e:
                    st.write(f"  [!!] {t} — {str(e)}")

            if not pam_results:
                status.update(label="No valid PAM results", state="error")
                return

            pam_context = "\n\n".join(r.to_context_string() for r in pam_results.values())

            # Step 2: RAG Retrieval
            st.write("Step 2/5: Retrieving knowledge documents...")
            retrieved_docs = _retrieve_docs(tickers)

            # Step 3: Chain Prompting
            st.write("Step 3/5: Running 4-step Gemini chain (Context > Analyst > Critic > Formatter)...")
            from streamlit_app.services.gemini_chain import run_chain
            live_data = "\n".join(
                f"{t}: ${r.current_price:.2f} | RSI: {r.rsi_14:.1f} | Vol ratio: {r.volume_ratio:.2f}x"
                for t, r in pam_results.items()
            )
            chain_result = run_chain(retrieved_docs, pam_context, live_data, list(pam_results.keys()))

            # Step 4: Scoring + Options
            st.write("Step 4/5: Computing scores, sizing, and options strategies...")
            analyses = chain_result.get("analyses", [])
            enriched = _enrich_analyses(analyses, pam_results)

            # Step 5: Store
            st.write("Step 5/5: Saving trade ideas...")
            _store_ideas(enriched, chain_result)

            result_data = {
                "macro_context": chain_result.get("macro_context", ""),
                "analyses": enriched,
                "chain_audit": chain_result.get("_chain_audit", {}),
            }
            st.session_state.analysis_results = result_data
            status.update(label=f"Analysis complete — {len(enriched)} ideas generated", state="complete")

            _display_results(result_data)

        except Exception as e:
            status.update(label=f"Error: {str(e)}", state="error")
            st.error(f"Analysis failed: {str(e)}")


def _retrieve_docs(tickers: list[str]) -> str:
    """Attempt RAG retrieval, fallback to direct knowledge file injection."""
    try:
        from core.models.database import SessionLocal
        from streamlit_app.services.retrieval import multi_collection_retrieve, format_retrieved_docs
        collections = ["macro_liquidity", "trading_methods", "pam_structures", "tech_reports"]
        query = f"Swing trading analysis for {', '.join(tickers)}. Macro liquidity, PAM patterns, options strategies."

        with SessionLocal() as db:
            docs = multi_collection_retrieve(db, query, collections, k_per_collection=4)
            formatted = format_retrieved_docs(docs)
            if formatted.strip():
                return formatted
    except Exception:
        pass

    # Fallback: inject knowledge files directly
    from pathlib import Path
    kb_dir = Path(__file__).parent.parent.parent / "data" / "knowledge"
    texts = []
    for f in sorted(kb_dir.glob("*.md")):
        try:
            texts.append(f"== {f.stem.upper()} ==\n{f.read_text()}")
        except Exception:
            pass
    return "\n\n".join(texts) if texts else "No knowledge documents available."


def _enrich_analyses(analyses: list[dict], pam_results: dict) -> list[dict]:
    """Add scoring, sizing, and options strategy to each analysis."""
    from core.scoring import compute_score, compute_sizing
    from core.options import select_strategy
    from dataclasses import asdict

    enriched = []
    for a in analyses:
        ticker = a.get("ticker", "")
        pam = pam_results.get(ticker)

        raw_macro = a.get("raw_macro", 50)
        raw_theme = a.get("raw_theme", 50)
        raw_pam = pam.micro_score if pam else a.get("raw_pam", 50)

        score = compute_score(raw_macro, raw_theme, raw_pam)

        entry = a.get("entry_price") or (pam.pattern.trigger_level if pam else None) or (pam.current_price if pam else 100)
        stop = a.get("stop_loss") or (pam.pattern.stop_level if pam else None) or entry * 0.95
        target = a.get("target_price") or (pam.pattern.target_level if pam else None) or entry * 1.10

        sizing = compute_sizing(score.probability_pct, entry, stop, target)

        opts = None
        if pam:
            opts = select_strategy(
                pam.pattern, pam.flow, pam.momentum, pam.current_price,
                rsi=pam.rsi_14, iv_rank=pam.iv_rank,
                near_earnings=pam.near_earnings, days_to_earnings=pam.days_to_earnings,
            )

        enriched.append({
            **a,
            "raw_macro": score.raw_macro,
            "raw_theme": score.raw_theme,
            "raw_pam": score.raw_pam,
            "raw_composite": score.raw_composite,
            "probability_pct": score.probability_pct,
            "confidence_tier": score.confidence_tier,
            "sizing": asdict(sizing),
            "options": {
                "strategy_name": opts.strategy_name if opts else None,
                "strategy_code": opts.strategy_code if opts else None,
                "direction": opts.direction if opts else None,
                "rationale": opts.rationale if opts else None,
                "max_profit": opts.max_profit if opts else None,
                "max_loss": opts.max_loss if opts else None,
                "breakeven": opts.breakeven if opts else None,
                "vol_regime": opts.vol_regime if opts else None,
                "bang_van_notes": opts.bang_van_notes if opts else None,
                "legs": [{"side": l.side, "type": l.type, "strike": l.strike, "expiry": l.expiry} for l in opts.legs] if opts else [],
            } if opts else None,
        })

    return enriched


def _store_ideas(analyses: list[dict], chain_result: dict):
    """Persist trade ideas to database."""
    try:
        from core.models.database import SessionLocal
        from core.models import TradeIdea, AnalysisJob
        import json

        job_id = f"st-{uuid.uuid4().hex[:8]}"
        tickers = [a.get("ticker", "") for a in analyses]

        with SessionLocal() as db:
            job = AnalysisJob(
                job_id=job_id,
                tickers=tickers,
                status="complete",
                macro_context=chain_result.get("macro_context", ""),
                completed_at=datetime.utcnow(),
            )
            db.add(job)

            for a in analyses:
                idea = TradeIdea(
                    job_id=job_id,
                    ticker=a.get("ticker", ""),
                    dt=date.today(),
                    raw_macro=a.get("raw_macro", 50),
                    raw_theme=a.get("raw_theme", 50),
                    raw_pam=a.get("raw_pam", 50),
                    raw_composite=a.get("raw_composite", 50),
                    probability_pct=a.get("probability_pct", 50),
                    direction=a.get("direction", "neutral"),
                    actionable=a.get("probability_pct", 0) >= 58,
                    thesis=a.get("thesis"),
                    swing_plan=a.get("swing_plan"),
                    entry_price=a.get("entry_price"),
                    stop_loss=a.get("stop_loss"),
                    target_price=a.get("target_price"),
                    option_strategy=a.get("options", {}).get("strategy_name") if a.get("options") else None,
                    option_legs=a.get("options", {}).get("legs") if a.get("options") else None,
                    option_rationale=a.get("options", {}).get("rationale") if a.get("options") else None,
                    kelly_fraction=a.get("sizing", {}).get("kelly_adjusted"),
                    suggested_capital=a.get("sizing", {}).get("capital_allocated"),
                    suggested_contracts=a.get("sizing", {}).get("contracts"),
                    max_risk_dollars=a.get("sizing", {}).get("dollar_risk"),
                    invalidation=a.get("invalidation"),
                    catalysts=a.get("catalysts", []),
                    llm_raw_output=json.dumps(a),
                )
                db.add(idea)

            db.commit()
    except Exception:
        pass  # non-blocking — analysis still shown


def _display_results(data: dict):
    st.divider()

    # Macro context
    if data.get("macro_context"):
        with st.expander("Macro Regime Context", expanded=True):
            st.markdown(data["macro_context"])

    # Per-ticker results
    for a in data.get("analyses", []):
        _render_analysis_card(a)

    # Chain audit
    if data.get("chain_audit"):
        with st.expander("Chain Audit", expanded=False):
            for k, v in data["chain_audit"].items():
                st.text(f"{k}: {v}")


def _render_analysis_card(a: dict):
    ticker = a.get("ticker", "???")
    prob = a.get("probability_pct", 50)
    direction = a.get("direction", "neutral").upper()
    tier = a.get("confidence_tier", "low")

    tier_colors = {"high": "green", "medium": "orange", "low": "red", "no_trade": "red"}
    color = tier_colors.get(tier, "gray")

    with st.expander(f"{ticker} — {direction} — {prob:.1f}% ({tier.upper()})", expanded=True):
        # Score row
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Probability", f"{prob:.1f}%")
        s2.metric("Macro", f"{a.get('raw_macro', 50):.0f}")
        s3.metric("Theme", f"{a.get('raw_theme', 50):.0f}")
        s4.metric("PAM", f"{a.get('raw_pam', 50):.0f}")

        # Thesis
        if a.get("thesis"):
            st.markdown(f"**Thesis:** {a['thesis']}")

        # Trade plan
        if a.get("entry_price") or a.get("stop_loss") or a.get("target_price"):
            t1, t2, t3 = st.columns(3)
            t1.metric("Entry", f"${a['entry_price']:.2f}" if a.get("entry_price") else "N/A")
            t2.metric("Stop", f"${a['stop_loss']:.2f}" if a.get("stop_loss") else "N/A")
            t3.metric("Target", f"${a['target_price']:.2f}" if a.get("target_price") else "N/A")

        if a.get("swing_plan"):
            st.markdown(f"**Swing Plan:** {a['swing_plan']}")

        # Options
        opts = a.get("options")
        if opts and opts.get("strategy_name"):
            st.subheader(f"Options: {opts['strategy_name']} ({opts.get('strategy_code', '')})")

            o1, o2, o3 = st.columns(3)
            o1.metric("Max Profit", opts.get("max_profit", "N/A"))
            o2.metric("Max Loss", opts.get("max_loss", "N/A"))
            o3.metric("Breakeven", opts.get("breakeven", "N/A"))

            st.markdown(f"**Rationale:** {opts.get('rationale', '')}")
            if opts.get("bang_van_notes"):
                st.caption(f"Bang Van: {opts['bang_van_notes']}")

            if opts.get("legs"):
                import pandas as pd
                legs_df = pd.DataFrame(opts["legs"])
                st.dataframe(legs_df, use_container_width=True, hide_index=True)

        # Sizing
        sizing = a.get("sizing")
        if sizing and sizing.get("shares", 0) > 0:
            st.subheader("Position Sizing")
            z1, z2, z3, z4 = st.columns(4)
            z1.metric("Shares", sizing.get("shares", 0))
            z2.metric("Contracts", sizing.get("contracts", 0))
            z3.metric("Capital", f"${sizing.get('capital_allocated', 0):,.0f}")
            z4.metric("Risk", f"${sizing.get('dollar_risk', 0):,.0f} ({sizing.get('risk_pct_of_portfolio', 0):.1f}%)")

        # Invalidation & Catalysts
        if a.get("invalidation"):
            st.warning(f"**Invalidation:** {a['invalidation']}")
        if a.get("catalysts"):
            cats = a["catalysts"]
            if isinstance(cats, list):
                st.info(f"**Catalysts:** {', '.join(str(c) for c in cats)}")

        if a.get("critic_notes"):
            st.caption(f"Critic: {a['critic_notes']}")
