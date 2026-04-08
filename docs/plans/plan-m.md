# Plan M — OVTLYR Swing Trading

|  |  |
| --- | --- |
| **Regime** | Bull (SPY 20d > +2%), or anytime setups exist |
| **Symbols** | S&P 500 stocks via OVTLYR |
| **Instrument** | Options, 0.80 delta calls/puts, 30+ DTE monthly |
| **Timeframe** | Daily |
| **Risk** | 5% equity ($3,500 per trade) |
| **Hold Period** | 17.5 days |
| **Backtest Edge** | 56.9% WR, PF 1.85, +$453,918 MC mean |

Plan M is the system's main swing-trading engine and its biggest historical profit contributor. The core idea is to only trade when three layers line up at once: the overall market, the stock's sector, and the stock itself.

If you are new to the terms on this page:

- **Delta** measures how much the option behaves like the stock. A 0.80 delta contract moves much more like stock than a 0.30 delta contract.
- **DTE** means Days to Expiration.
- **PF** means profit factor.
- **OVTLYR** is the external signal source that provides much of the market, sector, and stock structure for this plan.

See the [Glossary](../glossary/index.md) for the full definitions.

The most profitable plan. No profit targets. No expectations. Just a plan to get out when an exit signal hits.

## Entry — Three Layers

The reason for the three-layer model is simple: strong stocks work best when they are inside strong sectors that are inside a strong market. Plan M tries to make sure the wind is at the trade's back on all three levels.

ALL three layers must pass before entering. This is the filter that produces the edge.

### Market Layer (40% of the move)

1. **SPY bullish trend** — EMA 10/20/50 aligned bullish
2. **SPY buy signal** — OVTLYR buy signal active
3. **SPY F&G heatmap** — under 70 AND rising
4. **Full stocks breadth** — bullish cross of 10 EMA

!!! info "If market fails"
    Go to Plan ETF or SICADFU. Do not force trades.

The market layer answers, "Is the broad tape helping or fighting this trade?"

### Sector Layer (30% of the move)

1. **Sector F&G heatmap** — under 70 AND rising
2. **Sector relative greed > 1** — sector greed exceeds market greed
3. **Sector breadth** — bullish cross of 10 EMA
4. **OVTLYR channel** — M1S1 (market=1, sector>=1) or M2 (market=2, any sector)
5. **Healthcare permanently excluded**

The sector layer keeps the system from buying good-looking stocks inside weak neighborhoods.

### Stock Layer (30% of the move)

1. **Stock bullish trend** — EMA 10/20/50 aligned bullish
2. **Stock buy signal** — OVTLYR buy signal active
3. **Stock F&G heatmap** — any value, MUST be rising
4. **Stock >2% away from OB** — not sitting on resistance
5. **Price over 10 EMA**
6. **Price > $10** — options availability

Buy signal valid for up to **5 trading days** after generation.

An **OB**, or order block, is a prior supply/demand zone. Staying more than 2% away helps avoid buying directly into resistance.

## Options Liquidity Criteria

The option has to be tradable, not just theoretically available.

- **Monthly contracts** at least 30 DTE
- **200+ open interest** at chosen strike AND all the way down
- **10% max bid/ask spread** — (Ask - Bid) / Ask < 10%
- **30% absolute max extrinsic** — goal is 20% or less
- **Target 80 delta** — adjust strike for liquidity

## Position Sizing

The stop is set at 2 ATR from entry, then size is backed out from that risk. **ATR** is Average True Range, a measure of typical movement.

Stop = 2 ATR from entry.

```
shares    = (account_balance * 0.05) / (2 * ATR)
contracts = shares / delta
```

Example: $100K \* 0.05 / (2 \* 1.50) = 1,666 shares. 1,666 / 80 = 20 contracts.

## Rolling Strategy

Rolling is how Plan M takes partial profits without fully leaving a trade that still looks healthy. It sells the current option and buys a new one closer to the stock price.

- **First +0.5 ATR move** → roll (sell to close, buy to open closer to ATM)
- **Every +1 ATR after** → roll again
- If you CAN'T roll for a credit → hold existing trade
- Rolling takes partial profits, frees capital, keeps trade alive

## Exit Signals (close if ANY occur)

The exits are designed to close the trade when the original thesis weakens, a major risk event approaches, or price action becomes clearly abnormal.

1. **OVTLYR sell signal** — the signal reversed
2. **10/20 bearish cross** — EMA10 crosses below EMA20
3. **Hit OVTLYR block (120+ calendar days)** — old OB = strong resistance
4. **Earnings** — close BEFORE. 100% avoided. No exceptions.
5. **Gap & Crap** — 5% gap, close below gap candle low within 3 candles
6. **2 ATR stop** — hard stop from entry
7. **3 ATR emergency exit** — if price TOUCHES 3 ATR against you intraday, close immediately

!!! danger "Loss Throttle"
    3 losers in a single day = no NEW trades for at least 1 week.

## Backtest Results (OVTLYR data)

These numbers explain why Plan M is the system's primary bull-market engine.

| Metric | Value |
| --- | --- |
| Total Trades | 7,020 |
| Win Rate | 56.94% |
| Avg Win | +7.27% |
| Avg Loss | -4.41% |
| Profit Factor | 1.85 |
| Avg Days Held | 17.5 |

**Monte Carlo (1000 sims):** PF 1.85, avg max DD -24.4%, worst-case DD -49.5%

!!! note "Plan M Shorts"
    The short side of Plan M has its own screener, sizing rules, and exit logic. It is currently in [forward testing](plan-m-forward-test.md) — no backtest exists for shorts yet. The 7,020-trade backtest above covers **longs only**.
