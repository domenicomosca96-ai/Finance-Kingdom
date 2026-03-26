"""
Market Data + Deterministic PAM Engine.

Implements Piranha Profits (Adam Khoo / Alson Chew) methodology:
- Flow State: HH/HL vs LH/LL relative to 50 SMA
- Price Momentum: wave (~45) vs flush (>70) classification
- UC1 Continuation: pullback in uptrend to support -> trigger level breakout
- UR2 Reversal: double top/bottom with majority flush -> EXE bar confirmation
- Accumulation/Distribution Rotation Model: segments A-D

ALL pattern detection is deterministic Python.
"""

import math
import numpy as np
import pandas as pd
import yfinance as yf
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Optional


# ═══════════════════════════════════════════════════════════
#  DATA DOWNLOAD & INDICATORS
# ═══════════════════════════════════════════════════════════

def download_ohlcv(ticker: str, period: str = "2y") -> pd.DataFrame:
    """Download OHLCV and compute technical indicators."""
    df = yf.download(ticker, period=period, interval="1d", progress=False)
    if df.empty:
        return df

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.rename(columns=str.lower)
    df.index.name = "dt"
    df = df.reset_index()

    df["sma_20"] = df["close"].rolling(20).mean()
    df["sma_50"] = df["close"].rolling(50).mean()
    df["sma_150"] = df["close"].rolling(150).mean()
    df["ema_20"] = df["close"].ewm(span=20).mean()
    df["ema_50"] = df["close"].ewm(span=50).mean()

    h_l = df["high"] - df["low"]
    h_pc = (df["high"] - df["close"].shift()).abs()
    l_pc = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([h_l, h_pc, l_pc], axis=1).max(axis=1)
    df["atr_14"] = tr.rolling(14).mean()

    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["rsi_14"] = 100 - (100 / (1 + rs))

    df["swing_high"] = _detect_swing_highs(df, window=5)
    df["swing_low"] = _detect_swing_lows(df, window=5)

    return df


def _detect_swing_highs(df: pd.DataFrame, window: int = 5) -> pd.Series:
    highs = df["high"]
    swing = pd.Series(np.nan, index=df.index)
    for i in range(window, len(df) - window):
        if highs.iloc[i] == highs.iloc[i - window: i + window + 1].max():
            swing.iloc[i] = highs.iloc[i]
    return swing


def _detect_swing_lows(df: pd.DataFrame, window: int = 5) -> pd.Series:
    lows = df["low"]
    swing = pd.Series(np.nan, index=df.index)
    for i in range(window, len(df) - window):
        if lows.iloc[i] == lows.iloc[i - window: i + window + 1].min():
            swing.iloc[i] = lows.iloc[i]
    return swing


# ═══════════════════════════════════════════════════════════
#  FLOW STATE
# ═══════════════════════════════════════════════════════════

@dataclass
class FlowResult:
    state: str
    above_sma50: bool
    hh_hl_count: int
    lh_ll_count: int
    last_swing_high: float | None = None
    last_swing_low: float | None = None
    prev_swing_high: float | None = None
    prev_swing_low: float | None = None


