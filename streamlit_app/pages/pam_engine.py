"""PAM Engine — Single ticker deterministic analysis."""

import streamlit as st
from dataclasses import asdict


def render():
    st.title("PAM Engine")
    st.caption("Deterministic Price Action & Momentum analysis (Piranha Profits methodology)")

    col1, col2 = st.columns([3, 1])
    with col1:
        ticker = st.text_input("Ticker Symbol", value="AAPL", placeholder="e.g., NVDA, AAPL, MSFT").strip().upper()
    with col2:
        st.markdown("")
        st.markdown("")
        run_btn = st.button("Run PAM Analysis", type="primary", use_container_width=True)

    if run_btn and ticker:
        _run_pam(ticker)
    elif "pam_result" in st.session_state:
        _display_result(st.session_state.pam_result)


def _run_pam(ticker: str):
    with st.status(f"Running PAM analysis for {ticker}...", expanded=True) as status:
        try:
            st.write("Downloading market data...")
            from core.pam import run_full_pam
            result = run_full_pam(ticker)
            st.session_state.pam_result = result
            status.update(label=f"PAM analysis complete for {ticker}", state="complete")
            _display_result(result)
        except Exception as e:
            status.update(label=f"Error: {str(e)}", state="error")
            st.error(f"Failed to analyze {ticker}: {str(e)}")


def _display_result(result):
    st.divider()

    # ── Header metrics ──
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Price", f"${result.current_price:.2f}")
    c2.metric("SMA 50", f"${result.sma_50:.2f}" if result.sma_50 else "N/A")
    c3.metric("RSI 14", f"{result.rsi_14:.1f}" if result.rsi_14 else "N/A")
    c4.metric("ATR 14", f"${result.atr_14:.2f}" if result.atr_14 else "N/A")
    c5.metric("Micro Score", f"{result.micro_score:.1f}/100")

    st.divider()

    # ── Two columns: Flow/Momentum | Pattern/Rotation ──
    left, right = st.columns(2)

    with left:
        st.subheader("Flow State")
        flow = result.flow
        flow_label = flow.state.replace("_", " ").title()
        if flow.state == "positive_flow":
            st.success(f"**{flow_label}** — Bullish structure")
        elif flow.state == "negative_flow":
            st.error(f"**{flow_label}** — Bearish structure")
        elif flow.state in ("transition_up", "transition_down"):
            st.warning(f"**{flow_label}** — Mixed structure")
        else:
            st.info(f"**{flow_label}**")

        fc1, fc2, fc3 = st.columns(3)
        fc1.metric("Above SMA50", "Yes" if flow.above_sma50 else "No")
        fc2.metric("HH/HL Count", flow.hh_hl_count)
        fc3.metric("LH/LL Count", flow.lh_ll_count)

        st.subheader("Momentum")
        mom = result.momentum
        mom_type = "FLUSH" if mom.is_flush else "WAVE" if mom.is_wave else "Neutral"
        direction = mom.direction.upper()

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Type", mom_type)
        mc2.metric("Direction", direction)
        mc3.metric("Angle", f"{mom.angle_degrees:.1f} deg")

        mc4, mc5 = st.columns(2)
        mc4.metric("Flush Bars", mom.flush_bar_count)
        mc5.metric("Move Length", f"{mom.bars_in_move} bars")

    with right:
        st.subheader("Pattern Detection")
        pat = result.pattern
        if pat.pattern != "NONE":
            if pat.confirmed:
                st.success(f"**{pat.pattern}** — CONFIRMED (Confidence: {pat.confidence:.0f}%)")
            else:
                st.warning(f"**{pat.pattern}** — Forming (Confidence: {pat.confidence:.0f}%)")

            pc1, pc2, pc3 = st.columns(3)
            pc1.metric("Trigger", f"${pat.trigger_level:.2f}" if pat.trigger_level else "N/A")
            pc2.metric("Stop", f"${pat.stop_level:.2f}" if pat.stop_level else "N/A")
            pc3.metric("Target", f"${pat.target_level:.2f}" if pat.target_level else "N/A")

            if pat.rr_ratio:
                st.metric("Risk:Reward", f"{pat.rr_ratio:.2f}:1")

            st.info(pat.description)
        else:
            st.info("No clear PAM setup detected at current levels.")
            if pat.description:
                st.caption(pat.description)

        st.subheader("Rotation Segment")
        seg = result.rotation_segment
        seg_names = {"A": "Accumulation (hidden, bullish)", "B": "Distribution (obvious flush up, be bearish)",
                     "C": "Distribution (hidden, bearish)", "D": "Accumulation (panic flush down, be bullish)"}
        seg_desc = seg_names.get(seg, seg)

        if seg in ("A", "D"):
            st.success(f"**Segment {seg}** — {seg_desc}")
        else:
            st.error(f"**Segment {seg}** — {seg_desc}")

        st.subheader("Options Context")
        oc1, oc2, oc3 = st.columns(3)
        oc1.metric("IV Rank", f"{result.iv_rank:.0f}%" if result.iv_rank is not None else "N/A")
        oc2.metric("Days to Earnings", f"{result.days_to_earnings}d" if result.days_to_earnings else "N/A")
        oc3.metric("Volume Ratio", f"{result.volume_ratio:.2f}x" if result.volume_ratio else "N/A")

        if result.near_earnings:
            st.warning("Near earnings — consider earnings-specific strategies.")

    # ── Full context string ──
    with st.expander("Raw PAM Context (for LLM injection)", expanded=False):
        st.code(result.to_context_string(), language="text")
