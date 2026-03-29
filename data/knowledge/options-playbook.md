# AlphaEdge Options Strategy Playbook — Construction & Management

Source: Professional Advanced Options Trading Course, Bang Pham Van & Adam Khoo (2024)
Integrated with: AlphaEdge macro regime framework

---

## MASTER RULE: When to Use Options vs Equity

- **Options ONLY when:** probability_score ≥ 72% AND options_liquid = true AND IV rank context is known
- **Prefer equity when:** probability < 72%, thin market, earnings within 10 days (unless earnings play), EU/crypto underlying
- **IV Rank (IVR):** IVR > 50 = HIGH IV → sell premium; IVR < 30 = LOW IV → buy premium; 30–50 = neutral, lean to buy
- **Critical:** Never sell naked. Never buy options with < 21 DTE unless specifically an earnings play.

---

## STRATEGY 1: BULL BANG (BB)

### What It Is
Aggressive pure bullish play. Buys directional upside with defined risk. No hedging — maximum bullish expression at LOW IV.

### When to Use
- IV Rank < 30 (LOW IV environment)
- Strong bullish conviction: macro score ≥ 70, PAM_VALID = true, pattern = UC1 or UR2
- Liquidity regime: Accelerating or Calm/Speculation phase
- Underlying: liquid US stock or ETF, options volume > 500 contracts/day

### Construction
```
BUY  1× ATM Call (delta 0.50–0.55)
DTE: 30–60 days
Strike: ATM or 1 strike OTM (nearest $5 increment for stocks >$100)
```

### Entry Rules
- Enter on PAM trigger confirmation (EXE bar close or next bar open)
- Ideal entry: price pulling back to 20/50 SMA in established uptrend
- Avoid entering Monday open or Friday close
- Position size: risk ≤ 2% of portfolio (cost of premium = max loss)

### Exit Rules
- **Profit target:** Close at 50% of max profit (e.g., bought for $3.00 → close at $4.50)
- **Stop loss:** Close at 2× premium paid (e.g., bought for $3.00 → close if worth $1.00)
- **Time stop:** Exit with 7–10 DTE remaining regardless of P&L (avoids theta decay acceleration)
- **Hard rule:** Never hold through earnings unless intended as earnings play

### Ideal Macro Context
- Liquidity phase: Calm or Speculation (best), Rebound (acceptable)
- Inflation: Benign disinflation or sweet-spot reflation
- Avoid: Turbulence phase, stagflation, DXY spike from flight-to-safety

---

## STRATEGY 2: BULL BANG COLLAR (BBC)

### What It Is
Bull Bang + short OTM call for premium offset. Reduces net debit, caps upside. Best for moderate bullish conviction where premium reduction matters.

### When to Use
- IV Rank < 40 (LOW to mild IV)
- Moderate bullish conviction: macro score 55–70, probability 65–75%
- Underlying in confirmed uptrend but near resistance level
- Reduces cost of Bull Bang when premium is expensive

### Construction
```
BUY  1× ATM Call (delta 0.50–0.55)   ← long leg
SELL 1× OTM Call (delta 0.25–0.30)   ← short collar
Same expiration. DTE: 30–60 days.
Net debit = long premium − short premium received
```

### Entry Rules
- Short strike should be above nearest resistance / prior swing high
- Net debit should be < 60% of the width of the spread
- Example: $5 wide spread (buy 100C / sell 105C) → max pay $3.00 debit

### Exit Rules
- **Profit target:** 50–75% of max profit width (e.g., $5 spread → target $2.50–$3.75 credit)
- **Stop loss:** Close full spread if net debit doubles (paid $3 → close at $1)
- **Time stop:** Exit with 10 DTE remaining
- **Roll:** If short call threatened (price near short strike) → buy back short call or roll up and out

### Ideal Macro Context
- Same as Bull Bang but less aggressive
- Preferred in "Flat" liquidity regime where upside is limited
- Good for sideways-to-up markets with defined resistance levels

---

## STRATEGY 3: DIAGONAL SPREAD (DS)

### What It Is
"Lease" strategy. Own long-dated deep ITM call (LEAPS-like), sell short-dated OTM call against it repeatedly. Generates income. Similar to covered call but capital-efficient.

### When to Use
- ANY IV environment (works best when front-month IV > back-month IV = positive skew)
- Moderate to high bullish conviction on long-term direction
- Want income generation + upside participation
- Ideal for core watchlist positions (Tier 1) held over 3–6 months
- Underlying: liquid stock, options volume robust at both DTEs

