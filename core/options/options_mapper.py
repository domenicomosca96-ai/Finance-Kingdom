"""
Options Strategy Engine — Bang Pham Van / Adam Khoo complete matrix.

Two key questions:
  1. Are you BULLISH, BEARISH or NEUTRAL?
  2. Is Implied Volatility HIGH or LOW?
"""

import math
import numpy as np
from dataclasses import dataclass, field
from core.pam.market_data import PatternResult, FlowResult, MomentumResult


@dataclass
class OptionLeg:
    side: str
    type: str
    strike: float
    expiry: str
    quantity: int = 1


@dataclass
class PayoffPoint:
    price: float
    pnl: float
    pnl_pct: float
    label: str = ""


@dataclass
class OptionsRecommendation:
    strategy_name: str
    strategy_code: str
    direction: str
    legs: list[OptionLeg]
    rationale: str
    max_profit: str
    max_loss: str
    breakeven: str
    payoff_matrix: list[PayoffPoint]
    vol_regime: str
    near_earnings: bool
    bang_van_notes: str = ""


def classify_vol_regime(iv_rank: float | None, rsi: float | None) -> str:
    if iv_rank is not None:
        return "high" if iv_rank > 50 else "low"
    if rsi is not None:
        return "high" if (rsi < 30 or rsi > 70) else "low"
    return "low"


def select_strategy(
    pattern: PatternResult, flow: FlowResult, momentum: MomentumResult,
    current_price: float, rsi: float | None = None, iv_rank: float | None = None,
    near_earnings: bool = False, days_to_earnings: int | None = None,
    is_index: bool = False,
) -> OptionsRecommendation:
    vol = classify_vol_regime(iv_rank, rsi)
    direction = _pattern_direction(pattern)
    earnings_imminent = near_earnings or (days_to_earnings and days_to_earnings <= 14)

    if direction == "long":
        if vol == "high":
            return _bullish_high_iv(current_price, pattern, momentum, earnings_imminent)
        else:
            return _bullish_low_iv(current_price, pattern, flow, momentum, earnings_imminent)
    elif direction == "short":
        if vol == "high":
            return _bearish_high_iv(current_price, pattern)
        else:
            return _bearish_low_iv(current_price, pattern)
    else:
        if vol == "high":
            return _neutral_high_iv(current_price, pattern, is_index)
        else:
            return _neutral_low_iv(current_price, pattern, earnings_imminent)


def _pattern_direction(pattern: PatternResult) -> str:
    if pattern.pattern in ("UC1", "UC2", "DR1", "DR2"):
        return "long"
    if pattern.pattern in ("DC1", "DC2", "UR1", "UR2"):
        return "short"
    return "neutral"


# ═══════════════════════════════════════════════════════════
#  BULLISH + HIGH IV
# ═══════════════════════════════════════════════════════════

def _bullish_high_iv(price, pattern, momentum, near_earnings):
    if not near_earnings:
        return _cash_secured_put(price, pattern)
    else:
        return _bull_put_spread(price, pattern)


def _cash_secured_put(price, pattern):
    strike = round(price * 0.93, 2)
    premium = price * 0.02
    legs = [OptionLeg("SELL", "PUT", strike, "30d")]
    return OptionsRecommendation(
        strategy_name="Cash Secured Put", strategy_code="CSP", direction="long",
        legs=legs,
        rationale=f"High IV — sell premium. Collect ${premium*100:.0f}/contract or own at ${strike:.0f} discount.",
        max_profit=f"${premium*100:.0f}/contract", max_loss=f"${strike*100:.0f} (assignment)",
        breakeven=f"${strike - premium:.2f}",
        payoff_matrix=_payoff_csp(price, strike, premium),
        vol_regime="high", near_earnings=False,
        bang_van_notes="CSP for fundamentally good stocks.",
    )


def _bull_put_spread(price, pattern):
    sell_strike = round(price * 0.94, 2)
    buy_strike = round(price * 0.88, 2)
    width = sell_strike - buy_strike
    credit = width * 0.35
    legs = [OptionLeg("SELL", "PUT", sell_strike, "30d"), OptionLeg("BUY", "PUT", buy_strike, "30d")]
    return OptionsRecommendation(
        strategy_name="Bull Put Spread", strategy_code="BPS", direction="long",
        legs=legs,
        rationale=f"High IV credit spread. Profit if above ${sell_strike:.0f}.",
        max_profit=f"${credit*100:.0f}/contract", max_loss=f"${(width - credit)*100:.0f}/contract",
        breakeven=f"${sell_strike - credit:.2f}",
        payoff_matrix=_payoff_vertical(price, buy_strike, sell_strike, credit, "put_credit"),
        vol_regime="high", near_earnings=True,
        bang_van_notes="Avoid BPS near earnings with gap risk.",
    )


