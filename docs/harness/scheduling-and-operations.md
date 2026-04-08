# Scheduling and Operations

## Cron as heartbeat

The harness runs on cron, not on hope.

More than 40 cron jobs fire across the trading day. That replaced session-bound loops such as `/loop`, which die when the laptop closes, the session crashes, or the model gets interrupted. Cron survives all of those failure modes. It wakes the scripts on time, whether anyone is in chat or not.

Each job writes to a log. State files capture outputs that need structure. The daily digest reads those state files and logs, then turns them into a dashboard and a Telegram summary. The result feels like a heartbeat because the system keeps moving without a live operator in front of it.

## The trading day

The day starts at 4:50 AM Pacific with maintenance health checks. That pass verifies the machine, the local models, the scheduler, credentials, and a set of production assumptions that can drift overnight.

At 5:15 AM, the X sentiment scan runs. It pulls the premarket read before the trading scripts start making watchlists.

At 5:55 AM and 6:05 AM, the Plan M long and short screeners run. The position monitor starts at 6:00 AM. By 6:15 AM and 6:25 AM, the short tracker and the symbol monitors take over. They keep watch during market hours, while the log watcher checks the health of the logging surface every five minutes.

The afternoon cycle is shorter. At 1:30 PM, the Plan Alpha screener runs. At 1:35 PM, the pattern tracker evaluates late entries and invalidations. At 1:45 PM, the Plan Alpha tracker updates, and the daily digest builds the operator-facing summary for the day.

## Health checks with AI triage

The maintenance pass does not guess. It runs a fixed set of deterministic checks, about 18 at the time of writing. The list covers the OpenClaw gateway, the MLX server on port 8897, `caffeinate`, OVTLYR cookies, cron freshness, WireGuard, the Tradier key, disk use, heartbeat freshness, the GCP failover VM, loss throttle state, screener output, and CVE scan or remediation state.

After the checks finish, the script writes a report and sends that report to the local MLX model for triage. The model returns a short prioritization with likely causes and suggested fixes. If the local server is down, the script falls back to the Grok API and labels the triage with the model that produced it. That small detail matters when the operator reads the report later. A local Qwen judgment and a Grok fallback are not the same thing.

## Log watcher

`log_watcher.py` runs every five minutes during market hours. It checks three layers at once: log freshness, process status, and structured error counts from JSONL logs.

The watcher also grew from a health checker into a screener summary surface. For the short screener, it reads the latest structured run log and reports bearish sectors, raw sell signal count, filter breakdown, and the split between new candidates, repeat candidates, and near misses. That turns a stale log file into an operational summary.

## Alert fatigue

The system sends a lot of Telegram. Blocks from the audit hook. Warnings from shell safety checks. Maintenance failures. Screener results. Daily summaries.

That volume creates its own risk. If every event looks urgent, none of them do.

The harness attacks the problem in two ways. It throttles repeat alert types with a five-minute cooldown, and it aggregates broad state into the daily digest. Those controls help. They do not solve the whole problem. The operator still needs signal discipline from the scripts themselves. A trading system that pages on every wobble trains its human to ignore the page.
