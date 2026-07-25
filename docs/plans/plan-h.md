# Plan H — Day Trading (H9 Race v3)

|  |  |
| --- | --- |
| **Regime** | Choppy only (SPY 20d return −2% to +2%) |
| **Symbols** | SPY, QQQ |
| **Instrument** | Options, target **0.42 Δ**, **3–5 DTE** |
| **Timeframe** | **5-min** bars (1-min → resample; Plan C uses 2-min) |
| **Risk** | **6% equity** per trade → **2%** after **3** consecutive losses (global across symbols) |
| **Hold Period** | Intraday; entries **09:40–11:00 ET**; force close **11:28 ET** |
| **Live code** | `workspace/trading_plans/production/plan_h/symbol_monitor.py` |
| **Backtest Edge** | Race v3 2016–2026 (choppy): 1,092 trades, 48.1% WR, PF 1.34, +$184K on $70K flat |

Plan H is the intraday workhorse for sideways, messy markets. It uses two signal types — **pullback** and **breakout** — in a race condition. Pullback is checked first on every bar; breakout only if pullback did not fire and time ≤ **10:10**. Default max **1 trade per symbol per day**, with an optional **dual-slot** size bump (below).

If you are new to the terms on this page:

- **EMA21** is a 21-period Exponential Moving Average — main pullback touch and initial stop.
- **VWAP** is Volume-Weighted Average Price (session-anchored 09:30 ET).
- **ATR** is Average True Range — normalizes move-from-open and EMA fan filters.
- **Delta** and **DTE** describe the option contract. See the [Glossary](../glossary/index.md).

## Signal Types

### Pullback (primary) — `pullback_ema21`

Catches price snapping back from a brief touch of EMA21 inside a trend. Window: full **09:40–11:00 ET** (or **10:00–11:00** on gap days).

**CALL** — all true on the same 5-min bar:

1. VWAP slope (2-bar) **> 0**
2. Close **> VWAP**
3. Stack: **EMA5 > EMA10 > EMA21**
4. Close **> EMA21**
5. Prior bar close **≥ prior EMA21**
6. Bar low **≤ EMA21 × 1.002** (touch)
7. Move from open: `(close − day_open) / ATR ≥ 1.0`
8. EMA fan: `|EMA5 − EMA10| / ATR ≥ 0.25`

**PUT** — mirror:

1. VWAP slope **< 0**
2. Close **< VWAP**
3. Stack: **EMA5 < EMA10 < EMA21**
4. Close **< EMA21**
5. Prior bar close **≤ prior EMA21**
6. Bar high **≥ EMA21 × 0.998**
7. `(day_open − close) / ATR ≥ 1.0`
8. Same EMA fan filter

### Breakout (supplemental) — `breakout_ema_stack`

Strong early trend that never needs an EMA21 touch. Window: **09:40–10:10 ET** only (no lookback bar). Same stack / VWAP / MFO / fan filters as pullback, **without** the EMA21 touch conditions.

The 10:10 cutoff exists because later breakouts historically mean-reverted in chop. Cutting the window at 10:10 alone flipped 2024 from −$9.8K to +$3.9K in the race-v3 study.

### The race condition

On every completed 5-min bar:

1. Check **pullback** first (full entry window).
2. Else if `t ≤ 10:10`, check **breakout**.
3. First fire wins for that symbol (subject to dual-slot sizing).

### Dual-slot sizing

If a **pullback** fires **and** `t ≤ 10:10` **and** MFO ≥ **1.5 ATR**, the signal is tagged `dual_slot=True` and the main loop **doubles contracts** (capped at `2 × MAX_CONTRACTS`). Intent: both PB and BO regimes are “on” the same bar with enough extension.

## Entry Filters (both signal types)

1. **Regime:** SPY 20d return in **[−2%, +2%]** (choppy). Off in bull / crash / unknown (start script writes `regime_blocked_today.txt`).
2. **Session:** 09:40–11:00 ET; gap days start at **10:00** if `|open − prior_close| / prior_close ≥ 0.5%`.
3. **EMA5–10 spread:** `|EMA5 − EMA10| / ATR ≥ 0.25`.
4. **Move from open (MFO):** directional open→close / ATR ≥ **1.0**.
5. **Macro skip:** no entries on scheduled **FOMC / CPI / NFP** days (hardcoded calendar in monitor).
6. **Markov overlay (live, on):** reject if lookback is too choppy, state just left chop, or breakout state duration is too short (see below).
7. **Already in position:** skip new signals for that symbol.

## Markov overlay (live filter)

Walk-forward overlay (enabled). Uses a 5-state classification on 5-min bars (trend up/dn, pullback bull/bear, choppy) and a transition matrix trained on ~60 sessions.

Reject a signal when:

| Rule | Condition |
| --- | --- |
| Chop fraction | > **50%** of last **8** bars classified choppy |
| Fresh from chop | State duration ≤ 1 **and** prior state was choppy |
| Breakout duration | Breakout signal **and** directional-state duration **< 4** bars |

Does not change the base H9 rules; it **filters** low-quality setups before order placement.

## Option selection

Target **|Δ| ≈ 0.42**, **3–5 DTE**. Hard block if no valid expiry (no arbitrary DTE fallback).

Live selection (post–Jul 2026 fix):

1. **Black–Scholes delta** from **live spot** + each strike’s IV (`mid_iv` / `smv_vol`).
2. **Reject junk IV:** IV ≤ 0 or **IV > 3.0 (300%)** — prevents deep-ITM wings from scoring as ~0.42Δ.
3. **ORATS fallback** only if BS cannot run: use chain delta **only if OTM** (put strike < spot / call strike > spot).
4. Return **live |Δ|** into sizing (not stale overnight ORATS).

