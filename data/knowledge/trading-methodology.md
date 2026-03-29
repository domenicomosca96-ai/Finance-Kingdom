# Trading Methodology — Adam Khoo + Bang Van Principles

## Core Swing Trading Rules (Adam Khoo)

### Trend Identification
- Uptrend: Series of higher highs (HH) and higher lows (HL) on daily chart
- Downtrend: Series of lower highs (LH) and lower lows (LL)
- Confirmation: Price above 50 EMA AND 50 EMA above 150 EMA = bullish structure
- Never trade against the primary trend on daily timeframe

### Entry Timing
- Buy on pullback to dynamic support (20/50 EMA) in confirmed uptrend
- Wait for reversal candle (hammer, engulfing, morning star) at support
- Volume confirmation: declining volume on pullback, rising on reversal
- Ideal entry: test of rising 50 EMA with bullish candle close

### Exit & Risk Management
- Stop loss: below swing low or below 50 EMA (whichever is tighter)
- Never risk more than 1-2% of portfolio per trade
- Target: minimum 2:1 reward/risk, ideally 3:1
- Trail stop using 20 EMA once trade moves 1R in profit
- Scale out: 50% at 2R, trail remaining to breakeven

### Position Management
- Add to winners (scale in) at next pullback only if trend intact
- Never average down on losers
- Maximum 5 concurrent swing positions
- Cut losers fast, let winners run — asymmetry is everything

## Bang Van — Price Action Mastery

### Key Principles
- Price action tells the story before indicators confirm
- Volume precedes price movement
- Institutional footprints visible in order flow and candle structure
- Multi-timeframe alignment: weekly → daily → 4H for entry precision

### High-Probability Setups
1. Breakout & Retest: price breaks key level, returns to test it as new support/resistance
2. Pullback to Value: trend intact, pullback to VWAP or key moving average
3. Range Breakout: consolidation followed by expansion with volume
4. Momentum Ignition: large-body candle with above-average volume after compression

## Risk Management Framework

### Per-Trade Rules
- Risk per trade: 1% of account (max 2% for high-conviction)
- Position size = (Account × Risk%) / (Entry - Stop Loss)
- Never let a winning trade turn into a loser beyond 1R
- If stopped out twice on same setup, skip and re-evaluate

### Portfolio-Level Rules
- Maximum portfolio heat: 6% (sum of all open position risks)
- Correlated positions count as single risk unit
- Reduce exposure when win rate drops below 40% over last 20 trades
- Increase exposure when in "zone" (win rate >60% over last 20)

---

## Hard Risk Constraints (System-Enforced)

These rules are enforced by the AlphaEdge system. The AI assistant MUST follow them.

### Streak Management
- **5-loss consecutive stop**: After 5 consecutive losing trades, PAUSE all new entries for 48 hours. Re-evaluate the macro regime before resuming. If the regime hasn't changed, reduce position sizing to 0.5× for the next 5 trades.
- If stopped out twice on the SAME setup and SAME ticker, skip that setup entirely until the next regime review.

### Kelly Criterion & Position Sizing
- **Fractional Kelly (25%)**: Full Kelly = mathematically optimal but equity curve is extremely volatile. 25% fractional Kelly = much smoother equity curve with ~75% of the long-run return. NEVER exceed 25% Kelly.
- Kelly sizing is always capped by: MAX_RISK_PER_TRADE = 2%, MAX_POSITION = 5%, MAX_PORTFOLIO_HEAT = 6%.
- The smallest of Kelly-adjusted size and the hard caps applies.

### PAM Scoring Bonus (NOT a Gate)
- Trades with PAM_VALID = true (confirmed pattern + defined trigger/stop/target) receive a **+10 composite scoring bonus**
- Trades WITHOUT PAM confirmation are **NOT blocked** — they simply receive no PAM bonus and are naturally deprioritized in the ranking
- PAM confirmation increases conviction and allows tighter stops, which improves R:R and Kelly sizing

### Behavioral Constraints (AI Must Follow)
1. **Macro gate**: If macro_score < 45 → output is **WATCHLIST ONLY** regardless of PAM or theme score. No trade recommendation.
2. **Divergent world sizing**: If divergent_world = true → reduce ALL suggested position sizes by 30%. Flag in output.
3. **Options liquidity**: NEVER recommend options on underlyings where options_liquid = false. Convert to equity-only.
4. **Invalidation required**: ALWAYS state the invalidation level (price that breaks the thesis) BEFORE the entry recommendation.
5. **Liquidity alignment**: NEVER recommend a trade that goes against the primary liquidity trend direction (Howell phase). Example: do not recommend aggressive longs in Turbulence phase; do not recommend shorts in Rebound/Calm.
6. **Correlation awareness**: If recommending multiple trades, flag correlated positions (same sector, same factor exposure) and count them as a single risk unit for portfolio heat calculation.

---
NOTE: Enhance this document by uploading your specific Adam Khoo and Bang Van PDF materials.
The system will merge them into this collection automatically.
