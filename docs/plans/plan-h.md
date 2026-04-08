# Plan H — Day Trading (H9 Race v3)

|  |  |
| --- | --- |
| **Regime** | Choppy only (SPY 20d return -2% to +2%) |
| **Symbols** | SPY, QQQ |
| **Instrument** | Options, 0.42 delta, 3-5 DTE |
| **Timeframe** | 5-min |
| **Risk** | $4,200 = 6% of $70K (throttles to 2% after 3 consecutive losses) |
| **Hold Period** | Intraday, entries 09:40-11:00 ET, force close 11:28 ET |
| **Backtest Edge** | 1,092 trades, 48.1% WR, PF 1.34, +$184K |

Plan H is the intraday workhorse for sideways, messy markets. It uses two signal types — **pullback** and **breakout** — in a race condition. The system checks for pullback first on every bar, and only considers breakout if pullback didn't fire. Max 1 trade per symbol per day.

If you are new to the terms on this page:

- **EMA21** is a 21-period Exponential Moving Average, used here as the main pullback/stop line.
- **VWAP** is the Volume-Weighted Average Price, a common intraday reference for where most trading has happened.
- **ATR** is Average True Range, used to normalize movement.
- **Delta** and **DTE** describe the option contract. See the [Glossary](../glossary/index.md).

## Signal Types

### Pullback (primary)

Catches price snapping back from a brief touch of EMA21 within a trend. Fires across the full **09:40-11:00 ET** window.

The idea: the market is already moving in one direction, briefly pulls back toward EMA21, and then starts pushing again. Like catching a breath inside a move, not trying to predict a reversal.

All must be true on the same 5-min bar:

### Breakout (supplemental)

Catches strong early-morning trends that never pull back to EMA21. Fires only in a restricted **09:40-10:10 ET** window. Requires a clean EMA stack instead of a pullback touch.

### The race condition

On every 5-min bar, the system checks pullback first. Only if pullback doesn't fire does it check breakout (and only before 10:10). Once either signal fires and enters a trade, that symbol is done for the day.

The 10:10 cutoff for breakouts exists because late-morning breakout entries historically mean-reverted — they fired after price had already moved 1+ ATR in low-vol choppy conditions. Cutting the window at 10:10 alone flipped 2024 from -\(9.8K to +\)3.9K.

## Entry Filters

These filters apply to both signal types:

1. **Race limit:** Max 1 signal per symbol per day (pullback or breakout, whichever fires first)
2. **EMA5-10 spread:** |EMA5 - EMA10| / ATR >= 0.25 (trend must be fanning)
3. **Move from open:** Directional move from day open / ATR >= 1.0
4. **Min stop distance:** |entry - EMA21| >= $0.10 (avoids micro-stop entries)
5. **Gap delay:** If |open - prior\_close| / prior\_close >= 0.5%, delay entries to 10:00 ET
6. **Macro skip:** No entries on FOMC, CPI, NFP days
7. **Regime gate:** Only trade choppy regime (SPY 20d return -2% to +2%)

The **gap delay** exists because the opening minutes can be distorted after a big overnight move.

## Sizing

Plan H sizes from the distance to EMA21. If price is farther from the stop line, position size shrinks automatically.

```
current_risk  = 0.02 if consecutive_losses >= 3 else 0.06
risk_dollars  = equity * current_risk
stop_dist     = max(|entry - EMA21|, 0.10)
risk_per_ct   = stop_dist * 0.42 * 100
contracts     = min(floor(risk_dollars / risk_per_ct), 50)
entry_premium = max(ATR14 * 0.42 * 0.5, 0.50)
```

The throttle from 6% to 2% after 3 consecutive losses persists across days and symbols. It resets on the next win.

## Exit Rules (priority order)

The exit structure cuts failed trades quickly and protects profits once the option starts moving.

1. **Force close (11:28 ET):** Exit all positions — no exceptions
2. **EMA5 trailing stop:** Once trailing is activated, exit if close crosses EMA5 against direction
3. **EMA21 initial stop:** Before trailing activates, exit if close crosses EMA21 against direction
4. **Profit trail switch:** Option P&L >= +15% activates EMA5 trail (tighter stop, locks in gains)

Entry executes on the **next bar's open** after signal fires (not the signal bar itself).