def compute_flow(df: pd.DataFrame) -> FlowResult:
    if len(df) < 60:
        return FlowResult("ranging", False, 0, 0)

    current_close = df["close"].iloc[-1]
    sma50 = df["sma_50"].iloc[-1]
    above_sma50 = current_close > sma50

    swing_highs = df.dropna(subset=["swing_high"]).tail(6)
    swing_lows = df.dropna(subset=["swing_low"]).tail(6)

    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return FlowResult("ranging", above_sma50, 0, 0)

    sh_vals = swing_highs["swing_high"].values
    sl_vals = swing_lows["swing_low"].values

    hh_count = sum(1 for i in range(1, len(sh_vals)) if sh_vals[i] > sh_vals[i - 1])
    hl_count = sum(1 for i in range(1, len(sl_vals)) if sl_vals[i] > sl_vals[i - 1])
    hh_hl = min(hh_count, hl_count)

    lh_count = sum(1 for i in range(1, len(sh_vals)) if sh_vals[i] < sh_vals[i - 1])
    ll_count = sum(1 for i in range(1, len(sl_vals)) if sl_vals[i] < sl_vals[i - 1])
    lh_ll = min(lh_count, ll_count)

    if above_sma50 and hh_hl >= 2:
        state = "positive_flow"
    elif not above_sma50 and lh_ll >= 2:
        state = "negative_flow"
    elif above_sma50 and lh_ll >= 1:
        state = "transition_up"
    elif not above_sma50 and hh_hl >= 1:
        state = "transition_down"
    else:
        state = "ranging"

    return FlowResult(
        state=state, above_sma50=above_sma50,
        hh_hl_count=hh_hl, lh_ll_count=lh_ll,
        last_swing_high=float(sh_vals[-1]),
        last_swing_low=float(sl_vals[-1]),
        prev_swing_high=float(sh_vals[-2]) if len(sh_vals) >= 2 else None,
        prev_swing_low=float(sl_vals[-2]) if len(sl_vals) >= 2 else None,
    )


# ═══════════════════════════════════════════════════════════
#  PRICE MOMENTUM
# ═══════════════════════════════════════════════════════════

@dataclass
class MomentumResult:
    is_flush: bool
    is_wave: bool
    angle_degrees: float
    direction: str
    flush_bar_count: int
    bars_in_move: int


def compute_momentum(df: pd.DataFrame, lookback: int = 20) -> MomentumResult:
    if len(df) < lookback + 10:
        return MomentumResult(False, False, 0, "neutral", 0, 0)

    recent = df.tail(lookback).copy()
    price_change = recent["close"].iloc[-1] - recent["close"].iloc[0]
    avg_bar_range = (recent["high"] - recent["low"]).mean()

    if avg_bar_range > 0:
        normalized_slope = abs(price_change) / (lookback * avg_bar_range)
        angle = math.degrees(math.atan(normalized_slope * 3))
    else:
        angle = 0

    direction = "up" if price_change > 0 else "down" if price_change < 0 else "neutral"

    bar_ranges = recent["high"] - recent["low"]
    flush_bars = (bar_ranges > avg_bar_range * 1.5).sum()

    is_flush = angle > 65
    is_wave = 30 < angle < 60

    return MomentumResult(
        is_flush=is_flush, is_wave=is_wave,
        angle_degrees=round(angle, 1), direction=direction,
        flush_bar_count=int(flush_bars), bars_in_move=lookback,
    )


# ═══════════════════════════════════════════════════════════
#  PATTERN DETECTION
# ═══════════════════════════════════════════════════════════

@dataclass
class PatternResult:
    pattern: str
    confirmed: bool
    confidence: float
    trigger_level: float | None = None
    stop_level: float | None = None
    target_level: float | None = None
    rr_ratio: float | None = None
    description: str = ""


def detect_uc1(df: pd.DataFrame, flow: FlowResult) -> PatternResult:
    if flow.state != "positive_flow":
        return PatternResult("NONE", False, 0)

    current = df.iloc[-1]
    close = current["close"]
    sma20 = current.get("sma_20")
    sma50 = current.get("sma_50")

    if pd.isna(sma20) or pd.isna(sma50):
        return PatternResult("NONE", False, 0)

    sma_zone_top = max(sma20, sma50) * 1.02
    sma_zone_bottom = min(sma20, sma50) * 0.98
    in_pullback_zone = sma_zone_bottom <= close <= sma_zone_top

    recent_low = df["low"].tail(5).min()
    bounced_from_zone = (recent_low <= sma_zone_top) and (close > sma20)

    if not (in_pullback_zone or bounced_from_zone):
        return PatternResult("NONE", False, 0)

    trigger = flow.last_swing_high
    stop = flow.last_swing_low
    if trigger is None or stop is None:
        return PatternResult("NONE", False, 0)

    risk = abs(close - stop)
    if risk <= 0:
        return PatternResult("NONE", False, 0)

    reward = risk * 2.0
    target = close + reward
    rr = reward / risk

    confirmed = close > trigger
    confidence = 70 if confirmed else 55

    vol_recent = df["volume"].tail(5).mean()
    vol_prior = df["volume"].tail(20).head(15).mean()
    if vol_prior > 0 and vol_recent < vol_prior * 0.8:
        confidence += 10

    return PatternResult(
        pattern="UC1", confirmed=confirmed,
        confidence=min(confidence, 100),
        trigger_level=round(trigger, 2),
        stop_level=round(stop, 2),
        target_level=round(target, 2),
        rr_ratio=round(rr, 2),
        description=f"UC1 in positive flow. Pullback to SMA zone. "
                    f"Trigger: break above {trigger:.2f}. Stop below {stop:.2f}.",
    )