### Construction
```
BUY  1× Deep ITM Call (delta 0.70–0.80), back month
     DTE: 60–90 days (or LEAPS at 180+ days for long hold)
     Strike: typically 10–15% below current price (ITM)

SELL 1× ATM or OTM Call (delta 0.25–0.35), front month
     DTE: 14–30 days (weekly if available and liquid)
     Strike: at or above current price (ATM/OTM)
```

### Entry Rules
- Long leg delta should be ≥ 0.70 to behave like stock ownership
- Short leg: target delta 0.25–0.35 (OTM, above current price)
- Net debit = long call cost − short call premium received
- Effective entry cost often 30–50% lower than owning stock

### Exit Rules — Short Leg (repeat cycle)
- **Profit target:** Buy back short call at 50% of credit received → re-sell next week/month
- **Stop (short leg):** If underlying rips through short strike → buy back and roll short call up/out same expiry or to next month
- **Time stop:** Buy back short call at 5 DTE → avoid pin risk

### Exit Rules — Full Position
- **Full close:** If underlying breaks below long leg's strike − 5% → close both legs (thesis broken)
- **Roll long leg:** When long leg has < 30 DTE → roll to next expiry (pay debit to extend)
- **Target overall:** Harvest 3–5 rounds of short call income to pay off long leg cost

### Ideal Macro Context
- Liquidity phase: Any, but best in Calm or Speculation
- Works well in range-bound markets (short call income keeps coming)
- Avoid: Gap-up stock with very high IV spike (short call risks assignment)

---

## STRATEGY 4: DS HAMMER (Diagonal Spread Hammer)

### What It Is
Bearish/defensive diagonal. Long-dated deep ITM PUT + short near-term OTM put. Mirror of DS for downside protection or bearish income. Used for hedging long positions or speculative bearish plays.

### When to Use
- IV Rank < 40 (LOW IV, buying puts is cheaper)
- Bearish conviction: macro score < 40, liquidity decelerating, DC1 or DR2 PAM pattern
- Hedging core longs during regime uncertainty (Turbulence phase)
- Underlying in downtrend below 50 SMA

### Construction
```
BUY  1× Deep ITM Put (delta −0.70 to −0.80), back month
     DTE: 60–90 days
     Strike: 10–15% above current price (ITM)

SELL 1× ATM or OTM Put (delta −0.25 to −0.30), front month
     DTE: 14–30 days
     Strike: at or slightly below current price
```

### Entry Rules
- Use at PAM DC1 EXE bar confirmation (bearish continuation)
- For pure hedge: enter when macro_score drops below 45 or liquidity regime turns Decelerating
- Size hedge to offset 30–50% of long equity exposure delta

