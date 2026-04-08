<div class="hero">
<h1 id="master-rulebook-trading-system">Master Rulebook Trading System</h1>
<p class="subtitle"><strong>Rules-based options trading across all market regimes.</strong>
Four plans. Fully automated screening. Backtested edge.</p>
</div>

This wiki explains a personal options trading system called Master Rulebook. The core idea is simple: different market environments reward different behaviors, so the system classifies the current **regime** first, then routes capital to the plan built for that environment. If you are new to trading terms, the [Glossary](glossary/index.md) is the best companion page to keep open.

---

<div class="stat-grid">
<div class="stat-card">
<div class="label">Dec 10 → Feb 28</div>
<div class="value">+812%</div>
<div class="detail">$9,650 → $88,000 in 11 weeks</div>
</div>
<div class="stat-card">
<div class="label">Plan M Backtest PF</div>
<div class="value">1.85</div>
<div class="detail">7,020 trades, 56.9% win rate</div>
</div>
<div class="stat-card">
<div class="label">Plan Alpha PF</div>
<div class="value">2.68</div>
<div class="detail">908 trades, 75.1% win rate</div>
</div>
<div class="stat-card">
<div class="label">Combined Backtest</div>
<div class="value">+$554K</div>
<div class="detail">$70K → $624K (2016-2026)</div>
</div>
</div>

These cards are the high-level proof that the system is not just a collection of ideas. The first shows what happened when the rules were followed in live trading. The others show what the major plans produced in historical testing.

---

## System at a Glance

A **regime** is just market "weather." Instead of asking, "What do I feel like trading today?", Master Rulebook asks, "What kind of market are we in, and which plan was built for that?" That routing decision is the system's master switch.

| Regime | SPY 20d Return | Active Plan | Edge |
| --- | --- | --- | --- |
| **Choppy** | -2% to +2% | [Plan H](plans/plan-h.md) (day trading) | EMA21 pullback on SPY/QQQ |
| **Bull** | > +2% | [Plan M](plans/plan-m.md) (swing trading) | OVTLYR signals, 80-delta options |
| **Crash** | < -4%, RV >= 15% | [Plan C](plans/plan-c.md) (shorts) | EMA stack shorts on SPY |
| **Crash** | SPY 20d <= -5% | [Plan Alpha](plans/plan-alpha.md) (calls) | RSI(5)<15 mean reversion |
| **Nothing** | Any | [SICADFU](plans/sicadfu.md) | Park in SGOV, earn yield |

Every regime has a plan. No regime is "sit and hope."

## Core Philosophy

This system is built around a few simple beliefs:

1. **Rules are the edge.** Every dollar lost came from breaking rules, not from the system.
2. **Automate the screening, execute the plan.** Screeners run daily on cron. The human decides, the system finds.
3. **No profit targets.** Exit when the signal says exit, not when it "feels right."
4. **Risk first.** Fixed-fraction sizing (5-6%), hard stops, no exceptions.
5. **Backtest everything.** No live trade without historical validation.

In plain English: the system does the repetitive scanning and filtering, then the operator's job is to execute cleanly rather than improvise.

<div class="live-results">
<h3 id="live-results">Live Results</h3>
<p>These numbers matter because they show both sides of the system: what happened when the rules were followed, and what happened when they were not.</p>
<ul>
<li><strong>Sep - Dec 10:</strong> $20K → $9,650 (tuition — no system yet)</li>
<li><strong>Dec 10 - Feb 28:</strong> $9,650 → $88,000 (~812% in 11 weeks)</li>
<li><strong>Current:</strong> ~$70,000 (gave back $18K by breaking rules, still up ~625%)</li>
</ul>
<p>The $18K given back is the proof: <strong>the system works, deviation doesn't.</strong></p>
</div>

## Quick Links

If you want the short path through the wiki, start here:

- [All Trading Plans](plans/overview.md) — how each plan works and when it fires
- [Regime Detection](regime/detection.md) — the master switch that routes capital
- [Backtest Results](backtests/results.md) — combined numbers across all plans
- [What Doesn't Work](backtests/rejected.md) — tested and rejected ideas (save yourself the time)
- [Lessons Learned](journal/lessons.md) — rules violations and their costs in real dollars