def detect_ur2(df: pd.DataFrame, flow: FlowResult, momentum: MomentumResult) -> PatternResult:
    if flow.state != "positive_flow":
        return PatternResult("NONE", False, 0)
    if not momentum.is_flush or momentum.direction != "up":
        return PatternResult("NONE", False, 0)

    swing_highs = df.dropna(subset=["swing_high"]).tail(4)
    if len(swing_highs) < 2:
        return PatternResult("NONE", False, 0)

    lp = swing_highs["swing_high"].iloc[-1]
    prev_high = swing_highs["swing_high"].iloc[-2]

    if abs(lp - prev_high) / prev_high > 0.03:
        return PatternResult("NONE", False, 0)

    point_x = prev_high
    swing_lows = df.dropna(subset=["swing_low"]).tail(4)
    if len(swing_lows) < 1:
        return PatternResult("NONE", False, 0)

    point_y_candidates = swing_lows[swing_lows.index > swing_highs.index[-2]]
    if len(point_y_candidates) == 0:
        return PatternResult("NONE", False, 0)

    point_y = point_y_candidates["swing_low"].min()
    midpoint = point_y + (point_x - point_y) * 0.5

    recent_lows = df["low"].tail(10)
    flush_started_below_mid = recent_lows.min() < midpoint

    if not flush_started_below_mid:
        return PatternResult("NONE", False, 0)

    last_bars = df.tail(4)
    exe_found = False
    for _, bar in last_bars.iterrows():
        is_bearish = bar["close"] < bar["open"]
        bar_range = bar["high"] - bar["low"]
        avg_range = df["high"].tail(20).mean() - df["low"].tail(20).mean()
        is_large = bar_range > avg_range * 1.2
        closes_below_lp = bar["close"] <= lp
        if is_bearish and is_large and closes_below_lp:
            exe_found = True
            break

    if not exe_found:
        return PatternResult("NONE", False, 0, description="UR2 forming, awaiting bearish EXE bar")

    current = df.iloc[-1]["close"]
    stop = lp * 1.01
    risk = abs(stop - current)
    target = current - risk * 2.0

    return PatternResult(
        pattern="UR2", confirmed=True, confidence=75,
        trigger_level=round(lp, 2), stop_level=round(stop, 2),
        target_level=round(target, 2), rr_ratio=2.0,
        description=f"UR2 double top reversal at {lp:.2f}. "
                    f"Majority flush confirmed. Bearish EXE formed. SHORT signal.",
    )


