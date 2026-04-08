# Position Sizing

Position sizing is how the system decides how big each trade should be. This is one of the most important pages in the wiki because a strategy can be directionally right and still blow up if the size is wrong.

The basic idea is simple: the system first decides how much account risk it is willing to take, then backs into the number of contracts from the stop distance and the option's **delta**. If terms like **ATR**, **EMA**, or **delta** are unfamiliar, see the [Glossary](../glossary/index.md).

## The Rules

- **Fixed-fraction sizing.** Never Kelly. Kelly + costs = death spiral.
- **Risk per trade is a hard cap.** No exceptions for "high conviction."

The first rule exists because **Kelly sizing** is too aggressive once real trading costs are included. The second rule exists because "this one looks amazing" is how traders talk themselves into oversized losses.

## By Plan

### Plan H (Day Trading)

Plan H sizes off the distance to **EMA21**, which acts as the initial stop line. The farther price is from that line, the fewer contracts the system can take.

```
base_risk = 6% of equity
throttle  = 2% if 3+ consecutive losses (resets daily)
stop_dist = max(|close - EMA21|, 0.10)
risk_per_contract = stop_dist * 0.43 * 100
contracts = min(floor(risk / risk_per_contract), 50)
```

### Plan M (Swing Trading)

Plan M uses **ATR**, or Average True Range, to estimate how much a stock normally moves. The stop is set at 2 ATR, then contract count is derived from that.

```
risk = 5% of equity ($3,500 on $70K)
stop = 2 ATR from entry
shares = risk / (2 * ATR)
contracts = shares / delta (0.80)
```

### Plan C (Crash Shorts)

Plan C is the crash short plan, so its size depends on the distance between entry and **EMA50**, which acts as the initial stop.

```
risk = 5% of equity
stop_dist = |entry - EMA50|
contracts = floor(risk / (stop_dist * 0.43 * 100))
```

### Plan Alpha

Plan Alpha keeps sizing deliberately simple. Instead of tying size to account equity every time, it uses a flat budget per trade so multiple crash signals can be diversified across names.

```
budget = $3,500 per trade (flat)
contracts = floor(budget / (option_mid * 100))
```

No daily cap — take every signal with liquid options. Lowest RSI gets priority.

**RSI** is the Relative Strength Index, a momentum measure. Lower RSI means the stock has been sold more aggressively.

## Pyramiding (Plan H Only)

**Pyramiding** means adding to a winning position instead of starting at full size. Plan H only does this after the trade has already proven itself.

- **Tier 2 (+30% option P&L):** Add floor(base \* 0.5) contracts (max 25)
- **Tier 3 (+100% option P&L):** Add floor(base \* 0.25) contracts (max 12)
- T2/T3 P&L measured from THEIR entry, not base entry
- Each tier charged separately for fees

## Loss Throttles

These rules are there to slow the system down when conditions or execution quality are deteriorating.

- **Plan H:** 3 consecutive losses → risk drops from 6% to 2% until first winner
- **Plan M:** 3 losers in a single day → no new trades for 1 week
- **Global:** Loss state tracked in `global_loss_state.json`
