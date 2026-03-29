# AlphaEdge Ticker Registry — Per-Ticker Regime & Strategy Mapping

Source: AlphaEdge internal — PROJECT_MEMORY_MASTER
Purpose: Pre-built LLM lookup table. Use this to avoid reasoning from scratch.
Format: ticker | duration_bucket | best_liquidity_phases | dxy_sensitivity | pam_bias | preferred_options | avoid_conditions

---

## DURATION BUCKET DEFINITIONS

- **long_duration_growth** — High-beta to liquidity acceleration, hurt by rising rates & dollar; e.g., tech/growth
- **monetary_hedge** — Outperforms in fiscal dominance & monetary inflation; e.g., gold, BTC
- **cyclical_reflation** — Outperforms when China eases, DXY weakens, commodities rally
- **medium_duration_defensive** — Quality/dividend names; hold in Flat/Turbulence phases
- **short_duration_collateral** — Cash-like; T-bills, ultra-short bonds; max defense
- **financial_leverage** — Banks, exchanges, financials; benefit from steepening yield curve + growth
- **china_special** — Chinese ADRs/names subject to China debt-deflation/easing logic (see Insight 6)
- **hybrid_growth_defense** — Platform businesses with pricing power + growth; mixed sensitivity

---

## US LARGE-CAP TECHNOLOGY & AI

### NVDA — NVIDIA Corporation
- **Duration bucket:** long_duration_growth
- **Best liquidity phases:** Calm, Speculation
- **DXY sensitivity:** Moderate (global revenue, but USD-denominated; benefits from weak DXY globally)
- **PAM bias:** UC1 (trend continuation dominant), UR2 on major sell-offs with capitulation flush
- **Preferred options:** Diagonal DS (core position), Bull Bang (tactical breakout), Back Ratio (pre-earnings low IV)
- **Avoid conditions:** Turbulence phase, DXY spike from flight-to-safety, hyperscaler capex freeze signal, Liquidity decelerating hard

### AAPL — Apple
- **Duration bucket:** long_duration_growth (but defensive moat)
- **Best liquidity phases:** Calm, Speculation, Rebound
- **DXY sensitivity:** Low-moderate (pricing power shields partially; large buybacks support)
- **PAM bias:** UC1 (very reliable trend-follower), DR2 rarely worthwhile (strong buyback floor)
- **Preferred options:** CBS (sell premium in High IV), Diagonal DS (long-term hold), BBC (moderate conviction)
- **Avoid conditions:** Strong bear market, services miss + China sales collapse simultaneously

### MSFT — Microsoft
- **Duration bucket:** long_duration_growth (cloud moat = defensive growth)
- **Best liquidity phases:** Calm, Speculation, Flat (holds well)
- **DXY sensitivity:** Low (USD revenue dominant, limited EM exposure)
- **PAM bias:** UC1 (extremely reliable in established uptrend)
- **Preferred options:** CBS (Flat/Calm phases), Diagonal DS (core), Bull Bang (breakout)
- **Avoid conditions:** Turbulence, cloud spending freeze, rates spike hard (duration pressure)

### GOOGL — Alphabet
- **Duration bucket:** long_duration_growth
- **Best liquidity phases:** Calm, Speculation
- **DXY sensitivity:** Low-moderate (global ads revenue but USD-denominated)
- **PAM bias:** UC1, UR2 on major corrections (deep value floor from buybacks + cash)
- **Preferred options:** Bull Bang (breakout), BBC (moderate bull), CBS (flat/calm)
- **Avoid conditions:** Regulatory antitrust action (idiosyncratic), Turbulence phase

### META — Meta Platforms
- **Duration bucket:** long_duration_growth
- **Best liquidity phases:** Speculation, Calm
- **DXY sensitivity:** Moderate (global ad revenue; EM users matter for growth)
- **PAM bias:** UC1 (momentum name), aggressive UR2 on oversold sentiment washes
- **Preferred options:** Bull Bang, Back Ratio (pre-earnings conviction play)
- **Avoid conditions:** Turbulence, regulatory/privacy catalysts, DXY strong from US stress

### AMZN — Amazon
- **Duration bucket:** long_duration_growth
- **Best liquidity phases:** Calm, Speculation
- **DXY sensitivity:** Low-moderate (AWS global, but USD-priced)
- **PAM bias:** UC1 dominant
- **Preferred options:** Bull Bang, Diagonal DS (core AWS compounder position)
- **Avoid conditions:** Consumer recession signal + cloud spending slowdown simultaneously

