"""Scoring Engine — Logistic normalization + Fractional Kelly + PAM risk rules."""

import math
from dataclasses import dataclass
from core.config import settings


@dataclass
class ScoreResult:
    raw_macro: float
    raw_theme: float
    raw_pam: float
    raw_composite: float
    probability_pct: float
    confidence_tier: str


@dataclass
class SizingResult:
    shares: int
    contracts: int
    capital_allocated: float
    dollar_risk: float
    kelly_raw: float
    kelly_adjusted: float
    risk_reward_ratio: float
    risk_pct_of_portfolio: float


def logistic_probability(raw: float, k: float | None = None, c: float | None = None) -> float:
    _k = k or settings.LOGISTIC_K
    _c = c or settings.LOGISTIC_C
    exponent = -_k * (raw - _c)
    exponent = max(min(exponent, 50), -50)
    return 100.0 / (1.0 + math.exp(exponent))


def compute_score(
    raw_macro: float, raw_theme: float, raw_pam: float,
    w_macro: float | None = None, w_theme: float | None = None, w_pam: float | None = None,
) -> ScoreResult:
    wm = w_macro or settings.W_MACRO
    wt = w_theme or settings.W_THEME
    wp = w_pam or settings.W_PAM

    total_w = wm + wt + wp
    wm, wt, wp = wm / total_w, wt / total_w, wp / total_w

    raw = wm * raw_macro + wt * raw_theme + wp * raw_pam
    prob = logistic_probability(raw)

    if prob >= 72:
        tier = "high"
    elif prob >= 58:
        tier = "medium"
    elif prob >= 45:
        tier = "low"
    else:
        tier = "no_trade"

    return ScoreResult(
        raw_macro=round(raw_macro, 1), raw_theme=round(raw_theme, 1),
        raw_pam=round(raw_pam, 1), raw_composite=round(raw, 1),
        probability_pct=round(prob, 1), confidence_tier=tier,
    )


def compute_sizing(
    probability: float, entry_price: float, stop_price: float, target_price: float,
    portfolio_size: float | None = None, max_risk_pct: float | None = None,
    kelly_fraction: float | None = None,
) -> SizingResult:
    portfolio = portfolio_size or settings.PORTFOLIO_SIZE
    max_risk = max_risk_pct or settings.MAX_RISK_PER_TRADE_PCT
    frac = kelly_fraction or settings.KELLY_FRACTION

    risk_per_share = abs(entry_price - stop_price)
    reward_per_share = abs(target_price - entry_price)

    if risk_per_share <= 0:
        return SizingResult(0, 0, 0, 0, 0, 0, 0, 0)

    rr_ratio = reward_per_share / risk_per_share
    max_dollar_risk = portfolio * (max_risk / 100.0)

    p = probability / 100.0
    q = 1 - p
    b = rr_ratio
    kelly_raw = (b * p - q) / b if b > 0 else 0
    kelly_raw = max(kelly_raw, 0)
    kelly_adj = kelly_raw * frac
    kelly_dollar_risk = kelly_adj * portfolio

    dollar_risk = min(max_dollar_risk, kelly_dollar_risk)

    shares = int(dollar_risk / risk_per_share) if risk_per_share > 0 else 0
    capital = shares * entry_price

    max_capital = portfolio * (settings.MAX_POSITION_PCT / 100.0)
    if capital > max_capital:
        shares = int(max_capital / entry_price)
        capital = shares * entry_price
        dollar_risk = shares * risk_per_share

    contracts = max(1, shares // 100) if shares >= 50 else 0

    return SizingResult(
        shares=shares, contracts=contracts,
        capital_allocated=round(capital, 2), dollar_risk=round(dollar_risk, 2),
        kelly_raw=round(kelly_raw, 4), kelly_adjusted=round(kelly_adj, 4),
        risk_reward_ratio=round(rr_ratio, 2),
        risk_pct_of_portfolio=round((dollar_risk / portfolio) * 100, 2),
    )
