# Trading Plans Overview

This page is the map of the whole system. Master Rulebook does not use one strategy all the time; it chooses a plan based on the current **regime**, which is just a structured way of saying "what kind of market are we in right now?"

If terms like **delta**, **DTE**, **profit factor**, or **regime** are unfamiliar, see the [Glossary](../glossary/index.md).

The system has a plan for every market condition. No guessing, no hoping.

## Regime → Plan Routing

The routing logic comes first because the "why" is simple: the same trading setup behaves very differently in a bull market, a sideways market, and a crash. Master Rulebook tries to trade each environment with the tool built for it.

```
Bull (>+2%)           → Plan M (swing trades, OVTLYR signals)
Choppy (-2% to +2%)   → Plan H (day trading, H9 EMA21 pullback)
Crash (<-4%) + RV≥15% → Plan C (EMA stack shorts, SPY only)
Crash + SPY 20d≤-5%   → Plan Alpha (mean reversion calls, S&P 500 stocks)
Crash + RV<15%         → Sit out (slow grind, no edge)
Transition (-4% to -2%)→ Sit out (recovery risk)
Nothing set up         → SICADFU (park in SGOV)
```

**RV** means realized volatility, which tells the system whether a selloff is violent enough for the crash short plan to have an edge.

## Plan Comparison

This table is the quickest way to understand how different the plans really are: intraday versus multi-day, aggressive options versus defensive ETF shares, and high-frequency versus rare high-quality setups.

| Plan | Timeframe | Instrument | Risk | Avg Hold | Backtest PF |
| --- | --- | --- | --- | --- | --- |
| **H** | 5-min intraday | 0.43Δ options | 6% | 1-2 hours | 1.50 |
| **M** | Daily swing | 0.80Δ options | 5% | 17.5 days | 1.85 |
| **C** | 2-min intraday | 0.43Δ puts | 5% | 1 day | N/A |
| **Alpha** | Daily | 0.30Δ calls | $3,500 flat | 4-5 days | 2.68 |
| **ETF** | Daily swing | 3x ETF shares | All cash | Variable | N/A |

**Delta** is the option's directional sensitivity. Higher delta options behave more like the stock. Lower delta options are cheaper but need bigger stock moves to pay off.

## When Each Plan Fires

The trigger timing matters because each plan looks at a different market rhythm.

- **Plan H:** 09:40-11:00 ET, AM session only. 2 signals per day max.
- **Plan M:** Screener runs daily 5:55/6:05 PT. Signals valid 5 trading days.
- **Plan C:** Single entry at 10:30 ET during crash regime.
- **Plan Alpha:** Screener runs 1:30 PM PT. First 2 signal days per crash episode.
- **Plan ETF:** Enter anytime conditions are active, exit on signal reversal.
