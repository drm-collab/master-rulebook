# Plan ETF — Defensive Index Play

|  |  |
| --- | --- |
| **Regime** | Market is bullish but no individual stock setups exist |
| **Symbols** | TQQQ, SPXL |
| **Instrument** | Shares only: TQQQ (3x QQQ) and/or SPXL (3x SPY), not options |
| **Risk** | All available cash |

Plan ETF is the fallback plan for bullish conditions. The idea is: if the overall market looks healthy but the stock-specific setup quality is weak, keep exposure simple and broad instead of forcing lower-quality individual trades.

## Entry — TQQQ

The plan wants leveraged index exposure only when the underlying market is already behaving well and price is not badly extended.

1. Uptrend in QQQ
2. QQQ buy signal (OVTLYR)
3. QQQ heatmap < 70 (direction doesn't matter)
4. Price between 20 EMA and 2 ATR over 20 EMA ("Value Zone")
5. Order blocks > 2% away (at least 30 calendar days old)

**EMA** is a faster-moving trend average. **ATR** measures normal price movement. An **order block** is a prior supply/demand zone that can act like resistance or support. See the [Glossary](../glossary/index.md).

## Entry — SPXL

Same rules, applied to SPY instead of QQQ.

## Exit Signals

Close if ANY occur, then go to SICADFU:

1. Sell signal on underlying (QQQ/SPY)
2. 10/20 bearish cross on underlying
3. 30 Day+ order block hit
4. Close price > 3 ATR above 20 EMA (overextended)

In plain English, the exit is looking for either trend damage or the market getting too stretched to justify staying in.

## Backtest

TQQQ with QQQ signals: $100K → $954K (+854%), vs QQQ B&H +180%, TQQQ B&H +343%.
Max DD -27.7%, Sharpe 1.25.