### Exit Rules
- **Same mechanic as DS:** Roll short put monthly, close full position if underlying reclaims key resistance
- **Hedge close:** If macro re-confirms bullish → close DS Hammer immediately (don't hold full term)
- **Stop (short leg):** Buy back short put if underlying drops through short strike

### Ideal Macro Context
- Liquidity: Decelerating or Turbulence phase
- Inflation: Stagflation or debt-deflation scare
- DXY: Strong from flight-to-safety (bearish for risk)
- China: Debt-deflation risk present

---

## STRATEGY 5: CBS — CROUCHING BULL SPREAD

### What It Is
Defined-risk bull strategy combining a bull call spread with a short put (CSP). Higher income than plain bull call spread. Net credit or very small debit. Profitable if stock stays flat or rises.

### When to Use
- HIGH IV (IVR > 50) → sell premium
- Moderate bullish conviction: macro score 55–65, PAM = UC1 (continuation)
- Want to profit from TIME DECAY + modest upside
- Underlying near support, not expected to fall sharply

### Construction
```
BUY  1× ATM Call (delta 0.50)
SELL 1× OTM Call (delta 0.25)            ← cap upside
SELL 1× OTM Put (delta −0.20 to −0.25)  ← collect extra premium

All same expiration. DTE: 30–45 days.
Net: usually small credit or near-zero debit.
```

### Entry Rules
- Short put strike should be at or below key support level
- Call spread width: $5–$10 depending on stock price
- Short put should not be below recent swing low (invalidation level)
- Ideal entry: 2–3 weeks before expiry cycle, not during earnings period

### Exit Rules
- **Target:** 50% of max credit received (or 50–75% of theoretical max profit)
- **Stop:** If short put is threatened (price near short put strike) → close full position
- **Time stop:** Close at 21 DTE → avoid gamma risk on short legs
- **Never let short put go deep ITM** — close or roll immediately if tested

### Ideal Macro Context
- Liquidity: Calm or Flat (stock-picking regime)
- Inflation: Benign or sweet-spot
- Works poorly in turbulence (short put risk)
- Only on fundamentally strong stocks (you'd be OK owning them at short put strike)

---

## STRATEGY 6: BACK RATIO SPREAD

### What It Is
Asymmetric volatility play. Buy fewer contracts at one strike, sell more at a different strike. Creates a position that profits from a BIG move in the favorable direction AND from a volatility explosion. Often structured for near-zero or small credit.

### When to Use
- LOW IV environment (IVR < 30) → buying extra options is cheap
- High conviction for explosive directional move
- Earnings catalyst, macro breakout, technical breakout from long consolidation
- Accepts small loss in middle zone, targets big win on large move

### Bullish Back Ratio (1:2 or 1:3 Call Back Ratio)
```
SELL 1× ITM or ATM Call (delta 0.55–0.65)   ← finance the position
BUY  2× or 3× OTM Calls (delta 0.25–0.35)   ← explosive upside

DTE: 30–60 days.
Target: zero-cost or slight credit to enter.
```

### Bearish Back Ratio (1:2 Put Back Ratio)
```
SELL 1× ITM or ATM Put (delta −0.55 to −0.65)
BUY  2× or 3× OTM Puts (delta −0.25 to −0.30)

DTE: 30–60 days.
```

### Risk Profile
- **Max loss zone:** Price finishes between the two strikes at expiry (limited, bounded)
- **Max gain:** Unlimited (bullish) or bounded by zero (bearish) if stock moves explosively
- **Breakeven:** Two breakeven points — below entry range AND above the long strikes
- **Ideal:** Stock explodes through OTM strikes = back ratios print

### Entry Rules
- Enter when IV is LOW (options cheap → more longs = good)
- Use on tickers with catalyst: earnings soon, macro announcement, technical compression
- Size: total risk (max loss zone) ≤ 1% of portfolio
- Never use on low-volume underlyings (wide bid/ask destroys edge)

### Exit Rules
- **Target:** Close when long leg doubles (2× the OTM call price paid)
- **Stop:** Close if short leg goes deep ITM without corresponding move in long direction → thesis failed
- **Time stop:** Exit before 14 DTE if no move materialized → don't hold through expiry

### Ideal Macro Context
- Pre-breakout compression: stock in tight range, GLI about to inflect
- Liquidity: Rebound to Calm transition (inflection point)
- Best timing: before a major catalyst in a low-IV environment

---

## QUICK REFERENCE TABLE

| Strategy | Conviction | IV Env | DTE | Risk Type | Best Phase |
|---|---|---|---|---|---|
| Bull Bang | HIGH bull | LOW (<30) | 30–60d | Premium paid | Calm/Speculation |
| BBC | MOD bull | LOW–MID (<40) | 30–60d | Net debit | Calm/Flat |
| Diagonal DS | HIGH long bull | ANY | 60–180d + weekly | Net debit (recouped) | Calm/Speculation |
| DS Hammer | BEARISH/hedge | LOW (<40) | 60–90d + weekly | Net debit | Turbulence/Decel |
| CBS | MOD bull | HIGH (>50) | 30–45d | Small debit/credit | Calm/Flat |
| Back Ratio | EXPLOSIVE move | LOW (<30) | 30–60d | Bounded middle zone | Rebound inflection |

---

## OPTIONS GATING CHECKLIST (run before every options trade)

1. ✅ probability_score ≥ 72%
2. ✅ options_liquid = true (volume > 500 contracts/day on target strikes)
3. ✅ No earnings within 10 days (unless earnings play)
4. ✅ IV Rank context known (IVR determines sell vs buy premium)
5. ✅ PAM_VALID = true (trigger level, stop, target all defined)
6. ✅ Macro score ≥ 55 (if macro < 45, options are WATCHLIST ONLY)
7. ✅ Position risk ≤ 2% of portfolio (max loss on the structure)
8. ✅ Not in divergent world with regime_alignment = "low" for this ticker

---

## EXIT DISCIPLINE — UNIVERSAL RULES

- **Never hold options through earnings unintentionally** — close 2 days before if not an earnings play
- **50% profit rule:** Take profit at 50% of max gain — let time work for you, don't get greedy
- **2× stop rule:** Never let a long option position lose more than 2× the premium paid
- **7–10 DTE time stop:** All long options expire or close at 7–10 DTE (theta kills returns)
- **21 DTE short stop:** Close all short premium positions at 21 DTE (gamma risk rises)
- **Winning trade protection:** Once a position reaches +1R, move stop to breakeven (never let winner become loser)
