# Plan M Short — Forward Test

| | |
|---|---|
| **Strategy** | Plan M Short side |
| **Test Start** | 2026-03-14 |
| **Status** | Live paper trading |
| **Benchmark** | TBD (no short backtest) |

**Started:** 2026-03-14 | **Review dates:** Mid-April (day 30), Mid-May (day 60)  
**Status:** Live paper trading — 14 open, 4 closed, 11 near misses  
**Benchmark target:** None yet — no short-specific backtest exists. The 56.9% WR / PF 1.85 numbers are from the Plan M **long** backtest and are not directly comparable.

This page tracks the real-world dress rehearsal for the Plan M short pipeline. It matters because a good backtest is not enough; the system still has to prove that the live screener, options lookup, sizing, and exits all behave as expected in paper trading.

If you are new to the shorthand:

- **WR** means win rate.
- **PF** means profit factor.
- **ATR** measures normal price movement.
- **OB** means order block, a prior support or resistance zone.

See the [Glossary](../glossary.md) for the deeper definitions.

## Why Forward Test?

The Plan M short screener is automated but the strategy has never been paper traded with the full pipeline: real OVTLYR signals → options chain lookup → sizing → entry → rolling → exit. This forward test validates the entire chain before committing real capital.

In plain English, this is the "does the machine work outside the lab?" phase.

## Screener Pipeline

The daily short screener runs at 6:05 AM PT:

1. **OVTLYR bearish sectors** → sell signals (`watchlist`)
2. **Price action filter** — RSI > 33 (not oversold), not extended >15% in 20d, no earnings within 5 days
3. **Options chain** — Tradier lookup, delta walk 80→55, 30-120 DTE monthlies first, ≤10% spread
4. **Final filters** — spread%, OI (5x est_contracts), weekly RSI <71, monthly RSI <71, IV/HV ≥ 0.70, OB proximity >2%

Stocks that pass options but fail final filters become **near misses** — stored permanently for OB-break monitoring.

**IV/HV** compares implied volatility to historical volatility. The **delta walk 80→55** means the screener starts with deeper-in-the-money puts and relaxes toward lower delta only if needed.

## Paper Trade Model

### Sizing

```text
RISK_DOLLARS = $3,500 (5% of $70K)
contracts = max(1, floor(3500 / (2 * ATR * |delta| * 100)))
```

COT Yen overlay adjusts sizing:

- Dealer positioning > 75th pct → 1.3x short contracts
- Dealer positioning < 25th pct → 0.5x short contracts

### Exit Signals (Priority Order)

1. **Gap & Crap** — bar opens ≥5% above prior close (adverse gap up)
2. **3 ATR emergency** — bar high ≥ entry + 3×ATR → close immediately
3. **2 ATR hard stop** — bar high ≥ entry + 2×ATR
4. **OB target hit** — bar low ≤ support OB target (profit target)
5. **EMA cross** — EMA10 crosses above EMA20 (trend reversal)
6. **120-day backstop** — still open after 120 days → close

### Rolling

Rolling means selling the current put and buying a new one after the stock moves in the trade's favor, usually to take some profit and keep exposure alive.

Milestone-based rolling (no position change in paper test):

- Triggers at stock dropping 0.5, 1.5, 2.5, 3.5 ATR from entry
- Each roll records old/new strike, old/new put mid, credit received
- Credits accumulate: `total_pnl = delta_pnl + cumulative_roll_credits`

!!! note "Delta Approximation"
    Roll strikes are approximate (delta-adjusted, not real chain lookup). For live trading, pick the nearest real listed strike with appropriate delta.

## Signal Funnel

This funnel is a diagnostic tool. It shows where candidates are getting rejected, which tells you whether the bottleneck is market quality, options liquidity, or final risk filters.

The tracker logs the daily screening funnel:

```text
raw signals → failed price action → failed options → near misses → entered
```

This shows conversion rate and where signals are dying. If too many die at options liquidity, the delta/DTE ranges may need widening.

## OB Proximity Rule

The 2% rule is critical for shorts because being too close to support means the trade may be entering just as the stock is ready to bounce.

- **IDEAL (>5% from support OB):** Full conviction entry
- **CAUTION (2-5% from support OB):** Enter with awareness
- **ON_SUPPORT or OB_BROKEN:** → near miss, do not enter

SJM (0.2% from OB) and SMCI (1.9% from OB) were retroactively removed for this reason.

## Current Stats

| Metric | Value |
|--------|-------|
| Total picks | 69 |
| Open positions | 11 |
| Closed trades | 16 |
| Near misses | 16 |
| Win Rate | 81% (13W / 3L) |
| Total P&L | +$75,121 |
| Avg Hold | 8.3 days |
| Backtest target WR | TBD (no short backtest yet) |
| Backtest target PF | TBD (no short backtest yet) |

!!! warning "Early Days"
    16 closed trades is not a meaningful sample. The forward test needs 30-60 days and 20+ closed trades before drawing conclusions. The 81% WR will almost certainly regress.

## Trades
Click any summary row to expand the dashboard-style detail panel. Category headers collapse or reopen each bucket.

<style>
.pmft-trades {
  --pmft-bg: var(--md-default-bg-color);
  --pmft-surface: var(--md-code-bg-color);
  --pmft-border: var(--md-default-fg-color--lightest);
  --pmft-border-strong: var(--md-default-fg-color--lighter);
  --pmft-text: var(--md-default-fg-color);
  --pmft-muted: var(--md-default-fg-color--light);
  --pmft-link: var(--md-typeset-a-color);
  --pmft-positive: #22c55e;
  --pmft-negative: #ef4444;
  --pmft-caution: #f59e0b;
  --pmft-info: #60a5fa;
  margin: 2rem 0;
  padding: 0;
  max-width: 100%;
  color: var(--pmft-text);
  font-variant-numeric: tabular-nums;
}
[data-md-color-scheme="default"] .pmft-trades {
  --pmft-panel-bg: rgba(15, 23, 42, 0.028);
  --pmft-row-hover: rgba(15, 23, 42, 0.04);
  --pmft-row-open: rgba(15, 23, 42, 0.055);
  --pmft-strong-bg: rgba(34, 197, 94, 0.08);
  --pmft-watching-bg: rgba(239, 68, 68, 0.08);
  --pmft-working-bg: rgba(245, 158, 11, 0.10);
  --pmft-flat-bg: rgba(96, 165, 250, 0.08);
}
[data-md-color-scheme="slate"] .pmft-trades {
  --pmft-panel-bg: rgba(148, 163, 184, 0.05);
  --pmft-row-hover: rgba(148, 163, 184, 0.06);
  --pmft-row-open: rgba(148, 163, 184, 0.10);
  --pmft-strong-bg: rgba(34, 197, 94, 0.12);
  --pmft-watching-bg: rgba(239, 68, 68, 0.13);
  --pmft-working-bg: rgba(245, 158, 11, 0.13);
  --pmft-flat-bg: rgba(96, 165, 250, 0.13);
}
.pmft-intro {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
  margin-bottom: 1rem;
}
.pmft-kicker {
  font-size: 0.72rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--pmft-muted);
  margin-bottom: 0.2rem;
}
.pmft-title {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.2;
}
.pmft-copy {
  margin: 0.35rem 0 0;
  color: var(--pmft-muted);
  font-size: 0.78rem;
}
.pmft-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  justify-content: flex-end;
}
.pmft-chip {
  border: 1px solid var(--pmft-border);
  background: var(--pmft-surface);
  border-radius: 999px;
  padding: 0.35rem 0.7rem;
  font-size: 0.74rem;
  color: var(--pmft-muted);
}
.pmft-stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.55rem;
  margin-bottom: 1rem;
}
.pmft-stat-card {
  background: var(--pmft-surface);
  border: 1px solid var(--pmft-border);
  border-radius: 0.6rem;
  padding: 0.65rem 0.8rem;
}
.pmft-stat-label {
  font-size: 0.7rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--pmft-muted);
}
.pmft-stat-value {
  margin-top: 0.2rem;
  font-size: 1.1rem;
  font-weight: 700;
  line-height: 1.1;
}
.pmft-stat-note {
  margin-top: 0.28rem;
  color: var(--pmft-muted);
  font-size: 0.8rem;
}
.pmft-section + .pmft-section {
  margin-top: 1.4rem;
}
.pmft-section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
  margin-bottom: 0.65rem;
}
.pmft-section-title {
  margin: 0;
  font-size: 0.85rem;
}
.pmft-section-note {
  margin: 0.25rem 0 0;
  color: var(--pmft-muted);
  font-size: 0.83rem;
}
.pmft-section-meta {
  color: var(--pmft-muted);
  font-size: 0.8rem;
  text-align: right;
}
.pmft-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--pmft-border);
  border-radius: 1rem;
  background: var(--pmft-bg);
}
.pmft-table {
  width: 100%;
  min-width: 840px;
  border-collapse: collapse;
  font-size: 0.75rem;
}
.pmft-table th {
  text-align: left;
  padding: 0.8rem 0.9rem;
  font-size: 0.66rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--pmft-muted);
  border-bottom: 1px solid var(--pmft-border);
  background: var(--pmft-surface);
}
.pmft-table td {
  padding: 0.8rem 0.9rem;
  border-bottom: 1px solid var(--pmft-border);
  vertical-align: top;
}
.pmft-table tbody tr:last-child td {
  border-bottom: none;
}
.pmft-summary-row {
  cursor: pointer;
}
.pmft-summary-row:hover td {
  background: var(--pmft-row-hover);
}
.pmft-summary-row[aria-expanded="true"] td {
  background: var(--pmft-row-open);
}
.pmft-group-row td {
  padding: 0;
  border-bottom: 1px solid var(--pmft-border);
}
.pmft-group-row.pmft-group-strong td { background: var(--pmft-strong-bg); }
.pmft-group-row.pmft-group-watching td { background: var(--pmft-watching-bg); }
.pmft-group-row.pmft-group-working td { background: var(--pmft-working-bg); }
.pmft-group-row.pmft-group-flat td { background: var(--pmft-flat-bg); }
.pmft-group-button {
  width: 100%;
  border: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: left;
  padding: 0.85rem 0.9rem;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}
.pmft-group-left,
.pmft-group-right {
  display: flex;
  align-items: baseline;
  gap: 0.65rem;
  flex-wrap: wrap;
}
.pmft-group-chevron,
.pmft-row-chevron {
  display: inline-flex;
  width: 1rem;
  justify-content: center;
  color: var(--pmft-muted);
  font-weight: 700;
}
.pmft-group-name {
  font-weight: 700;
}
.pmft-group-subtitle,
.pmft-group-pnl {
  color: var(--pmft-muted);
  font-size: 0.78rem;
}
.pmft-symbol-wrap {
  display: flex;
  align-items: flex-start;
  gap: 0.45rem;
}
.pmft-symbol {
  font-weight: 700;
  letter-spacing: 0.01em;
}
.pmft-cell-main {
  color: var(--pmft-text);
}
.pmft-cell-sub {
  margin-top: 0.15rem;
  color: var(--pmft-muted);
  font-size: 0.76rem;
}
.pmft-strike-old {
  text-decoration: line-through;
  color: var(--pmft-muted);
  margin-right: 0.35rem;
}
.pmft-strike-new {
  color: var(--pmft-text);
  font-weight: 600;
}
.pmft-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  border: 1px solid var(--pmft-border);
  background: var(--pmft-surface);
  font-size: 0.7rem;
  color: var(--pmft-muted);
}
.pmft-sector {
  font-weight: 600;
}
.pmft-sector-sub {
  margin-top: 0.16rem;
  color: var(--pmft-muted);
  font-size: 0.76rem;
}
.pmft-detail-row td {
  padding: 0;
  background: var(--pmft-bg);
}
.pmft-detail-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1px;
  background: var(--pmft-border);
}
.pmft-detail-panel {
  background: var(--pmft-panel-bg);
  padding: 1rem 1.05rem;
}
.pmft-panel-title {
  margin: 0 0 0.75rem;
  font-size: 0.66rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--pmft-muted);
}
.pmft-detail-line + .pmft-detail-line,
.pmft-metric-grid,
.pmft-roll-ladder,
.pmft-roll-history,
.pmft-zone-stack {
  margin-top: 0.5rem;
}
.pmft-label {
  color: var(--pmft-muted);
  margin-right: 0.35rem;
}
.pmft-value-link {
  color: var(--pmft-link);
  font-weight: 600;
}
.pmft-inline-note {
  color: var(--pmft-muted);
  font-size: 0.74rem;
}
.pmft-roll-ladder {
  display: flex;
  flex-wrap: wrap;
  gap: 0.42rem;
}
.pmft-roll-done,
.pmft-roll-next,
.pmft-roll-pending {
  display: inline-flex;
  align-items: center;
  padding: 0.12rem 0.45rem;
  border-radius: 999px;
  border: 1px solid var(--pmft-border);
  font-size: 0.75rem;
}
.pmft-roll-done {
  color: var(--pmft-muted);
  text-decoration: line-through;
}
.pmft-roll-next {
  color: var(--pmft-caution);
  font-weight: 700;
}
.pmft-roll-pending {
  color: var(--pmft-muted);
}
.pmft-zone + .pmft-zone,
.pmft-roll-history-line + .pmft-roll-history-line {
  margin-top: 0.4rem;
}
.pmft-zone-sub,
.pmft-roll-history-line {
  color: var(--pmft-muted);
  font-size: 0.76rem;
}
.pmft-metric-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.65rem;
}
.pmft-metric-label {
  font-size: 0.65rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--pmft-muted);
}
.pmft-metric-value {
  margin-top: 0.12rem;
  font-weight: 700;
}
.pmft-positive { color: var(--pmft-positive); }
.pmft-negative { color: var(--pmft-negative); }
.pmft-caution { color: var(--pmft-caution); }
.pmft-neutral,
.pmft-muted,
.pmft-empty {
  color: var(--pmft-muted);
}
.pmft-empty td {
  color: var(--pmft-muted);
  font-style: italic;
}
@media (max-width: 960px) {
  .pmft-intro,
  .pmft-section-head {
    flex-direction: column;
    align-items: flex-start;
  }
  .pmft-chip-row {
    justify-content: flex-start;
  }
  .pmft-section-meta {
    text-align: left;
  }
  .pmft-detail-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 600px) {
  .pmft-trades {
    margin: 1rem 0;
    padding: 0;
    font-size: 0.72rem;
  }
  .pmft-title {
    font-size: 0.85rem;
    word-break: break-word;
  }
  .pmft-stat-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.4rem;
  }
  .pmft-stat-card {
    padding: 0.5rem 0.6rem;
  }
  .pmft-stat-value {
    font-size: 0.95rem;
  }
  .pmft-table {
    min-width: 600px;
    font-size: 0.68rem;
  }
  .pmft-table th,
  .pmft-table td {
    padding: 0.5rem 0.45rem;
  }
  .pmft-group-button {
    padding: 0.65rem 0.5rem;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.3rem;
  }
  .pmft-detail-panel {
    padding: 0.7rem;
  }
  .pmft-chip {
    padding: 0.25rem 0.5rem;
    font-size: 0.68rem;
  }
}
</style>

