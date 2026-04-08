# What Doesn't Work

This page is a graveyard of ideas that looked promising and failed when tested properly. It matters because a trading system gets stronger not just from what it adds, but from what it refuses to keep.

If you want the vocabulary behind terms like **profit factor**, **RSI**, **delta**, or **order block**, see the [Glossary](../glossary/index.md).

Everything below was tested and rejected. These are closed doors.

## 1. OB Confluence (Order Block Gate)

Think of an **order block** as a price zone where large buyers or sellers previously showed their hand. The idea was to only take H9 entries when they lined up with those zones.

**Tested:** Use order block proximity as an entry filter for H9.
**Result:** Look-ahead biased. Without bias, all variants hit 99%+ max drawdown.
**Status:** Removed from live code and strategy.

## 2. Kelly Sizing

The **Kelly criterion** is a bet-sizing formula that can be powerful in clean mathematical models. In live options trading, costs make it dangerous.

**Tested:** Kelly criterion for position sizing.
**Result:** Costs inside the Kelly loop create a death spiral. 97%+ max drawdown.
**Fix:** Fixed-fraction (6%) is the correct approach.

## 3. PM Session

This tested whether Plan H could simply keep trading into the afternoon. More hours sounds good in theory. The numbers said otherwise.

**Tested:** Trading H9 signals in the afternoon session.
**Result:** Net -$14K over 10 years across all variants. AM-only is strictly better.
**Status:** PM session permanently disabled. Force close at 11:28 ET.

## 4. sig=3+

Here, `sig` means the number of signals allowed per day. The question was whether taking the third, fourth, or later setup would add profit.

**Tested:** Allowing 3 or more signals per day.
**Result:** Extra signals are net losers. They dilute edge and increase drawdown.
**Fix:** sig=2 is optimal.

## 5. OB Quality Scoring

Instead of just checking whether an order block existed, this version tried to grade each one.

**Tested:** Scoring order blocks by quality metrics to filter entries.
**Result:** Inverse correlation (r=-0.33). Higher quality = worse performance.
**Status:** Rejected.

## 6. 1-Min Chart Filters

This was an attempt to use finer-grained 1-minute price patterns to improve 5-minute entries.

**Tested:** Using 1-minute chart patterns to filter 5-minute entries.
**Result:** No discriminating power between winners and losers at entry.
**Status:** Rejected.

## 7. Midday Skip

The hypothesis was simple: midday is usually quiet, so skip it. The data showed those quiet periods were not damaging enough to justify the filter.

**Tested:** Skipping signals during the midday dead zone.
**Result:** Hurts P&L. Dead zone losses are tiny — not worth filtering out.
**Status:** Rejected.

## 8. J1 Gap Reversal

A **gap reversal** tries to trade the market snapping back after a strong move between yesterday's close and today's open.

**Tested:** Gap reversal signal as a complement to H9.
**Result:** 286 trades, -\(51K net. H9-only (\)556K) beats H9+J1 ($512K).
**Status:** Permanently parked.

## 9. TSLA in Plan H

This tested whether the H9 intraday logic could be ported from index ETFs to a single high-volatility stock.

**Tested:** Running H9 on TSLA during bull regimes.
**Result:** H9 was designed/optimized on index ETFs, not single stocks. TSLA options have wider spreads and the $33K bull backtest was never validated against realistic execution costs.
**Status:** Removed 2026-03-19. Bull regime capital goes to Plan M.

!!! tip "The Lesson"
    Every rejected idea seemed promising in theory. Data killed them. This is why we backtest everything before going live.