### TSLA — Tesla
- **Duration bucket:** long_duration_growth (HIGHEST beta to sentiment)
- **Best liquidity phases:** Speculation (top performer), Rebound early
- **DXY sensitivity:** Moderate (global EV sales; China exposure)
- **PAM bias:** UR2 and UC1 both active (extreme flush/wave cycles), aggressive reversals
- **Preferred options:** Back Ratio (volatility explosion plays), Bull Bang (breakout only)
- **Avoid conditions:** Turbulence, brand damage events, macro + China slowdown combo; do NOT use Diagonal DS (too volatile, short call risk)

### AVGO — Broadcom
- **Duration bucket:** long_duration_growth (AI semiconductor + software)
- **Best liquidity phases:** Calm, Speculation
- **DXY sensitivity:** Moderate
- **PAM bias:** UC1
- **Preferred options:** Bull Bang, CBS (high IV after earnings)
- **Avoid conditions:** Semiconductor cycle downturn, Turbulence

### ADBE — Adobe
- **Duration bucket:** long_duration_growth (high-multiple SaaS)
- **Best liquidity phases:** Calm, Speculation
- **DXY sensitivity:** Low-moderate
- **PAM bias:** UC1
- **Preferred options:** Bull Bang, CBS
- **Avoid conditions:** Turbulence, AI disruption narrative spike, rates rising hard

### CRM — Salesforce
- **Duration bucket:** long_duration_growth
- **Best liquidity phases:** Calm, Speculation
- **DXY sensitivity:** Low-moderate
- **PAM bias:** UC1, UR2 on oversold corrections
- **Preferred options:** Diagonal DS, CBS
- **Avoid conditions:** Turbulence, growth deceleration signal

---

## SEMICONDUCTORS

### TSM — Taiwan Semiconductor
- **Duration bucket:** long_duration_growth (geopolitical risk premium)
- **Best liquidity phases:** Calm, Speculation
- **DXY sensitivity:** High (USD/TWD, geopolitical tension → DXY spike hurts)
- **PAM bias:** UC1
- **Preferred options:** Bull Bang (breakout), CBS (high IV spikes)
- **Avoid conditions:** Taiwan Strait tension escalation, US-China semiconductor restrictions, Turbulence + DXY strong

### INTC — Intel
- **Duration bucket:** long_duration_growth (turnaround/value hybrid)
- **Best liquidity phases:** Rebound, Calm (contrarian recovery play)
- **DXY sensitivity:** Moderate
- **PAM bias:** UR2 (recovery reversal thesis), DC1 still valid while trend broken
- **Preferred options:** CBS (defined risk given turnaround uncertainty)
- **Avoid conditions:** Speculation phase without recovery confirmation, AI GPU share loss worsening

### MU — Micron Technology
- **Duration bucket:** long_duration_growth (semiconductor cycle)
- **Best liquidity phases:** Rebound (early cycle), Calm
- **DXY sensitivity:** Moderate
- **PAM bias:** UC1 in upcycle, DC1/DR2 in downcycle; strong flush/reversal patterns
- **Preferred options:** Back Ratio (cycle inflection plays), Bull Bang (early cycle)
- **Avoid conditions:** Memory pricing downcycle, inventory correction, Turbulence

### SMH / SOXX — Semiconductor ETFs
- **Duration bucket:** long_duration_growth
- **Best liquidity phases:** Calm, Speculation, Rebound
- **DXY sensitivity:** Moderate
- **PAM bias:** UC1, UR2
- **Preferred options:** Bull Bang, Diagonal DS
- **Avoid conditions:** Turbulence, global capex freeze

---

## FINANCIALS & PAYMENT NETWORKS

### JPM — JPMorgan Chase
- **Duration bucket:** financial_leverage
- **Best liquidity phases:** Calm, Speculation (credit expansion)
- **DXY sensitivity:** Low (domestic + global, USD-priced)
- **PAM bias:** UC1
- **Preferred options:** CBS, Diagonal DS
- **Avoid conditions:** Yield curve inversion deep (NIM compression), credit crisis, Turbulence

### V / MA — Visa / Mastercard
- **Duration bucket:** hybrid_growth_defense (toll-road model)
- **Best liquidity phases:** Calm, Speculation, Flat (resilient)
- **DXY sensitivity:** Moderate (global volume; strong DXY from US growth = OK)
- **PAM bias:** UC1 (very smooth trends)
- **Preferred options:** CBS, Diagonal DS (core quality compounder position)
- **Avoid conditions:** Consumer recession, transaction volume collapse

### SPGI — S&P Global
- **Duration bucket:** hybrid_growth_defense
- **Best liquidity phases:** Calm, Flat
- **DXY sensitivity:** Low
- **PAM bias:** UC1
- **Preferred options:** Diagonal DS, CBS
- **Avoid conditions:** Debt issuance freeze (ratings + data revenue hit), Turbulence

