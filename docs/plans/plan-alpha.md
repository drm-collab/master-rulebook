# Plan Alpha — Crash/Correction Mean Reversion

|  |  |
| --- | --- |
| **Regime** | SPY 20d return <= -5% (crash/correction specialist) |
| **Symbols** | S&P 500 |
| **Instrument** | 0.30 delta calls on oversold S&P 500 stocks |
| **Timeframe** | Daily |
| **Risk** | $3,500 options / $1K shares |
| **Hold Period** | 4-5 days (hybrid exit) |
| **Backtest Edge** | 75.1% WR, PF 2.68, highest edge strategy in the system |

Plan Alpha is the long side of the crash playbook. It buys fear.

The idea behind this plan is simple: during broad market panics, even strong stocks can get sold too hard for a few days. Plan Alpha tries to buy those stretched-down names while they are still above their long-term trend, then exit once the rebound shows up or fails to show up quickly.

If you are new to the terms on this page:

- **RSI** is the Relative Strength Index, a momentum gauge. Think of it like a rubber band: the lower it goes, the more stretched the recent selling has been.
- **SMA200** is the 200-day Simple Moving Average, a long-term trend line.
- **PF** means profit factor, or gross profit divided by gross loss.
- **Delta** and **DTE** are option-contract settings. See the [Glossary](../glossary/index.md) for full definitions.

## Signal Detection

The "why" comes first: Plan Alpha is looking for stocks that are temporarily beaten down during a market-level selloff, but not actually broken. The conditions below are how the system measures "beaten down, but still intact."

All must be true on the same trading day:

1. **RSI(5) < 15** — Wilder RSI, EWM (com=4, min\_periods=5)
2. **Close > SMA200 \* 1.01** — stock in uptrend AND at least 1% above SMA200
3. **S&P 500 member** — point-in-time constituent universe
4. **Not Energy or Materials sector** — excluded via [BQS](../glossary/index.md) precompute sector data
5. **Not FOMC/CPI/NFP day** — macro days are PF 1.30 vs 1.65 non-macro

Condition 1 says the stock has been hit hard in the last 5 days. Condition 2 says the stock has not yet lost its long-term structure. Conditions 3-5 keep the universe and trading context clean enough for the historical edge to matter.

!!! info "SMA200 Distance Filter"
    Stocks 0-1% above SMA200 have 64.5% WR vs 75.8% for stocks 1%+ above. They're teetering on the edge of losing support. The 1% filter improves PF from 2.37 to 2.58 while shedding only 15% of trades. See [Glossary](../glossary/index.md#sma200-distance-buckets-plan-alpha) for the full distance analysis.

## Episode Logic

This plan does not treat every crash day as equally good. The best trades come from the first burst of panic, not from a market that just keeps grinding lower.

- **Episode:** Consecutive crash signals within 7 calendar days
- **Entry window:** First 2 signal days per episode ONLY
- Sharp 1-2 day panics are the best (90%+ WR)
- If still firing signals after day 2, market is trending down, not dipping

!!! warning "Entry Window is Critical"
    Day 3+ signals are dramatically weaker. The edge is in the initial panic, not the grind.

## Options Specification

The contract choice reflects the job this strategy is doing: buy rebound exposure cheaply across several names without paying for ultra-short expiry.

| Parameter | Value |
| --- | --- |
| Type | Call (long) |
| Delta Target | 0.30 (range: 0.20-0.40) |
| DTE | 30-120 days |
| Spread | <= 15% bid-ask |
| OI Minimum | 5x estimated volume |
| Sizing | $3,500 risk budget per trade |

## Exit Rules (Hybrid)

The exit logic asks one question: did the bounce work quickly enough? If yes, take it. If not, get out by the fifth day.

1. **Catastrophic stop:** Close < SMA200 \* 0.93 → exit immediately (~1.8% of trades)
2. **Green at day 4:** If cumulative return > 0 at day 4 close → exit (locks in momentum)
3. **Day 5 mandatory:** Exit at day 5 close regardless

No daily stop-loss. Position can go negative intraday; exits fire only at close.

!!! info "Why Day 4 Hybrid?"
    42% of day-4 winners give back profits by day 5. Day-4 late bloomers (12% of winners) contribute only 4% of total winner profits. Exit early when green.

## Backtest Results (2016-2026, first 2 days per episode)

These are the numbers that justify waiting so patiently for this setup.

| Metric | Value |
| --- | --- |
| Trades | 908 |
| Win Rate | 75.1% |
| Profit Factor | 2.68 |
| Total P&L | \(18,411 (\)1K flat sizing) |
| 0.30Δ Options PF | 3.73 |
| Avg Winner | +96% |
| Avg Loser | -47% |
| Monte Carlo Ruin | 0% |

24 episodes over 10 years. Fires every ~4.6 months on average. Active 5.9% of the time.

## Episode Patterns

This breakdown explains why the entry window is so strict. Not all crashes bounce the same way.

- **Sharp V-bounce** (1-5 days, SPY +1.5%+): WR 90%+, PF >11
- **Extended recovery** (multi-week, choppy): WR 50-60%, PF <2
- **Grinding decline** (15+ days): WR <50%, often losses

**Losing episodes (3 of 24):** Jan 2016, Jun 2022, Mar 2023 — all sustained downtrends, not V-shaped recoveries.

## Execution Pipeline

The screener runs as a single end-to-end script (`plan_alpha_screener.py`) at 1:30 PM PT:

1. **Regime check** — SPY 20d return via Tradier. Gate: <= -5%.
2. **Macro skip** — FOMC/CPI/NFP calendar check.
3. **Bulk scan** — yfinance download of full S&P 500, filter by RSI(5)/SMA200/sector.
4. **Options lookup** — Tradier chains, walk strikes/expirations for 0.30Δ with liquidity.
5. **Alpaca paper execution** — options for liquid names (at ask), shares ($1K each) for illiquid names.
6. **Telegram alert** — total hits split by options vs shares.
7. **Tracker init** — auto-loads positions into `plan_alpha_positions_tracker.py`.

**Warmup screen** at 14:45 ET (11:45 AM PT) gives an early look at developing signals before the main run.

**Position monitoring** runs daily at 1:45 PM PT via `plan_alpha_positions_tracker.py`. If any position drops within 3% of the catastrophic stop, the intraday monitor activates — polling every 5 minutes and executing emergency exits if SMA200 \* 0.93 is breached.

## Regime Gate: Return vs SMA

This comparison answers a design question: should the crash gate be based on a 20-day return or distance from a moving average? The return gate won because it catches the fast panic phase earlier.

Backtested both approaches (2016-2026):

| Gate | WR | PF | Day-1 WR | Episodes |
| --- | --- | --- | --- | --- |
| **20d Return** (current) | 76.0% | 2.89 | 79.0% | 24 |
| 20d SMA Distance | 72.7% | 2.53 | 60.8% | 15 |

The SMA gate triggers late — it misses the sharp panics where the best edge lives. Return gate catches 13 episodes the SMA gate misses entirely.
