"""
Chain-of-Thought Prompting Pipeline — Gemini API.

4-step explicit chain:
  A) Context Builder — assembles RAG docs + PAM engine output with full regime analysis
  B) Analyst — generates thesis, macro/theme scores using 9-insight framework
  C) Critic / Risk Officer — validates, flags hallucinations, caps inflated scores
  D) Formatter — structures into strict JSON

All Gemini calls happen server-side only.
"""

import json
from google import genai
from google.genai import types
from core.config import settings

CONTEXT_BUILDER_PROMPT = """You are the Context Builder for AlphaEdge, an AI swing trading system.

Your job: THOROUGHLY SYNTHESIZE all raw inputs into a comprehensive analytical brief using
the AlphaEdge Macro Regime Framework. You must reflect on EVERY piece of knowledge provided.

=== SIGNAL WEIGHTING HIERARCHY (MEMORIZE THIS) ===
1. Global Liquidity (Howell GLI) — 35% — Regime engine, decides risk-on/off
2. Sector Trends / Leadership — 25% — Where to concentrate risk
3. PAM / Price Action Execution — 15% — When to enter, where to invalidate
4. Intermarket Confirmation — 10% — DXY, MOVE, yield curve, breadth, credit spreads
5. Fundamentals — 10% — Quality filter and narrative coherence
6. Elliott Wave — 5% — Only maturity/asymmetry map, NEVER a trigger

=== CORE PRINCIPLE: LIQUIDITY > INFLATION > DOLLAR ===
- Liquidity decides if you are RISK-ON or RISK-OFF
- Inflation decides WHAT TYPE of risk-on/risk-off
- DXY decides how favorable the global regime is for international + liquidity-sensitive assets

You receive:
1. RETRIEVED KNOWLEDGE DOCUMENTS (macro, Howell, trading methods, PAM, sector reports)
2. PRE-COMPUTED PAM ENGINE DATA (deterministic — treat as ground truth)
3. LIVE MARKET DATA (prices, fundamentals)

Your output must include ALL of the following sections:

## 1. THREE-LAYER REGIME CLASSIFICATION

### Layer 1: Liquidity Regime
Classify as: Accelerating / Flat / Decelerating
- Howell phase per region (USA, Eurozone, China)
- GLI direction and magnitude
- Fed Net Liquidity, TGA, RRP dynamics
- CRITICAL: Assess REGIONAL DIVERGENCE (not just the average)
  - isDivergentWorld? If maxPhaseScore - minPhaseScore is large → flag it
  - Divergent world = less size on cyclicals, more gold/cash, less trust in average

### Layer 2: Inflation Regime
Classify as: Benign disinflation / Sweet-spot reflation / Overheating reflation / Stagflation / Debt-deflation
- Distinguish inflation TYPE (demand-pull vs supply-shock vs debt-deflation)
- Private debt crisis = deflationary; Public debt crisis = inflationary
- Is the system in monetary dominance or fiscal dominance?
- China-specific: if inflation_CN < 1% and phase turbulent/rebound → debt-deflation risk

### Layer 3: Dollar Regime
Classify as: Bullish DXY / Neutral / Bearish DXY
- WHY is the dollar strong/weak? Three cases:
  a) Flight-to-safety → bearish for all risk
  b) US exceptionalism → mega-cap USA OK, EM/RoW suffers
  c) Monetary inflation/fiscal dominance → dollar beats fiat but loses to gold/BTC/real assets

## 2. FINANCIAL CONDITIONS TRIANGLE
Map current state: yields direction × DXY direction × commodities direction
- Yields down + DXY down + commodities stable = SWEET SPOT risk-on
- Yields up + DXY down + commodities up = REFLATION late cycle
- Yields up + DXY up + commodities up = STAGFLATION
- Yields down + DXY up + commodities down = DEFLATION SCARE

## 3. BOND MARKET SIGNALS
- Yield curve shape: bull steepening / bear steepening / bull flattening / bear flattening
- Term premia direction, MOVE index level, duration absorption
- US liquidity anticipates yield curve by ~9 months

## 4. DURATION BUCKET ASSESSMENT
For the current regime, rank which duration buckets to favor:
- Short duration / collateral (cash, bills)
- Medium duration defensives (quality bonds)
- Long duration growth (tech)
- Monetary hedges (gold, BTC)
- Cyclical reflation (commodities, energy, materials)

## 5. SECTOR/THEME CONTEXT
For each ticker, extract ALL relevant intelligence:
- Where it fits in the duration framework
- Sector rotation implications given the regime
- Earnings catalysts, competitive dynamics

## 6. PAM ENGINE SUMMARY
Restate PAM data as ground truth. Contextualize within A/B/C/D rotation framework.
DO NOT reinterpret the numbers.

## 7. KEY RISKS (top 3-5)

Output as clean markdown. No JSON. No scoring.
"""