# ═══════════════════════════════════════════════════════════
#  BULLISH + LOW IV
# ═══════════════════════════════════════════════════════════

def _bullish_low_iv(price, pattern, flow, momentum, near_earnings):
    if near_earnings:
        return _bull_bang_collar(price, pattern)
    if pattern.pattern in ("DR2",) or (momentum.is_flush and momentum.direction == "down"):
        return _crouching_bull(price, pattern)
    if pattern.confidence >= 80:
        return _long_call(price, pattern)
    if pattern.pattern in ("UC1", "UC2"):
        return _diagonal_spread(price, pattern)
    return _bull_call_spread(price, pattern)


def _long_call(price, pattern):
    strike = round(price * 0.98, 2)
    premium = price * 0.045
    legs = [OptionLeg("BUY", "CALL", strike, "45d")]
    return OptionsRecommendation(
        strategy_name="Long Call", strategy_code="LC", direction="long",
        legs=legs, rationale="Low IV + high conviction. Unlimited upside.",
        max_profit="Unlimited", max_loss=f"${premium*100:.0f}/contract",
        breakeven=f"${strike + premium:.2f}",
        payoff_matrix=_payoff_long_option(price, strike, premium, "call"),
        vol_regime="low", near_earnings=False,
        bang_van_notes="Long Call for high conviction bullish in low IV.",
    )


def _bull_call_spread(price, pattern):
    buy_strike = round(price * 0.99, 2)
    sell_strike = round(price * 1.08, 2)
    debit = (sell_strike - buy_strike) * 0.40
    legs = [OptionLeg("BUY", "CALL", buy_strike, "45d"), OptionLeg("SELL", "CALL", sell_strike, "45d")]
    return OptionsRecommendation(
        strategy_name="Bull Call Spread", strategy_code="BuCS", direction="long",
        legs=legs,
        rationale=f"Low IV debit spread. R:R = {((sell_strike - buy_strike - debit) / debit):.1f}:1.",
        max_profit=f"${(sell_strike - buy_strike - debit)*100:.0f}/contract",
        max_loss=f"${debit*100:.0f}/contract",
        breakeven=f"${buy_strike + debit:.2f}",
        payoff_matrix=_payoff_vertical(price, buy_strike, sell_strike, debit, "call_debit"),
        vol_regime="low", near_earnings=False,
        bang_van_notes="BuCS for moderate bullish, low IV.",
    )


def _diagonal_spread(price, pattern):
    buy_strike = round(price * 0.97, 2)
    sell_strike = round(price * 1.05, 2)
    debit = price * 0.035
    legs = [OptionLeg("BUY", "CALL", buy_strike, "60d"), OptionLeg("SELL", "CALL", sell_strike, "30d")]
    return OptionsRecommendation(
        strategy_name="Diagonal Spread", strategy_code="DS", direction="long",
        legs=legs,
        rationale="Low IV, UC continuation. Short leg generates theta, long captures upside.",
        max_profit=f"~${(sell_strike - buy_strike)*100:.0f}/contract",
        max_loss=f"${debit*100:.0f}/contract",
        breakeven=f"~${buy_strike + debit:.2f}",
        payoff_matrix=_payoff_vertical(price, buy_strike, sell_strike, debit, "call_debit"),
        vol_regime="low", near_earnings=False,
        bang_van_notes="DS for fundamentally good stocks, neutral-to-bullish.",
    )


def _bull_bang_collar(price, pattern):
    call_strike = round(price * 1.03, 2)
    put_sell = round(price * 0.95, 2)
    put_buy = round(price * 0.90, 2)
    net_cost = price * 0.012
    legs = [
        OptionLeg("BUY", "CALL", call_strike, "45d"),
        OptionLeg("SELL", "PUT", put_sell, "45d"),
        OptionLeg("BUY", "PUT", put_buy, "45d"),
    ]
    return OptionsRecommendation(
        strategy_name="Bull Bang Collar", strategy_code="BBC", direction="long",
        legs=legs,
        rationale=f"Earnings protection. Upside from call, funded by put sale. Floor at ${put_buy:.0f}.",
        max_profit=f"Unlimited above ${call_strike:.0f}",
        max_loss=f"~${(put_sell - put_buy + net_cost)*100:.0f}/contract",
        breakeven=f"~${call_strike + net_cost:.2f}",
        payoff_matrix=_payoff_vertical(price, put_buy, call_strike, net_cost, "collar"),
        vol_regime="low", near_earnings=True,
        bang_van_notes="BBC for good stocks near earnings.",
    )


