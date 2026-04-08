# Combined Backtest Results

This page pulls the system-level scorecard into one place. It matters because the trading plans are meant to work together across different market environments, not as isolated experiments.

All backtests: 2016-2026, $70K flat sizing, net of costs (2% slippage + $1.30/contract).

If you're new to trading metrics, two terms matter most here:

- **Win rate** is the percentage of trades that made money.
- **Profit factor (PF)** is gross profit divided by gross loss. A PF above 1.0 means the strategy made more than it lost; the further above 1.0, the better. See the [Glossary](../glossary/index.md) for full definitions.

## Headline Numbers

Think of this table as the system's top-line business report: what each plan contributed and what the combined portfolio looked like.

| Plan | P&L | Notes |
| --- | --- | --- |
| Plan H (choppy) | +$75,717 | SPY+QQQ, 1,109 trades |
| Plan C (crash) | +$24,760 | Deterministic, SPY only |
| Plan M (MC mean) | +$453,918 | 7,020 trades, PF 1.85 |
| Plan Alpha | +$18,411 | 908 trades, PF 2.68 ($1K flat) |
| **Combined** | **+$554K → $624K** | P10: $293K, P90: $951K |

`P10` and `P90` are percentile outcomes from simulation. In plain English: a rough "bad but plausible" case and "good but plausible" case.

## Plan H Detailed

Plan H is the intraday plan for choppy markets, where prices whip around instead of trending smoothly. The combined row is the key one because the strategy trades both SPY and QQQ.

| Metric | SPY | QQQ | Combined |
| --- | --- | --- | --- |
| Trades | 579 | 530 | 1,109 |
| Win Rate | 49.1% | 47.2% | 48.2% |
| Profit Factor | 1.572 | 1.430 | 1.504 |
| Gross P&L | +$141K | +$97K | +$239K |
| Net-of-cost P&L | — | — | +$149K |

Independently validated by 3 agents who derived the strategy from source code with zero shared code. All produced profitable PF (1.19-1.50).

## Plan M Monte Carlo

A **Monte Carlo** test reshuffles or resamples trade outcomes many times to estimate how a strategy might behave across different sequences of wins and losses. It helps answer: "Even if the backtest edge is real, how ugly could the ride get?"

1,000 simulations, rate=0.375/bull-day:

| Metric | Value |
| --- | --- |
| Avg return/trade | 1.66% |
| Win Rate | 54.17% |
| Profit Factor | 1.85 |
| Avg max DD | -24.4% |
| Worst-case DD | -49.5% |

`DD` means drawdown, or the percentage drop from the account's high-water mark to its next low.

## Plan Alpha Episode Breakdown

Plan Alpha only trades during sharp market stress, so it makes more sense to judge it by **episodes** than by a constant daily rhythm. An episode is a cluster of qualifying crash signals within 7 calendar days.

| Pattern | WR | PF | Frequency |
| --- | --- | --- | --- |
| Sharp V-bounce (1-5d) | 90%+ | >11 | Best |
| Extended recovery | 50-60% | <2 | Middle |
| Grinding decline (15+d) | <50% | Loss | Worst |

24 episodes over 10 years. Active 5.9% of the time. Fires every ~4.6 months.

## Cost Model

These assumptions matter because options backtests can look unrealistically great if trading costs are ignored.

- **Slippage:** 2% round-trip (winners: -2%, losers: +2%)
- **Fees:** $1.30 per contract per tier
- **P&L per tier:** `(move * delta * 100 * contracts) * slip_factor - ($1.30 * contracts)`

**Delta** is an option's directional sensitivity, often used as a rough proxy for how much the option behaves like the stock. See the [Glossary](../glossary/index.md) for the fuller options definitions.
