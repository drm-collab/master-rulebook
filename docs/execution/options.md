# Options Selection

This page explains how the system chooses which option contract to trade after a stock or ETF has already qualified. That matters because a good stock idea can still become a bad trade if the contract is too illiquid, too expensive, or too short-dated.

If you are new to options:

- **Delta** measures how much the option tends to move when the stock moves, and it is also used as a rough proxy for how likely the option is to finish in the money.
- **DTE** means Days to Expiration.
- **Open interest (OI)** is the number of open contracts.
- **Bid/ask spread** is the gap between what buyers are offering and sellers are asking.

See the [Glossary](../glossary/index.md) for the fuller definitions.

## Delta Targets by Plan

Different plans use different contracts because they are solving different problems. Short-dated intraday trades need leverage without too much time value. Multi-day swing trades need contracts that behave more like the stock and decay more slowly.

| Plan | Delta | DTE | Why |
| --- | --- | --- | --- |
| **H** | 0.43 | 3-5 days | Balance of leverage and time decay for intraday |
| **M** | 0.80 | 30-120 days | Deep ITM, minimal extrinsic, swing-friendly |
| **C** | 0.43 | 3-5 days | Same as Plan H, puts instead of calls |
| **Alpha** | 0.30 | 30-120 days | Cheap, gamma-rich, max diversification across signals |

**Extrinsic value** is the "time premium" in an option beyond its immediate intrinsic value. Lower extrinsic is usually better when the plan wants the contract to track the stock more directly.

## Plan M Liquidity Screen

Plan M uses larger, longer-held positions, so contract quality matters a lot. The goal is to avoid getting trapped in wide spreads or thin open interest.

1. **Monthly contracts** at least 30 DTE (go further out for liquidity)
2. **200+ open interest** at chosen strike AND all the way down
3. **10% max bid/ask spread** — (Ask - Bid) / Ask < 10%
4. **30% absolute max extrinsic** — goal is 20% or less
5. Target 80 delta, adjust strike up/down to find liquidity

## Plan Alpha Options

Plan Alpha wants cheaper upside exposure across multiple names during crashes, so it accepts lower delta than Plan M.

1. Find expirations with 30-120 DTE
2. Prioritize monthly (3rd Friday, day 15-21)
3. Find all calls with delta in [0.20, 0.40]
4. Sort by: closest to 0.30 delta, tightest spread, highest OI
5. Spread must be <= 15%, OI >= 5x estimated volume

## Strike Walking

Sometimes the "ideal" strike on paper is not actually tradable. Strike walking is the practical fallback.

When the target strike doesn't have liquidity:

1. Check one strike closer to ATM
2. Check one strike further OTM
3. If neither passes liquidity, try next expiration date
4. If no expiration works, skip the trade

**ATM** means at-the-money, or near the current stock price. **OTM** means out-of-the-money, farther away from the current price.

!!! warning "DTE and Delta are Hard Blocks"
    No valid contract = alert + skip. Never force a trade into an illiquid contract.