### PYPL — PayPal
- **Duration bucket:** long_duration_growth (fintech)
- **Best liquidity phases:** Rebound, Calm
- **DXY sensitivity:** Low-moderate
- **PAM bias:** UR2 (turnaround/recovery thesis), DC1 if still in downtrend
- **Preferred options:** Bull Bang (breakout confirmation only), CBS
- **Avoid conditions:** Continued market share loss, Turbulence, no PAM reversal confirmation

### COIN — Coinbase Global
- **Duration bucket:** monetary_hedge (crypto proxy)
- **Best liquidity phases:** Speculation, Rebound
- **DXY sensitivity:** High inverse (weak DXY = strong crypto = strong COIN)
- **PAM bias:** UR2 (extreme flush-reversal cycles), UC1 in crypto bull
- **Preferred options:** Bull Bang, Back Ratio (volatility plays)
- **Avoid conditions:** Turbulence, BTC bear market, regulatory risk spike, DXY strong from stress

---

## HEALTHCARE & BIOTECH

### LLY — Eli Lilly
- **Duration bucket:** hybrid_growth_defense (GLP-1 structural growth)
- **Best liquidity phases:** Calm, Flat, Speculation
- **DXY sensitivity:** Low (defensive quality)
- **PAM bias:** UC1 (structural grower)
- **Preferred options:** CBS, Diagonal DS (long-term position)
- **Avoid conditions:** GLP-1 clinical setback (idiosyncratic), reimbursement risk

### NVO — Novo Nordisk
- **Duration bucket:** hybrid_growth_defense
- **Best liquidity phases:** Calm, Flat
- **DXY sensitivity:** Low-moderate (Danish Krone denominated)
- **PAM bias:** UC1, UR2 on corrections
- **Preferred options:** Bull Bang, CBS
- **Avoid conditions:** GLP-1 competition risk, strong EUR/USD tailwinds reversing

### UNH — UnitedHealth Group
- **Duration bucket:** medium_duration_defensive
- **Best liquidity phases:** Flat, Turbulence (defensive)
- **DXY sensitivity:** Very low
- **PAM bias:** UC1
- **Preferred options:** CBS, Diagonal DS
- **Avoid conditions:** Healthcare regulatory overhaul risk, Speculation (underperforms high-beta)

### ZTS — Zoetis
- **Duration bucket:** medium_duration_defensive (animal health compounder)
- **Best liquidity phases:** Calm, Flat
- **DXY sensitivity:** Low
- **PAM bias:** UC1
- **Preferred options:** Diagonal DS
- **Avoid conditions:** Turbulence hard sell-off (defensive but not immune)

---

## DEFENSIVES & CONSUMER STAPLES

### PG / PEP / JNJ / WM / PM / HSY
- **Duration bucket:** medium_duration_defensive
- **Best liquidity phases:** Flat, Turbulence, Rebound (defensive income)
- **DXY sensitivity:** Low (domestic pricing power)
- **PAM bias:** UC1 (slow steady), DC1/DR2 less common
- **Preferred options:** CBS (sell premium in elevated IV), Diagonal DS for income
- **Avoid conditions:** Speculation phase (massive underperformance vs growth), inflation crush on margins (PEP/HSY)

---

## PLATFORM & CONSUMER INTERNET

### UBER — Uber Technologies
- **Duration bucket:** hybrid_growth_defense (platform network effects)
- **Best liquidity phases:** Calm, Speculation
- **DXY sensitivity:** Moderate (global rides + EM exposure)
- **PAM bias:** UC1, UR2
- **Preferred options:** Bull Bang, BBC
- **Avoid conditions:** Turbulence, recession (discretionary rides), gig-economy regulation

### BKNG / ABNB — Booking Holdings / Airbnb
- **Duration bucket:** long_duration_growth (travel platform)
- **Best liquidity phases:** Speculation, Calm
- **DXY sensitivity:** Moderate (global travel; strong DXY = US travel less globally, but USD revenue)
- **PAM bias:** UC1
- **Preferred options:** Bull Bang, CBS
- **Avoid conditions:** Travel demand recession, Turbulence, geopolitical disruption

### MELI — MercadoLibre
- **Duration bucket:** long_duration_growth + cyclical_reflation (EM component)
- **Best liquidity phases:** Speculation, Rebound
- **DXY sensitivity:** HIGH inverse (EM currency exposure; weak DXY = strong EM = strong MELI)
- **PAM bias:** UR2 (large flush/reversal cycles), UC1 in strong bull
- **Preferred options:** Bull Bang, Back Ratio
- **Avoid conditions:** Strong DXY (EM currency compression), Turbulence, Argentina/Brazil FX crisis

