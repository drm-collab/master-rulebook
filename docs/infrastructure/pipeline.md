# Daily Cron Pipeline

This page shows the system's daily automation schedule. It matters because Master Rulebook is not one script; it is a pipeline of checks, screeners, monitors, and summaries that have to fire in the right order.

All times in Pacific Time. Weekdays only.

## Pre-Market (4:50 - 6:00 AM)

This block prepares the system before the opening bell: health checks first, then data and market prep.

| Time | Script | Purpose |
| --- | --- | --- |
| 4:50 | `run_maintenance.sh` | Health checks, auto-repairs, Telegram alerts |
| 5:00 | `check_screeners.sh cookies` | Validate OVTLYR cookies before screeners |
| 5:15 | X Expose premarket | Market sentiment from curated X accounts |
| 5:55 | Plan M long screener | OVTLYR buy signals scan |

## Market Open (6:00 - 6:35 AM)

This is the live handoff into the trading session. Monitors start, regime state is refreshed, and the morning screeners come online.

| Time | Script | Purpose |
| --- | --- | --- |
| 6:00 | Position monitor | EMA5 trailing stop daemon starts |
| 6:05 | Plan M short screener | OVTLYR sell signals → puts |
| 6:15 | `update_regime.py` | Fresh regime state for monitors |
| 6:20 | Substack digest | Market Sleuth newsletter fetch |
| 6:25 | Symbol monitors (SPY, QQQ) | Plan H signal detection starts |
| 6:25 | Convergence detector | Multi-signal convergence scan |
| 6:25 | Bottom monitor | Bottom formation evidence tracking |
| 6:30 | Check screeners monitors | Verify all screeners ran |
| 6:35 | Monitor watchdog | Verify monitors running, auto-restart |

## Post-Market (1:30 - 1:50 PM)

The close is when the slower, daily-timeframe parts of the system take over, especially the crash mean-reversion work.

| Time | Script | Purpose |
| --- | --- | --- |
| 1:30 | Plan Alpha screener | RSI(5)<15 mean reversion scan |
| 1:35 | Pattern tracker | Entry trigger/invalidation check |
| 1:40 | `update_regime.py` | Fresh regime state for digest |
| 1:45 | Short tracker PM update | End-of-day P&L replay |
| 1:50 | Convergence + Daily digest | Dashboard HTML + Telegram summary |

## Weekly

These jobs handle the slower maintenance and reporting cycle.

| Time | Script | Purpose |
| --- | --- | --- |
| Fri 1:45 PM | Weekly summary | Weekly performance report |
| Sun 8:00 AM | Maintenance | Weekend health check |