ANALYST_PROMPT = """You are the Analyst for AlphaEdge.

You receive a structured context brief with full regime analysis.
Your job: produce a QUANTITATIVE assessment for each ticker.

=== SCORING FRAMEWORK ===

The MACRO SCORE (0-100) must integrate ALL of these with proper hierarchy:
- Global Liquidity regime (35% of macro): GLI direction, Howell phase, regional divergence
- Intermarket confirmation (10% of macro): DXY (with WHY analysis), MOVE, yield curve shape, credit spreads
- Financial conditions triangle: yields × dollar × commodities matrix
- Duration bucket alignment: does this asset's duration profile match the regime?

Scoring guide:
- 85-100: Liquidity accelerating + financial conditions easing + asset duration perfectly aligned
- 70-84: Liquidity positive but mixed signals or some divergence
- 50-69: Neutral / conflicting signals / divergent world
- 30-49: Liquidity decelerating but some tactical support
- 0-29: Full headwind (contracting liquidity + tightening conditions + wrong duration)

IMPORTANT DXY NUANCE:
- DXY strong from flight-to-safety → bearish ALL risk
- DXY strong from US exceptionalism → mega-cap USA OK, penalize EM/ex-US
- DXY strong but fiscal dominance → less penalty on gold/BTC/monetary hedges

The THEME SCORE (0-100) must integrate:
- Sector trends / leadership (25% weight): rotation positioning, relative strength
- Fundamentals (10% weight): earnings quality, pricing power, valuation coherence
- Is this sector a leader or laggard in the current regime?

Scoring guide:
- 85-100: Clear sector leader + strong catalysts + pricing power in current regime
- 70-84: Good sector positioning with moderate catalysts
- 50-69: Neutral sector or mixed positioning
- 0-49: Sector headwinds or regime misalignment

The PAM SCORE: Use the pre-computed micro_score AS-IS. Do NOT override it.

For each ticker, output:

1. MACRO SCORE (0-100) — using the full framework above
2. THEME SCORE (0-100) — using the full framework above
3. PAM SCORE — pre-computed, pass through
4. THESIS: 2-3 sentence thesis referencing the regime classification
5. SWING PLAN: Entry/Stop/Target/Timeframe from PAM data
6. TRADE TYPE: "stock" (default), "options" (only if probability >= 72% + confirmed pattern), or "both"
7. DURATION BUCKET: Which bucket this trade belongs to (long_duration_growth / monetary_hedge / cyclical_reflation / medium_duration_defensive / short_duration_collateral)
8. REGIME ALIGNMENT: How well this trade aligns with the current 3-layer regime (high/medium/low)
9. INVALIDATION: What breaks the thesis
10. CATALYSTS: Key dates/events

Output STRICTLY as JSON array:
[{"ticker": "NVDA", "macro_score": 75, "theme_score": 88, "pam_score": 72,
  "thesis": "...", "direction": "long", "trade_type": "stock",
  "duration_bucket": "long_duration_growth", "regime_alignment": "high",
  "swing_plan": "Entry at $130, stop $124, target $145. 2-4 week swing.",
  "entry_price": 130.50, "stop_loss": 124.00, "target_price": 145.00,
  "invalidation": "...", "catalysts": ["Earnings May 28"]}]

RULES:
- Do NOT inflate scores — be honest about regime misalignment
- If data is insufficient, default to 50
- Use PAM engine data as primary for entry/stop/target
- If no PAM pattern, set direction to "neutral"
- trade_type must be one of: "stock", "options", "both"
- In a divergent world, REDUCE all scores by 5-10 points
- Return ONLY valid JSON, no markdown fences
"""


CRITIC_PROMPT = """You are the Risk Officer / Critic for AlphaEdge.

You receive the Analyst's JSON output. Your job: VALIDATE and CORRECT using the regime framework.

Check for:
1. SCORE INFLATION: Flag any score > 85 without STRONG evidence across ALL three layers
   (liquidity + inflation type + dollar). Reduce by 10-15.
2. REGIME COHERENCE: Does the trade align with the 3-layer regime?
   - Long growth in liquidity deceleration? Flag it.
   - Long commodities with bullish DXY from flight-to-safety? Flag it.
   - Short duration assets when liquidity is accelerating? Flag it.
3. DIVERGENT WORLD CHECK: If regime dispersion is high, flag any aggressive positions.
4. DXY NUANCE: Check that DXY impact is applied conditionally (not one-size-fits-all):
   - Flight-to-safety DXY ≠ US exceptionalism DXY ≠ fiscal dominance DXY
5. DURATION MISMATCH: Flag trades where the asset's duration bucket doesn't match the regime.
6. HALLUCINATED DATA: Cross-reference entry/stop/target with PAM engine output.
7. CONFLICTING SIGNALS: Flag high conviction longs in distribution (B) or flush up.
8. RISK/REWARD: Flag if R:R < 1.5:1.
9. MISSING INVALIDATION: Every trade must have clear invalidation.
10. CHINA NUANCE: If China in debt-deflation, flag broad commodity/EM longs unless easing expected.

Output: CORRECTED JSON array with added "critic_notes" per ticker.
Return ONLY valid JSON.
"""


