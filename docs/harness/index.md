# Agent Harness

This section documents the operating layer that sits between you and the AI models. Not the trading strategies, not the backtest results. The harness. The thing that makes an AI agent remember what happened yesterday, route work to the right model, block dangerous actions before they happen, and run 40 jobs a day without anyone touching a keyboard.

It started as a chatbot with some scripts. It turned into something closer to an operating system for AI agents.

## What the harness does

Five jobs, running all day:

1. **Remembers context.** File-based memory that persists across sessions, models, and restarts. The agent picks up where it left off because the state lives in files, not inside a model's context window.
2. **Routes work to the right model.** Claude handles orchestration. Codex handles bounded code tasks. Grok handles live web research. A local model on the Mac handles cheap triage. Each model does what it does best. None of them do everything.
3. **Enforces guardrails.** Every tool call gets logged. Writes to production files get blocked. Dangerous shell commands get flagged. External content gets sanitized through a local model before it enters the system. The agent has hands, but some doors are locked.
4. **Runs on a schedule.** Cron jobs fire screeners, monitors, health checks, and reports throughout the day. The agent does not wait to be asked. It wakes up, does the work, and goes back to sleep.
5. **Connects to outside systems.** Broker APIs for trade execution. Market data feeds for signals. Telegram for alerts and remote control. YouTube and X for research inputs. Each integration follows the same pattern: fetch, validate, act, log.

## What this section covers

| Page | What you'll find |
| --- | --- |
| [How We Got Here](how-we-got-here.md) | The path from chatbot to production agent, told through the mistakes that forced each upgrade |
| [System Architecture](architecture.md) | The actors, state stores, and design principles that hold it together |
| [Memory and Continuity](memory-and-continuity.md) | How the agent remembers things and how sessions hand off to each other |
| [Model Coordination](model-coordination.md) | Which model does what, and the routing rules that prevent waste |
| [Security and Guardrails](security-and-guardrails.md) | Audit trails, protected files, bash bypass detection, and external content sandboxing |
| [Scheduling and Operations](scheduling-and-operations.md) | The cron pipeline, health checks, and AI-powered triage |
| [Tool Integrations](tool-integrations.md) | How the agent talks to brokers, data feeds, messaging, and research tools |
| [Dev Pipeline](dev-pipeline.md) | The PLAN-BUILD-VERIFY-REVIEW-COMMIT-DEPLOY discipline |
| [Lessons and Failure Modes](lessons-and-failure-modes.md) | What broke, what we learned, and what we would build earlier next time |

## What this section does not cover

Trading rules, position sizing, backtest edge, or market analysis. Those live in the [Trading Plans](../plans/overview.md) section. This section is about the machine that runs the plans.

## If you're new here

Start with [How We Got Here](how-we-got-here.md) for the story, then [System Architecture](architecture.md) for the map. After that, pick the topic that matters most to you. If you run systems, go to Security and Scheduling. If you build things, go to Model Coordination and the Dev Pipeline. Everyone should read the Lessons page at the end.
