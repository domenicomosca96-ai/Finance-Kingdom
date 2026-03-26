# AlphaEdge Macro Regime Framework
## Master Decision Engine — Signal Weighting & Regime Classification

### SIGNAL WEIGHTING HIERARCHY

| Layer | Weight | Role |
|-------|--------|------|
| Global Liquidity (Howell GLI) | 35% | Regime engine. Decides long aggressive, long selective, or defense. Also decides country over/underweight based on liquidity + inflation regime + intermarket confirmation. |
| Sector Trends / Leadership | 25% | Decides where to concentrate risk. |
| PAM / Price Action Execution | 15% | Decides WHEN to enter, WHERE to invalidate, HOW to structure the trade. |
| Intermarket Confirmation | 10% | DXY, MOVE, yield curve, term premium, breadth, credit spreads. |
| Fundamentals | 10% | Quality filter and narrative coherence. |
| Elliott Wave | 5% | Only maturity/asymmetry map, NEVER a trigger. |

---

### INSIGHT 1: LIQUIDITY > INFLATION > DOLLAR (Layer Hierarchy)

The dominant variable is NOT "CPI high or low" per se, but WHETHER LIQUIDITY IS ACCELERATING OR DECELERATING, and whether the system is in MONETARY DOMINANCE or FISCAL DOMINANCE.

In fiscal dominance:
- Bonds and equity no longer behave like classic 60/40
- Gold, Bitcoin, and real assets assume a much stronger role
- Equity valuations are better around 2-3% inflation, but ONLY in low monetary instability regimes

**Rule**: Liquidity = Layer 1, Inflation = Layer 2, DXY = Layer 3. Never reverse this.

- **Liquidity** decides if you are risk-on or risk-off
- **Inflation** decides WHAT TYPE of risk-on/risk-off you are living
- **DXY** decides how favorable or hostile the global regime is for international assets and liquidity-sensitive assets

---

### INSIGHT 2: REGIONAL DIVERGENCE > SIMPLE AVERAGE

The weighted average (USA 50%, Eurozone 30%, China 20%) is useful as a base but HIDES DIVERGENCE, which for Howell is often the core problem.

Examples:
- USA in Calm/Speculation + China in Turbulence/deflation ≠ simple "Calm" average. It means: strong dollar, export pressure, Asian debt-deflation, global squeeze risk.
- USA not too hot + China expanding liquidity = one of the BEST contexts for commodities and global beta.

**New variable: Regime Dispersion**
- regimeDispersion = maxPhaseScore - minPhaseScore
- isDivergentWorld = true if dispersion > threshold

In a DIVERGENT world:
- Less size on global cyclical assets
- More emphasis on gold/cash
- Less trust in the simple weighted average

---

### INSIGHT 3: INFLATION TYPE MATTERS MORE THAN LEVEL

Not "how high is inflation?" but "WHAT TYPE of inflation?"

Three inflation archetypes:
1. **Demand-pull reflation** (liquidity-driven): Equities OK, commodities strong, bonds weak. Tradeable.
2. **Supply-shock / tariff inflation** (cost-push with slowing growth): Stagflation territory. Large-cap pricing power + gold + BTC outperform bonds and broad market.
3. **Debt-deflation** (private debt crisis): Deflationary. Bonds rally, risk assets suffer.

**Critical distinction**:
- Private debt crisis = DEFLATIONARY
- Public debt crisis = INFLATIONARY
- Tariffs + supply shock = slow growth + stubborn inflation → Treasury QE may support assets but increases need for monetary hedges

---

### INSIGHT 4: THREE-LAYER REGIME CLASSIFICATION

#### Layer 1: Liquidity Regime
- **Accelerating**: Risk-on. Favor long duration, growth, BTC, commodities.
- **Flat**: Selective. Stock-picking matters more. Favor quality.
- **Decelerating**: Risk-off. Favor cash, short duration, defensive.

#### Layer 2: Inflation Regime
- **Benign disinflation**: Best for bonds + growth equities. Goldilocks.
- **Sweet-spot reflation** (2-3%): Best for broad equities. Ideal.
- **Overheating reflation**: Commodities lead. Trim long-duration growth.
- **Stagflation**: Gold, BTC, pricing-power stocks only. Avoid bonds + cyclicals.
- **Debt-deflation**: Maximum defense. Duration + cash.

#### Layer 3: Dollar Regime
- **Bullish DXY**: See DXY nuance below (Insight 5).
- **Neutral DXY**: Minimal directional bias.
- **Bearish DXY**: Boost to commodities, BTC, ex-US, EM.

---

