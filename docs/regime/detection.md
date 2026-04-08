# Regime Detection

The regime gate is the master switch. It determines which plan runs.

A **regime** is just the system's name for the current market environment. Think of it like a weather report for trading: bull, choppy, transition, or crash. Master Rulebook checks that weather first because the same setup can work beautifully in one environment and fail badly in another.

## Primary: SPY 20-Day Return

The system starts with a simple measurement: how much has SPY moved over the last 20 trading days? That one number does most of the routing work.

| SPY 20d Return | Regime | Action |
| --- | --- | --- |
| > +2% | **Bull** | Plan H OFF → Plan M |
| -2% to +2% | **Choppy** | Plan H ON (best regime) |
| -4% to -2% | **Transition** | Sit out (recovery risk) |
| < -4%, RV >= 15% | **Crash Active** | Plan C (shorts) |
| < -4%, RV < 15% | **Crash Sit Out** | No edge (slow grind) |
| <= -5% | **Plan Alpha Gate** | Mean reversion calls fire |

**RV** means realized volatility. It tells the system whether a selloff is violent enough to activate the crash short plan, or just a slow downward grind that is better avoided.

## Secondary Indicators

These do not override the main gate, but they help confirm the feel of the market.

- **VIX > 18** = choppy bias
- **VIX < 15** = bull bias
- **High ATR** = choppy
- **Whipsawing 50-day MA** = choppy

**VIX** is the market's implied volatility index. Higher VIX usually means more fear and more two-way movement. **ATR** is Average True Range, a direct measure of movement size.

## Implementation

This is the core logic in code form. The important part is not the syntax; it is the ordering of the checks and the thresholds used to classify the market.

```
closes = get_spy_daily_closes(days=20)
ret_20d = (closes[-1] - closes[-21]) / closes[-21]

# Realized volatility (annualized)
daily_rets = [closes[i]/closes[i-1] - 1 for i in range(1, len(closes))]
rv_20d = stdev(daily_rets[-20:]) * sqrt(252) * 100

if ret_20d < -0.04:
    regime = "crash_active" if rv_20d >= 15 else "crash_sit_out"
elif ret_20d > 0.02:
    regime = "bull"
elif -0.02 <= ret_20d <= 0.02:
    regime = "choppy"
else:
    regime = "transition"
```

State written to `regime_state.json`. Updated by `update_regime.py` at 6:15 AM PT (before monitors) and 1:40 PM PT (before digest).

## Key Insight

**83% of Plan H profits come from the choppy regime.** The regime filter eliminates the sustained low-vol bull markets where H9 is a net loser. Pre-2022 data (2016-2021) shows Plan H loses money in prolonged bulls.
