# Regime Transitions

This page covers what happens when the market crosses from one regime into another. These boundary periods matter because they are where traders are most tempted to keep doing what worked yesterday even though the environment has changed.

## What Happens at Boundaries

Regime transitions are the most dangerous periods. The system has explicit rules:

### Choppy → Bull (SPY 20d crosses +2%)

- Plan H monitors stop taking new entries
- Existing Plan H positions run to exit (EMA5 trail or session close)
- Plan M screeners become primary
- No new Plan H signals until regime returns to choppy

This is the handoff from intraday mean-reversion style trading to swing trading in stronger trends.

### Choppy → Transition (SPY 20d crosses -2%)

- Plan H reduces to SPY only (QQQ paused)
- Watch for further deterioration toward crash
- Plan Alpha early warning triggers at SPY 20d <= -3%

Transition is basically the market's unstable middle ground: not healthy enough to trust, not broken enough for the crash playbook.

### Transition → Crash (SPY 20d crosses -4%)

- Plan H fully OFF
- If RV >= 15%: Plan C activates (EMA stack shorts)
- If RV < 15%: Sit out entirely (slow grind, no edge)
- Plan Alpha gate at SPY 20d <= -5%

Here again, **RV** means realized volatility. The system only wants the short crash plan when the selloff has real speed and violence behind it.

### Crash → Recovery

- Crash regime doesn't turn off instantly
- SPY 20d must recover above -4% to exit crash
- Whipsaw protection: don't flip between crash and transition daily

A **whipsaw** is when the market keeps flipping direction just enough to trigger bad entries and exits. This protection is there to keep the system from thrashing.

## The Dead Zones

- **Transition (-4% to -2%):** No plan has edge here. Sit out.
- **Crash + low RV:** Market grinding down slowly. Plan C needs volatility for the EMA stack to work. Sit out.

!!! warning "Fail Closed"
    If regime detection fails (API error, bad data), default to sit out. Unknown regime = no trades. This is a hard rule in `symbol_monitor.py`.
