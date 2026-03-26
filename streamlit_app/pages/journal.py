"""Journal — Save, review, and close trade entries."""

import streamlit as st
import pandas as pd
from datetime import datetime


def render():
    st.title("Journal")
    st.caption("Trade journal — track entries, exits, and P/L for feedback")

    tab1, tab2 = st.tabs(["Open Trades", "New Entry"])

    with tab1:
        _render_trades()

    with tab2:
        _render_new_entry()


def _render_trades():
    entries = _get_entries()
    if not entries:
        st.info("No journal entries yet. Create one from the **New Entry** tab or save an analysis.")
        return

    # Summary metrics
    open_trades = [e for e in entries if e.status == "open"]
    closed_trades = [e for e in entries if e.status == "closed"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open Trades", len(open_trades))
    c2.metric("Closed Trades", len(closed_trades))

    total_pnl = sum(e.pnl or 0 for e in closed_trades)
    win_rate = (sum(1 for e in closed_trades if (e.pnl or 0) > 0) / len(closed_trades) * 100) if closed_trades else 0
    c3.metric("Total P/L", f"${total_pnl:,.2f}")
    c4.metric("Win Rate", f"{win_rate:.0f}%")

    st.divider()

    # Open trades
    if open_trades:
        st.subheader("Open Positions")
        for e in open_trades:
            with st.expander(f"{e.ticker} — {e.direction.upper()} — Score: {e.ai_score:.0f}%" if e.ai_score else f"{e.ticker} — {e.direction.upper()}"):
                oc1, oc2, oc3 = st.columns(3)
                oc1.metric("Entry", f"${e.entry_price:.2f}")
                oc2.metric("Stop", f"${e.stop_loss:.2f}")
                oc3.metric("Target", f"${e.target_price:.2f}")

                if e.strategy:
                    st.markdown(f"**Strategy:** {e.strategy}")
                if e.notes:
                    st.markdown(f"**Notes:** {e.notes}")
                if e.conviction:
                    st.markdown(f"**Conviction:** {e.conviction}")

                st.caption(f"Opened: {e.opened_at.strftime('%Y-%m-%d') if e.opened_at else 'N/A'}")

                # Close trade form
                st.markdown("---")
                st.markdown("**Close this trade:**")
                close_col1, close_col2 = st.columns(2)
                with close_col1:
                    exit_price = st.number_input(f"Exit Price ({e.ticker})", min_value=0.01, value=float(e.entry_price), key=f"exit_{e.id}")
                with close_col2:
                    close_notes = st.text_input(f"Close Notes ({e.ticker})", key=f"cnotes_{e.id}")

                if st.button(f"Close Trade {e.ticker}", key=f"close_{e.id}"):
                    _close_trade(e.id, exit_price, close_notes)
                    st.rerun()

    # Closed trades table
    if closed_trades:
        st.subheader("Closed Trades")
        df = pd.DataFrame([{
            "Ticker": e.ticker,
            "Direction": e.direction.upper(),
            "Entry": f"${e.entry_price:.2f}",
            "Exit": f"${e.exit_price:.2f}" if e.exit_price else "N/A",
            "P/L $": f"${e.pnl:.2f}" if e.pnl else "N/A",
            "P/L %": f"{e.pnl_pct:.1f}%" if e.pnl_pct else "N/A",
            "Strategy": e.strategy or "",
            "Score": f"{e.ai_score:.0f}" if e.ai_score else "",
            "Opened": e.opened_at.strftime("%Y-%m-%d") if e.opened_at else "",
            "Closed": e.closed_at.strftime("%Y-%m-%d") if e.closed_at else "",
        } for e in closed_trades])
        st.dataframe(df, use_container_width=True, hide_index=True)


def _render_new_entry():
    st.subheader("New Journal Entry")

    with st.form("new_journal_entry"):
        col1, col2 = st.columns(2)
        with col1:
            ticker = st.text_input("Ticker", placeholder="NVDA").strip().upper()
            direction = st.selectbox("Direction", ["long", "short"])
            entry_price = st.number_input("Entry Price", min_value=0.01, value=100.0)
        with col2:
            stop_loss = st.number_input("Stop Loss", min_value=0.01, value=95.0)
            target_price = st.number_input("Target Price", min_value=0.01, value=110.0)
            strategy = st.text_input("Strategy", placeholder="Bull Call Spread")

        conviction = st.selectbox("Conviction", ["high", "medium", "low"])
        notes = st.text_area("Notes", placeholder="Why am I taking this trade?")
        ai_score = st.number_input("AI Score (optional)", min_value=0.0, max_value=100.0, value=50.0)

        submitted = st.form_submit_button("Save Entry", type="primary")

        if submitted and ticker:
            _save_entry(ticker, direction, entry_price, stop_loss, target_price, strategy, conviction, notes, ai_score)


def _save_entry(ticker, direction, entry_price, stop_loss, target_price, strategy, conviction, notes, ai_score):
    try:
        from core.models.database import SessionLocal
        from core.models import JournalEntry

        with SessionLocal() as db:
            entry = JournalEntry(
                ticker=ticker, direction=direction,
                entry_price=entry_price, stop_loss=stop_loss, target_price=target_price,
                strategy=strategy, conviction=conviction, notes=notes, ai_score=ai_score,
            )
            db.add(entry)
            db.commit()
        st.success(f"Journal entry saved for {ticker}")
    except Exception as e:
        st.error(f"Failed to save: {str(e)}")


def _close_trade(entry_id: int, exit_price: float, notes: str):
    try:
        from core.models.database import SessionLocal
        from core.models import JournalEntry

        with SessionLocal() as db:
            entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
            if entry:
                entry.exit_price = exit_price
                entry.status = "closed"
                entry.closed_at = datetime.utcnow()

                if entry.direction == "long":
                    entry.pnl = (exit_price - entry.entry_price)
                    entry.pnl_pct = ((exit_price - entry.entry_price) / entry.entry_price) * 100
                else:
                    entry.pnl = (entry.entry_price - exit_price)
                    entry.pnl_pct = ((entry.entry_price - exit_price) / entry.entry_price) * 100

                if notes:
                    entry.notes = (entry.notes or "") + f"\n[Close] {notes}"

                db.commit()
                st.success(f"Trade closed — P/L: ${entry.pnl:.2f} ({entry.pnl_pct:.1f}%)")
    except Exception as e:
        st.error(f"Failed to close: {str(e)}")


def _get_entries():
    try:
        from core.models.database import SessionLocal
        from core.models import JournalEntry
        with SessionLocal() as db:
            return db.query(JournalEntry).order_by(JournalEntry.opened_at.desc()).all()
    except Exception:
        return []