def _crouching_bull(price, pattern):
    buy_strike = round(price * 0.92, 2)
    sell_strike = round(price * 1.02, 2)
    debit = (sell_strike - buy_strike) * 0.55
    legs = [OptionLeg("BUY", "CALL", buy_strike, "90d"), OptionLeg("SELL", "CALL", sell_strike, "90d")]
    return OptionsRecommendation(
        strategy_name="Crouching Bull Spread", strategy_code="CBS", direction="long",
        legs=legs,
        rationale="Oversold reversal play. Deep ITM long call, high delta. 90d for thesis.",
        max_profit=f"${(sell_strike - buy_strike - debit)*100:.0f}/contract",
        max_loss=f"${debit*100:.0f}/contract",
        breakeven=f"${buy_strike + debit:.2f}",
        payoff_matrix=_payoff_vertical(price, buy_strike, sell_strike, debit, "call_debit"),
        vol_regime="low", near_earnings=False,
        bang_van_notes="CBS for beaten-down fundamentally good stocks.",
    )


# ═══════════════════════════════════════════════════════════
#  BEARISH
# ═══════════════════════════════════════════════════════════

def _bearish_high_iv(price, pattern):
    sell_strike = round(price * 1.05, 2)
    buy_strike = round(price * 1.12, 2)
    credit = (buy_strike - sell_strike) * 0.35
    legs = [OptionLeg("SELL", "CALL", sell_strike, "30d"), OptionLeg("BUY", "CALL", buy_strike, "30d")]
    return OptionsRecommendation(
        strategy_name="Bear Call Spread", strategy_code="BCS", direction="short",
        legs=legs,
        rationale=f"High IV call credit spread. Profit if below ${sell_strike:.0f}.",
        max_profit=f"${credit*100:.0f}/contract",
        max_loss=f"${(buy_strike - sell_strike - credit)*100:.0f}/contract",
        breakeven=f"${sell_strike + credit:.2f}",
        payoff_matrix=_payoff_vertical(price, sell_strike, buy_strike, credit, "call_credit"),
        vol_regime="high", near_earnings=False,
        bang_van_notes="BCS in high IV bearish.",
    )


def _bearish_low_iv(price, pattern):
    buy_strike = round(price * 1.01, 2)
    sell_strike = round(price * 0.92, 2)
    debit = (buy_strike - sell_strike) * 0.35
    legs = [OptionLeg("BUY", "PUT", buy_strike, "45d"), OptionLeg("SELL", "PUT", sell_strike, "45d")]
    return OptionsRecommendation(
        strategy_name="Bear Put Spread", strategy_code="BePS", direction="short",
        legs=legs,
        rationale=f"Low IV debit put spread. Max profit at ${sell_strike:.0f}.",
        max_profit=f"${(buy_strike - sell_strike - debit)*100:.0f}/contract",
        max_loss=f"${debit*100:.0f}/contract",
        breakeven=f"${buy_strike - debit:.2f}",
        payoff_matrix=_payoff_vertical(price, sell_strike, buy_strike, debit, "put_debit"),
        vol_regime="low", near_earnings=False,
        bang_van_notes="BePS for low IV bearish.",
    )


# ═══════════════════════════════════════════════════════════
#  NEUTRAL
# ═══════════════════════════════════════════════════════════

def _neutral_high_iv(price, pattern, is_index):
    ps = round(price * 0.93, 2)
    pl = round(price * 0.88, 2)
    cs = round(price * 1.07, 2)
    cl = round(price * 1.12, 2)
    credit = price * 0.018
    legs = [
        OptionLeg("SELL", "PUT", ps, "30d"), OptionLeg("BUY", "PUT", pl, "30d"),
        OptionLeg("SELL", "CALL", cs, "30d"), OptionLeg("BUY", "CALL", cl, "30d"),
    ]
    return OptionsRecommendation(
        strategy_name="Iron Condor", strategy_code="IC", direction="neutral",
        legs=legs,
        rationale=f"High IV — sell premium both sides. Profit zone: ${ps:.0f}-${cs:.0f}.",
        max_profit=f"${credit*100:.0f}/contract",
        max_loss=f"${(cs - cl + credit)*100:.0f}/contract",
        breakeven=f"${ps - credit:.2f} / ${cs + credit:.2f}",
        payoff_matrix=_payoff_ic(price, pl, ps, cs, cl, credit),
        vol_regime="high", near_earnings=False,
        bang_van_notes="IC preferred on futures or indices (SPX, NDX, RUT).",
    )