def detect_dr2(df: pd.DataFrame, flow: FlowResult, momentum: MomentumResult) -> PatternResult:
    if flow.state != "negative_flow":
        return PatternResult("NONE", False, 0)
    if not momentum.is_flush or momentum.direction != "down":
        return PatternResult("NONE", False, 0)

    swing_lows = df.dropna(subset=["swing_low"]).tail(4)
    if len(swing_lows) < 2:
        return PatternResult("NONE", False, 0)

    lp = swing_lows["swing_low"].iloc[-1]
    prev_low = swing_lows["swing_low"].iloc[-2]

    if abs(lp - prev_low) / prev_low > 0.03:
        return PatternResult("NONE", False, 0)

    point_x = prev_low
    swing_highs = df.dropna(subset=["swing_high"]).tail(4)
    if len(swing_highs) == 0:
        return PatternResult("NONE", False, 0)

    point_y_candidates = swing_highs[swing_highs.index > swing_lows.index[-2]]
    if len(point_y_candidates) == 0:
        return PatternResult("NONE", False, 0)

    point_y = point_y_candidates["swing_high"].max()
    midpoint = point_x + (point_y - point_x) * 0.5

    recent_highs = df["high"].tail(10)
    flush_started_above_mid = recent_highs.max() > midpoint

    if not flush_started_above_mid:
        return PatternResult("NONE", False, 0)

    last_bars = df.tail(4)
    exe_found = False
    for _, bar in last_bars.iterrows():
        is_bullish = bar["close"] > bar["open"]
        bar_range = bar["high"] - bar["low"]
        avg_range = df["high"].tail(20).mean() - df["low"].tail(20).mean()
        is_large = bar_range > avg_range * 1.2
        closes_above_lp = bar["close"] >= lp
        if is_bullish and is_large and closes_above_lp:
            exe_found = True
            break

    if not exe_found:
        return PatternResult("NONE", False, 0, description="DR2 forming, awaiting bullish EXE bar")

    current = df.iloc[-1]["close"]
    stop = lp * 0.99
    risk = abs(current - stop)
    target = current + risk * 2.0

    return PatternResult(
        pattern="DR2", confirmed=True, confidence=75,
        trigger_level=round(lp, 2), stop_level=round(stop, 2),
        target_level=round(target, 2), rr_ratio=2.0,
        description=f"DR2 double bottom reversal at {lp:.2f}. "
                    f"Majority flush down confirmed. Bullish EXE formed. LONG signal.",
    )


def detect_dc1(df: pd.DataFrame, flow: FlowResult) -> PatternResult:
    if flow.state != "negative_flow":
        return PatternResult("NONE", False, 0)

    current = df.iloc[-1]
    close = current["close"]
    sma20 = current.get("sma_20")
    sma50 = current.get("sma_50")

    if pd.isna(sma20) or pd.isna(sma50):
        return PatternResult("NONE", False, 0)

    sma_zone_top = max(sma20, sma50) * 1.02
    sma_zone_bottom = min(sma20, sma50) * 0.98
    in_rally_zone = sma_zone_bottom <= close <= sma_zone_top

    recent_high = df["high"].tail(5).max()
    rejected_from_zone = (recent_high >= sma_zone_bottom) and (close < sma20)

    if not (in_rally_zone or rejected_from_zone):
        return PatternResult("NONE", False, 0)

    trigger = flow.last_swing_low
    stop = flow.last_swing_high
    if trigger is None or stop is None:
        return PatternResult("NONE", False, 0)

    risk = abs(stop - close)
    if risk <= 0:
        return PatternResult("NONE", False, 0)

    target = close - risk * 2.0
    confirmed = close < trigger

    return PatternResult(
        pattern="DC1", confirmed=confirmed,
        confidence=65 if confirmed else 50,
        trigger_level=round(trigger, 2), stop_level=round(stop, 2),
        target_level=round(target, 2), rr_ratio=2.0,
        description=f"DC1 continuation short. Rally to SMA resistance. "
                    f"Trigger: break below {trigger:.2f}.",
    )


# ═══════════════════════════════════════════════════════════
#  ROTATION SEGMENTS
# ═══════════════════════════════════════════════════════════

def classify_rotation_segment(momentum: MomentumResult, flow: FlowResult) -> str:
    if momentum.direction == "up":
        if momentum.is_flush:
            return "B"
        elif momentum.is_wave:
            return "A"
    elif momentum.direction == "down":
        if momentum.is_flush:
            return "D"
        elif momentum.is_wave:
            return "C"
    return "A" if flow.state == "positive_flow" else "C"