!!! warning "AM Only"
    PM session was a net -$14K over 10 years across all variants. Never trade PM.

## Pyramiding

**Pyramiding** means adding to a trade only after it is already working, rather than betting full size immediately.

- **Tier 2 (+30% option P&L):** Add floor(base \* 0.5) contracts (max 25). Activates EMA5 trail.
- **Tier 3 (+100% option P&L):** Requires T2 fired. Add floor(base \* 0.25) contracts (max 12).

## Backtest Results (2016-2026, choppy, $70K flat)

These numbers are the reason the regime filter matters so much. This plan works best when the market is messy, not when it is in a clean sustained bull run.

### Race v3 (current live config)

| Metric | Value |
| --- | --- |
| Trades | 1,092 |
| Win Rate | 48.1% |
| Profit Factor | 1.34 |
| Total P&L | +$184,476 |
| Avg Trade | +$169 |
| Positive Years | 8/11 |
| Modern (2019-2026) | +$231,940 |
| Early (2016-2018) | -$47,465 |

### Year-by-year

| Year | Pullback | PB P&L | Breakout | BO P&L | Total |  |
| --- | --- | --- | --- | --- | --- | --- |
| 2016 | 78 | -$8,590 | 59 | -$7,451 | -$16,041 |  |
| 2017 | 149 | -$26,333 | 47 | -$2,881 | -$29,214 |  |
| 2018 | 82 | -$11,066 | 34 | +$8,857 | -$2,209 |  |
| 2019 | 42 | -$4,278 | 35 | +$13,846 | +$9,568 |  |
| 2020 | 20 | +$10,253 | 27 | +$796 | +$11,048 |  |
| 2021 | 74 | -$16,590 | 45 | +$30,263 | +$13,673 |  |
| 2022 | 20 | +$19,686 | 26 | -$11,611 | +$8,074 |  |
| 2023 | 54 | -$3,461 | 39 | +$39,743 | +$36,283 |  |
| 2024 | 57 | +$6,263 | 33 | -$2,356 | +$3,907 |  |
| 2025 | 81 | +$26,215 | 38 | +$26,094 | +$52,309 |  |
| 2026 | 34 | +$75,401 | 18 | +$21,678 | +$97,079 |  |

### Signal type breakdown

| Signal | Trades | P&L | Win Rate |
| --- | --- | --- | --- |
| Pullback | 691 (63%) | +$67,498 | 41.4% |
| Breakout | 401 (37%) | +$116,977 | 59.6% |

Pullback has lower WR but asymmetric payoff — wins are nearly 2x losses. Breakout has higher WR and accounts for 63% of total P&L despite being only 37% of trades.

See the full [Backtest](plan-h-backtest.md) for an interactive equity curve and trade-by-trade log.

### Monte Carlo simulation (10,000 runs)

Bootstrap resampling of all 1,092 trades with replacement to estimate the distribution of outcomes over the same number of trades.

| Percentile | P&L | Final Equity |
| --- | --- | --- |
| P10 (bear case) | +$105K | $175K |
| P25 | +$142K | $212K |
| P50 (median) | +$183K | $253K |
| P75 | +$225K | $295K |
| P90 (bull case) | +$266K | $336K |

| Risk Metric | Value |
| --- | --- |
| Probability profitable | 99.9% |
| Probability double account | 97.1% |
| Probability of ruin (<50%) | 2.1% |
| Mean max drawdown | -24.9% |
| Annualized Sharpe | 0.93 |

### Key discoveries

- Early years (2016-2018) are net negative. The strategy's edge is modern — post-2019 market microstructure with tighter spreads and faster reversion. This is not a concern for live trading.
- Breakout accounts for 63% of total P&L despite being only 37% of trades — the restricted 10:10 window filters out weak entries effectively.
- The 2.1% ruin probability comes from extreme drawdown sequences in the bootstrap — the actual backtest never approached 50% drawdown.

## Indicators

All computed on 5-min bars resampled from 1-min:

- **EMA5, EMA10, EMA21** — span-based, adjust=False
- **ATR14** — 14-period SMA of true range
- **VWAP** — full-day, anchored 09:30 ET
- **VWAP slope** — 2-bar diff on 5-min VWAP (10-min momentum)