<!-- GENERATED by generate_wiki_forward_test.py — 2026-04-08 10:31:41 -->

<div class="pmft-trades">
  <div class="pmft-intro">
    <div>
      <div class="pmft-kicker">Live Tracker Snapshot</div>
      <p class="pmft-title">Plan M short forward-test trade ledger</p>
      <p class="pmft-copy">This block is generated from <code>short_tracker.json</code>. Current tracker totals are 11 open, 16 closed, and +$75,121 combined P&amp;L.</p>
    </div>
    <div class="pmft-chip-row">
      <span class="pmft-chip">Click row: expand detail</span>
      <span class="pmft-chip">Click category: collapse group</span>
    </div>
  </div>

  <div class="pmft-stat-grid">
    <div class="pmft-stat-card"><div class="pmft-stat-label">Open positions</div><div class="pmft-stat-value pmft-positive">11</div><div class="pmft-stat-note">Unrealized <span class="pmft-positive">+$18,491</span></div></div>
    <div class="pmft-stat-card"><div class="pmft-stat-label">Closed trades</div><div class="pmft-stat-value pmft-positive">16</div><div class="pmft-stat-note">Realized <span class="pmft-positive">+$56,630</span></div></div>
    <div class="pmft-stat-card"><div class="pmft-stat-label">Closed win rate</div><div class="pmft-stat-value pmft-positive">81%</div><div class="pmft-stat-note">13 winners &middot; 3 losers</div></div>
    <div class="pmft-stat-card"><div class="pmft-stat-label">Average closed hold</div><div class="pmft-stat-value">8.3d</div><div class="pmft-stat-note">Based on realized trades only</div></div>
  </div>

  <section class="pmft-section">
    <div class="pmft-section-head">
      <div>
        <p class="pmft-section-title">Open positions</p>
        <p class="pmft-section-note">Grouped the same way as the daily dashboard: strong, watching, working, then flat.</p>
      </div>
      <div class="pmft-section-meta">Unrealized <span class="pmft-positive">+$18,491</span></div>
    </div>
    <div class="pmft-table-wrap">
      <table class="pmft-table">
        <thead>
          <tr><th>Ticker</th><th>Entry</th><th>Held</th><th>Stock Move</th><th>Option</th><th>P&amp;L</th><th>Sector</th></tr>
        </thead>
        <tbody>
          <tr class="pmft-group-row pmft-group-strong"><td colspan="7">
            <button id="pmft-group-btn-strong" class="pmft-group-button" type="button" aria-expanded="true" onclick="if(window.pmftToggleGroup){pmftToggleGroup('strong')}else{(function(btn,group){var expanded=btn.getAttribute('aria-expanded')==='true';btn.setAttribute('aria-expanded',expanded?'false':'true');var chevron=btn.querySelector('.pmft-group-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';document.querySelectorAll('[data-group="'+group+'"]').forEach(function(row){if(row.classList.contains('pmft-detail-row')){row.hidden=expanded||row.dataset.open!=='true';}else{row.hidden=expanded;}});})(this,'strong')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleGroupFromKey){pmftToggleGroupFromKey(event,'strong')}else{this.click();}}"><span class="pmft-group-left"><span class="pmft-group-chevron">&#x25BE;</span><span class="pmft-group-name">Strong</span><span class="pmft-group-subtitle">&gt; +15% risk</span></span><span class="pmft-group-right"><span class="pmft-group-subtitle">8 positions</span><span class="pmft-group-pnl pmft-positive">+$21,571</span></span></button>
          </td></tr>
          <tr id="pmft-summary-open-strong-1" class="pmft-summary-row"  data-group="strong" aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('open-strong-1')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'open-strong-1')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'open-strong-1')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">CEG</div><div class="pmft-cell-sub">3 rolls &middot; +$4,560 credits</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-25</div><div class="pmft-cell-sub">signal Mar 23, 2026</div></td>
            <td><div class="pmft-cell-main">14d</div><div class="pmft-cell-sub">37d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$306.38 &rarr; $285.50</div><div class="pmft-cell-sub pmft-positive">-6.8%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-old">$370p</span><span class="pmft-strike-new">$320p</span></div><div class="pmft-cell-sub">$67.60 &rarr; $39.95 &middot; &delta; 0.82 &middot; 1ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$4,555</div><div class="pmft-cell-sub pmft-positive">+130.1%</div></td>
            <td><div class="pmft-sector">Utilities</div><div class="pmft-sector-sub">XLU</div></td>
          </tr>
          <tr id="pmft-detail-open-strong-1" class="pmft-detail-row" data-group="strong" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 23, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Utilities</span> <span class="pmft-inline-note">(XLU)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $14.15</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 50</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 48</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 56</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>230 OI</span> <span class="pmft-inline-note">&middot; spread 4.4%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$306.38</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-old">$370p</span><span class="pmft-strike-new">$320p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$67.60</span> <span class="pmft-inline-note">&rarr;</span> <span>$39.95</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>1 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.82 &middot; 51d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $334.68</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $348.83</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$254.00</span> <span class="pmft-inline-note"> (11.0% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$204.87</span> <span class="pmft-inline-note"> (28.2% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-done">&circlearrowright;1 $299.31</span><span class="pmft-roll-done">&circlearrowright;2 $285.15</span><span class="pmft-roll-done">&circlearrowright;3 $271.00</span><span class="pmft-roll-next">&circlearrowright;4 $256.86</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$243.30&ndash;$254.00</span></div><div class="pmft-zone-sub">Undated &middot; 17.1% from entry &middot; $52.38</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$188.01&ndash;$204.87</span></div><div class="pmft-zone-sub">Undated &middot; 33.1% from entry &middot; $101.51</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$161.35&ndash;$189.79</span></div><div class="pmft-zone-sub">Undated &middot; 38.1% from entry &middot; $116.59</div></div>
</div>
                  <div class="pmft-roll-history">
<div class="pmft-roll-history-line">Roll #1 on 2026-03-26: $370p &rarr; $340p, credit $29.00/ct</div>
<div class="pmft-roll-history-line">Roll #2 on 2026-03-31: $340p &rarr; $330p, credit $8.65/ct</div>
<div class="pmft-roll-history-line">Roll #3 on 2026-04-02: $330p &rarr; $320p, credit $7.95/ct</div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Strong performer. The stock has moved materially in the trade&#x27;s favor. Next roll sits at $256.86 (-10.0% from current). OB1 at $254.00 is 11.0% away.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">14d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">37d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$13.59</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$1.18</div></div>
<div><div class="pmft-metric-label">Risk removed</div><div class="pmft-metric-value pmft-positive">67%</div></div>
<div><div class="pmft-metric-label">Next roll</div><div class="pmft-metric-value pmft-caution">$256.86</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-open-strong-2" class="pmft-summary-row"  data-group="strong" aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('open-strong-2')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'open-strong-2')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'open-strong-2')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">ADBE</div><div class="pmft-cell-sub">2 rolls &middot; +$4,462 credits</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-16</div><div class="pmft-cell-sub">signal Mar 16, 2026</div></td>
            <td><div class="pmft-cell-main">23d</div><div class="pmft-cell-sub">9d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$254.35 &rarr; $242.92</div><div class="pmft-cell-sub pmft-positive">-4.5%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-old">$275p</span><span class="pmft-strike-new">$250p</span></div><div class="pmft-cell-sub">$24.10 &rarr; $9.62 &middot; &delta; 0.79 &middot; 2ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$4,454</div><div class="pmft-cell-sub pmft-positive">+127.3%</div></td>
            <td><div class="pmft-sector">Information Technology</div><div class="pmft-sector-sub">XLK</div></td>
          </tr>
          <tr id="pmft-detail-open-strong-2" class="pmft-detail-row" data-group="strong" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 16, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Information Technology</span> <span class="pmft-inline-note">(XLK)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">-2.4%</span> <span class="pmft-inline-note">&middot; ATR $9.93</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 38</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 33</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 32</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>576 OI</span> <span class="pmft-inline-note">&middot; spread 9.8%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$254.35</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-old">$275p</span><span class="pmft-strike-new">$250p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$24.10</span> <span class="pmft-inline-note">&rarr;</span> <span>$9.62</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>2 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.79 &middot; 32d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $274.21</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $284.14</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-done">&circlearrowright;1 $249.38</span><span class="pmft-roll-done">&circlearrowright;2 $239.45</span><span class="pmft-roll-next">&circlearrowright;3 $229.53</span><span class="pmft-roll-pending">&circlearrowright;4 $219.59</span></div>
                  <div class="pmft-roll-history">
<div class="pmft-roll-history-line">Roll #1 on 2026-03-16: $275p &rarr; $255p, credit $18.58/ct</div>
<div class="pmft-roll-history-line">Roll #2 on 2026-03-24: $255p &rarr; $250p, credit $3.73/ct</div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Strong performer. The stock has moved materially in the trade&#x27;s favor. Next roll sits at $229.53 (-5.5% from current).</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">23d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">9d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$8.33</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$1.79</div></div>
<div><div class="pmft-metric-label">Risk removed</div><div class="pmft-metric-value pmft-positive">93%</div></div>
<div><div class="pmft-metric-label">Next roll</div><div class="pmft-metric-value pmft-caution">$229.53</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-open-strong-3" class="pmft-summary-row"  data-group="strong" aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('open-strong-3')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'open-strong-3')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'open-strong-3')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">EQT</div><div class="pmft-cell-sub">1 roll &middot; +$3,290 credits</div></div></div></td>
            <td><div class="pmft-cell-main">2026-04-07</div><div class="pmft-cell-sub">signal Apr 06, 2026</div></td>
            <td><div class="pmft-cell-main">1d</div><div class="pmft-cell-sub">37d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$60.40 &rarr; $59.44</div><div class="pmft-cell-sub pmft-positive">-1.6%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-old">$70p</span><span class="pmft-strike-new">$65p</span></div><div class="pmft-cell-sub">$10.25 &rarr; $6.55 &middot; &delta; 0.85 &middot; 7ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$3,272</div><div class="pmft-cell-sub pmft-positive">+93.5%</div></td>
            <td><div class="pmft-sector">Energy</div><div class="pmft-sector-sub">XLE</div></td>
          </tr>
          <tr id="pmft-detail-open-strong-3" class="pmft-detail-row" data-group="strong" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Apr 06, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Energy</span> <span class="pmft-inline-note">(XLE)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $2.76</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 42</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 54</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 60</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>147 OI</span> <span class="pmft-inline-note">&middot; spread 14.6%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$60.40</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-old">$70p</span><span class="pmft-strike-new">$65p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$10.25</span> <span class="pmft-inline-note">&rarr;</span> <span>$6.55</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>7 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.85 &middot; 38d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $65.92</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $68.68</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$55.68</span> <span class="pmft-inline-note"> (6.3% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$50.93</span> <span class="pmft-inline-note"> (14.3% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-done">&circlearrowright;1 $59.02</span><span class="pmft-roll-next">&circlearrowright;2 $56.26</span><span class="pmft-roll-pending">&circlearrowright;3 $53.50</span><span class="pmft-roll-pending">&circlearrowright;4 $50.74</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$54.01&ndash;$55.68</span></div><div class="pmft-zone-sub">Undated &middot; 7.8% from entry &middot; $4.72</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$49.26&ndash;$50.93</span></div><div class="pmft-zone-sub">Undated &middot; 15.7% from entry &middot; $9.47</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$48.47&ndash;$50.50</span></div><div class="pmft-zone-sub">Undated &middot; 16.4% from entry &middot; $9.90</div></div>
