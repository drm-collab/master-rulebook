# Plan C — Crash Regime EMA Stack Shorts

|  |  |
| --- | --- |
| **Regime** | Crash (SPY 20d < -4% AND realized volatility >= 15%) |
| **Symbols** | SPY only |
| **Instrument** | Options — puts |
| **Timeframe** | 2-min bars; entry 10:30 ET (single entry per day) |
| **Risk** | 5% = $3,500 |
| **Hold Period** | Intraday, force close 15:50 ET |
| **Backtest Edge** | 54.3% WR, PF 1.47, +$24,760 |

Plan C is the system's direct short bet on a violent market selloff. The "why" is straightforward: when the entire market is breaking down fast and volatility is high, the index itself can be the cleanest thing to short.

If you are new to the language here:

- **EMA** means Exponential Moving Average, a faster-reacting trend line.
- **Realized volatility** measures how much the market has actually been moving.
- **SPY** is the S&P 500 ETF, used here as the market proxy.

See the [Glossary](../glossary/index.md) for the full definitions.

## When It Fires

Plan C activates when the market is in freefall with high volatility. If SPY 20d < -4% but RV < 15%, that's a slow grind — sit out, no edge.

That distinction matters. A fast, emotional selloff creates the kind of momentum this plan wants. A slow drip lower usually does not.

## Entry — EMA Stack Bearish

The plan is trying to confirm that short-term, medium-term, and long-term trend measures are all pointing down together. Think of it as requiring multiple layers of downward pressure to line up before taking the trade.

All conditions on completed 2-min bar at or after 10:30 ET:

1. Bearish EMA stack: EMA5 < EMA10 < EMA21 < EMA50
2. Price below EMA200 (macro downtrend confirmed)
3. Close below EMA21

Max 1 signal per day in crash regime.

## Sizing

The size is based on how far price is from EMA50, which acts as the initial stop line.

```
risk_pct  = 5%
stop_dist = |entry_price - EMA50|
contracts = floor((equity * 0.05) / (stop_dist * 0.43 * 100))
```

## Stop Logic

The stop starts wider, then tightens once the trade moves in the right direction.

- **Initial stop:** EMA50
- **Trail activation:** Price moves below entry (first profitable bar) → stop moves to EMA21

## Backtest Results (2016-2026, $70K flat)

Total P&L: **+$108K** (deterministic, no Monte Carlo needed)

!!! note "Never Live Tested"
    Plan C has never run in a live crash regime. First real crash will be the first live test.

## Strategic Fit

Plan C is the short side of the crash playbook. Plan Alpha is the long side (buying oversold individual stocks with calls). Together they form a natural hedge: short the index + long the strongest individual bounces.