---

## CHINESE ADRs (CHINA_SPECIAL TREATMENT)

### BABA / PDD / JD / NIO / BIDU
- **Duration bucket:** china_special
- **Best liquidity phases:** Rebound (on PBoC easing confirmation), early Calm
- **DXY sensitivity:** HIGH (USD/CNY + flight from EM; strong DXY = heavy penalty)
- **PAM bias:** UR2 (major reversal plays only with PBoC catalyst), DC1 in absence of easing
- **Preferred options:** Bull Bang (tactical, catalyst-driven only), no Diagonal DS (too volatile long-term)
- **Avoid conditions:**
  - CN CPI < 1% AND CN phase = Turbulence → debt-deflation risk, DO NOT BUY
  - DXY Bullish from flight-to-safety → FULL penalty on all China names
  - No PBoC easing signal → hold cash, not China longs
  - Regulatory crackdown narrative active
- **Special rule:** Require BOTH (1) CN liquidity turning + (2) PAM UR2 confirmation before any long entry

---

## DEFENSE & AEROSPACE

### LMT — Lockheed Martin
- **Duration bucket:** medium_duration_defensive (geopolitical hedge)
- **Best liquidity phases:** Flat, Turbulence, Calm
- **DXY sensitivity:** Very low
- **PAM bias:** UC1
- **Preferred options:** CBS, Diagonal DS
- **Avoid conditions:** Peace diplomacy driving budget cuts (long-duration geopolitical risk)

### PPA — Invesco Aerospace & Defense ETF / SHLD — Defense Tech ETF
- **Duration bucket:** medium_duration_defensive
- **Best liquidity phases:** Flat, Turbulence
- **DXY sensitivity:** Low
- **PAM bias:** UC1
- **Preferred options:** Bull Bang (breakout on geopolitical escalation), CBS
- **Avoid conditions:** Speculation phase (tends to underperform high-beta tech)

---

## ETFs — MACRO REGIME INSTRUMENTS

### SPY / VTI — S&P 500 / Total Market
- **Duration bucket:** long_duration_growth (broad market)
- **Best liquidity phases:** All except Turbulence
- **DXY sensitivity:** Low-moderate
- **Preferred options:** SNIPEX (SPX), Iron Condor (neutral), CBS (bull), Bull Bang (breakout)
- **Avoid:** Turbulence phase, use GLD/TLT instead

### QQQ — Nasdaq 100
- **Duration bucket:** long_duration_growth (max tech beta)
- **Best liquidity phases:** Calm, Speculation
- **DXY sensitivity:** Low (USD-priced)
- **Preferred options:** Bull Bang, Back Ratio (before breakout), Diagonal DS
- **Avoid:** Turbulence, rates spike hard

### IWM — iShares Russell 2000 (Small Cap)
- **Duration bucket:** cyclical_reflation (most rate-sensitive + domestic)
- **Best liquidity phases:** Rebound early, Calm (rate peak expectations)
- **DXY sensitivity:** Low (domestic)
- **Preferred options:** Bull Bang (cycle turn play), CBS
- **Avoid:** Rates rising, credit tightening, Turbulence, DXY strong from stress

### TLT — iShares 20+ Year Treasury
- **Duration bucket:** medium_duration_defensive (long bonds)
- **Best liquidity phases:** Turbulence, Deflation scare, Bull flattening
- **DXY sensitivity:** Inverse (flight to USD quality = TLT up)
- **PAM bias:** UR2 on rate spike reversals
- **Preferred options:** Bull Bang (rate peak play), CBS
- **Avoid:** Bear steepening, stagflation, fiscal dominance (long bonds lose real value)

### GLD — SPDR Gold Trust
- **Duration bucket:** monetary_hedge
- **Best liquidity phases:** ALL (outperforms in Turbulence + fiscal dominance + stagflation)
- **DXY sensitivity:** Inverse moderate (but fiscal dominance overrides — gold can rise WITH DXY in monetary inflation)
- **PAM bias:** UC1 in structural bull, UR2 on sharp corrections
- **Preferred options:** Bull Bang (breakout), CBS (income during consolidation)
- **Avoid:** Sweet-spot reflation with strong real rates (temporary headwind), risk-on Speculation where BTC dominates

### SMH / SOXX — Semiconductor ETFs
- (See individual semi section above — same logic aggregated)