</div>
                  <div class="pmft-roll-history">
<div class="pmft-roll-history-line">Roll #1 on 2026-04-08: $70p &rarr; $65p, credit $4.70/ct</div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Strong performer. The stock has moved materially in the trade&#x27;s favor. Next roll sits at $56.26 (-5.3% from current). OB1 at $55.68 is 6.3% away.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">1d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">37d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$3.82</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$1.90</div></div>
<div><div class="pmft-metric-label">Risk removed</div><div class="pmft-metric-value pmft-positive">46%</div></div>
<div><div class="pmft-metric-label">Next roll</div><div class="pmft-metric-value pmft-caution">$56.26</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-open-strong-4" class="pmft-summary-row"  data-group="strong" aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('open-strong-4')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'open-strong-4')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'open-strong-4')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">PYPL</div><div class="pmft-cell-sub">1 roll &middot; +$2,704 credits</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-17</div><div class="pmft-cell-sub">signal Mar 17, 2026</div></td>
            <td><div class="pmft-cell-main">22d</div><div class="pmft-cell-sub">9d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-negative">$45.42 &rarr; $46.13</div><div class="pmft-cell-sub pmft-negative">+1.6%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-old">$50p</span><span class="pmft-strike-new">$48p</span></div><div class="pmft-cell-sub">$5.05 &rarr; $1.92 &middot; &delta; 0.77 &middot; 13ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$2,670</div><div class="pmft-cell-sub pmft-positive">+76.3%</div></td>
            <td><div class="pmft-sector">Financials</div><div class="pmft-sector-sub">XLF</div></td>
          </tr>
          <tr id="pmft-detail-open-strong-4" class="pmft-detail-row" data-group="strong" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 17, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Financials</span> <span class="pmft-inline-note">(XLF)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $1.63</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 47</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 32</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 33</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>4,359 OI</span> <span class="pmft-inline-note">&middot; spread 17.8%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$45.42</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-old">$50p</span><span class="pmft-strike-new">$48p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$5.05</span> <span class="pmft-inline-note">&rarr;</span> <span>$1.92</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>13 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.77 &middot; 31d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $48.68</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $50.31</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$40.28</span> <span class="pmft-inline-note"> (12.7% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-done">&circlearrowright;1 $44.61</span><span class="pmft-roll-next">&circlearrowright;2 $42.98</span><span class="pmft-roll-pending">&circlearrowright;3 $41.34</span><span class="pmft-roll-pending">&circlearrowright;4 $39.72</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$38.46&ndash;$40.28</span></div><div class="pmft-zone-sub">Undated &middot; 11.3% from entry &middot; $5.14</div></div>
</div>
                  <div class="pmft-roll-history">
<div class="pmft-roll-history-line">Roll #1 on 2026-03-18: $50p &rarr; $48p, credit $2.08/ct</div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Strong performer. The stock has moved materially in the trade&#x27;s favor. Next roll sits at $42.98 (-6.8% from current). OB1 at $40.28 is 12.7% away.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">22d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">9d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$4.60</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$3.43</div></div>
<div><div class="pmft-metric-label">Risk removed</div><div class="pmft-metric-value pmft-positive">41%</div></div>
<div><div class="pmft-metric-label">Next roll</div><div class="pmft-metric-value pmft-caution">$42.98</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-open-strong-5" class="pmft-summary-row"  data-group="strong" aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('open-strong-5')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'open-strong-5')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'open-strong-5')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">SBUX</div><div class="pmft-cell-sub">1 roll &middot; +$2,443 credits</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-25</div><div class="pmft-cell-sub">signal Mar 19, 2026</div></td>
            <td><div class="pmft-cell-main">14d</div><div class="pmft-cell-sub">37d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-negative">$92.47 &rarr; $96.72</div><div class="pmft-cell-sub pmft-negative">+4.6%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-old">$105p</span><span class="pmft-strike-new">$100p</span></div><div class="pmft-cell-sub">$13.18 &rarr; $6.55 &middot; &delta; 0.81 &middot; 7ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$2,404</div><div class="pmft-cell-sub pmft-positive">+68.7%</div></td>
            <td><div class="pmft-sector">Consumer Discretionary</div><div class="pmft-sector-sub">XLY</div></td>
          </tr>
          <tr id="pmft-detail-open-strong-5" class="pmft-detail-row" data-group="strong" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 19, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Consumer Discretionary</span> <span class="pmft-inline-note">(XLY)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $2.90</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 41</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 51</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 50</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>148 OI</span> <span class="pmft-inline-note">&middot; spread 16.3%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$92.47</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-old">$105p</span><span class="pmft-strike-new">$100p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$13.18</span> <span class="pmft-inline-note">&rarr;</span> <span>$6.55</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>7 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.81 &middot; 51d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $98.27</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $101.17</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$84.96</span> <span class="pmft-inline-note"> (12.2% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$84.00</span> <span class="pmft-inline-note"> (13.2% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-done">&circlearrowright;1 $91.02</span><span class="pmft-roll-next">&circlearrowright;2 $88.12</span><span class="pmft-roll-pending">&circlearrowright;3 $85.22</span><span class="pmft-roll-pending">&circlearrowright;4 $82.32</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$83.02&ndash;$84.96</span></div><div class="pmft-zone-sub">Undated &middot; 8.1% from entry &middot; $7.52</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$81.97&ndash;$84.00</span></div><div class="pmft-zone-sub">Undated &middot; 9.2% from entry &middot; $8.47</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$76.15&ndash;$83.27</span></div><div class="pmft-zone-sub">Undated &middot; 10.0% from entry &middot; $9.20</div></div>
</div>
                  <div class="pmft-roll-history">
<div class="pmft-roll-history-line">Roll #1 on 2026-03-26: $105p &rarr; $100p, credit $3.49/ct</div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Strong performer. The stock has moved materially in the trade&#x27;s favor. Next roll sits at $88.12 (-8.9% from current). OB1 at $84.96 is 12.2% away.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">14d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">37d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$7.43</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$6.12</div></div>
<div><div class="pmft-metric-label">Risk removed</div><div class="pmft-metric-value pmft-positive">26%</div></div>
<div><div class="pmft-metric-label">Next roll</div><div class="pmft-metric-value pmft-caution">$88.12</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-open-strong-6" class="pmft-summary-row"  data-group="strong" aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('open-strong-6')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'open-strong-6')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'open-strong-6')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">INTU</div><div class="pmft-cell-sub">1 roll &middot; +$1,895 credits</div></div></div></td>
            <td><div class="pmft-cell-main">2026-04-03</div><div class="pmft-cell-sub">signal Mar 27, 2026</div></td>
            <td><div class="pmft-cell-main">5d</div><div class="pmft-cell-sub">37d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$422.48 &rarr; $399.27</div><div class="pmft-cell-sub pmft-positive">-5.5%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-old">$490p</span><span class="pmft-strike-new">$470p</span></div><div class="pmft-cell-sub">$73.10 &rarr; $73.35 &middot; &delta; 0.82 &middot; 1ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$1,892</div><div class="pmft-cell-sub pmft-positive">+54.1%</div></td>
            <td><div class="pmft-sector">Information Technology</div><div class="pmft-sector-sub">XLK</div></td>
          </tr>
          <tr id="pmft-detail-open-strong-6" class="pmft-detail-row" data-group="strong" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 27, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Information Technology</span> <span class="pmft-inline-note">(XLK)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $19.59</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 43</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 36</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 35</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>34 OI</span> <span class="pmft-inline-note">&middot; spread 12.0%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$422.48</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-old">$490p</span><span class="pmft-strike-new">$470p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$73.10</span> <span class="pmft-inline-note">&rarr;</span> <span>$73.35</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>1 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.82 &middot; 42d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $461.66</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $481.25</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$374.94</span> <span class="pmft-inline-note"> (6.1% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$371.66</span> <span class="pmft-inline-note"> (6.9% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-done">&circlearrowright;1 $412.69</span><span class="pmft-roll-next">&circlearrowright;2 $393.10</span><span class="pmft-roll-pending">&circlearrowright;3 $373.50</span><span class="pmft-roll-pending">&circlearrowright;4 $353.92</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$349.00&ndash;$374.94</span></div><div class="pmft-zone-sub">Undated &middot; 11.3% from entry &middot; $47.54</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$352.63&ndash;$371.66</span></div><div class="pmft-zone-sub">Undated &middot; 12.0% from entry &middot; $50.82</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$355.22&ndash;$370.40</span></div><div class="pmft-zone-sub">Undated &middot; 12.3% from entry &middot; $52.08</div></div>
</div>
                  <div class="pmft-roll-history">
<div class="pmft-roll-history-line">Roll #1 on 2026-04-06: $490p &rarr; $470p, credit $18.95/ct</div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Strong performer. The stock has moved materially in the trade&#x27;s favor. Next roll sits at $393.10 (-1.5% from current). OB1 at $374.94 is 6.1% away.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">5d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">37d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$6.26</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$0.03</div></div>
<div><div class="pmft-metric-label">Risk removed</div><div class="pmft-metric-value pmft-positive">26%</div></div>
<div><div class="pmft-metric-label">Next roll</div><div class="pmft-metric-value pmft-caution">$393.10</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-open-strong-7" class="pmft-summary-row"  data-group="strong" aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('open-strong-7')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'open-strong-7')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'open-strong-7')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">PLTR</div><div class="pmft-cell-sub">1 roll &middot; +$1,344 credits</div></div></div></td>
            <td><div class="pmft-cell-main">2026-04-01</div><div class="pmft-cell-sub">signal Mar 30, 2026</div></td>
            <td><div class="pmft-cell-main">7d</div><div class="pmft-cell-sub">37d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$146.28 &rarr; $144.94</div><div class="pmft-cell-sub pmft-positive">-0.9%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-old">$180p</span><span class="pmft-strike-new">$175p</span></div><div class="pmft-cell-sub">$35.33 &rarr; $31.42 &middot; &delta; 0.84 &middot; 3ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$1,336</div><div class="pmft-cell-sub pmft-positive">+38.2%</div></td>
            <td><div class="pmft-sector">Information Technology</div><div class="pmft-sector-sub">XLK</div></td>
          </tr>
          <tr id="pmft-detail-open-strong-7" class="pmft-detail-row" data-group="strong" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 30, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Information Technology</span> <span class="pmft-inline-note">(XLK)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $6.73</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 47</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 46</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 62</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>5,180 OI</span> <span class="pmft-inline-note">&middot; spread 1.8%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$146.28</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-old">$180p</span><span class="pmft-strike-new">$175p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$35.33</span> <span class="pmft-inline-note">&rarr;</span> <span>$31.42</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>3 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.84 &middot; 44d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $159.74</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $166.47</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$136.32</span> <span class="pmft-inline-note"> (5.9% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$133.56</span> <span class="pmft-inline-note"> (7.9% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-done">&circlearrowright;1 $142.91</span><span class="pmft-roll-next">&circlearrowright;2 $136.19</span><span class="pmft-roll-pending">&circlearrowright;3 $129.45</span><span class="pmft-roll-pending">&circlearrowright;4 $122.72</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$128.51&ndash;$136.32</span></div><div class="pmft-zone-sub">Undated &middot; 6.8% from entry &middot; $9.96</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$126.23&ndash;$133.56</span></div><div class="pmft-zone-sub">Undated &middot; 8.7% from entry &middot; $12.72</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$118.93&ndash;$132.85</span></div><div class="pmft-zone-sub">Undated &middot; 9.2% from entry &middot; $13.43</div></div>
</div>
                  <div class="pmft-roll-history">
<div class="pmft-roll-history-line">Roll #1 on 2026-04-02: $180p &rarr; $175p, credit $4.48/ct</div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Strong performer. The stock has moved materially in the trade&#x27;s favor. Next roll sits at $136.19 (-6.0% from current). OB1 at $136.32 is 5.9% away.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">7d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">37d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$5.67</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$6.84</div></div>
<div><div class="pmft-metric-label">Risk removed</div><div class="pmft-metric-value pmft-positive">13%</div></div>
<div><div class="pmft-metric-label">Next roll</div><div class="pmft-metric-value pmft-caution">$136.19</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-open-strong-8" class="pmft-summary-row"  data-group="strong" aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('open-strong-8')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'open-strong-8')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'open-strong-8')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">FISV</div><div class="pmft-cell-sub">No rolls</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-16</div><div class="pmft-cell-sub">signal Mar 11, 2026</div></td>
            <td><div class="pmft-cell-main">23d</div><div class="pmft-cell-sub">37d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$57.05 &rarr; $57.03</div><div class="pmft-cell-sub pmft-positive">-0.0%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-new">$65p</span></div><div class="pmft-cell-sub">$7.94 &rarr; $9.05 &middot; &delta; 0.81 &middot; 9ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$987</div><div class="pmft-cell-sub pmft-positive">+28.2%</div></td>
            <td><div class="pmft-sector">Information Technology</div><div class="pmft-sector-sub">XLK</div></td>
          </tr>
          <tr id="pmft-detail-open-strong-8" class="pmft-detail-row" data-group="strong" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 11, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Information Technology</span> <span class="pmft-inline-note">(XLK)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">-10.0%</span> <span class="pmft-inline-note">&middot; ATR $2.23</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 37</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 24</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 33</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>685 OI</span> <span class="pmft-inline-note">&middot; spread 4.7%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$57.05</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-new">$65p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$7.94</span> <span class="pmft-inline-note">&rarr;</span> <span>$9.05</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>9 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.81 &middot; 32d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $61.51</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $63.74</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-next">&circlearrowright;1 $55.93</span><span class="pmft-roll-pending">&circlearrowright;2 $53.70</span><span class="pmft-roll-pending">&circlearrowright;3 $51.47</span><span class="pmft-roll-pending">&circlearrowright;4 $49.24</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Strong performer. The stock has moved materially in the trade&#x27;s favor. Next roll sits at $55.93 (-1.9% from current).</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">23d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">37d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$7.26</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$4.40</div></div>
