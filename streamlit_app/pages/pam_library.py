"""PAM Setup Library — Browse, filter, and test PAM trade setups."""

import streamlit as st


# ═══════════════════════════════════════════════════════════
#  BUILT-IN SETUP DEFINITIONS (standalone fallback)
#  Used when core.pam.setup_library is not yet available.
# ═══════════════════════════════════════════════════════════

_BUILTIN_SETUPS = [
    {
        "name": "UC1 — Uptrend Continuation (First Pullback)",
        "category": "Continuation",
        "flow_required": "Bullish",
        "mandatory_conditions": [
            "Price in confirmed uptrend (HH + HL)",
            "First pullback to rising 20 EMA or prior breakout level",
            "Volume contraction on pullback",
        ],
        "optional_conditions": [
            "RSI bouncing off 40-50 zone",
            "Bullish engulfing or hammer at support",
        ],
        "invalidations": [
            "Break below prior HL",
            "Volume expansion on selloff",
            "Close below 50 EMA",
        ],
        "entry_logic": "Enter on close above pullback high or breakout candle high",
        "stop_logic": "Below pullback low or 20 EMA, whichever is tighter",
        "target_logic": "1.5-2R at prior swing high; trail above 20 EMA",
        "quality": "A",
        "ideal_context": "Trending market, sector strength, post-earnings momentum",
        "avoid_when": "Choppy index, pre-FOMC, extended from 200 EMA",
        "options_compatible": True,
        "options_strategies": ["Long Call", "Bull Call Spread", "Diagonal Spread"],
    },
    {
        "name": "UC2 — Uptrend Continuation (Second Pullback)",
        "category": "Continuation",
        "flow_required": "Bullish",
        "mandatory_conditions": [
            "Price in confirmed uptrend with at least 2 HH + HL",
            "Second pullback holding above first pullback low",
            "20 EMA still rising",
        ],
        "optional_conditions": [
            "Tighter consolidation than first pullback",
            "Decreasing volume on pullback",
        ],
        "invalidations": [
            "Break below first pullback low",
            "Bearish divergence on RSI",
            "Failed breakout on high volume",
        ],
        "entry_logic": "Enter on breakout above consolidation high",
        "stop_logic": "Below second pullback low",
        "target_logic": "Measured move from consolidation range; 2-3R",
        "quality": "A",
        "ideal_context": "Strong sector rotation, institutional accumulation",
        "avoid_when": "Late-stage trend, overbought weekly RSI > 80",
        "options_compatible": True,
        "options_strategies": ["Bull Call Spread", "Long Call"],
    },
    {
        "name": "DR1 — Downtrend Reversal (First Attempt)",
        "category": "Reversal",
        "flow_required": "Shifting Bullish",
        "mandatory_conditions": [
            "Price in downtrend making LL + LH",
            "Climactic selling volume (flush)",
            "Bullish divergence on RSI or MACD",
        ],
        "optional_conditions": [
            "Hammer / morning star at key support",
            "Sector peers showing relative strength",
        ],
        "invalidations": [
            "New low on high volume after signal",
            "No follow-through within 3 bars",
            "Gap down below signal candle",
        ],
        "entry_logic": "Enter on close above signal bar high with volume confirmation",
        "stop_logic": "Below flush low (wider stop, reduce size)",
        "target_logic": "1R at declining 20 EMA; 2R at 50 EMA",
        "quality": "B",
        "ideal_context": "Oversold market, VIX spike, capitulation breadth",
        "avoid_when": "Fundamental deterioration, earnings miss, sector weakness",
        "options_compatible": True,
        "options_strategies": ["Crouching Bull Spread", "Bull Put Spread"],
    },
    {
        "name": "DR2 — Downtrend Reversal (Confirmed)",
        "category": "Reversal",
        "flow_required": "Bullish",
        "mandatory_conditions": [
            "DR1 held — first HL confirmed",
            "Price reclaimed 20 EMA",
            "Volume increasing on up moves",
        ],
        "optional_conditions": [
            "Break above declining trendline",
            "Reclaimed VWAP anchored from prior high",
        ],
        "invalidations": [
            "Retest and break of DR1 low",
            "Volume dries up at resistance",
        ],
        "entry_logic": "Enter on breakout above first recovery high",
        "stop_logic": "Below first HL",
        "target_logic": "Prior breakdown level; 2-3R",
        "quality": "A",
        "ideal_context": "Broad market recovery, sector rotation into beaten-down names",
        "avoid_when": "Bear market rally with no breadth improvement",
        "options_compatible": True,
        "options_strategies": ["Long Call", "Bull Call Spread", "Crouching Bull Spread"],
    },
    {
        "name": "DC1 — Downtrend Continuation (First Rally)",
        "category": "Continuation",
        "flow_required": "Bearish",
        "mandatory_conditions": [
            "Price in confirmed downtrend (LH + LL)",
            "First relief rally into declining 20 EMA",
            "Volume contraction on rally",
        ],
        "optional_conditions": [
            "RSI rejected at 50-60 zone",
            "Bearish engulfing at resistance",
        ],
        "invalidations": [
            "Close above prior LH",
            "Volume surge on rally (accumulation)",
        ],
        "entry_logic": "Enter short on rejection candle at 20 EMA or resistance",
        "stop_logic": "Above prior LH or 50 EMA",
        "target_logic": "Prior low; 1.5-2R",
        "quality": "A",
        "ideal_context": "Weak market, sector underperformance, rising VIX",
        "avoid_when": "Pre-earnings, oversold bounce in strong sector",
        "options_compatible": True,
        "options_strategies": ["Bear Call Spread", "Bear Put Spread"],
    },
    {
        "name": "DC2 — Downtrend Continuation (Second Rally)",
        "category": "Continuation",
        "flow_required": "Bearish",
        "mandatory_conditions": [
            "Confirmed downtrend with at least 2 LH + LL",
            "Second rally weaker than the first",
            "20 EMA still declining",
        ],
        "optional_conditions": [
            "Lower volume on second rally",
            "Bearish divergence on momentum",
        ],
        "invalidations": [
            "Rally exceeds first LH",
            "Bullish divergence forming",
        ],
        "entry_logic": "Enter short on break below rally consolidation low",
        "stop_logic": "Above second rally high",
        "target_logic": "Measured move down; 2-3R",
        "quality": "B",
        "ideal_context": "Broad market weakness, deteriorating fundamentals",
        "avoid_when": "Major support nearby, extreme oversold",
        "options_compatible": True,
        "options_strategies": ["Bear Put Spread", "Bear Call Spread"],
    },
    {
        "name": "UR1 — Uptrend Reversal (First Failure)",
        "category": "Reversal",
        "flow_required": "Shifting Bearish",
        "mandatory_conditions": [
            "Price in uptrend making HH + HL",
            "Climactic buying volume (blowoff top)",
            "Bearish divergence on RSI or MACD",
        ],
        "optional_conditions": [
            "Shooting star / evening star at resistance",
            "Sector peers rolling over",
        ],
        "invalidations": [
            "New high on strong volume after signal",
            "Immediate reclaim of breakdown level",
        ],
        "entry_logic": "Enter short on close below signal bar low",
        "stop_logic": "Above blowoff high (wider stop, reduce size)",
        "target_logic": "1R at rising 20 EMA; 2R at 50 EMA",
        "quality": "B",
        "ideal_context": "Extended market, rising VIX from low levels, distribution days",
        "avoid_when": "Strong earnings momentum, sector breakout",
        "options_compatible": True,
        "options_strategies": ["Bear Call Spread", "Bear Put Spread"],
    },
    {
        "name": "UR2 — Uptrend Reversal (Confirmed)",
        "category": "Reversal",
        "flow_required": "Bearish",
        "mandatory_conditions": [
            "UR1 held — first LH confirmed",
            "Price broke below 20 EMA",
            "Volume increasing on down moves",
        ],
        "optional_conditions": [
            "Break below rising trendline",
            "Lost VWAP anchored from prior low",
        ],
        "invalidations": [
            "Price reclaims 20 EMA with volume",
            "Failed breakdown (bear trap)",
        ],
        "entry_logic": "Enter short on break below first recovery low",
        "stop_logic": "Above first LH",
        "target_logic": "Prior breakout level; 2-3R",
        "quality": "A",
        "ideal_context": "Market topping, rotation out of sector, rising yields",
        "avoid_when": "Extreme oversold with support confluence nearby",
        "options_compatible": True,
        "options_strategies": ["Bear Put Spread", "Bear Call Spread"],
    },
]


