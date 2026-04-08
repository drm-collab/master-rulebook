# How We Got Here

The harness was not designed. It was forced into existence by a series of problems that got worse until they were fixed. Every piece of infrastructure described in this section exists because something broke badly enough that leaving it unfixed was no longer an option.

## Phase 1: Chatbot with scripts

The system started as Claude Code with a pile of Python scripts. Ask it a question, get an answer, run a script manually, check the output. It worked well enough for research and one-off tasks.

The problems showed up fast:

- Every new session started from zero. The agent had no idea what happened yesterday. You had to re-explain context, re-state preferences, and re-describe the system layout every time.
- Scripts ran manually. If you forgot to run the screener before market open, it didn't run. If you forgot to check the monitor, nobody checked.
- The agent would give different advice in the afternoon than it gave in the morning because it had no record of the morning conversation.

At this point, the "system" was a person babysitting scripts and an AI that couldn't remember anything.

## Phase 2: Automation pressure

The trading system needed things done on a schedule. Screeners had to run before market open. Monitors had to check positions every minute. Health checks had to verify that everything was still running. Alerts had to fire when something went wrong.

Cron jobs solved the scheduling problem. But cron jobs created new problems:

- The screener ran, but nobody reviewed the output until hours later.
- Monitors crashed silently and nobody noticed until a position wasn't managed properly.
- Logs accumulated without rotation. State files grew without cleanup.
- Three different scripts all had their own Telegram alert logic, each with different formatting and error handling.

The agent could help with all of this, but only during active conversations. Between sessions, the system was on autopilot with no one watching.

Memory became the first real infrastructure investment. A file-based system where the agent could read what happened in prior sessions, pick up context from a thread tracker, and know what the current priorities were. Not because it was elegant, but because re-explaining everything every session was wasting hours a week.

## Phase 3: The incidents that forced structure

Three incidents turned the system from "scripts with memory" into a hardened harness.

**The Codex incident.** A Codex sub-agent was sent to do research on a strategy question. Instead of just researching, it autonomously edited `symbol_monitor.py`, a live trading file that executes real orders. The change had to be reverted. After that, protected file lists existed. Then bash bypass detection. Then the full audit hook. One unauthorized edit created an entire security layer.

**The public repo.** While setting up GitHub Pages for the wiki, the private workspace repository was accidentally made public. It contained trading strategies, API credentials in git history, and infrastructure details. It was reverted within 30 seconds, but the rule became permanent: the workspace repo never goes public under any circumstances. A separate public repo was created for the wiki, and a memory file was written to block the mistake from happening again.

**The Kelly sizing failure.** Backtests showed that Kelly criterion sizing produced better returns than fixed-fraction sizing. In live paper trading, Kelly sizing created a death spiral: a few consecutive losses shrank position sizes so dramatically that recovery became mathematically impractical once you added realistic transaction costs. Fixed-fraction sizing at 6% replaced it. The lesson was not about Kelly. It was that a good backtest is not the same as a good live system, and the harness needed to encode that kind of hard-won knowledge in memory so the mistake would never be repeated.

Each of these incidents left a scar in the system. The scars became guardrails. The guardrails became architecture.

## Phase 4: What became general-purpose

Somewhere during the third round of infrastructure fixes, the harness stopped being specific to trading. The patterns worked for any long-running agent system:

- Persistent memory that survives session boundaries
- Multi-model routing based on task type and cost
- Audit trails that log every tool call and block dangerous ones
- Scheduled automation with health monitoring and AI-powered triage
- A development pipeline that requires evidence before claiming completion
- Feedback loops where corrections accumulate over time instead of being forgotten

The trading use case drove the requirements. The harness itself is the transferable part. That is what the rest of this section documents.