<div><div class="pmft-metric-label">Next roll</div><div class="pmft-metric-value pmft-caution">$55.93</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr class="pmft-group-row pmft-group-watching"><td colspan="7">
            <button id="pmft-group-btn-watching" class="pmft-group-button" type="button" aria-expanded="true" onclick="if(window.pmftToggleGroup){pmftToggleGroup('watching')}else{(function(btn,group){var expanded=btn.getAttribute('aria-expanded')==='true';btn.setAttribute('aria-expanded',expanded?'false':'true');var chevron=btn.querySelector('.pmft-group-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';document.querySelectorAll('[data-group="'+group+'"]').forEach(function(row){if(row.classList.contains('pmft-detail-row')){row.hidden=expanded||row.dataset.open!=='true';}else{row.hidden=expanded;}});})(this,'watching')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleGroupFromKey){pmftToggleGroupFromKey(event,'watching')}else{this.click();}}"><span class="pmft-group-left"><span class="pmft-group-chevron">&#x25BE;</span><span class="pmft-group-name">Watching</span><span class="pmft-group-subtitle">&lt; &minus;15% risk</span></span><span class="pmft-group-right"><span class="pmft-group-subtitle">2 positions</span><span class="pmft-group-pnl pmft-negative">$-2,733</span></span></button>
          </td></tr>
          <tr id="pmft-summary-open-watching-1" class="pmft-summary-row"  data-group="watching" aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('open-watching-1')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'open-watching-1')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'open-watching-1')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">MRSH</div><div class="pmft-cell-sub">No rolls</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-17</div><div class="pmft-cell-sub">signal Mar 11, 2026</div></td>
            <td><div class="pmft-cell-main">22d</div><div class="pmft-cell-sub">9d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-negative">$173.76 &rarr; $175.00</div><div class="pmft-cell-sub pmft-negative">+0.7%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-new">$190p</span></div><div class="pmft-cell-sub">$17.55 &rarr; $16.35 &middot; &delta; 0.85 &middot; 5ct</div></td>
            <td><div class="pmft-cell-main pmft-negative">$-606</div><div class="pmft-cell-sub pmft-negative">-17.3%</div></td>
            <td><div class="pmft-sector">Financials</div><div class="pmft-sector-sub">XLF</div></td>
          </tr>
          <tr id="pmft-detail-open-watching-1" class="pmft-detail-row" data-group="watching" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 11, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Financials</span> <span class="pmft-inline-note">(XLF)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $4.02</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 40</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 39</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 40</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>75 OI</span> <span class="pmft-inline-note">&middot; spread 17.7%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$173.76</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-new">$190p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$17.55</span> <span class="pmft-inline-note">&rarr;</span> <span>$16.35</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>5 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.85 &middot; 31d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $181.80</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $185.82</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$156.65</span> <span class="pmft-inline-note"> (10.5% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$155.20</span> <span class="pmft-inline-note"> (11.3% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-next">&circlearrowright;1 $171.75</span><span class="pmft-roll-pending">&circlearrowright;2 $167.73</span><span class="pmft-roll-pending">&circlearrowright;3 $163.71</span><span class="pmft-roll-pending">&circlearrowright;4 $159.69</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$148.13&ndash;$156.65</span></div><div class="pmft-zone-sub">Undated &middot; 9.8% from entry &middot; $17.11</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$150.78&ndash;$155.20</span></div><div class="pmft-zone-sub">Undated &middot; 10.7% from entry &middot; $18.56</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$151.86&ndash;$154.57</span></div><div class="pmft-zone-sub">Undated &middot; 11.0% from entry &middot; $19.19</div></div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-negative">Watching closely. Position is underwater and may need attention. Next roll sits at $171.75 (-1.9% from current). OB1 at $156.65 is 10.5% away.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">22d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">9d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$5.10</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$2.53</div></div>
<div><div class="pmft-metric-label">Next roll</div><div class="pmft-metric-value pmft-caution">$171.75</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-open-watching-2" class="pmft-summary-row"  data-group="watching" aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('open-watching-2')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'open-watching-2')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'open-watching-2')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">ETSY</div><div class="pmft-cell-sub">No rolls</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-17</div><div class="pmft-cell-sub">signal Mar 16, 2026</div></td>
            <td><div class="pmft-cell-main">22d</div><div class="pmft-cell-sub">9d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-negative">$53.14 &rarr; $54.89</div><div class="pmft-cell-sub pmft-negative">+3.3%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-new">$60p</span></div><div class="pmft-cell-sub">$7.82 &rarr; $5.47 &middot; &delta; 0.74 &middot; 9ct</div></td>
            <td><div class="pmft-cell-main pmft-negative">$-2,127</div><div class="pmft-cell-sub pmft-negative">-60.8%</div></td>
            <td><div class="pmft-sector">Consumer Discretionary</div><div class="pmft-sector-sub">XLY</div></td>
          </tr>
          <tr id="pmft-detail-open-watching-2" class="pmft-detail-row" data-group="watching" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 16, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Consumer Discretionary</span> <span class="pmft-inline-note">(XLY)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $2.56</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 48</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 47</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 44</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>191 OI</span> <span class="pmft-inline-note">&middot; spread 7.0%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$53.14</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-new">$60p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$7.82</span> <span class="pmft-inline-note">&rarr;</span> <span>$5.47</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>9 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.74 &middot; 31d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $58.26</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $60.82</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$46.87</span> <span class="pmft-inline-note"> (14.6% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$46.34</span> <span class="pmft-inline-note"> (15.6% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-next">&circlearrowright;1 $51.86</span><span class="pmft-roll-pending">&circlearrowright;2 $49.30</span><span class="pmft-roll-pending">&circlearrowright;3 $46.74</span><span class="pmft-roll-pending">&circlearrowright;4 $44.18</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$41.51&ndash;$46.87</span></div><div class="pmft-zone-sub">Undated &middot; 11.8% from entry &middot; $6.27</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$44.00&ndash;$46.34</span></div><div class="pmft-zone-sub">Undated &middot; 12.8% from entry &middot; $6.80</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$40.05&ndash;$44.94</span></div><div class="pmft-zone-sub">Undated &middot; 15.4% from entry &middot; $8.20</div></div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-negative">Watching closely. Position is underwater and may need attention. Next roll sits at $51.86 (-5.5% from current). OB1 at $46.87 is 14.6% away.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">22d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">9d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$11.73</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$5.38</div></div>
<div><div class="pmft-metric-label">Next roll</div><div class="pmft-metric-value pmft-caution">$51.86</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr class="pmft-group-row pmft-group-flat"><td colspan="7">
            <button id="pmft-group-btn-flat" class="pmft-group-button" type="button" aria-expanded="true" onclick="if(window.pmftToggleGroup){pmftToggleGroup('flat')}else{(function(btn,group){var expanded=btn.getAttribute('aria-expanded')==='true';btn.setAttribute('aria-expanded',expanded?'false':'true');var chevron=btn.querySelector('.pmft-group-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';document.querySelectorAll('[data-group="'+group+'"]').forEach(function(row){if(row.classList.contains('pmft-detail-row')){row.hidden=expanded||row.dataset.open!=='true';}else{row.hidden=expanded;}});})(this,'flat')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleGroupFromKey){pmftToggleGroupFromKey(event,'flat')}else{this.click();}}"><span class="pmft-group-left"><span class="pmft-group-chevron">&#x25BE;</span><span class="pmft-group-name">Flat</span><span class="pmft-group-subtitle">&minus;15 to 0% risk</span></span><span class="pmft-group-right"><span class="pmft-group-subtitle">1 position</span><span class="pmft-group-pnl pmft-negative">$-346</span></span></button>
          </td></tr>
          <tr id="pmft-summary-open-flat-1" class="pmft-summary-row"  data-group="flat" aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('open-flat-1')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'open-flat-1')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'open-flat-1')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">OKTA</div><div class="pmft-cell-sub">No rolls</div></div></div></td>
            <td><div class="pmft-cell-main">2026-04-01</div><div class="pmft-cell-sub">signal Mar 26, 2026</div></td>
            <td><div class="pmft-cell-main">7d</div><div class="pmft-cell-sub">37d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-negative">$78.71 &rarr; $79.06</div><div class="pmft-cell-sub pmft-negative">+0.4%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-new">$95p</span></div><div class="pmft-cell-sub">$16.98 &rarr; $16.30 &middot; &delta; 0.85 &middot; 5ct</div></td>
            <td><div class="pmft-cell-main pmft-negative">$-346</div><div class="pmft-cell-sub pmft-negative">-9.9%</div></td>
            <td><div class="pmft-sector">Information Technology</div><div class="pmft-sector-sub">XLK</div></td>
          </tr>
          <tr id="pmft-detail-open-flat-1" class="pmft-detail-row" data-group="flat" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 26, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Information Technology</span> <span class="pmft-inline-note">(XLK)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $3.77</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 50</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 45</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 44</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>118 OI</span> <span class="pmft-inline-note">&middot; spread 11.5%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$78.71</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-new">$95p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$16.98</span> <span class="pmft-inline-note">&rarr;</span> <span>$16.30</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>5 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.85 &middot; 44d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $86.25</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $90.02</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$73.55</span> <span class="pmft-inline-note"> (7.0% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$70.95</span> <span class="pmft-inline-note"> (10.3% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-next">&circlearrowright;1 $76.82</span><span class="pmft-roll-pending">&circlearrowright;2 $73.05</span><span class="pmft-roll-pending">&circlearrowright;3 $69.28</span><span class="pmft-roll-pending">&circlearrowright;4 $65.51</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$68.77&ndash;$73.55</span></div><div class="pmft-zone-sub">Undated &middot; 6.6% from entry &middot; $5.16</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$65.04&ndash;$70.95</span></div><div class="pmft-zone-sub">Undated &middot; 9.9% from entry &middot; $7.76</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$66.69&ndash;$70.79</span></div><div class="pmft-zone-sub">Undated &middot; 10.1% from entry &middot; $7.92</div></div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-muted">Flat. Position is slightly negative but within normal range. Next roll sits at $76.82 (-2.8% from current). OB1 at $73.55 is 7.0% away.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">7d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">37d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$1.75</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$4.24</div></div>
<div><div class="pmft-metric-label">Next roll</div><div class="pmft-metric-value pmft-caution">$76.82</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="pmft-section">
    <div class="pmft-section-head">
      <div>
        <p class="pmft-section-title">Closed trades</p>
        <p class="pmft-section-note">16 total &mdash; sorted by exit date descending.</p>
      </div>
      <div class="pmft-section-meta">Realized <span class="pmft-positive">+$56,630</span></div>
    </div>
    <div class="pmft-table-wrap">
      <table class="pmft-table">
        <thead>
          <tr><th>Ticker</th><th>Entry</th><th>Held</th><th>Stock Move</th><th>Option</th><th>P&amp;L</th><th>Sector</th></tr>
        </thead>
        <tbody>
          <tr id="pmft-summary-closed-1" class="pmft-summary-row"  aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('closed-1')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'closed-1')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'closed-1')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">GPN</div><div class="pmft-cell-sub">1 roll &middot; +$3,000 credits</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-16</div><div class="pmft-cell-sub">signal Mar 11, 2026</div></td>
            <td><div class="pmft-cell-main">23d</div><div class="pmft-cell-sub">37d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$68.30 &rarr; $66.00</div><div class="pmft-cell-sub pmft-positive">-3.4%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-old">$75p</span><span class="pmft-strike-new">$70p</span></div><div class="pmft-cell-sub">$7.07 &rarr; ? &middot; &delta; 0.76 &middot; 8ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$4,398</div><div class="pmft-cell-sub pmft-positive">+125.7%</div></td>
            <td><div class="pmft-sector">Information Technology</div><div class="pmft-sector-sub">XLK</div></td>
          </tr>
          <tr id="pmft-detail-closed-1" class="pmft-detail-row pmft-closed-detail" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 11, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Information Technology</span> <span class="pmft-inline-note">(XLK)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">-2.1%</span> <span class="pmft-inline-note">&middot; ATR $2.80</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 34</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 41</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 32</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>525 OI</span> <span class="pmft-inline-note">&middot; spread 7.9%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$68.30</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-old">$75p</span><span class="pmft-strike-new">$70p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$7.07</span> <span class="pmft-inline-note">&rarr;</span> <span>&mdash;</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>8 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.76 &middot; 32d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $73.90</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $76.70</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-done">&circlearrowright;1 $66.90</span><span class="pmft-roll-next">&circlearrowright;2 $64.10</span><span class="pmft-roll-pending">&circlearrowright;3 $61.30</span><span class="pmft-roll-pending">&circlearrowright;4 $58.50</span></div>
                  <div class="pmft-roll-history">