### INSIGHT 5: DXY IS NOT ONE-SIZE-FITS-ALL

Bullish DXY is NOT always bearish for everything. Depends on WHY the dollar is strong:

1. **DXY strong from flight-to-safety / stress**: Bearish for risk assets globally, EM, BTC, industrial commodities.
2. **DXY strong from US exceptionalism / relative growth**: Mega-cap USA can hold fine. EM and rest-of-world suffer more.
3. **DXY strong but monetary inflation / fiscal dominance accelerating**: Dollar beats other fiat but LOSES ground vs gold/BTC/real assets.

**Conditional logic**:
- DXY Bullish + China weak + inflation low/deflationary → FULL wrecking ball
- DXY Bullish + US liquidity rising + inflation sticky → Penalize EM/industrial commodities, but LESS on gold and mega-cap
- DXY Bearish + China easing → STRONG boost to commodities, BTC, ex-US

---

### INSIGHT 6: CHINA IS SPECIAL — NOT JUST ANOTHER REGION

Chinese low inflation ≠ "bond bullish" in the simple sense. It can mean:
- Internal weakness
- Need for easing
- FX pressure
- Future push on commodities and global liquidity IF PBoC opens the taps

**China-specific logic**:
- If inflation_CN < 1% AND phase_CN in [Turbulence, Rebound] → debt-deflation risk HIGH
- If debt-deflation risk high BUT policy easing expected → POSITIVE CONVEXITY for future commodities/BTC/gold (but not immediate broad risk-on)

This prevents the classic error: reading China in deflation as simple reason to buy global bonds.

---

### INSIGHT 7: BOND MARKET SIGNALS AS REGIME CONFIRMATION

The bond market is THE most important price. US liquidity anticipates the yield curve by ~9 months.

**Yield Curve Shape Matrix**:
| Shape | Meaning | Action |
|-------|---------|--------|
| Bull steepening | Early/mid risk-on, healthy | Go long growth + cyclicals |
| Bear steepening | Late cycle / reflation / inflation + bond supply pressure | Trim duration, favor commodities |
| Bull flattening | Risk-off / strong slowdown | Add duration, reduce beta |
| Bear flattening | Classic tightening / liquidity withdrawal | Defensive positioning |

Must monitor: steepening, term premia, duration absorption, MOVE index, mid-duration rally.

---

### INSIGHT 8: FINANCIAL CONDITIONS TRIANGLE

**"Financial conditions are bond yields, dollar, commodities."**

| Yields | DXY | Commodities | Regime | Action |
|--------|-----|-------------|--------|--------|
| Down | Down | Stable/moderate | SWEET SPOT risk-on | Full risk-on, growth + BTC |
| Up | Down | Up | Reflation / late cycle | Commodities lead, trim growth duration |
| Up | Up | Up | Stagflation / conditions worsening | Gold + BTC + pricing power only |
| Down | Up | Down | Deflation scare / risk-off | Duration up, cash up, reduce everything |

---

### INSIGHT 9: DURATION BUCKET FRAMEWORK

Instead of thinking by asset class, think in DURATION / LIQUIDITY SENSITIVITY buckets:

| Bucket | Assets | When to favor |
|--------|--------|---------------|
| Short duration / collateral | Cash, T-bills | Liquidity decelerating, stress |
| Medium duration defensives | Quality bonds, defensives | Deflation scare, bull flattening |
| Long duration growth | Tech, growth equities | Liquidity accelerating + fin conditions easing |
| Monetary hedges | Gold, Bitcoin | Fiscal dominance, monetary inflation, all stress regimes |
| Cyclical reflation | Commodities, energy, materials | China easing, bearish DXY, bear steepening |

**Duration rules**:
- Liquidity accelerating + financial conditions easing → FAVOR long-duration growth + BTC + gold
- Liquidity decelerating + inflation rising → REDUCE long-duration growth, KEEP gold/commodities, CUT long bonds
- True deflation scare → FAVOR medium-long duration bonds + cash, REDUCE BTC/commodities

---

### STRATEGIC vs TACTICAL DISTINCTION

**Strategic weights** (determine the baseline bias):
- Global Liquidity: 35-40%
- Sector trends / leadership: 20-25%
- PAM: 20-25%
- Inflation / financial conditions: 10-15%
- Elliott / Fundamentals: 5-10%

**Tactical adjusters** (determine how aggressive within the regime):
- DXY direction and WHY
- Yield curve shape
- TGA / RRP / QT / QE / Treasury issuance
- Term premia
- MOVE / credit stress
- Price action extension (overbought/oversold)

The strategic weights set the DIRECTION. The tactical adjusters set the SIZE and TIMING.
