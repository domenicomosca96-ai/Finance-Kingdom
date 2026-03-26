"""
Chain-of-Thought Prompting Pipeline — Gemini 3 API.

4-step explicit chain:
  A) Context Builder — assembles RAG docs + PAM engine output
  B) Analyst — generates thesis, macro/theme scores
  C) Critic / Risk Officer — validates, flags hallucinations, caps inflated scores
  D) Formatter — structures into strict JSON

All Gemini calls happen server-side only.
"""

import json
from google import genai
from google.genai import types
from core.config import settings

CONTEXT_BUILDER_PROMPT = """You are the Context Builder for AlphaEdge, an AI swing trading system.

Your job: ORGANIZE the raw inputs into a clean analytical brief for the Analyst.

You receive:
1. RETRIEVED DOCUMENTS from the knowledge base (macro, trading methods, sector reports)
2. PRE-COMPUTED PAM ENGINE DATA (deterministic — treat as ground truth)
3. LIVE MARKET DATA (prices, fundamentals)

Your output must be a structured context brief with these sections:

## MACRO REGIME
Synthesize the macro/liquidity documents. Identify:
- Current Howell liquidity phase (Rebound/Calm/Speculation/Turbulence)
- Fed Net Liquidity direction
- DXY, MOVE Index, yield curve positioning
- Net assessment for risk assets

## SECTOR/THEME CONTEXT
For each ticker, extract relevant sector intelligence from the documents:
- AI value chain position, capex cycle, earnings catalysts
- Any specific fundamental insights

## PAM ENGINE SUMMARY
Restate the pre-computed PAM data clearly. DO NOT reinterpret it.
The PAM engine has already computed: flow state, pattern, momentum, micro score.
Simply confirm and contextualize.

## KEY RISKS
List the top 3-5 risks visible from the documents.

Output as clean markdown. No JSON. No scoring — that's the Analyst's job.
"""


ANALYST_PROMPT = """You are the Analyst for AlphaEdge.

You receive a structured context brief from the Context Builder.
Your job: produce a QUANTITATIVE assessment for each ticker.

For each ticker, output:

1. MACRO SCORE (0-100): How aligned is the liquidity regime with this trade?
   - 80-100: Strong tailwind (expanding GLI, favorable phase, weak DXY)
   - 50-79: Neutral/mixed
   - 0-49: Headwind (contracting liquidity, strong DXY, repo stress)

2. THEME SCORE (0-100): How strong are sector catalysts?
   - 80-100: Major catalysts, sector leadership
   - 50-79: Moderate support
   - 0-49: Headwinds or commoditized

3. PAM SCORE: Use the pre-computed micro_score from the PAM engine AS-IS.
   Do NOT override it.

4. THESIS: 2-3 sentence investment thesis.

5. SWING PLAN: If the PAM engine detected a pattern, specify:
   - Entry zone, Stop loss, Target, Timeframe

6. INVALIDATION: What breaks this thesis?

7. CATALYSTS: Key dates/events.

Output STRICTLY as JSON array:
[{"ticker": "NVDA", "macro_score": 75, "theme_score": 88, "pam_score": 72,
  "thesis": "...", "direction": "long", "swing_plan": "...",
  "entry_price": 130.50, "stop_loss": 124.00, "target_price": 145.00,
  "invalidation": "...", "catalysts": ["Earnings May 28"]}]

RULES:
- Do NOT inflate scores
- If data is insufficient, default to 50
- Use PAM engine data as primary for entry/stop/target
- If no PAM pattern, set direction to "neutral"
- Return ONLY valid JSON, no markdown fences
"""


CRITIC_PROMPT = """You are the Risk Officer / Critic for AlphaEdge.

You receive the Analyst's JSON output. Your job: VALIDATE and CORRECT.

Check for:
1. SCORE INFLATION: Flag any score > 85 without strong evidence. Reduce by 10-15.
2. HALLUCINATED DATA: Cross-reference entry/stop/target with PAM engine output.
3. CONFLICTING SIGNALS: Flag high conviction longs in distribution (B) or flush up.
4. RISK/REWARD: Flag if R:R < 1.5:1.
5. MISSING INVALIDATION: Every trade must have clear invalidation.

Output: CORRECTED JSON array with added "critic_notes" per ticker.
Return ONLY valid JSON.
"""


FORMATTER_PROMPT = """You are the Formatter for AlphaEdge.

You receive the Critic-validated JSON. Ensure STRICT schema compliance.

Required output format:
{
  "macro_context": "2-3 sentence regime summary",
  "analyses": [
    {
      "ticker": "NVDA", "raw_macro": 75, "raw_theme": 88, "raw_pam": 72,
      "direction": "long", "thesis": "...", "swing_plan": "...",
      "entry_price": 130.50, "stop_loss": 124.00, "target_price": 145.00,
      "invalidation": "...", "catalysts": ["..."], "critic_notes": "..."
    }
  ]
}

RULES:
- All number fields must be actual numbers (not strings)
- direction is one of: "long", "short", "neutral"
- catalysts is always an array
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

    # Step A: Context Builder
    context_input = (
        f"TICKERS: {ticker_str}\n\n"
        f"=== RETRIEVED KNOWLEDGE DOCUMENTS ===\n{retrieved_docs}\n\n"
        f"=== PAM ENGINE OUTPUT (DETERMINISTIC) ===\n{pam_context}\n\n"
        f"=== LIVE MARKET DATA ===\n{live_data}\n"
    )
    context_brief = _call_llm(CONTEXT_BUILDER_PROMPT, context_input, temperature=0.2, max_tokens=3000)

    # Step B: Analyst
    analyst_input = (
        f"TICKERS: {ticker_str}\n\n"
        f"=== CONTEXT BRIEF ===\n{context_brief}\n\n"
        f"=== PAM ENGINE SCORES ===\n{pam_context}\n"
    )
    analyst_output = _call_llm(ANALYST_PROMPT, analyst_input, temperature=0.3, max_tokens=4000)

    # Step C: Critic
    critic_input = (
        f"=== ANALYST OUTPUT ===\n{analyst_output}\n\n"
        f"=== PAM ENGINE REFERENCE (ground truth) ===\n{pam_context}\n"
    )
    critic_output = _call_llm(CRITIC_PROMPT, critic_input, temperature=0.15, max_tokens=4000)

    # Step D: Formatter
    formatter_input = (
        f"=== CRITIC-VALIDATED OUTPUT ===\n{critic_output}\n\n"
        f"Format into strict schema. Macro context from the brief:\n{context_brief[:500]}"
    )
    final_output = _call_llm(FORMATTER_PROMPT, formatter_input, temperature=0.1, max_tokens=4000)

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