Also: max **10% equity** in premium; hard cap **50** contracts per trade (dual-slot can go to **100**).

## Sizing

```
current_risk  = 0.02 if consecutive_losses >= 3 else 0.06
risk_dollars  = equity * current_risk
stop_dist     = max(|entry - EMA21|, 0.10)
risk_per_ct   = stop_dist * live_delta * 100
contracts     = min(floor(risk_dollars / risk_per_ct), 50)
# dual_slot → contracts = min(contracts * 2, 100)
# also cap by premium: floor(0.10 * equity / (ask * 100))
```

Global loss throttle persists across **days and symbols** (shared state file). Resets on the next win.

## Exit Rules (priority order)

1. **Force close (11:28 ET):** flatten — no exceptions.
2. **EMA5 trailing stop:** after trail is armed, exit if close crosses EMA5 against the trade.
3. **EMA21 initial stop:** before trail arms, exit if close crosses EMA21 against the trade.
4. **Trail arm (live):** EMA5 trail arms when **underlying moves +1.0 point** in favor of the trade (size-independent; matches backtest).  
   *Deprecated live rule (removed): option P&L ≥ +15% or +$1,000 estimated P&L.*

Live fills: **Alpaca paper** immediately; **Tradier sandbox** delayed ~15 min (quote freshness).

!!! warning "AM Only"
    PM session was a net −$14K over 10 years across variants. Plan H does **not** trade PM.

## What live does **not** do

- **No pyramiding** (no Tier 2 / Tier 3 adds). Size is set at entry (with optional dual-slot 2×).
- **No PM session.**
- **No trading outside choppy** for Plan H (Plan C is a separate crash path in the same process).

## Indicators

All Plan H signals on **5-min** bars (warmup: prior session + today):

- **EMA5, EMA10, EMA21** — span-based, `adjust=False` (EMA21 column is `ema20` in code for historical reasons)
- **ATR14** — 14-period mean true range
- **VWAP** — full day, anchored 09:30 ET
- **VWAP slope** — 2-bar diff on 5-min VWAP (~10-min momentum)

## Ops

| Piece | Role |
| --- | --- |
| `start_monitor_multi.sh SPY QQQ` | Cron Mon–Fri ~06:25 ET; respects holiday + regime gate |
| `monitor_watchdog.sh` | Restarts hung/dead monitors during AM window |
| `position_monitor.py` | Companion exit authority path (stop/trail coordination) |
| `regime_state.json` | Choppy / bull / crash from Tradier-driven update |

## Backtest Results (2016–2026, choppy, $70K flat)

Historical **Race v3** study (pre–Markov, pre–dual-slot, pre–+1.0 pt trail). Live adds those overlays; use this section for baseline edge, not as a 1:1 live fill ledger.

### Race v3 (baseline)

| Metric | Value |
| --- | --- |
| Trades | 1,092 |
| Win Rate | 48.1% |
| Profit Factor | 1.34 |
| Total P&L | +$184,476 |
| Avg Trade | +$169 |
| Positive Years | 8/11 |
| Modern (2019–2026) | +$231,940 |
| Early (2016–2018) | −$47,465 |

### Year-by-year

| Year | Pullback | PB P&L | Breakout | BO P&L | Total |
| --- | --- | --- | --- | --- | --- |
| 2016 | 78 | −$8,590 | 59 | −$7,451 | −$16,041 |
| 2017 | 149 | −$26,333 | 47 | −$2,881 | −$29,214 |
| 2018 | 82 | −$11,066 | 34 | +$8,857 | −$2,209 |
| 2019 | 42 | −$4,278 | 35 | +$13,846 | +$9,568 |
| 2020 | 20 | +$10,253 | 27 | +$796 | +$11,048 |
| 2021 | 74 | −$16,590 | 45 | +$30,263 | +$13,673 |
| 2022 | 20 | +$19,686 | 26 | −$11,611 | +$8,074 |
| 2023 | 54 | −$3,461 | 39 | +$39,743 | +$36,283 |
| 2024 | 57 | +$6,263 | 33 | −$2,356 | +$3,907 |
| 2025 | 81 | +$26,215 | 38 | +$26,094 | +$52,309 |
| 2026 | 34 | +$75,401 | 18 | +$21,678 | +$97,079 |

### Signal type breakdown

| Signal | Trades | P&L | Win Rate |
| --- | --- | --- | --- |
| Pullback | 691 (63%) | +$67,498 | 41.4% |
| Breakout | 401 (37%) | +$116,977 | 59.6% |

Pullback has lower WR but asymmetric payoff. Breakout accounts for most of total P&L despite fewer trades.

See the full [Backtest](plan-h-backtest.md) for equity curve and trade log.

### Monte Carlo (10,000 runs, baseline race-v3 book)

| Percentile | P&L | Final Equity |
| --- | --- | --- |
| P10 | +$105K | $175K |
| P25 | +$142K | $212K |
| P50 | +$183K | $253K |
| P75 | +$225K | $295K |
| P90 | +$266K | $336K |

| Risk Metric | Value |
| --- | --- |
| Probability profitable | 99.9% |
| Probability double account | 97.1% |
| Probability of ruin (<50%) | 2.1% |
| Mean max drawdown | −24.9% |
| Annualized Sharpe | 0.93 |

### Key discoveries

- Early years (2016–2018) are net negative; edge is modern (post-2019 microstructure).
- Breakout carries a large share of P&L under the 10:10 gate.
- Live **Markov** and **dual-slot** are operational overlays not fully reflected in the 1,092-trade table above.