### VWO / IEMG — Emerging Market ETFs
- **Duration bucket:** cyclical_reflation
- **Best liquidity phases:** Rebound, early Calm
- **DXY sensitivity:** HIGH inverse (weak DXY = EM outperform)
- **PAM bias:** UR2 on major lows with DXY reversal
- **Preferred options:** Bull Bang (DXY peak catalyst), CBS
- **Avoid:** DXY Bullish, Turbulence, China debt-deflation risk active

---

## CRYPTO

### BTC-USD — Bitcoin
- **Duration bucket:** monetary_hedge (highest beta to liquidity)
- **Best liquidity phases:** Speculation (peak outperformance), Rebound
- **DXY sensitivity:** HIGH inverse (weak DXY + fiscal dominance = BTC explosive)
- **Lead indicators:** GLI leads BTC by ~6 weeks; CN PBoC easing leads BTC by ~13 weeks
- **PAM bias:** UR2 and UC1 both active; extreme flush/wave cycles
- **Preferred strategy:** Spot only or regulated futures; avoid options unless on COIN stock
- **Avoid conditions:** Turbulence + DXY spike from stress (max drawdown risk), rates spike from inflation (not from growth); debt-deflation scare
- **Special rule:** In fiscal dominance scenario → BTC = monetary inflation hedge DESPITE DXY strength (distinguish cause of DXY strength)

### ETH-USD — Ethereum
- **Duration bucket:** monetary_hedge (1.5× beta to BTC roughly)
- **Best liquidity phases:** Speculation, Rebound
- **DXY sensitivity:** HIGH inverse
- **PAM bias:** UR2, UC1 in bull
- **Avoid conditions:** Same as BTC + staking/regulatory risks
- **Note:** ETH correlation to GLI ~150% vs BTC ~90%; higher vol, higher beta

### SOL-USD — Solana
- **Duration bucket:** monetary_hedge (speculative tier, 2–3× BTC beta)
- **Best liquidity phases:** Speculation only for primary allocation
- **DXY sensitivity:** Very high inverse
- **PAM bias:** UR2 (extreme cycles)
- **Avoid conditions:** Turbulence, BTC bear, regulatory action; high idiosyncratic risk

---

## EU STOCKS

### ASML.AS — ASML Holding
- **Duration bucket:** long_duration_growth (monopoly EUV, global capex cycle)
- **Best liquidity phases:** Calm, Speculation
- **DXY sensitivity:** High (EUR-denominated; strong USD = cheaper for US buyers but hurts EUR P&L)
- **PAM bias:** UC1, UR2 on corrections
- **Preferred options:** Bull Bang (on US exchanges via ADR-equivalent)
- **Avoid conditions:** Semiconductor capex freeze, chip export controls expansion, Turbulence

### MC.PA — LVMH
- **Duration bucket:** cyclical_reflation / hybrid (luxury = China + global wealth)
- **Best liquidity phases:** Calm, Speculation
- **DXY sensitivity:** Moderate (EUR stock; strong EUR = headwind for USD investors)
- **PAM bias:** UC1, UR2 on China stimulus rebounds
- **Avoid conditions:** China consumption collapse, DXY strong + EUR weak combo (margin squeeze)

---

## REGIME-BASED ALLOCATION QUICK REFERENCE

| Regime | Favor | Reduce | Avoid |
|--------|-------|--------|-------|
| Liquidity Accelerating + Benign | long_duration_growth, BTC, gold | medium_duration_defensive | short_duration_collateral |
| Liquidity Flat / Calm | hybrid_growth_defense, financial_leverage | speculative crypto | low-quality growth |
| Liquidity Decelerating + Stagflation | monetary_hedge (gold, BTC), pricing-power | long_duration_growth, bonds | cyclical_reflation |
| Turbulence / Debt-Deflation | short_duration_collateral, gold, TLT | BTC, equity | cyclical_reflation, china_special |
| DXY Bearish + China Easing | cyclical_reflation, VWO, MELI, BTC | USD-only defensives | — |
| Divergent World (high dispersion) | gold, cash, single-stock quality | global cyclicals, EM | China ADRs (absent catalyst) |

---

## SCORING MODIFIERS (apply to composite_score in engine)

| Condition | Modifier |
|-----------|----------|
| regime_alignment = "high" (ticker bucket matches active regime) | +5 pts |
| duration_bucket matches financial conditions triangle regime | +3 pts |
| divergent_world = true AND regime_alignment = "low" | −10 pts |
| china_special ticker without PBoC easing signal | −15 pts |
| options_liquid = false but options recommended | veto options, equity only |
| PAM_VALID = false | veto trade output entirely (watchlist only) |
| macro_score < 45 | downgrade all to WATCHLIST regardless of PAM |
