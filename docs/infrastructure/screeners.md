# Automated Screeners

A screener is an automated filter that scans a large universe of markets and returns only the names that fit the rules. This page explains what each screener looks for and why those filters exist.

If terms like **RSI**, **DTE**, **delta**, or **order block** are new, keep the [Glossary](../glossary/index.md) nearby.

## Plan M Long Screener

**Cron:** 5:55 AM PT daily | **Script:** `plan_m_long_screener.py`

This screener is trying to answer a simple question: "Which stocks are aligned with the market, their sector, and their own trend, and also have tradable options?"

Pipeline:
1. OVTLYR market check — SPY/RSP trend, buy signal, F&G heatmap, sector breadth
2. OVTLYR buy signals — stocks in bullish sectors (>1M vol, buy signal, heatmap up, green overlay)
3. Price action filter — not extended (>15% up in 20d), not overbought (RSI >67)
4. Higher TF RSI — weekly/monthly confirms room to run
5. Options liquidity screen
6. OB detection — resistance targets above
7. Position sizing calculation

**F&G heatmap** is OVTLYR's fear-and-greed style measure. **Higher TF** means higher timeframe, in this case weekly and monthly charts.

## Plan M Short Screener

**Cron:** 6:05 AM PT daily | **Script:** `plan_m_short_screener.py`

This is the bearish mirror image of the long screener: find weak stocks in weak sectors, then check whether the options are liquid enough to trade.

Pipeline:
1. OVTLYR sector breadth — bearish sectors (bull% < EMA10 + sell signal)
2. OVTLYR sell signals — stocks in bearish sectors (price >= $30, vol >= 2M, region <= -1)
3. Price action filter — not extended (>15% down in 20d), not oversold (RSI <33)
4. Higher TF RSI — weekly/monthly < 71
5. Options liquidity screen
6. OB detection — support targets below
7. Position sizing + Yen COT overlay

Output: JSON results, HTML report, TradingView watchlist, Telegram alert.

**COT** stands for Commitment of Traders, a positioning report used here as an overlay on short sizing.

## Plan Alpha Screener

**Cron:** 1:30 PM PT daily | **Script:** `plan_alpha_screener.py`

Plan Alpha is looking for stocks that have been sold hard during a market correction or crash, but are still holding above their long-term trend. Think of it like searching for strong names being temporarily panic-sold.

Pipeline:
1. SPY 20d regime check (exits immediately if > -5%)
2. Early warning alert at SPY 20d <= -3%
3. S&P 500 universe scan — RSI(5) < 15, close > SMA200
4. FOMC/CPI/NFP macro day skip
5. Episode detection (7-day gap = new episode)
6. Entry window enforcement (first 2 signal days only)
7. Options chain lookup (0.30 delta, 30-120 DTE)
8. Telegram alert with candidates

**RSI(5) < 15** means five-day momentum is extremely washed out. **SMA200** is the 200-day Simple Moving Average, used as a long-term trend line. **FOMC/CPI/NFP** are major scheduled macro events that can distort the normal edge.

## Convergence Detector

**Cron:** 6:25 AM + 1:50 PM PT | **Script:** `convergence_detector.py`

This screener looks for names showing up in multiple places at once. The idea is straightforward: if different signal sources are pointing to the same stock, conviction is usually higher. If they disagree, caution goes up.

Scans for stocks appearing in multiple signal sources (Plan M, bottom formation, X Expose). Confirming signals = higher conviction. Contradictory signals = caution.

## Bottom Formation Screener

**Cron:** 6:25 AM PT | **Script:** `bottom_monitor.py`

This is a chain-of-evidence screener. Instead of relying on one indicator, it looks for multiple signs that a beaten-down stock may be starting to base and recover.

Chain-of-evidence pipeline: volume breakout detection, relative strength scoring, trap classification, Grok research agent for fundamental context.