def _neutral_low_iv(price, pattern, near_earnings):
    strike = round(price, 2)
    debit = price * 0.015
    legs = [OptionLeg("BUY", "CALL", strike, "60d"), OptionLeg("SELL", "CALL", strike, "30d")]
    return OptionsRecommendation(
        strategy_name="Calendar Spread", strategy_code="CS", direction="neutral",
        legs=legs,
        rationale="Low IV — time value differential. Profits from theta decay.",
        max_profit="Varies (max near ATM at short expiry)",
        max_loss=f"${debit*100:.0f}/contract",
        breakeven=f"~${strike:.2f} +/- spread width",
        payoff_matrix=_payoff_calendar(price, strike, debit),
        vol_regime="low", near_earnings=near_earnings,
        bang_van_notes="Calendar for stocks with good weekly premiums.",
    )


# ═══════════════════════════════════════════════════════════
#  PAYOFF HELPERS
# ═══════════════════════════════════════════════════════════

def _payoff_vertical(price, lower, upper, cost, style):
    points = []
    for tp in np.linspace(price * 0.85, price * 1.20, 8):
        if style == "call_debit":
            pnl = (max(tp - lower, 0) - max(tp - upper, 0) - cost) * 100
        elif style == "put_debit":
            pnl = (max(upper - tp, 0) - max(lower - tp, 0) - cost) * 100
        elif style == "call_credit":
            pnl = (cost - max(tp - lower, 0) + max(tp - upper, 0)) * 100
        elif style == "put_credit":
            pnl = (cost - max(lower - tp, 0) + max(upper - tp, 0)) * 100
        elif style == "collar":
            pnl = (max(tp - upper, 0) - cost) * 100
        else:
            pnl = 0
        pnl_pct = (pnl / max(abs(cost) * 100, 1)) * 100
        label = "~breakeven" if abs(pnl) < abs(cost) * 15 else ""
        points.append(PayoffPoint(round(tp, 2), round(pnl, 0), round(pnl_pct, 1), label))
    return points


def _payoff_csp(price, strike, premium):
    points = []
    for tp in np.linspace(price * 0.80, price * 1.15, 8):
        pnl = (premium - max(strike - tp, 0)) * 100
        pnl_pct = (pnl / (premium * 100)) * 100 if premium > 0 else 0
        label = "max profit" if tp >= strike else ""
        points.append(PayoffPoint(round(tp, 2), round(pnl, 0), round(pnl_pct, 1), label))
    return points


def _payoff_long_option(price, strike, premium, opt_type):
    points = []
    for tp in np.linspace(price * 0.80, price * 1.25, 8):
        if opt_type == "call":
            pnl = (max(tp - strike, 0) - premium) * 100
        else:
            pnl = (max(strike - tp, 0) - premium) * 100
        pnl_pct = (pnl / (premium * 100)) * 100 if premium > 0 else 0
        points.append(PayoffPoint(round(tp, 2), round(pnl, 0), round(pnl_pct, 1), ""))
    return points


def _payoff_ic(price, pl, ps, cs, cl, credit):
    points = []
    for tp in np.linspace(price * 0.83, price * 1.17, 8):
        put_loss = max(ps - tp, 0) - max(pl - tp, 0)
        call_loss = max(tp - cs, 0) - max(tp - cl, 0)
        pnl = (credit - put_loss - call_loss) * 100
        pnl_pct = (pnl / (credit * 100)) * 100 if credit > 0 else 0
        points.append(PayoffPoint(round(tp, 2), round(pnl, 0), round(pnl_pct, 1), ""))
    return points


def _payoff_calendar(price, strike, debit):
    points = []
    for tp in np.linspace(price * 0.88, price * 1.12, 8):
        dist = abs(tp - strike) / price
        remaining_value = debit * max(0, 1 - dist * 8)
        pnl = (remaining_value - debit) * 100
        pnl_pct = (pnl / (debit * 100)) * 100 if debit > 0 else 0
        label = "max profit" if dist < 0.01 else ""
        points.append(PayoffPoint(round(tp, 2), round(pnl, 0), round(pnl_pct, 1), label))
    return points