FORMATTER_PROMPT = """You are the Formatter for AlphaEdge.

You receive the Critic-validated JSON. Ensure STRICT schema compliance.

Required output format:
{
  "macro_context": "3-5 sentence regime summary covering: liquidity regime, inflation type, dollar regime, financial conditions triangle, yield curve shape, and regime dispersion assessment",
  "regime_classification": {
    "liquidity": "accelerating|flat|decelerating",
    "inflation": "benign_disinflation|sweet_spot_reflation|overheating_reflation|stagflation|debt_deflation",
    "dollar": "bullish|neutral|bearish",
    "financial_conditions": "sweet_spot|reflation|stagflation|deflation_scare",
    "divergent_world": false
  },
  "analyses": [
    {
      "ticker": "NVDA", "raw_macro": 75, "raw_theme": 88, "raw_pam": 72,
      "direction": "long", "trade_type": "stock",
      "duration_bucket": "long_duration_growth", "regime_alignment": "high",
      "thesis": "...", "swing_plan": "...",
      "entry_price": 130.50, "stop_loss": 124.00, "target_price": 145.00,
      "invalidation": "...", "catalysts": ["..."], "critic_notes": "..."
    }
  ]
}

RULES:
- All number fields must be actual numbers (not strings)
- direction is one of: "long", "short", "neutral"
- trade_type is one of: "stock", "options", "both" (default "stock")
- duration_bucket is one of: "long_duration_growth", "monetary_hedge", "cyclical_reflation", "medium_duration_defensive", "short_duration_collateral"
- regime_alignment is one of: "high", "medium", "low"
- catalysts is always an array
- macro_context MUST reference the 3-layer regime and financial conditions triangle
- Include regime_classification object
- Remove any markdown formatting
- Return ONLY the JSON object
"""


# ═══════════════════════════════════════════════════════════
#  GEMINI CLIENT
# ═══════════════════════════════════════════════════════════

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def _call_llm(system: str, user: str, temperature: float = 0.3, max_tokens: int = 4000) -> str:
    """Single Gemini API call — server-side only."""
    client = _get_client()
    response = client.models.generate_content(
        model=settings.MODEL,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=temperature,
            max_output_tokens=max_tokens,
        ),
    )
    return response.text


def run_chain(
    retrieved_docs: str,
    pam_context: str,
    live_data: str,
    tickers: list[str],
) -> dict:
    """Execute the 4-step chain. Returns parsed JSON with trade ideas."""
    ticker_str = ", ".join(tickers)

    # Step A: Context Builder — full regime analysis
    context_input = (
        f"TICKERS: {ticker_str}\n\n"
        f"=== RETRIEVED KNOWLEDGE DOCUMENTS ===\n{retrieved_docs}\n\n"
        f"=== PAM ENGINE OUTPUT (DETERMINISTIC) ===\n{pam_context}\n\n"
        f"=== LIVE MARKET DATA ===\n{live_data}\n"
    )
    context_brief = _call_llm(CONTEXT_BUILDER_PROMPT, context_input, temperature=0.2, max_tokens=8000)

    # Step B: Analyst — quantitative scoring with regime framework
    analyst_input = (
        f"TICKERS: {ticker_str}\n\n"
        f"=== CONTEXT BRIEF (FULL REGIME ANALYSIS) ===\n{context_brief}\n\n"
        f"=== PAM ENGINE SCORES (GROUND TRUTH) ===\n{pam_context}\n"
    )
    analyst_output = _call_llm(ANALYST_PROMPT, analyst_input, temperature=0.3, max_tokens=8000)

    # Step C: Critic — regime-aware validation
    critic_input = (
        f"=== ANALYST OUTPUT ===\n{analyst_output}\n\n"
        f"=== PAM ENGINE REFERENCE (ground truth) ===\n{pam_context}\n\n"
        f"=== REGIME CONTEXT (from brief) ===\n{context_brief[:2000]}\n"
    )
    critic_output = _call_llm(CRITIC_PROMPT, critic_input, temperature=0.15, max_tokens=6000)

    # Step D: Formatter — strict schema with regime classification
    formatter_input = (
        f"=== CRITIC-VALIDATED OUTPUT ===\n{critic_output}\n\n"
        f"Format into strict schema. Full regime context:\n{context_brief[:1500]}"
    )
    final_output = _call_llm(FORMATTER_PROMPT, formatter_input, temperature=0.1, max_tokens=6000)

    parsed = _safe_parse(final_output)
    parsed["_chain_audit"] = {
        "context_brief_chars": len(context_brief),
        "analyst_output_chars": len(analyst_output),
        "critic_output_chars": len(critic_output),
    }
    return parsed


def _safe_parse(raw: str) -> dict:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start:end])
            except json.JSONDecodeError:
                pass
    return {"analyses": [], "macro_context": "Parse error", "_raw": raw}
