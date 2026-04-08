# System Architecture

## The actors

Six things participate in this system. They do not all run at the same time, and most of them do not talk to each other directly.

**Human operator.** Sets goals, reviews results, approves risky actions, and makes final trading decisions. The harness reduces the operator's workload but never removes the operator from decisions that matter.

**Claude Code (Opus 4.6).** The orchestrator. Runs interactively during sessions, delegates to other models, reads and writes memory, manages state files, and makes tool calls. When the system needs judgment, Claude provides it. When the system needs speed or specialized capability, Claude delegates.

**Codex (GPT-5.4).** Handles bounded, parallel work. Code audits, builds, backtests, and design tasks get dispatched through a wrapper script that constrains filesystem access and budget. Codex does not see the operator's conversation. It receives a prompt file and returns a response file.

**Grok (xAI).** Handles live web research. Two delivery paths: a browser automation script that uses a Chrome session for free deep research, and an API wrapper for fast automated lookups. Grok searches the web. Claude does not.

**Local MLX model (Qwen3-Coder-Next).** Runs on the Mac Studio for zero-cost triage and analysis. The maintenance system sends health check reports to this model for prioritized assessment. If the local model is down, the system falls back to the Grok API automatically.

**Cron scheduler.** The heartbeat. Over 40 jobs run throughout the day on fixed schedules. Screeners, monitors, trackers, health checks, log watchers, and report generators all fire without human intervention. Cron is more reliable than session-based scheduling because it survives restarts, crashes, and closed laptops.

## Control plane vs work plane

The harness separates two concerns:

The **control plane** handles orchestration, memory, guardrails, and state management. It answers: what should happen, who should do it, what happened last time, and is this action safe.

The **work plane** handles the actual tasks. Screeners scan for trading signals. Monitors track positions. Backtests simulate strategies. Research agents search the web. The work plane does useful things. The control plane makes sure those things are done correctly and remembered.

This separation matters because the trading scripts change often, but the memory system, audit hook, and scheduling infrastructure barely change at all. New strategies get added to the work plane. The control plane stays stable.

## State stores

State lives in files, not inside any model. This is a deliberate choice. Files persist across sessions, models, and restarts. Model context windows do not.

**conversation\_state.json.** The thread ledger. Tracks active and closed threads with summaries, next steps, and metadata. When a new session starts, this file tells the agent what work is in progress across all channels.

**memory/\*.md files.** Long-term memory. Each file has YAML frontmatter with a name, description, and type (user, feedback, project, or reference). MEMORY.md is a short index that gets loaded every session. Individual memory files are loaded on demand when relevant.

**JSONL audit logs.** Every tool call gets a one-line JSON entry with timestamp, session ID, tool name, file path, blocked/warning status, and a command snippet. This is the forensic record.

**JSON state files.** Regime state, loss throttle, episode tracking, position data, signal diffs, and forward test results all live in dedicated JSON files. Scripts read and write these files. The dashboard reads all of them.

**Tracker JSON files.** The short tracker and Plan Alpha positions file hold every open and closed trade with full attribution: entry price, option details, roll history, P&L, exit reason, and timestamps.

## Design principles

Four rules that shaped every decision in the harness:

**Recoverability over cleverness.** The system should be easy to restart, easy to debug, and easy to understand after a crash. Files over databases. JSON over binary formats. Explicit state over inferred state.

**Explicit files over hidden state.** If a fact matters, it goes in a file with a name that describes what it contains. No relying on model memory, conversation history, or "the agent just knows."

**Fail-open on infrastructure, fail-closed on safety.** If the audit hook crashes, the tool call still executes. The session does not die because a logging script had a bug. But if a write targets a protected file, the action is blocked regardless of context.

**Skip bureaucracy, not evidence.** The development pipeline has stages for a reason. A quick fix does not need a full planning phase. But every code change needs verification (did it compile, did it run) and review (did it touch anything unexpected). Speed changes. Evidence requirements do not.