<div class="pmft-roll-history-line">Roll #1 on 2026-03-27: $75p &rarr; $70p, credit $3.75/ct</div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Closed winner. Exited via gap crap after 23 days for +$4,398.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">23d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">37d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$8.57</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$7.19</div></div>
<div><div class="pmft-metric-label">Risk removed</div><div class="pmft-metric-value pmft-positive">53%</div></div>
<div><div class="pmft-metric-label">Exit reason</div><div class="pmft-metric-value">gap crap</div></div>
<div><div class="pmft-metric-label">Exit date</div><div class="pmft-metric-value">2026-04-08</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-closed-2" class="pmft-summary-row"  aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('closed-2')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'closed-2')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'closed-2')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">PANW</div><div class="pmft-cell-sub">No rolls</div></div></div></td>
            <td><div class="pmft-cell-main">2026-04-01</div><div class="pmft-cell-sub">signal Mar 26, 2026</div></td>
            <td><div class="pmft-cell-main">7d</div><div class="pmft-cell-sub">37d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-negative">$160.32 &rarr; $173.18</div><div class="pmft-cell-sub pmft-negative">+8.0%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-new">$180p</span></div><div class="pmft-cell-sub">$21.35 &rarr; ? &middot; &delta; 0.78 &middot; 3ct</div></td>
            <td><div class="pmft-cell-main pmft-negative">$-3,009</div><div class="pmft-cell-sub pmft-negative">-86.0%</div></td>
            <td><div class="pmft-sector">Information Technology</div><div class="pmft-sector-sub">XLK</div></td>
          </tr>
          <tr id="pmft-detail-closed-2" class="pmft-detail-row pmft-closed-detail" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 26, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Information Technology</span> <span class="pmft-inline-note">(XLK)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $6.43</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 50</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 43</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 48</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>1,367 OI</span> <span class="pmft-inline-note">&middot; spread 14.5%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$160.32</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-new">$180p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$21.35</span> <span class="pmft-inline-note">&rarr;</span> <span>&mdash;</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>3 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.78 &middot; 44d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $173.18</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $179.61</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$147.52</span> <span class="pmft-inline-note"> (14.8% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$137.99</span> <span class="pmft-inline-note"> (20.3% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-next">&circlearrowright;1 $157.10</span><span class="pmft-roll-pending">&circlearrowright;2 $150.67</span><span class="pmft-roll-pending">&circlearrowright;3 $144.25</span><span class="pmft-roll-pending">&circlearrowright;4 $137.81</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$139.57&ndash;$147.52</span></div><div class="pmft-zone-sub">Undated &middot; 8.0% from entry &middot; $12.80</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$130.04&ndash;$137.99</span></div><div class="pmft-zone-sub">Undated &middot; 13.9% from entry &middot; $22.33</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$132.50&ndash;$136.69</span></div><div class="pmft-zone-sub">Undated &middot; 14.7% from entry &middot; $23.63</div></div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-negative">Closed loser. Exited via stop 2atr after 7 days for $-3,009.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">7d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">37d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$1.88</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$11.82</div></div>
<div><div class="pmft-metric-label">Exit reason</div><div class="pmft-metric-value">stop 2atr</div></div>
<div><div class="pmft-metric-label">Exit date</div><div class="pmft-metric-value">2026-04-08</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-closed-3" class="pmft-summary-row"  aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('closed-3')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'closed-3')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'closed-3')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">EXE</div><div class="pmft-cell-sub">No rolls</div></div></div></td>
            <td><div class="pmft-cell-main">2026-04-07</div><div class="pmft-cell-sub">signal Apr 02, 2026</div></td>
            <td><div class="pmft-cell-main">1d</div><div class="pmft-cell-sub">37d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$103.55 &rarr; $99.35</div><div class="pmft-cell-sub pmft-positive">-4.1%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-new">$110p</span></div><div class="pmft-cell-sub">$9.25 &rarr; ? &middot; &delta; 0.66 &middot; 6ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$1,663</div><div class="pmft-cell-sub pmft-positive">+47.5%</div></td>
            <td><div class="pmft-sector">Energy</div><div class="pmft-sector-sub">XLE</div></td>
          </tr>
          <tr id="pmft-detail-closed-3" class="pmft-detail-row pmft-closed-detail" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Apr 02, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Energy</span> <span class="pmft-inline-note">(XLE)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $3.92</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 42</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 46</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 52</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>149 OI</span> <span class="pmft-inline-note">&middot; spread 14.1%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$103.55</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-new">$110p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$9.25</span> <span class="pmft-inline-note">&rarr;</span> <span>&mdash;</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>6 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.66 &middot; 38d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $111.39</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $115.31</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$100.51</span> <span class="pmft-inline-note"> (1.2% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$93.12</span> <span class="pmft-inline-note"> (6.3% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-next">&circlearrowright;1 $101.59</span><span class="pmft-roll-pending">&circlearrowright;2 $97.67</span><span class="pmft-roll-pending">&circlearrowright;3 $93.75</span><span class="pmft-roll-pending">&circlearrowright;4 $89.83</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$98.60&ndash;$100.51</span></div><div class="pmft-zone-sub">Undated &middot; 2.9% from entry &middot; $3.04</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$91.02&ndash;$93.12</span></div><div class="pmft-zone-sub">Undated &middot; 10.1% from entry &middot; $10.43</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$82.69&ndash;$85.38</span></div><div class="pmft-zone-sub">Undated &middot; 17.5% from entry &middot; $18.17</div></div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Closed winner. Exited via ob1 close inside after 1 days for +$1,663.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">1d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">37d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$5.80</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$1.12</div></div>
<div><div class="pmft-metric-label">Exit reason</div><div class="pmft-metric-value">ob1 close inside</div></div>
<div><div class="pmft-metric-label">Exit date</div><div class="pmft-metric-value">2026-04-08</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-closed-4" class="pmft-summary-row"  aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('closed-4')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'closed-4')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'closed-4')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">ICE</div><div class="pmft-cell-sub">No rolls</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-17</div><div class="pmft-cell-sub">signal Mar 13, 2026</div></td>
            <td><div class="pmft-cell-main">21d</div><div class="pmft-cell-sub">163d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-negative">$162.41 &rarr; $166.39</div><div class="pmft-cell-sub pmft-negative">+2.5%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-new">$180p</span></div><div class="pmft-cell-sub">$19.70 &rarr; $18.45 &middot; &delta; 0.79 &middot; 5ct</div></td>
            <td><div class="pmft-cell-main pmft-negative">$-632</div><div class="pmft-cell-sub pmft-negative">-18.0%</div></td>
            <td><div class="pmft-sector">Financials</div><div class="pmft-sector-sub">XLF</div></td>
          </tr>
          <tr id="pmft-detail-closed-4" class="pmft-detail-row pmft-closed-detail" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 13, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Financials</span> <span class="pmft-inline-note">(XLF)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $3.98</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 51</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 49</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 53</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>272 OI</span> <span class="pmft-inline-note">&middot; spread 14.2%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$162.41</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-new">$180p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$19.70</span> <span class="pmft-inline-note">&rarr;</span> <span>$18.45</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>5 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.79 &middot; 93d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $170.37</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $174.35</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$152.13</span> <span class="pmft-inline-note"> (8.6% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$146.21</span> <span class="pmft-inline-note"> (12.1% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-next">&circlearrowright;1 $160.42</span><span class="pmft-roll-pending">&circlearrowright;2 $156.44</span><span class="pmft-roll-pending">&circlearrowright;3 $152.46</span><span class="pmft-roll-pending">&circlearrowright;4 $148.48</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$144.18&ndash;$152.13</span></div><div class="pmft-zone-sub">Undated &middot; 6.3% from entry &middot; $10.28</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$143.17&ndash;$146.21</span></div><div class="pmft-zone-sub">Undated &middot; 10.0% from entry &middot; $16.20</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$142.29&ndash;$143.94</span></div><div class="pmft-zone-sub">Undated &middot; 11.4% from entry &middot; $18.47</div></div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-negative">Closed loser. Exited via ovtlyr flip to buy after 21 days for $-632.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">21d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">163d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$6.18</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$2.83</div></div>
<div><div class="pmft-metric-label">Exit reason</div><div class="pmft-metric-value">ovtlyr flip to buy</div></div>
<div><div class="pmft-metric-label">Exit date</div><div class="pmft-metric-value">2026-04-07</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-closed-5" class="pmft-summary-row"  aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('closed-5')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'closed-5')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'closed-5')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">ODFL</div><div class="pmft-cell-sub">No rolls</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-17</div><div class="pmft-cell-sub">signal Mar 11, 2026</div></td>
            <td><div class="pmft-cell-main">16d</div><div class="pmft-cell-sub">37d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-negative">$186.81 &rarr; $199.63</div><div class="pmft-cell-sub pmft-negative">+6.9%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-new">$220p</span></div><div class="pmft-cell-sub">$35.80 &rarr; $24.40 &middot; &delta; 0.82 &middot; 2ct</div></td>
            <td><div class="pmft-cell-main pmft-negative">$-2,283</div><div class="pmft-cell-sub pmft-negative">-65.2%</div></td>
            <td><div class="pmft-sector">Industrials</div><div class="pmft-sector-sub">XLI</div></td>
          </tr>
          <tr id="pmft-detail-closed-5" class="pmft-detail-row pmft-closed-detail" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 11, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Industrials</span> <span class="pmft-inline-note">(XLI)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $9.46</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 47</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 58</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 55</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>10 OI</span> <span class="pmft-inline-note">&middot; spread 16.8%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$186.81</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-new">$220p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$35.80</span> <span class="pmft-inline-note">&rarr;</span> <span>$24.40</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>2 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.82 &middot; 59d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $205.73</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $215.19</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$173.55</span> <span class="pmft-inline-note"> (13.1% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$173.30</span> <span class="pmft-inline-note"> (13.2% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-next">&circlearrowright;1 $182.08</span><span class="pmft-roll-pending">&circlearrowright;2 $172.62</span><span class="pmft-roll-pending">&circlearrowright;3 $163.16</span><span class="pmft-roll-pending">&circlearrowright;4 $153.70</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$168.00&ndash;$173.55</span></div><div class="pmft-zone-sub">Undated &middot; 7.4% from entry &middot; $13.85</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$169.99&ndash;$173.30</span></div><div class="pmft-zone-sub">Undated &middot; 7.5% from entry &middot; $14.10</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$156.00&ndash;$160.15</span></div><div class="pmft-zone-sub">Undated &middot; 14.5% from entry &middot; $27.25</div></div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-negative">Closed loser. Exited via ovtlyr flip to buy after 16 days for $-2,283.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">16d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">37d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$4.76</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$7.93</div></div>
<div><div class="pmft-metric-label">Exit reason</div><div class="pmft-metric-value">ovtlyr flip to buy</div></div>
<div><div class="pmft-metric-label">Exit date</div><div class="pmft-metric-value">2026-04-02</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-closed-6" class="pmft-summary-row"  aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('closed-6')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'closed-6')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'closed-6')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">MSTR</div><div class="pmft-cell-sub">No rolls</div></div></div></td>
            <td><div class="pmft-cell-main">2026-04-01</div><div class="pmft-cell-sub">signal Mar 26, 2026</div></td>
            <td><div class="pmft-cell-main">1d</div><div class="pmft-cell-sub">37d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$124.80 &rarr; $119.83</div><div class="pmft-cell-sub pmft-positive">-4.0%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-new">$165p</span></div><div class="pmft-cell-sub">$42.05 &rarr; ? &middot; &delta; 0.83 &middot; 2ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$825</div><div class="pmft-cell-sub pmft-positive">+23.6%</div></td>
            <td><div class="pmft-sector">Information Technology</div><div class="pmft-sector-sub">XLK</div></td>
          </tr>
          <tr id="pmft-detail-closed-6" class="pmft-detail-row pmft-closed-detail" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 26, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Information Technology</span> <span class="pmft-inline-note">(XLK)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $7.57</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 41</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 28</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 41</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>2,186 OI</span> <span class="pmft-inline-note">&middot; spread 7.8%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$124.80</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-new">$165p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$42.05</span> <span class="pmft-inline-note">&rarr;</span> <span>&mdash;</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>2 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.83 &middot; 44d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $139.94</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $147.51</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$122.00</span> <span class="pmft-inline-note"> (1.8% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$110.93</span> <span class="pmft-inline-note"> (7.4% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-next">&circlearrowright;1 $121.02</span><span class="pmft-roll-pending">&circlearrowright;2 $113.44</span><span class="pmft-roll-pending">&circlearrowright;3 $105.88</span><span class="pmft-roll-pending">&circlearrowright;4 $98.30</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$104.17&ndash;$122.00</span></div><div class="pmft-zone-sub">Undated &middot; 2.2% from entry &middot; $2.80</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$101.00&ndash;$110.93</span></div><div class="pmft-zone-sub">Undated &middot; 11.1% from entry &middot; $13.87</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$46.75&ndash;$50.86</span></div><div class="pmft-zone-sub">Undated &middot; 59.2% from entry &middot; $73.94</div></div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Closed winner. Exited via ob1 close inside after 1 days for +$825.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">1d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">37d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$6.73</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$1.20</div></div>