def _load_setups() -> list[dict]:
    """Load setups from setup_library module if available, else use builtins."""
    try:
        from core.pam.setup_library import SETUP_LIBRARY
        if isinstance(SETUP_LIBRARY, list) and len(SETUP_LIBRARY) > 0:
            return SETUP_LIBRARY
    except (ImportError, AttributeError):
        pass
    return _BUILTIN_SETUPS


# ═══════════════════════════════════════════════════════════
#  QUALITY BADGE RENDERING
# ═══════════════════════════════════════════════════════════

_QUALITY_COLORS = {"A": "#22c55e", "B": "#f59e0b", "C": "#ef4444"}
_QUALITY_LABELS = {"A": "A  High Quality", "B": "B  Medium Quality", "C": "C  Lower Quality"}


def _quality_badge(quality: str) -> str:
    """Return HTML for a colored quality badge."""
    color = _QUALITY_COLORS.get(quality, "#8b949e")
    label = _QUALITY_LABELS.get(quality, quality)
    return (
        f'<span style="background-color:{color}20; color:{color}; '
        f'padding:4px 12px; border-radius:6px; font-weight:600; '
        f'font-size:0.85rem; border:1px solid {color}40;">{label}</span>'
    )


def _options_badge(strategies: list[str]) -> str:
    """Return HTML for options strategy badges."""
    if not strategies:
        return '<span style="color:#8b949e;">No options strategies</span>'
    badges = []
    for s in strategies:
        badges.append(
            f'<span style="background-color:#3b82f620; color:#60a5fa; '
            f'padding:2px 8px; border-radius:4px; font-size:0.78rem; '
            f'margin-right:4px; border:1px solid #3b82f630;">{s}</span>'
        )
    return " ".join(badges)


