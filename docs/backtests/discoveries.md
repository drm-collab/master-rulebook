# Key Discoveries

This page is the short list of lessons the system had to learn the hard way. It matters because these are the findings that changed live rules, sizing, data sources, and even which strategies stayed alive.

If a term here is unfamiliar, check the [Glossary](../glossary/index.md). On this page, a **regime** means the broad market environment, such as bullish, choppy, or crashing.

## Sizing

- **Kelly sizing creates death spirals** when costs are inside the loop. Fixed-fraction (6% for Plan H, 5% for Plan M) is correct.
  Kelly sizing is a formula that tells you how aggressively to bet when you think you have an edge. In theory it is elegant. In real options trading, once slippage and fees are included, it becomes too aggressive and the account can spiral down fast.
- **Consecutive loss throttle:** After 3 losses, drop to 2% risk until first winner. Resets daily.
  This is the system's version of taking your foot off the gas after a skid.

## Signal Quality

- **83% of Plan H profits come from choppy markets.** The regime filter is the single most important parameter.
  "Choppy" means the market is moving back and forth instead of trending cleanly higher or lower. That messy environment turns out to be exactly where Plan H has its edge.
- **AM-only is strictly better.** PM session is a net loser. Every variant, every timeframe.
  The morning produces the cleanest moves. By afternoon, the setup quality drops enough that the extra screen time hurts results.
- **sig=2 is optimal.** More signals per day dilute the edge.
  In plain English: the first two opportunities are the good ones. After that, the system is usually chasing weaker leftovers.
- **VWAP slope as 2-bar diff** on 5-min VWAP captures 10-minute momentum without noise.
  **VWAP** is the volume-weighted average price, a common intraday reference line. Measuring its slope over two 5-minute bars gave a simple read on short-term momentum without overreacting to every tick.

## Data & Infrastructure

- **Alpaca IEX is unreliable for individual stocks.** RSI values come out wrong. Use Tradier for all price/RSI data.
  **RSI** stands for Relative Strength Index, a momentum indicator that helps measure whether a stock is stretched. If the price feed is off, the RSI is off, and the whole screener can be wrong.
- **Alpaca SIP cancelled** ($100/mo saved). Alpaca used for order execution only.
  That means Alpaca stays in the stack for placing trades, but not for the market data that drives the rules.
- **Keychain fails from cron** on macOS. Always load `.env` first, keychain as fallback. Remove `-a USER` flag from security commands.
  In other words, background automation behaves differently than a terminal session. The credential-loading order had to be designed for that reality.
- **Parquet timestamps must be ET tz-naive.** Use `df.index.hour` directly, never tz-convert.
  This is a plumbing lesson: if timestamps are stored the wrong way, the system can think a candle happened at the wrong market time.

## Strategy

- **OB confluence was look-ahead biased.** Without bias, it's worthless.
  **OB** means order block, a price area where heavy buying or selling previously showed up. The original version accidentally used future information, which makes a backtest look smarter than a real trader could ever be.
- **J1 gap reversal is a net loser** (-$51K). H9 alone beats H9+J1.
  The extra setup sounded additive. The data said it dragged down the stronger core strategy.
- **Plan Alpha fires every ~4.6 months** but has the highest PF (2.68). Patience is required.
  **PF**, or profit factor, means gross profit divided by gross loss. A PF of 2.68 is excellent, but it comes from a strategy that shows up rarely.
- **Pre-2022 data shows Plan H loses in sustained bulls.** The choppy filter eliminates these periods.
  This is one of the clearest examples of why regime classification matters. The same entry pattern behaves differently depending on the market weather.

## Live Trading

- **Every dollar lost came from breaking rules, not from the system.**
  That is the central lesson of the live account.
- **The system works when you let it work.** $9,650 → $88,000 when rules were followed. Gave back $18K when they weren't.
  Same trader, same tools, different behavior.
- **House money is the best money to trade with.** No fear, just execution.
  Once the original capital was recovered, decision-making got cleaner because the focus shifted from fear to process.
