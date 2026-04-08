# Glossary

Quick reference for acronyms, metrics, and terms used throughout the system. This is the page the rest of the wiki points back to whenever a concept needs a deeper definition.

If a page gives a short plain-English explanation and you want the exact technical definition, come back here.

---

## Metrics & Scores

| Term | Full Name | Definition |
| --- | --- | --- |
| **BQS** | Bounce Quality Score | Precomputed 0-1 score per ticker combining historical bounce rate, magnitude, and consistency. Higher = better mean reversion candidate. Used as primary sort key in Plan Alpha. Refreshed weekly (Sunday 8 PM PT). |
| **PF** | Profit Factor | Gross profit / gross loss. PF > 1.5 = edge worth trading. PF > 2.0 = strong edge. |
| **WR** | Win Rate | Percentage of trades that are profitable. Context-dependent — high WR with thin PF can still lose. |
| **RSI** | Relative Strength Index | Wilder's RSI using EWM (com=period-1). System uses RSI(5) for Plan Alpha and RSI(14) elsewhere. |
| **SMA** | Simple Moving Average | Arithmetic mean of last N closes. SMA200 = 200-day SMA, primary trend filter. |
| **EMA** | Exponential Moving Average | Weighted moving average favoring recent prices. EMA5/9/21/50 used in Plan H and Plan C. |
| **RV** | Realized Volatility | 20-day annualized volatility of daily returns. RV >= 15% qualifies Plan C. |
| **MFE** | Maximum Favorable Excursion | Best unrealized P&L during a trade's life. Used in forward test analysis. |
| **MAE** | Maximum Adverse Excursion | Worst unrealized P&L during a trade's life. Used to calibrate stops. |
| **ATR** | Average True Range | 14-day ATR. Used for Plan M stop placement (2 ATR) and forward test milestones. |
| **OI** | Open Interest | Outstanding option contracts. Minimum OI = 5x estimated contracts for Plan Alpha. |
| **DTE** | Days to Expiration | Calendar days until option expiry. Plan Alpha: 30-120 DTE. Plan M: 30-120 DTE. |
| **MFO** | Multi-Frame Overlap | Breakout signal strength across timeframes. Used in Plan H dual-slot logic. |
| **COT** | Commitment of Traders | CFTC weekly report. Yen COT (75/25 raw signal) used for Plan M short sizing. |

## Options Terms

| Term | Definition |
| --- | --- |
| **Delta (Δ)** | Probability proxy and directional exposure. 0.30Δ = ~30% ITM probability. Plan Alpha targets 0.30Δ calls; Plan M targets 0.80Δ puts/calls. |
| **OCC Symbol** | Options Clearing Corporation format: `SYMYYMMDDCSSSSSSSS` (e.g. `GILD260515C00150000` = GILD May 15 2026 150 Call). |
| **Spread %** | Bid-ask spread as percentage of mid price. Max 15% for Plan Alpha. |
| **Strike Walking** | Iterating through strikes to find the closest to target delta with acceptable liquidity. |
| **Expiration Walking** | Iterating through expirations (monthlies first, then weeklies) within DTE range. |

## Regime & Strategy

| Term | Definition |
| --- | --- |
| **Regime** | Market classification based on SPY 20-day return: Bull (>+2%), Choppy (-2% to +2%), Transition (-4% to -2%), Crash (<-4%). |
| **Episode** | A cluster of Plan Alpha signal days within 7 calendar days. Entry window = first 2 signal days only. |
| **Catastrophic Stop** | Emergency exit if stock closes below SMA200 \* 0.93 (-7% from SMA200). |
| **Hybrid Exit** | Plan Alpha exit rule: if green at day 4 close → exit; else hold to day 5 close. |
| **SICADFU** | Sit In Cash And Don't F\*\*\* Up. The "do nothing" plan for regimes with no edge. Park in SGOV. |
| **OVTLYR** | External signal provider for Plan M swing trades. Produces long/short candidates daily. |

## Infrastructure

| Term | Definition |
| --- | --- |
| **PIT Universe** | Point-in-time S&P 500 membership. Avoids survivorship bias in backtests. |
| **BQS Precompute** | Weekly Sunday job that calculates BQS and sector data for all S&P 500 tickers. |
| **GCS** | Google Cloud Storage. Used for state sync between Mac Studio and GCP VM. |
| **Warmup** | Plan Alpha 14:45 ET pre-screen. Runs RSI check before the main 1:30 PM PT screener. |
| **Forward Test** | Live paper tracking of signals against backtest benchmarks. Plan M short tracker started 2026-03-14. |

## SMA200 Distance Buckets (Plan Alpha)

Backtested 2016-2026. Distance = (close - SMA200) / SMA200.

This table answers a specific question: when a stock is above its 200-day trend line, how far above it is "healthy pullback" versus "too close to breaking down" or "already overextended"?

| Distance | Win Rate | Avg P&L | Verdict |
| --- | --- | --- | --- |
| 0-1% | 64.5% | 0.90% | **Filtered out** — too close to breakdown |
| 1-2% | 77.7% | 1.96% | Strong |
| 2-3% | 75.6% | 2.31% | Best avg P&L |
| 3-5% | 73.0% | 1.87% | Solid |
| 5-10% | 79.2% | 1.74% | Highest win rate |
| 10-20% | 75.6% | 1.06% | Returns diminish |
| 20%+ | 47.1% | -0.78% | Net loser — skip |