# ═══════════════════════════════════════════════════════════
#  SETUP SCORING TEST
# ═══════════════════════════════════════════════════════════

def _render_scoring_test(setups: list[dict]):
    """Render the Setup Scoring Test section."""
    st.subheader("Setup Scoring Test")
    st.caption("Input market conditions and see which setups match")

    score_cols = st.columns([1, 1, 1])
    with score_cols[0]:
        test_ticker = st.text_input(
            "Ticker", placeholder="e.g. NVDA", key="pam_test_ticker"
        )
        test_trend = st.selectbox(
            "Current Trend",
            ["Uptrend", "Downtrend", "Sideways"],
            key="pam_test_trend",
        )
    with score_cols[1]:
        test_flow = st.selectbox(
            "Flow / Bias",
            ["Bullish", "Bearish", "Shifting Bullish", "Shifting Bearish", "Neutral"],
            key="pam_test_flow",
        )
        test_pullback = st.checkbox(
            "Pullback to EMA / Support", value=False, key="pam_test_pullback"
        )
    with score_cols[2]:
        test_volume = st.selectbox(
            "Volume Behavior",
            ["Contracting", "Expanding on move", "Climactic", "Normal"],
            key="pam_test_volume",
        )
        test_divergence = st.checkbox(
            "RSI / MACD Divergence", value=False, key="pam_test_divergence"
        )

    if st.button("Run Setup Match", type="primary", key="pam_run_match"):
        if not test_ticker.strip():
            st.warning("Enter a ticker symbol to run the test.")
            return

        st.divider()
        st.markdown(f"**Results for {test_ticker.strip().upper()}**")

        matches = []
        for setup in setups:
            score = 0
            reasons = []

            # Flow alignment
            flow_req = setup.get("flow_required", "")
            if flow_req == test_flow:
                score += 3
                reasons.append("Flow matches exactly")
            elif test_flow.startswith("Shifting") and flow_req.startswith("Shifting"):
                score += 2
                reasons.append("Flow partially matches")

            # Trend context
            is_continuation = setup.get("category") == "Continuation"
            is_reversal = setup.get("category") == "Reversal"
            if is_continuation and test_trend == "Uptrend" and "Bullish" in flow_req:
                score += 2
                reasons.append("Uptrend continuation context")
            elif is_continuation and test_trend == "Downtrend" and "Bearish" in flow_req:
                score += 2
                reasons.append("Downtrend continuation context")
            elif is_reversal and test_trend == "Downtrend" and "Bullish" in flow_req:
                score += 2
                reasons.append("Reversal from downtrend")
            elif is_reversal and test_trend == "Uptrend" and "Bearish" in flow_req:
                score += 2
                reasons.append("Reversal from uptrend")

            # Pullback
            if test_pullback and is_continuation:
                score += 1
                reasons.append("Pullback fits continuation")

            # Volume
            if test_volume == "Contracting" and is_continuation:
                score += 1
                reasons.append("Volume contraction on pullback")
            elif test_volume == "Climactic" and is_reversal:
                score += 1
                reasons.append("Climactic volume for reversal")

            # Divergence
            if test_divergence and is_reversal:
                score += 1
                reasons.append("Divergence supports reversal")

            if score >= 3:
                matches.append((score, setup, reasons))

        matches.sort(key=lambda x: x[0], reverse=True)

        if not matches:
            st.info("No setups matched the given conditions (minimum score: 3).")
        else:
            for score, setup, reasons in matches:
                quality = setup.get("quality", "C")
                color = _QUALITY_COLORS.get(quality, "#8b949e")
                st.markdown(
                    f'<div style="background-color:#111820; border-left:4px solid {color}; '
                    f'padding:12px 16px; border-radius:0 8px 8px 0; margin-bottom:8px;">'
                    f'<strong style="color:#e6edf3;">{setup["name"]}</strong> '
                    f'<span style="color:{color}; font-weight:600;"> Score: {score}/8</span><br/>'
                    f'<span style="color:#8b949e; font-size:0.85rem;">{", ".join(reasons)}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


# ═══════════════════════════════════════════════════════════
#  PAGE RENDERER
# ═══════════════════════════════════════════════════════════

def render():
    st.title("PAM Setup Library")
    st.caption(
        "Price Action Mastery — Complete setup catalog with entry/exit rules, "
        "quality grades, and options compatibility"
    )

    setups = _load_setups()

    # ── Session state for active/inactive toggles ──
    if "pam_setup_active" not in st.session_state:
        st.session_state["pam_setup_active"] = {s["name"]: True for s in setups}

    # ── Filters ──
    filter_cols = st.columns(3)
    with filter_cols[0]:
        cat_filter = st.multiselect(
            "Category",
            options=sorted({s.get("category", "Other") for s in setups}),
            default=[],
            placeholder="All categories",
        )
    with filter_cols[1]:
        quality_filter = st.multiselect(
            "Quality Grade",
            options=["A", "B", "C"],
            default=[],
            placeholder="All grades",
        )
    with filter_cols[2]:
        flow_filter = st.multiselect(
            "Flow Required",
            options=sorted({s.get("flow_required", "") for s in setups}),
            default=[],
            placeholder="All flows",
        )

    st.divider()

    # ── Setup cards ──
    displayed = 0
    for setup in setups:
        # Apply filters
        if cat_filter and setup.get("category") not in cat_filter:
            continue
        if quality_filter and setup.get("quality") not in quality_filter:
            continue
        if flow_filter and setup.get("flow_required") not in flow_filter:
            continue

        displayed += 1
        name = setup["name"]
        quality = setup.get("quality", "C")
        is_active = st.session_state["pam_setup_active"].get(name, True)

        with st.expander(
            f"{'[ACTIVE]' if is_active else '[INACTIVE]'}  {name}",
            expanded=False,
        ):
            # Header row: quality badge + active toggle
            header_cols = st.columns([3, 1])
            with header_cols[0]:
                st.markdown(_quality_badge(quality), unsafe_allow_html=True)
                st.markdown(
                    f'<span style="color:#8b949e; font-size:0.85rem; margin-left:12px;">'
                    f'Category: {setup.get("category", "N/A")} | '
                    f'Flow: {setup.get("flow_required", "N/A")}</span>',
                    unsafe_allow_html=True,
                )
            with header_cols[1]:
                toggle_key = f"toggle_{name}"
                new_active = st.toggle("Active", value=is_active, key=toggle_key)
                if new_active != is_active:
                    st.session_state["pam_setup_active"][name] = new_active

            st.divider()

            # Conditions
            cond_cols = st.columns(2)
            with cond_cols[0]:
                st.markdown("**Mandatory Conditions**")
                for cond in setup.get("mandatory_conditions", []):
                    st.markdown(f"- {cond}")

                st.markdown("**Optional Conditions**")
                for cond in setup.get("optional_conditions", []):
                    st.markdown(f"- {cond}")

            with cond_cols[1]:
                st.markdown("**Invalidations**")
                for inv in setup.get("invalidations", []):
                    st.markdown(f"- {inv}")

            st.divider()

            # Entry / Stop / Target
            rule_cols = st.columns(3)
            with rule_cols[0]:
                st.markdown("**Entry Logic**")
                st.info(setup.get("entry_logic", "N/A"))
            with rule_cols[1]:
                st.markdown("**Stop Logic**")
                st.warning(setup.get("stop_logic", "N/A"))
            with rule_cols[2]:
                st.markdown("**Target Logic**")
                st.success(setup.get("target_logic", "N/A"))

            # Context
            ctx_cols = st.columns(2)
            with ctx_cols[0]:
                st.markdown("**Ideal Context**")
                st.markdown(f"_{setup.get('ideal_context', 'N/A')}_")
            with ctx_cols[1]:
                st.markdown("**Avoid When**")
                st.markdown(f"_{setup.get('avoid_when', 'N/A')}_")

            # Options compatibility
            st.divider()
            opts_compat = setup.get("options_compatible", False)
            if opts_compat:
                strategies = setup.get("options_strategies", [])
                st.markdown(
                    f"**Options Compatible** &mdash; {_options_badge(strategies)}",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("**Options:** Not recommended for this setup")

    if displayed == 0:
        st.info("No setups match the selected filters.")

    # ── Setup Scoring Test ──
    st.divider()
    _render_scoring_test(setups)
