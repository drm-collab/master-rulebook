# Exits & Stops

Entries get the attention, but exits decide whether a good idea becomes a real profit or a controlled loss. This page explains how each plan gets out of trades and why those exit rules exist.

If you're new to the terms: **EMA** means Exponential Moving Average, a moving average that reacts faster to recent price changes than a simple average. **ATR** means Average True Range, a common way to measure how much a stock typically moves. Full definitions are in the [Glossary](../glossary/index.md).

## Plan H Exits (Priority Order)

Plan H is an intraday options strategy, so the exits are designed to do two jobs: protect against a fast reversal and force the trade to end before the weaker afternoon session.

1. **Session close (11:28 ET):** Exit all. No PM trading.
2. **EMA5 trailing stop:** If trailing activated, close crosses EMA5 against direction
3. **EMA21 initial stop:** If NOT trailing, close crosses EMA21 against direction
4. **Profit trail switch:** Option P&L >= +15% activates EMA5 trail (no exit, just switches mode)

### Trail Activation

This is the handoff from "give the trade room" to "protect what the trade has earned."

Switches from EMA21 stop to EMA5 trail when EITHER:
- Option P&L reaches +15%, OR
- Tier 2 pyramid fires (whichever first)

## Plan M Exits (Any One Triggers Close)

Plan M is a swing-trading plan, so its exit logic mixes signal reversal, trend damage, old resistance, scheduled event risk, and hard stops.

1. **OVTLYR sell signal** — the signal reversed
2. **10/20 bearish cross** — EMA10 < EMA20
3. **OVTLYR block hit (120+ days)** — old OB = strong resistance
4. **Earnings** — close BEFORE. No exceptions.
5. **Gap & Crap** — 5% gap, close below gap candle low within 3 candles
6. **2 ATR hard stop** — from entry, no exceptions
7. **3 ATR emergency** — if price TOUCHES 3 ATR against you intraday, close IMMEDIATELY

An **earnings** release can gap a stock sharply overnight, which is why this plan refuses to hold through it. A **gap** is the jump between one candle's close and the next candle's open.

### Gap & Crap Rules

This rule is looking for a bullish-looking open that quickly fails, which is often a sign that the move was a trap rather than real strength.

- Gap = difference between one candle's CLOSE and next candle's OPEN
- At least a 2-day pattern with a 5% up move
- Line on the BOTTOM of the gap candle's wick (the low)
- If price closes below that point within 3 candles → close
- If not → follow other exit signals

## Plan C Exits

Plan C is the crash short plan, so it starts with a wider leash and then tightens once the trade proves itself.

- **Initial stop:** EMA50
- **Trail:** After first profitable bar, stop moves to EMA21
- **Force close:** 15:50 ET

## Plan Alpha Exits

Plan Alpha buys oversold stocks during market stress, so the exits are based on whether the bounce shows up quickly enough.

1. **Catastrophic stop:** Close < SMA200 \* 0.93 (any day 1-5)
2. **Green at day 4:** Cumulative return > 0 → exit
3. **Day 5 mandatory:** Exit at close regardless

**SMA200** means the 200-day Simple Moving Average, a long-term trend line. Falling too far below it means the stock may not be bouncing at all anymore.

!!! danger "Exit Authority"
    Stop and trail logic lives in ONE script only. Never split exit authority across multiple scripts. This is a coding rule enforced system-wide.