<div><div class="pmft-metric-label">Exit reason</div><div class="pmft-metric-value">ob1 close inside</div></div>
<div><div class="pmft-metric-label">Exit date</div><div class="pmft-metric-value">2026-04-02</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-closed-7" class="pmft-summary-row"  aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('closed-7')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'closed-7')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'closed-7')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">GFS</div><div class="pmft-cell-sub">1 roll &middot; +$3,870 credits</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-16</div><div class="pmft-cell-sub">signal Mar 12, 2026</div></td>
            <td><div class="pmft-cell-main">14d</div><div class="pmft-cell-sub">9d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$44.01 &rarr; $41.38</div><div class="pmft-cell-sub pmft-positive">-6.0%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-old">$50p</span><span class="pmft-strike-new">$45p</span></div><div class="pmft-cell-sub">$6.69 &rarr; ? &middot; &delta; 0.76 &middot; 9ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$5,669</div><div class="pmft-cell-sub pmft-positive">+162.0%</div></td>
            <td><div class="pmft-sector">Information Technology</div><div class="pmft-sector-sub">XLK</div></td>
          </tr>
          <tr id="pmft-detail-closed-7" class="pmft-detail-row pmft-closed-detail" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 12, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Information Technology</span> <span class="pmft-inline-note">(XLK)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">-8.7%</span> <span class="pmft-inline-note">&middot; ATR $2.52</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 46</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 56</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 50</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>244 OI</span> <span class="pmft-inline-note">&middot; spread 8.7%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$44.01</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-old">$50p</span><span class="pmft-strike-new">$45p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$6.69</span> <span class="pmft-inline-note">&rarr;</span> <span>&mdash;</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>9 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.76 &middot; 32d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $49.05</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $51.57</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$41.96</span> <span class="pmft-inline-note"> (1.4% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$35.62</span> <span class="pmft-inline-note"> (13.9% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-done">&circlearrowright;1 $42.75</span><span class="pmft-roll-next">&circlearrowright;2 $40.23</span><span class="pmft-roll-pending">&circlearrowright;3 $37.71</span><span class="pmft-roll-pending">&circlearrowright;4 $35.19</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$39.20&ndash;$41.96</span></div><div class="pmft-zone-sub">2026-02-03 &middot; 4.7% from entry &middot; $2.05</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$34.89&ndash;$35.62</span></div><div class="pmft-zone-sub">2025-12-31 &middot; 19.1% from entry &middot; $8.38</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$32.05&ndash;$33.78</span></div><div class="pmft-zone-sub">2025-11-20 &middot; 23.2% from entry &middot; $10.23</div></div>
</div>
                  <div class="pmft-roll-history">
<div class="pmft-roll-history-line">Roll #1 on 2026-03-16: $50p &rarr; $45p, credit $4.30/ct</div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Closed winner. Exited via ob1 close inside after 14 days for +$5,669.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">14d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">9d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$7.88</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$8.52</div></div>
<div><div class="pmft-metric-label">Risk removed</div><div class="pmft-metric-value pmft-positive">64%</div></div>
<div><div class="pmft-metric-label">Exit reason</div><div class="pmft-metric-value">ob1 close inside</div></div>
<div><div class="pmft-metric-label">Exit date</div><div class="pmft-metric-value">2026-03-30</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-closed-8" class="pmft-summary-row"  aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('closed-8')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'closed-8')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'closed-8')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">AVGO</div><div class="pmft-cell-sub">1 roll &middot; +$3,071 credits</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-18</div><div class="pmft-cell-sub">signal Mar 18, 2026</div></td>
            <td><div class="pmft-cell-main">12d</div><div class="pmft-cell-sub">9d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$315.93 &rarr; $293.41</div><div class="pmft-cell-sub pmft-positive">-7.1%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-old">$360p</span><span class="pmft-strike-new">$328p</span></div><div class="pmft-cell-sub">$46.65 &rarr; ? &middot; &delta; 0.84 &middot; 1ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$4,963</div><div class="pmft-cell-sub pmft-positive">+141.8%</div></td>
            <td><div class="pmft-sector">Information Technology</div><div class="pmft-sector-sub">XLK</div></td>
          </tr>
          <tr id="pmft-detail-closed-8" class="pmft-detail-row pmft-closed-detail" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 18, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Information Technology</span> <span class="pmft-inline-note">(XLK)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $12.99</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 41</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 46</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 64</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>1,543 OI</span> <span class="pmft-inline-note">&middot; spread 5.6%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$315.93</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-old">$360p</span><span class="pmft-strike-new">$328p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$46.65</span> <span class="pmft-inline-note">&rarr;</span> <span>&mdash;</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>1 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.84 &middot; 30d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $341.91</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $354.90</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$298.71</span> <span class="pmft-inline-note"> (1.8% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$295.49</span> <span class="pmft-inline-note"> (0.7% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-done">&circlearrowright;1 $309.44</span><span class="pmft-roll-next">&circlearrowright;2 $296.44</span><span class="pmft-roll-pending">&circlearrowright;3 $283.45</span><span class="pmft-roll-pending">&circlearrowright;4 $270.47</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$287.17&ndash;$298.71</span></div><div class="pmft-zone-sub">Undated &middot; 5.5% from entry &middot; $17.22</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$281.87&ndash;$295.49</span></div><div class="pmft-zone-sub">Undated &middot; 6.5% from entry &middot; $20.44</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$281.61&ndash;$292.64</span></div><div class="pmft-zone-sub">Undated &middot; 7.4% from entry &middot; $23.29</div></div>
</div>
                  <div class="pmft-roll-history">
<div class="pmft-roll-history-line">Roll #1 on 2026-03-19: $360p &rarr; $328p, credit $30.71/ct</div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Closed winner. Exited via ob1 close inside after 12 days for +$4,963.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">12d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">9d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$8.22</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$3.34</div></div>
<div><div class="pmft-metric-label">Risk removed</div><div class="pmft-metric-value pmft-positive">66%</div></div>
<div><div class="pmft-metric-label">Exit reason</div><div class="pmft-metric-value">ob1 close inside</div></div>
<div><div class="pmft-metric-label">Exit date</div><div class="pmft-metric-value">2026-03-30</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-closed-9" class="pmft-summary-row"  aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('closed-9')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'closed-9')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'closed-9')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">NDAQ</div><div class="pmft-cell-sub">1 roll &middot; +$1,400 credits</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-17</div><div class="pmft-cell-sub">signal Mar 16, 2026</div></td>
            <td><div class="pmft-cell-main">10d</div><div class="pmft-cell-sub">71d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$85.85 &rarr; $81.48</div><div class="pmft-cell-sub pmft-positive">-5.1%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-old">$98p</span><span class="pmft-strike-new">$95p</span></div><div class="pmft-cell-sub">$12.40 &rarr; ? &middot; &delta; 0.82 &middot; 7ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$3,908</div><div class="pmft-cell-sub pmft-positive">+111.7%</div></td>
            <td><div class="pmft-sector">Financials</div><div class="pmft-sector-sub">XLF</div></td>
          </tr>
          <tr id="pmft-detail-closed-9" class="pmft-detail-row pmft-closed-detail" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 16, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Financials</span> <span class="pmft-inline-note">(XLF)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $2.81</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 47</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 45</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 55</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>43 OI</span> <span class="pmft-inline-note">&middot; spread 17.7%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$85.85</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-old">$98p</span><span class="pmft-strike-new">$95p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$12.40</span> <span class="pmft-inline-note">&rarr;</span> <span>&mdash;</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>7 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.82 &middot; 93d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $91.47</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $94.28</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$81.58</span> <span class="pmft-inline-note"> (0.1% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$81.09</span> <span class="pmft-inline-note"> (0.5% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-done">&circlearrowright;1 $84.44</span><span class="pmft-roll-next">&circlearrowright;2 $81.63</span><span class="pmft-roll-pending">&circlearrowright;3 $78.82</span><span class="pmft-roll-pending">&circlearrowright;4 $76.01</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$78.90&ndash;$81.58</span></div><div class="pmft-zone-sub">Undated &middot; 5.0% from entry &middot; $4.27</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$77.09&ndash;$81.09</span></div><div class="pmft-zone-sub">Undated &middot; 5.5% from entry &middot; $4.76</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$64.84&ndash;$70.51</span></div><div class="pmft-zone-sub">Undated &middot; 17.9% from entry &middot; $15.34</div></div>
</div>
                  <div class="pmft-roll-history">
<div class="pmft-roll-history-line">Roll #1 on 2026-03-24: $98p &rarr; $95p, credit $2.00/ct</div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Closed winner. Exited via ob1 close inside after 10 days for +$3,908.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">10d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">71d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$5.65</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$1.93</div></div>
<div><div class="pmft-metric-label">Risk removed</div><div class="pmft-metric-value pmft-positive">16%</div></div>
<div><div class="pmft-metric-label">Exit reason</div><div class="pmft-metric-value">ob1 close inside</div></div>
<div><div class="pmft-metric-label">Exit date</div><div class="pmft-metric-value">2026-03-27</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-closed-10" class="pmft-summary-row"  aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('closed-10')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'closed-10')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'closed-10')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">AIG</div><div class="pmft-cell-sub">1 roll &middot; +$1,330 credits</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-17</div><div class="pmft-cell-sub">signal </div></td>
            <td><div class="pmft-cell-main">10d</div><div class="pmft-cell-sub">37d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$76.54 &rarr; $73.45</div><div class="pmft-cell-sub pmft-positive">-4.0%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-old">$80p</span><span class="pmft-strike-new">$78p</span></div><div class="pmft-cell-sub">$4.60 &rarr; ? &middot; &delta; 0.67 &middot; 14ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$4,228</div><div class="pmft-cell-sub pmft-positive">+120.8%</div></td>
            <td><div class="pmft-sector">Financials</div><div class="pmft-sector-sub">XLF</div></td>
          </tr>
          <tr id="pmft-detail-closed-10" class="pmft-detail-row pmft-closed-detail" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>&amp;mdash;</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Financials</span> <span class="pmft-inline-note">(XLF)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $1.82</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 43</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 46</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 46</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>113 OI</span> <span class="pmft-inline-note">&middot; spread 8.7%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$76.54</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-old">$80p</span><span class="pmft-strike-new">$78p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$4.60</span> <span class="pmft-inline-note">&rarr;</span> <span>&mdash;</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>14 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.67 &middot; 31d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $80.18</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $82.00</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$73.48</span> <span class="pmft-inline-note"> (0.0% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$72.43</span> <span class="pmft-inline-note"> (1.4% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-done">&circlearrowright;1 $75.63</span><span class="pmft-roll-next">&circlearrowright;2 $73.81</span><span class="pmft-roll-pending">&circlearrowright;3 $71.99</span><span class="pmft-roll-pending">&circlearrowright;4 $70.17</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$71.74&ndash;$73.48</span></div><div class="pmft-zone-sub">Undated &middot; 4.0% from entry &middot; $3.06</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$71.25&ndash;$72.43</span></div><div class="pmft-zone-sub">Undated &middot; 5.4% from entry &middot; $4.11</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$69.97&ndash;$71.65</span></div><div class="pmft-zone-sub">Undated &middot; 6.4% from entry &middot; $4.89</div></div>
</div>
                  <div class="pmft-roll-history">
<div class="pmft-roll-history-line">Roll #1 on 2026-03-18: $80p &rarr; $78p, credit $0.95/ct</div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Closed winner. Exited via ob1 close inside after 10 days for +$4,228.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">10d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">37d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$4.49</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$1.54</div></div>
<div><div class="pmft-metric-label">Risk removed</div><div class="pmft-metric-value pmft-positive">21%</div></div>
<div><div class="pmft-metric-label">Exit reason</div><div class="pmft-metric-value">ob1 close inside</div></div>
<div><div class="pmft-metric-label">Exit date</div><div class="pmft-metric-value">2026-03-27</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-closed-11" class="pmft-summary-row"  aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('closed-11')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'closed-11')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'closed-11')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">ANET</div><div class="pmft-cell-sub">1 roll &middot; +$4,290 credits</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-18</div><div class="pmft-cell-sub">signal Mar 18, 2026</div></td>
            <td><div class="pmft-cell-main">8d</div><div class="pmft-cell-sub">9d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$133.07 &rarr; $122.55</div><div class="pmft-cell-sub pmft-positive">-7.9%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-old">$155p</span><span class="pmft-strike-new">$140p</span></div><div class="pmft-cell-sub">$22.38 &rarr; ? &middot; &delta; 0.85 &middot; 3ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$6,973</div><div class="pmft-cell-sub pmft-positive">+199.2%</div></td>
            <td><div class="pmft-sector">Information Technology</div><div class="pmft-sector-sub">XLK</div></td>
          </tr>
          <tr id="pmft-detail-closed-11" class="pmft-detail-row pmft-closed-detail" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 18, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Information Technology</span> <span class="pmft-inline-note">(XLK)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $6.05</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 48</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 51</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 62</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>70 OI</span> <span class="pmft-inline-note">&middot; spread 13.6%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$133.07</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-old">$155p</span><span class="pmft-strike-new">$140p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$22.38</span> <span class="pmft-inline-note">&rarr;</span> <span>&mdash;</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>3 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.85 &middot; 30d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $145.17</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $151.22</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$126.83</span> <span class="pmft-inline-note"> (3.5% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$126.83</span> <span class="pmft-inline-note"> (3.5% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-done">&circlearrowright;1 $130.04</span><span class="pmft-roll-next">&circlearrowright;2 $123.99</span><span class="pmft-roll-pending">&circlearrowright;3 $117.94</span><span class="pmft-roll-pending">&circlearrowright;4 $111.89</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$121.63&ndash;$126.83</span></div><div class="pmft-zone-sub">Undated &middot; 4.7% from entry &middot; $6.24</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$122.37&ndash;$126.83</span></div><div class="pmft-zone-sub">Undated &middot; 4.7% from entry &middot; $6.24</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$120.00&ndash;$124.45</span></div><div class="pmft-zone-sub">Undated &middot; 6.5% from entry &middot; $8.61</div></div>
</div>
                  <div class="pmft-roll-history">
<div class="pmft-roll-history-line">Roll #1 on 2026-03-20: $155p &rarr; $140p, credit $14.30/ct</div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Closed winner. Exited via ob1 close inside after 8 days for +$6,973.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">8d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">9d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$7.94</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$3.86</div></div>
<div><div class="pmft-metric-label">Risk removed</div><div class="pmft-metric-value pmft-positive">64%</div></div>
<div><div class="pmft-metric-label">Exit reason</div><div class="pmft-metric-value">ob1 close inside</div></div>
<div><div class="pmft-metric-label">Exit date</div><div class="pmft-metric-value">2026-03-26</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-closed-12" class="pmft-summary-row"  aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('closed-12')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'closed-12')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'closed-12')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">MP</div><div class="pmft-cell-sub">1 roll &middot; +$2,784 credits</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-16</div><div class="pmft-cell-sub">signal Mar 16, 2026</div></td>
            <td><div class="pmft-cell-main">4d</div><div class="pmft-cell-sub">9d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$58.59 &rarr; $50.60</div><div class="pmft-cell-sub pmft-positive">-13.6%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-old">$70p</span><span class="pmft-strike-new">$65p</span></div><div class="pmft-cell-sub">$12.10 &rarr; ? &middot; &delta; 0.76 &middot; 6ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$6,427</div><div class="pmft-cell-sub pmft-positive">+183.6%</div></td>
            <td><div class="pmft-sector">Materials</div><div class="pmft-sector-sub">XLB</div></td>
          </tr>
          <tr id="pmft-detail-closed-12" class="pmft-detail-row pmft-closed-detail" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 16, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Materials</span> <span class="pmft-inline-note">(XLB)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">+2.9%</span> <span class="pmft-inline-note">&middot; ATR $3.60</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 46</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 50</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 67</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>394 OI</span> <span class="pmft-inline-note">&middot; spread 7.2%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$58.59</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-old">$70p</span><span class="pmft-strike-new">$65p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$12.10</span> <span class="pmft-inline-note">&rarr;</span> <span>&mdash;</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>6 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.76 &middot; 32d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $65.79</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $69.39</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$55.97</span> <span class="pmft-inline-note"> (10.6% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$51.20</span> <span class="pmft-inline-note"> (1.2% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-done">&circlearrowright;1 $56.79</span><span class="pmft-roll-next">&circlearrowright;2 $53.19</span><span class="pmft-roll-pending">&circlearrowright;3 $49.59</span><span class="pmft-roll-pending">&circlearrowright;4 $45.99</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$54.03&ndash;$55.97</span></div><div class="pmft-zone-sub">2026-02-23 &middot; 4.5% from entry &middot; $2.62</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$49.79&ndash;$51.20</span></div><div class="pmft-zone-sub">2025-12-31 &middot; 12.6% from entry &middot; $7.38</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$29.59&ndash;$31.30</span></div><div class="pmft-zone-sub">2025-07-09 &middot; 46.6% from entry &middot; $27.29</div></div>
</div>
                  <div class="pmft-roll-history">
<div class="pmft-roll-history-line">Roll #1 on 2026-03-19: $70p &rarr; $65p, credit $4.64/ct</div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Closed winner. Exited via ob2 close inside after 4 days for +$6,427.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">4d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">9d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$14.22</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$3.64</div></div>
<div><div class="pmft-metric-label">Risk removed</div><div class="pmft-metric-value pmft-positive">38%</div></div>
<div><div class="pmft-metric-label">Exit reason</div><div class="pmft-metric-value">ob2 close inside</div></div>
<div><div class="pmft-metric-label">Exit date</div><div class="pmft-metric-value">2026-03-20</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-closed-13" class="pmft-summary-row"  aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('closed-13')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'closed-13')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'closed-13')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">TTWO</div><div class="pmft-cell-sub">1 roll &middot; +$5,610 credits</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-17</div><div class="pmft-cell-sub">signal Mar 17, 2026</div></td>
            <td><div class="pmft-cell-main">3d</div><div class="pmft-cell-sub">9d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$207.69 &rarr; $200.63</div><div class="pmft-cell-sub pmft-positive">-3.4%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-old">$230p</span><span class="pmft-strike-new">$210p</span></div><div class="pmft-cell-sub">$24.20 &rarr; ? &middot; &delta; 0.80 &middot; 3ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$7,304</div><div class="pmft-cell-sub pmft-positive">+208.7%</div></td>
            <td><div class="pmft-sector">Communication Services</div><div class="pmft-sector-sub">XLC</div></td>
          </tr>
          <tr id="pmft-detail-closed-13" class="pmft-detail-row pmft-closed-detail" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 17, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Communication Services</span> <span class="pmft-inline-note">(XLC)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $6.30</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 45</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 40</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 51</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>27 OI</span> <span class="pmft-inline-note">&middot; spread 6.6%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$207.69</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-old">$230p</span><span class="pmft-strike-new">$210p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$24.20</span> <span class="pmft-inline-note">&rarr;</span> <span>&mdash;</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>3 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.80 &middot; 31d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $220.29</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $226.59</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$201.12</span> <span class="pmft-inline-note"> (0.2% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$194.68</span> <span class="pmft-inline-note"> (3.0% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-done">&circlearrowright;1 $204.54</span><span class="pmft-roll-next">&circlearrowright;2 $198.24</span><span class="pmft-roll-pending">&circlearrowright;3 $191.94</span><span class="pmft-roll-pending">&circlearrowright;4 $185.64</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$188.56&ndash;$201.12</span></div><div class="pmft-zone-sub">Undated &middot; 3.2% from entry &middot; $6.56</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$188.65&ndash;$194.68</span></div><div class="pmft-zone-sub">Undated &middot; 6.3% from entry &middot; $13.01</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$181.86&ndash;$184.53</span></div><div class="pmft-zone-sub">Undated &middot; 11.2% from entry &middot; $23.16</div></div>
</div>
                  <div class="pmft-roll-history">
<div class="pmft-roll-history-line">Roll #1 on 2026-03-18: $230p &rarr; $210p, credit $18.70/ct</div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Closed winner. Exited via ob1 close inside after 3 days for +$7,304.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">3d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">9d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$4.66</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$2.56</div></div>
<div><div class="pmft-metric-label">Risk removed</div><div class="pmft-metric-value pmft-positive">77%</div></div>
<div><div class="pmft-metric-label">Exit reason</div><div class="pmft-metric-value">ob1 close inside</div></div>
<div><div class="pmft-metric-label">Exit date</div><div class="pmft-metric-value">2026-03-20</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-closed-14" class="pmft-summary-row"  aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('closed-14')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'closed-14')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'closed-14')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">SMCI</div><div class="pmft-cell-sub">1 roll &middot; +$5,520 credits</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-17</div><div class="pmft-cell-sub">signal Mar 13, 2026</div></td>
            <td><div class="pmft-cell-main">1d</div><div class="pmft-cell-sub">9d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$32.48 &rarr; $30.35</div><div class="pmft-cell-sub pmft-positive">-6.6%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-old">$40p</span><span class="pmft-strike-new">$35p</span></div><div class="pmft-cell-sub">$7.90 &rarr; ? &middot; &delta; 0.85 &middot; 12ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$7,693</div><div class="pmft-cell-sub pmft-positive">+219.8%</div></td>
            <td><div class="pmft-sector">Information Technology</div><div class="pmft-sector-sub">XLK</div></td>
          </tr>
          <tr id="pmft-detail-closed-14" class="pmft-detail-row pmft-closed-detail" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 13, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Information Technology</span> <span class="pmft-inline-note">(XLK)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $1.63</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 54</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 45</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 47</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>2,299 OI</span> <span class="pmft-inline-note">&middot; spread 5.1%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$32.48</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-old">$40p</span><span class="pmft-strike-new">$35p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$7.90</span> <span class="pmft-inline-note">&rarr;</span> <span>&mdash;</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>12 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.85 &middot; 31d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $35.74</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $37.37</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$31.33</span> <span class="pmft-inline-note"> (3.2% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$30.41</span> <span class="pmft-inline-note"> (0.2% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-done">&circlearrowright;1 $31.66</span><span class="pmft-roll-next">&circlearrowright;2 $30.03</span><span class="pmft-roll-pending">&circlearrowright;3 $28.40</span><span class="pmft-roll-pending">&circlearrowright;4 $26.77</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$29.68&ndash;$31.33</span></div><div class="pmft-zone-sub">Undated &middot; 3.5% from entry &middot; $1.15</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$29.35&ndash;$30.41</span></div><div class="pmft-zone-sub">Undated &middot; 6.4% from entry &middot; $2.06</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$28.64&ndash;$30.17</span></div><div class="pmft-zone-sub">Undated &middot; 7.1% from entry &middot; $2.31</div></div>
</div>
                  <div class="pmft-roll-history">
<div class="pmft-roll-history-line">Roll #1 on 2026-03-17: $40p &rarr; $35p, credit $4.60/ct</div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Closed winner. Exited via ob1 close inside after 1 days for +$7,693.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">1d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">9d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$6.63</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$1.02</div></div>
<div><div class="pmft-metric-label">Risk removed</div><div class="pmft-metric-value pmft-positive">58%</div></div>
<div><div class="pmft-metric-label">Exit reason</div><div class="pmft-metric-value">ob1 close inside</div></div>
<div><div class="pmft-metric-label">Exit date</div><div class="pmft-metric-value">2026-03-18</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-closed-15" class="pmft-summary-row"  aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('closed-15')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'closed-15')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'closed-15')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">SJM</div><div class="pmft-cell-sub">1 roll &middot; +$4,200 credits</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-17</div><div class="pmft-cell-sub">signal Mar 11, 2026</div></td>
            <td><div class="pmft-cell-main">1d</div><div class="pmft-cell-sub">71d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$104.86 &rarr; $101.40</div><div class="pmft-cell-sub pmft-positive">-3.3%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-old">$120p</span><span class="pmft-strike-new">$110p</span></div><div class="pmft-cell-sub">$15.55 &rarr; ? &middot; &delta; 0.82 &middot; 5ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$5,619</div><div class="pmft-cell-sub pmft-positive">+160.5%</div></td>
            <td><div class="pmft-sector">Consumer Staples</div><div class="pmft-sector-sub">XLP</div></td>
          </tr>
          <tr id="pmft-detail-closed-15" class="pmft-detail-row pmft-closed-detail" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 11, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Consumer Staples</span> <span class="pmft-inline-note">(XLP)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $3.60</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 41</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 48</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 45</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>26 OI</span> <span class="pmft-inline-note">&middot; spread 19.9%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$104.86</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-old">$120p</span><span class="pmft-strike-new">$110p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$15.55</span> <span class="pmft-inline-note">&rarr;</span> <span>&mdash;</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>5 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.82 &middot; 93d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $112.06</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $115.66</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$102.79</span> <span class="pmft-inline-note"> (1.4% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$96.75</span> <span class="pmft-inline-note"> (4.6% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-done">&circlearrowright;1 $103.06</span><span class="pmft-roll-next">&circlearrowright;2 $99.46</span><span class="pmft-roll-pending">&circlearrowright;3 $95.86</span><span class="pmft-roll-pending">&circlearrowright;4 $92.26</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$100.67&ndash;$102.79</span></div><div class="pmft-zone-sub">Undated &middot; 2.0% from entry &middot; $2.11</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$94.18&ndash;$96.75</span></div><div class="pmft-zone-sub">Undated &middot; 7.8% from entry &middot; $8.16</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$93.30&ndash;$96.29</span></div><div class="pmft-zone-sub">Undated &middot; 8.2% from entry &middot; $8.61</div></div>
</div>
                  <div class="pmft-roll-history">
<div class="pmft-roll-history-line">Roll #1 on 2026-03-17: $120p &rarr; $110p, credit $8.40/ct</div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Closed winner. Exited via ob1 close inside after 1 days for +$5,619.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">1d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">71d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$4.74</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$1.17</div></div>
<div><div class="pmft-metric-label">Risk removed</div><div class="pmft-metric-value pmft-positive">54%</div></div>
<div><div class="pmft-metric-label">Exit reason</div><div class="pmft-metric-value">ob1 close inside</div></div>
<div><div class="pmft-metric-label">Exit date</div><div class="pmft-metric-value">2026-03-18</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
          <tr id="pmft-summary-closed-16" class="pmft-summary-row"  aria-expanded="false" role="button" tabindex="0" onclick="if(window.pmftToggleDetail){pmftToggleDetail('closed-16')}else{(function(row,id){var detail=document.getElementById('pmft-detail-'+id);if(!detail)return;var expanded=row.getAttribute('aria-expanded')==='true';row.setAttribute('aria-expanded',expanded?'false':'true');var chevron=row.querySelector('.pmft-row-chevron');if(chevron)chevron.textContent=expanded?'&#x25B8;':'&#x25BE;';detail.dataset.open=expanded?'false':'true';var group=row.dataset.group;if(group){var button=document.getElementById('pmft-group-btn-'+group);var groupOpen=!button||button.getAttribute('aria-expanded')==='true';detail.hidden=!(groupOpen&&detail.dataset.open==='true');}else{detail.hidden=expanded;}})(this,'closed-16')}" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();if(window.pmftToggleDetailFromKey){pmftToggleDetailFromKey(event,'closed-16')}else{this.click();}}">
            <td><div class="pmft-symbol-wrap"><span class="pmft-row-chevron">&#x25B8;</span><div><div class="pmft-symbol">BRO</div><div class="pmft-cell-sub">No rolls</div></div></div></td>
            <td><div class="pmft-cell-main">2026-03-17</div><div class="pmft-cell-sub">signal Mar 11, 2026</div></td>
            <td><div class="pmft-cell-main">1d</div><div class="pmft-cell-sub">71d DTE left</div></td>
            <td><div class="pmft-cell-main pmft-positive">$70.20 &rarr; $67.08</div><div class="pmft-cell-sub pmft-positive">-4.4%</div></td>
            <td><div class="pmft-cell-main"><span class="pmft-strike-new">$80p</span></div><div class="pmft-cell-sub">$10.85 &rarr; ? &middot; &delta; 0.77 &middot; 12ct</div></td>
            <td><div class="pmft-cell-main pmft-positive">+$2,883</div><div class="pmft-cell-sub pmft-positive">+82.4%</div></td>
            <td><div class="pmft-sector">Financials</div><div class="pmft-sector-sub">XLF</div></td>
          </tr>
          <tr id="pmft-detail-closed-16" class="pmft-detail-row pmft-closed-detail" data-open="false" hidden>
            <td colspan="7">
              <div class="pmft-detail-grid">
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Why It Triggered</div>
                  <div class="pmft-detail-line"><span class="pmft-label">OVTLYR sell</span><span>Mar 11, 2026</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Sector</span><span class="pmft-value-link">Financials</span> <span class="pmft-inline-note">(XLF)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">20d move</span><span class="pmft-neutral">&mdash;</span> <span class="pmft-inline-note">&middot; ATR $1.83</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">RSI</span><span class="pmft-neutral">D 47</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">W 35</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-neutral">M 38</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Liquidity</span><span>136 OI</span> <span class="pmft-inline-note">&middot; spread 13.8%</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">COT</span><span>neutral</span> <span class="pmft-inline-note">(1.0&times;)</span></div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Trade Setup</div>
                  <div class="pmft-detail-line"><span class="pmft-label">Entry stock</span><span>$70.20</span> <span class="pmft-inline-note">&middot; strike</span> <span class="pmft-strike-new">$80p</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Option mid</span><span>$10.85</span> <span class="pmft-inline-note">&rarr;</span> <span>&mdash;</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Contracts</span><span>12 ct</span> <span class="pmft-inline-note">&middot; &delta; 0.77 &middot; 93d at entry</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Stops</span><span class="pmft-caution">2 ATR $73.86</span> <span class="pmft-inline-note">&middot;</span> <span class="pmft-negative">3 ATR $75.69</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB1 target</span><span class="pmft-value-link">$68.61</span> <span class="pmft-inline-note"> (2.3% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">OB2 target</span><span class="pmft-value-link">$67.50</span> <span class="pmft-inline-note"> (0.6% below current)</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Roll ladder</span></div>
                  <div class="pmft-roll-ladder"><span class="pmft-roll-next">&circlearrowright;1 $69.28</span><span class="pmft-roll-pending">&circlearrowright;2 $67.45</span><span class="pmft-roll-pending">&circlearrowright;3 $65.62</span><span class="pmft-roll-pending">&circlearrowright;4 $63.80</span></div>
                  <div class="pmft-detail-line"><span class="pmft-label">Support zones</span></div>
                  <div class="pmft-zone-stack">
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$66.73&ndash;$68.61</span></div><div class="pmft-zone-sub">Undated &middot; 2.3% from entry &middot; $1.59</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$65.68&ndash;$67.50</span></div><div class="pmft-zone-sub">Undated &middot; 3.8% from entry &middot; $2.70</div></div>
<div class="pmft-zone"><div class="pmft-zone-main"><span class="pmft-value-link">$61.71&ndash;$62.77</span></div><div class="pmft-zone-sub">Undated &middot; 10.6% from entry &middot; $7.43</div></div>
</div>
                </div>
                <div class="pmft-detail-panel">
                  <div class="pmft-panel-title">Status / Outcome</div>
                  <div class="pmft-detail-line pmft-positive">Closed winner. Exited via ob1 close inside after 1 days for +$2,883.</div>
                  <div class="pmft-metric-grid">
<div><div class="pmft-metric-label">Days held</div><div class="pmft-metric-value ">1d</div></div>
<div><div class="pmft-metric-label">DTE left</div><div class="pmft-metric-value ">71d</div></div>
<div><div class="pmft-metric-label">Best move (MFE)</div><div class="pmft-metric-value pmft-positive">$5.28</div></div>
<div><div class="pmft-metric-label">Worst move (MAE)</div><div class="pmft-metric-value pmft-negative">$0.53</div></div>
<div><div class="pmft-metric-label">Exit reason</div><div class="pmft-metric-value">ob1 close inside</div></div>
<div><div class="pmft-metric-label">Exit date</div><div class="pmft-metric-value">2026-03-18</div></div>
</div>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="pmft-section">
    <div class="pmft-section-head">
      <div>
        <p class="pmft-section-title">Near misses</p>
        <p class="pmft-section-note">16 candidates that passed options but failed final filters.</p>
      </div>
    </div>
    <div class="pmft-table-wrap">
      <table class="pmft-table">
        <thead>
          <tr><th>Symbol</th><th>Screened</th><th>Filter Reason</th><th>Price</th><th>Sector</th></tr>
        </thead>
        <tbody>
          <tr><td><span class="pmft-symbol">GDS</span></td><td>2026-04-01</td><td>low OI: 0 vs 50 needed</td><td>$40.29</td><td>Information Technology</td></tr>
          <tr><td><span class="pmft-symbol">DT</span></td><td>2026-04-01</td><td>low OI: 53 vs 80 needed</td><td>$36.98</td><td>Information Technology</td></tr>
          <tr><td><span class="pmft-symbol">AMKR</span></td><td>2026-04-01</td><td>low OI: 0 vs 30 needed</td><td>$45.03</td><td>Information Technology</td></tr>
          <tr><td><span class="pmft-symbol">ADSK</span></td><td>2026-04-01</td><td>too close to support OB: 1.8% away (need &gt;2%) [ON_SUPPORT]</td><td>$239.40</td><td>Information Technology</td></tr>
          <tr><td><span class="pmft-symbol">PCOR</span></td><td>2026-04-01</td><td>low OI: 0 vs 35 needed</td><td>$57.00</td><td>Information Technology</td></tr>
          <tr><td><span class="pmft-symbol">LRCX</span></td><td>2026-04-01</td><td>monthly RSI bullish: 77.3</td><td>$213.66</td><td>Information Technology</td></tr>
          <tr><td><span class="pmft-symbol">GDS</span></td><td>2026-04-02</td><td>low OI: 0 vs 55 needed</td><td>$41.66</td><td>Information Technology</td></tr>
          <tr><td><span class="pmft-symbol">CSCO</span></td><td>2026-04-02</td><td>monthly RSI bullish: 71.2</td><td>$77.93</td><td>Information Technology</td></tr>
          <tr><td><span class="pmft-symbol">PCOR</span></td><td>2026-04-02</td><td>low OI: 0 vs 35 needed</td><td>$57.34</td><td>Information Technology</td></tr>
          <tr><td><span class="pmft-symbol">MU</span></td><td>2026-04-02</td><td>monthly RSI bullish: 73.8</td><td>$367.85</td><td>Information Technology</td></tr>
          <tr><td><span class="pmft-symbol">CSCO</span></td><td>2026-04-03</td><td>monthly RSI bullish: 72.2</td><td>$79.02</td><td>Information Technology</td></tr>
          <tr><td><span class="pmft-symbol">GDS</span></td><td>2026-04-03</td><td>low OI: 0 vs 45 needed</td><td>$39.91</td><td>Information Technology</td></tr>
          <tr><td><span class="pmft-symbol">PCOR</span></td><td>2026-04-03</td><td>low OI: 0 vs 35 needed</td><td>$58.02</td><td>Information Technology</td></tr>
          <tr><td><span class="pmft-symbol">BTU</span></td><td>2026-04-06</td><td>low OI: 9 vs 45 needed</td><td>$33.56</td><td>Energy</td></tr>
          <tr><td><span class="pmft-symbol">BTU</span></td><td>2026-04-07</td><td>low OI: 5 vs 45 needed</td><td>$33.03</td><td>Energy</td></tr>
          <tr><td><span class="pmft-symbol">BTU</span></td><td>2026-04-08</td><td>low OI: 5 vs 45 needed</td><td>$31.96</td><td>Energy</td></tr>
        </tbody>
      </table>
    </div>
  </section>
</div>

<script>
window.pmftToggleDetailFromKey = function(event, id) {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    window.pmftToggleDetail(id);
  }
};
window.pmftToggleGroupFromKey = function(event, group) {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    window.pmftToggleGroup(group);
  }
};
window.pmftRefreshGroup = function(group) {
  var button = document.getElementById('pmft-group-btn-' + group);
  if (!button) return;
  var expanded = button.getAttribute('aria-expanded') === 'true';
  var chevron = button.querySelector('.pmft-group-chevron');
  if (chevron) chevron.textContent = expanded ? '▾' : '▸';
  document.querySelectorAll('[data-group="' + group + '"]').forEach(function(row) {
    if (row.classList.contains('pmft-detail-row')) {
      row.hidden = !expanded || row.dataset.open !== 'true';
    } else {
      row.hidden = !expanded;
    }
  });
};
window.pmftToggleGroup = function(group) {
  var button = document.getElementById('pmft-group-btn-' + group);
  if (!button) return;
  var expanded = button.getAttribute('aria-expanded') === 'true';
  button.setAttribute('aria-expanded', expanded ? 'false' : 'true');
  window.pmftRefreshGroup(group);
};
window.pmftToggleDetail = function(id) {
  var summary = document.getElementById('pmft-summary-' + id);
  var detail = document.getElementById('pmft-detail-' + id);
  if (!summary || !detail) return;
  var expanded = summary.getAttribute('aria-expanded') === 'true';
  summary.setAttribute('aria-expanded', expanded ? 'false' : 'true');
  var chevron = summary.querySelector('.pmft-row-chevron');
  if (chevron) chevron.textContent = expanded ? '▸' : '▾';
  detail.dataset.open = expanded ? 'false' : 'true';
  var group = summary.dataset.group;
  if (group) {
    window.pmftRefreshGroup(group);
    return;
  }
  detail.hidden = expanded;
};
window.pmftInitTrades = function() {
  ['strong', 'watching', 'working', 'flat'].forEach(window.pmftRefreshGroup);
  document.querySelectorAll('.pmft-closed-detail').forEach(function(row) {
    row.hidden = row.dataset.open !== 'true';
  });
};
if (typeof document$ !== 'undefined') {
  document$.subscribe(window.pmftInitTrades);
}
window.pmftInitTrades();
</script>
## Known Limitations

1. **15 early picks have no entry_option_mid** — these predate the options dict being returned. Entry capital = $0 for those.
2. **OB-break polling not yet built** — `ob_watch_high` stored on near misses but nothing polls it yet
3. **Long screener near misses** — only short screener persists near misses. Long side doesn't yet.
4. **Backtest benchmark card** — not yet on dashboard (forward WR/PF vs targets)

## Next Steps

- [ ] Build OB-break polling for near misses
- [ ] Add benchmark card to daily dashboard (actual vs backtest WR/PF)
- [ ] 30-day review (mid-April): first meaningful sample
- [ ] 60-day review (mid-May): statistical confidence