# ═══════════════════════════════════════════════════════════
#  MICRO SCORE
# ═══════════════════════════════════════════════════════════

def compute_micro_score(
    pattern: PatternResult, flow: FlowResult,
    momentum: MomentumResult, segment: str,
) -> float:
    score = 0.0

    if pattern.pattern != "NONE":
        score += pattern.confidence * 0.4
    else:
        score += 20

    if pattern.pattern in ("UC1", "UC2", "UR1") and flow.state == "positive_flow":
        score += 20 + min(flow.hh_hl_count * 2.5, 5)
    elif pattern.pattern in ("DC1", "DC2", "DR1") and flow.state == "negative_flow":
        score += 20 + min(flow.lh_ll_count * 2.5, 5)
    elif pattern.pattern in ("UR2",) and flow.state == "positive_flow":
        score += 15
    elif pattern.pattern in ("DR2",) and flow.state == "negative_flow":
        score += 15
    else:
        score += 10

    if pattern.pattern in ("UC1", "DC1"):
        if momentum.is_wave:
            score += 20
        elif not momentum.is_flush:
            score += 15
        else:
            score += 5
    elif pattern.pattern in ("UR2", "DR2"):
        if momentum.is_flush:
            score += 20
        else:
            score += 10

    if pattern.pattern in ("UC1",) and segment == "A":
        score += 15
    elif pattern.pattern in ("UR2",) and segment == "B":
        score += 15
    elif pattern.pattern in ("DC1",) and segment == "C":
        score += 15
    elif pattern.pattern in ("DR2",) and segment == "D":
        score += 15
    else:
        score += 5

    return min(round(score, 1), 100.0)


# ═══════════════════════════════════════════════════════════
#  IV RANK + EARNINGS
# ═══════════════════════════════════════════════════════════

def _fetch_iv_and_earnings(ticker: str) -> tuple[float | None, int | None]:
    try:
        stock = yf.Ticker(ticker)

        days_to_earn = None
        try:
            cal = stock.calendar
            if cal is not None and not (hasattr(cal, 'empty') and cal.empty):
                if hasattr(cal, 'iloc'):
                    earn_date = cal.iloc[0, 0] if cal.shape[1] > 0 else None
                elif isinstance(cal, dict):
                    earn_date = cal.get("Earnings Date", [None])[0]
                else:
                    earn_date = None
                if earn_date is not None:
                    if hasattr(earn_date, 'date'):
                        earn_date = earn_date.date()
                    days_to_earn = (earn_date - date.today()).days
                    if days_to_earn < 0:
                        days_to_earn = None
        except Exception:
            pass

        iv_rank = None
        try:
            expirations = stock.options
            if expirations:
                chain = stock.option_chain(expirations[0])
                if not chain.calls.empty:
                    info = stock.info
                    price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
                    if price > 0:
                        calls = chain.calls.copy()
                        calls["dist"] = (calls["strike"] - price).abs()
                        atm = calls.nsmallest(1, "dist")
                        current_iv = float(atm["impliedVolatility"].iloc[0])

                        hist = stock.history(period="1y")
                        if len(hist) > 30:
                            returns = hist["Close"].pct_change().dropna()
                            rv_max = returns.rolling(20).std().max() * (252 ** 0.5)
                            rv_min = returns.rolling(20).std().min() * (252 ** 0.5)
                            if rv_max > rv_min:
                                iv_rank = ((current_iv - rv_min) / (rv_max - rv_min)) * 100
                                iv_rank = max(0, min(100, iv_rank))
        except Exception:
            pass

        return iv_rank, days_to_earn
    except Exception:
        return None, None


# ═══════════════════════════════════════════════════════════
#  FULL PAM ANALYSIS
# ═══════════════════════════════════════════════════════════

