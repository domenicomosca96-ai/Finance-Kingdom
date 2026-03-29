"""
PAM Setup Library — Canonical definitions for all tradeable PAM setups.

Each PAMSetup encodes the full rule set (mandatory conditions, invalidations,
entry/stop/target logic, quality defaults, context filters) so the
deterministic PAM engine output can be validated and scored against a
known playbook.

Setups currently defined:
  UC1  Uptrend Continuation 1
  DC1  Downtrend Continuation 1
  UR2  Uptrend Reversal 2
  DR2  Downtrend Reversal 2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ═══════════════════════════════════════════════════════════
#  DATACLASS
# ═══════════════════════════════════════════════════════════

@dataclass
class PAMSetup:
    """Canonical definition of a single PAM setup."""

    name: str                       # UC1, DC1, UR2, DR2
    category: str                   # continuation / reversal
    flow_required: str              # description of required flow
    mandatory_conditions: list[str]
    optional_conditions: list[str]
    invalidations: list[str]
    bar_lookback: int
    entry_logic: str
    stop_logic: str
    target_logic: str
    interpretive_notes: str
    quality_default: str            # A / B / C
    ideal_context: str
    avoid_when: str
    options_compatible: bool
    active: bool = True


# ═══════════════════════════════════════════════════════════
#  SETUP LIBRARY
# ═══════════════════════════════════════════════════════════

SETUP_LIBRARY: dict[str, PAMSetup] = {

    # ── UC1 — Uptrend Continuation 1 ─────────────────────
    "UC1": PAMSetup(
        name="UC1",
        category="continuation",
        flow_required="price above 50 SMA, positive flow",
        mandatory_conditions=[
            "retracement to 20 or 50 SMA zone",
            "hold above key support",
            "EXE bar confirmation within lookback",
        ],
        optional_conditions=[
            "volume expansion on EXE",
            "RSI not overbought",
        ],
        invalidations=[
            "close below 50 SMA",
            "lower low below swing low",
        ],
        bar_lookback=5,
        entry_logic="close of EXE bar or next bar open",
        stop_logic="below swing low or below 50 SMA",
        target_logic="prior swing high, then extension",
        interpretive_notes=(
            "Bread-and-butter trend continuation. Best when pullback is "
            "orderly (wave-style) rather than flush. Higher win-rate in "
            "confirmed uptrend with macro tailwind."
        ),
        quality_default="A",
        ideal_context="macro liquidity favorable, sector in leadership",
        avoid_when="late speculation phase, divergent world, sector lagging",
        options_compatible=True,
    ),

    # ── DC1 — Downtrend Continuation 1 ───────────────────
    "DC1": PAMSetup(
        name="DC1",
        category="continuation",
        flow_required="price below 50 SMA, negative flow",
        mandatory_conditions=[
            "retracement to 20 or 50 SMA zone from below",
            "resistance holds",
            "EXE bar down within lookback",
        ],
        optional_conditions=[
            "volume on breakdown",
            "RSI not oversold",
        ],
        invalidations=[
            "close above 50 SMA",
            "higher high above swing high",
        ],
        bar_lookback=5,
        entry_logic="close of EXE bar or next bar open (short)",
        stop_logic="above swing high or above 50 SMA",
        target_logic="prior swing low, then extension",
        interpretive_notes=(
            "Mirror of UC1 for shorts. Works well when macro liquidity is "
            "decelerating and the sector is under distribution. Avoid if "
            "oversold bounce signals are present."
        ),
        quality_default="A",
        ideal_context="macro liquidity decelerating, sector weak",
        avoid_when="early rebound phase, strong sector leadership",
        options_compatible=True,
    ),

    # ── UR2 — Uptrend Reversal 2 ─────────────────────────
    "UR2": PAMSetup(
        name="UR2",
        category="reversal",
        flow_required="transitioning from below to above 50 SMA",
        mandatory_conditions=[
            "flush down / majority flush",
            "retracement wider than UC1",
            "EXE bar up within lookback",
            "break above recent resistance",
        ],
        optional_conditions=[
            "volume climax on flush",
            "RSI divergence",
        ],
        invalidations=[
            "new lower low after EXE attempt",
            "fail to reclaim 20 SMA",
        ],
        bar_lookback=8,
        entry_logic="close of EXE bar or break above confirmation level",
        stop_logic="below flush low",
        target_logic="50 SMA first, then prior structure high",
        interpretive_notes=(
            "Higher-risk reversal play. Requires a clear flush / capitulation "
            "event followed by a convincing EXE bar. Position size should be "
            "smaller than continuation setups until the trend is confirmed."
        ),
        quality_default="B",
        ideal_context=(
            "liquidity turning from deceleration to flat/acceleration, "
            "oversold bounce"
        ),
        avoid_when="strong downtrend, liquidity still decelerating hard",
        options_compatible=True,
    ),

    # ── DR2 — Downtrend Reversal 2 ───────────────────────
    "DR2": PAMSetup(
        name="DR2",
        category="reversal",
        flow_required="transitioning from above to below 50 SMA",
        mandatory_conditions=[
            "flush up / majority flush",
            "retracement wider than DC1",
            "EXE bar down within lookback",
        ],
        optional_conditions=[
            "volume climax on flush up",
            "RSI divergence from high",
        ],
        invalidations=[
            "new higher high after EXE attempt",
        ],
        bar_lookback=8,
        entry_logic="close of EXE bar or break below confirmation",
        stop_logic="above flush high",
        target_logic="50 SMA first, then prior structure low",
        interpretive_notes=(
            "Mirror of UR2 for bearish reversals. Requires exhaustion / "
            "blow-off top followed by distribution. Default quality B "
            "reflects inherent reversal risk."
        ),
        quality_default="B",
        ideal_context=(
            "liquidity turning from acceleration to deceleration, overbought"
        ),
        avoid_when="strong uptrend, liquidity still accelerating",
        options_compatible=True,
    ),
}


# ═══════════════════════════════════════════════════════════
#  ACCESSOR HELPERS
# ═══════════════════════════════════════════════════════════

def get_active_setups() -> list[PAMSetup]:
    """Return all setups where ``active`` is True."""
    return [s for s in SETUP_LIBRARY.values() if s.active]


def get_setup(name: str) -> Optional[PAMSetup]:
    """Return a single setup by name, or ``None`` if not found."""
    return SETUP_LIBRARY.get(name.upper())


# ═══════════════════════════════════════════════════════════
#  VALIDATION / SCORING
# ═══════════════════════════════════════════════════════════

def _score_flow_alignment(pam_result: dict, setup: PAMSetup) -> int:
    """Score 0-25: how well the PAM engine flow state matches the setup requirement."""
    flow = pam_result.get("flow_state", "")
    above_sma50 = pam_result.get("above_sma50", None)

    if setup.category == "continuation":
        if setup.name in ("UC1",):
            # Need positive flow + price above 50 SMA
            if above_sma50 and flow in ("positive_flow", "POSITIVE"):
                return 25
            if above_sma50:
                return 15
            return 0
        if setup.name in ("DC1",):
            # Need negative flow + price below 50 SMA
            if not above_sma50 and flow in ("negative_flow", "NEGATIVE"):
                return 25
            if not above_sma50:
                return 15
            return 0

    if setup.category == "reversal":
        if setup.name in ("UR2",):
            # Transitioning from below to above
            if flow in ("transition_up", "TRANSITION_UP"):
                return 25
            if not above_sma50 and flow in ("positive_flow", "POSITIVE"):
                return 15  # not yet above but momentum turning
            if above_sma50:
                return 10  # already crossed — may be late
            return 0
        if setup.name in ("DR2",):
            if flow in ("transition_down", "TRANSITION_DOWN"):
                return 25
            if above_sma50 and flow in ("negative_flow", "NEGATIVE"):
                return 15
            if not above_sma50:
                return 10
            return 0

    return 0


def _score_pattern_match(pam_result: dict, setup: PAMSetup) -> int:
    """Score 0-25: does the detected pattern match the requested setup?"""
    detected = pam_result.get("pattern", "NONE").upper()
    confidence = pam_result.get("pattern_confidence", 0.0)

    if detected == setup.name.upper():
        # Scale by confidence: 25 * confidence (0.0-1.0)
        return min(25, int(round(25 * confidence)))

    # Partial credit for same family (e.g. UC2 vs UC1)
    if detected[:2] == setup.name[:2]:
        return min(15, int(round(15 * confidence)))

    return 0


def _score_structure_quality(pam_result: dict, setup: PAMSetup) -> int:
    """Score 0-25: structural quality checks (invalidations, flush, conditions)."""
    score = 0
    metadata = pam_result.get("metadata", {}) or {}

    # Check no invalidation is active
    invalidated = False
    if setup.name in ("UC1",) and pam_result.get("above_sma50") is False:
        invalidated = True
    if setup.name in ("DC1",) and pam_result.get("above_sma50") is True:
        invalidated = True

    if invalidated:
        return 0

    # Base points for not being invalidated
    score += 10

    # Flush detection bonus for reversals
    if setup.category == "reversal":
        if pam_result.get("flush_detected") or pam_result.get("is_flush"):
            score += 8
    else:
        # For continuation, wave-style pullback is better
        if pam_result.get("is_wave"):
            score += 8
        elif not pam_result.get("is_flush"):
            score += 4  # orderly pullback without flush — acceptable

    # Micro score contribution
    micro = pam_result.get("micro_score", 50.0)
    if micro >= 70:
        score += 7
    elif micro >= 50:
        score += 4
    elif micro >= 30:
        score += 2

    return min(25, score)


def _score_rr_ratio(pam_result: dict, setup: PAMSetup) -> int:
    """Score 0-25: reward-to-risk ratio from trigger/stop/target levels."""
    trigger = pam_result.get("trigger_level")
    stop = pam_result.get("stop_level")
    target = pam_result.get("target_level")

    if trigger is None or stop is None or target is None:
        return 0

    risk = abs(trigger - stop)
    if risk == 0:
        return 0

    reward = abs(target - trigger)
    rr = reward / risk

    if rr >= 3.0:
        return 25
    if rr >= 2.0:
        return 20
    if rr >= 1.5:
        return 15
    if rr >= 1.0:
        return 10
    if rr >= 0.5:
        return 5
    return 0


def validate_pam_against_setup(pam_result: dict, setup_name: str) -> dict:
    """
    Validate a PAM engine result dict against a named setup from the library.

    Parameters
    ----------
    pam_result : dict
        Output from the deterministic PAM engine.  Expected keys include
        ``flow_state``, ``above_sma50``, ``pattern``, ``pattern_confidence``,
        ``trigger_level``, ``stop_level``, ``target_level``,
        ``flush_detected``, ``is_flush``, ``is_wave``, ``micro_score``,
        and optionally ``metadata``.
    setup_name : str
        One of the keys in ``SETUP_LIBRARY`` (e.g. ``"UC1"``).

    Returns
    -------
    dict
        PAM_VALID            : bool   — all mandatory conditions plausible
        PAM_QUALITY_SCORE    : int    — composite 0-100
        PAM_CONTEXT_FIT_SCORE: int    — 0-100 based on flow + structure
        PAM_TRIGGER_READY    : bool   — trigger/stop/target levels present
        PAM_NOTES            : list[str] — human-readable scoring notes
    """
    setup = get_setup(setup_name)
    if setup is None:
        return {
            "PAM_VALID": False,
            "PAM_QUALITY_SCORE": 0,
            "PAM_CONTEXT_FIT_SCORE": 0,
            "PAM_TRIGGER_READY": False,
            "PAM_NOTES": [f"Unknown setup name: {setup_name}"],
        }

    if not setup.active:
        return {
            "PAM_VALID": False,
            "PAM_QUALITY_SCORE": 0,
            "PAM_CONTEXT_FIT_SCORE": 0,
            "PAM_TRIGGER_READY": False,
            "PAM_NOTES": [f"Setup {setup_name} is inactive"],
        }

    notes: list[str] = []

    # ── Individual score components ───────────────────────
    flow_score = _score_flow_alignment(pam_result, setup)
    pattern_score = _score_pattern_match(pam_result, setup)
    structure_score = _score_structure_quality(pam_result, setup)
    rr_score = _score_rr_ratio(pam_result, setup)

    quality_score = flow_score + pattern_score + structure_score + rr_score

    notes.append(
        f"flow_alignment={flow_score}/25, pattern_match={pattern_score}/25, "
        f"structure_quality={structure_score}/25, rr_ratio={rr_score}/25"
    )

    # ── Context fit (flow + structure, normalised to 0-100) ──
    context_fit = int(round((flow_score + structure_score) / 50 * 100))

    # ── Validity: flow alignment present + pattern detected ──
    pam_valid = flow_score >= 15 and pattern_score >= 10 and structure_score > 0
    if not pam_valid:
        if flow_score < 15:
            notes.append("INVALID: flow alignment insufficient")
        if pattern_score < 10:
            notes.append("INVALID: pattern not convincingly detected")
        if structure_score == 0:
            notes.append("INVALID: structure invalidated")

    # ── Trigger readiness ─────────────────────────────────
    trigger_ready = all(
        pam_result.get(k) is not None
        for k in ("trigger_level", "stop_level", "target_level")
    )
    if not trigger_ready:
        notes.append("Trigger NOT ready: missing trigger/stop/target levels")

    # ── Quality-default annotation ────────────────────────
    notes.append(f"Setup quality default: {setup.quality_default}")

    return {
        "PAM_VALID": pam_valid,
        "PAM_QUALITY_SCORE": quality_score,
        "PAM_CONTEXT_FIT_SCORE": context_fit,
        "PAM_TRIGGER_READY": trigger_ready,
        "PAM_NOTES": notes,
    }