@dataclass
class FullPAMResult:
    ticker: str
    dt: date
    flow: FlowResult
    momentum: MomentumResult
    pattern: PatternResult
    rotation_segment: str
    micro_score: float
    current_price: float
    sma_50: float | None
    atr_14: float | None
    rsi_14: float | None
    volume_ratio: float | None
    iv_rank: float | None = None
    days_to_earnings: int | None = None
    near_earnings: bool = False

    def to_context_string(self) -> str:
        iv_str = f"{self.iv_rank:.0f}%" if self.iv_rank is not None else "N/A"
        earn_str = f"{self.days_to_earnings}d" if self.days_to_earnings is not None else "N/A"
        return (
            f"== PAM ENGINE OUTPUT: {self.ticker} ({self.dt}) ==\n"
            f"Price: ${self.current_price:.2f} | SMA50: ${self.sma_50:.2f} | "
            f"ATR14: ${self.atr_14:.2f} | RSI14: {self.rsi_14:.1f}\n"
            f"IV Rank: {iv_str} | Days to Earnings: {earn_str} "
            f"{'!! NEAR EARNINGS' if self.near_earnings else ''}\n"
            f"Flow: {self.flow.state} (HH/HL: {self.flow.hh_hl_count}, LH/LL: {self.flow.lh_ll_count})\n"
            f"Momentum: angle={self.momentum.angle_degrees} deg "
            f"{'FLUSH' if self.momentum.is_flush else 'WAVE' if self.momentum.is_wave else 'neutral'} "
            f"{self.momentum.direction} | Flush bars: {self.momentum.flush_bar_count}\n"
            f"Rotation Segment: {self.rotation_segment}\n"
            f"Pattern: {self.pattern.pattern} | Confirmed: {self.pattern.confirmed} | "
            f"Confidence: {self.pattern.confidence:.0f}%\n"
            f"  Trigger: {self.pattern.trigger_level} | Stop: {self.pattern.stop_level} | "
            f"Target: {self.pattern.target_level} | R:R: {self.pattern.rr_ratio}\n"
            f"  {self.pattern.description}\n"
            f"MICRO SCORE: {self.micro_score:.1f}/100\n"
            f"Volume Ratio (vs 20d avg): {self.volume_ratio:.2f}x\n"
        )


def run_full_pam(ticker: str) -> FullPAMResult:
    df = download_ohlcv(ticker)
    if df.empty or len(df) < 60:
        raise ValueError(f"Insufficient data for {ticker}")

    flow = compute_flow(df)
    momentum = compute_momentum(df)
    segment = classify_rotation_segment(momentum, flow)

    patterns = [
        detect_uc1(df, flow),
        detect_ur2(df, flow, momentum),
        detect_dr2(df, flow, momentum),
        detect_dc1(df, flow),
    ]
    best = max(patterns, key=lambda p: p.confidence)
    if best.pattern == "NONE":
        best = PatternResult("NONE", False, 0, description="No clear PAM setup detected")

    micro = compute_micro_score(best, flow, momentum, segment)
    iv_rank, days_to_earnings = _fetch_iv_and_earnings(ticker)
    near_earnings = days_to_earnings is not None and days_to_earnings <= 14

    current = df.iloc[-1]
    avg_vol = df["volume"].tail(20).mean()
    vol_ratio = current["volume"] / avg_vol if avg_vol > 0 else 1.0

    return FullPAMResult(
        ticker=ticker,
        dt=current["dt"].date() if hasattr(current["dt"], "date") else date.today(),
        flow=flow, momentum=momentum, pattern=best,
        rotation_segment=segment, micro_score=micro,
        current_price=round(float(current["close"]), 2),
        sma_50=round(float(current["sma_50"]), 2) if pd.notna(current["sma_50"]) else None,
        atr_14=round(float(current["atr_14"]), 2) if pd.notna(current["atr_14"]) else None,
        rsi_14=round(float(current["rsi_14"]), 1) if pd.notna(current["rsi_14"]) else None,
        volume_ratio=round(vol_ratio, 2),
        iv_rank=round(iv_rank, 1) if iv_rank is not None else None,
        days_to_earnings=days_to_earnings,
        near_earnings=near_earnings,
    )
