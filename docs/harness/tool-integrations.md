# Tool Integrations

## Execution surfaces

The harness talks to brokers through plain REST APIs.

Tradier is the main market data surface for price series, RSI, and options chains. It also serves as a paper trading venue through the sandbox. Alpaca handles paper order execution. That split reflects a lesson learned in production: execution and data do not need to come from the same place.

Both integrations look for credentials in `~/.openclaw/.env` first. On macOS, they can fall back to the Keychain when the environment file is missing or the cron environment is thin. The scripts do not fail in silence. They print a detectable error string such as `ERROR: Tradier API key not found` or `ERROR: No Alpaca credentials`, then exit nonzero so the caller can see that auth failed and act on it.

## Signal and data inputs

OVTLYR is the signal feed for Plan M. The harness does not drive it through a browser in production. `ovtlyr_api.py` talks to the site through its AJAX endpoints with cookie-based authentication. Cookies come from the Apple SSO login flow and need refresh when they expire. That makes OVTLYR a useful feed, but also one that needs operational care.

X is another input, but not a trusted one. The harness uses `fetch_x.py` instead of generic web fetch tools. With the `--sanitize` flag, that script routes the content through the local content filter before the rest of the system sees it.

YouTube fills a different role. The system uses `youtube_transcript_api` to pull transcripts for research and review work, then treats that text as outside content in the same way it treats anything else from the internet.

## Human interface

Telegram is the human-facing shell around the harness.

The system uses three bots with separate roles. The alerts bot, `@MRB_serveralerts_bot`, pushes one-way notifications. The Claude proxy bot, `@Macstudio_claude_bot`, carries two-way chat with the Claude bridge. `@Ash_clw_bot` is the OpenClaw gateway bot. That split did not exist at the start. It arrived after the operator hit the limits of one bot trying to handle alerts, chat, and gateway traffic at once.

`trading_plans/production/infra/telegram_alerts.py` is the shared sender. More than 30 scripts route notifications through that one utility now, which means formatting, auth lookup, and error handling live in one place instead of thirty.

## Skills system

The harness packages reusable capabilities as skill directories. Each skill has a `SKILL.md` file that defines when to use it and how to run it. Most also carry a `feedback.log` file plus supporting scripts. That structure turns a one-off instruction into a reusable tool.

The pattern matters more than any single skill. Codex dispatch, Grok research, repo evaluation, transcript search, and content filtering all use the same shape. Before a skill runs, it reads its own `feedback.log`. That means corrections from prior sessions do not vanish into chat history. They become part of the tool.

## MCP and memory access

The memory system follows the same high-level idea as Nate B. Jones' Open Brain: persistent state exposed through a standard access pattern instead of hidden in a live chat. The implementation chooses files over SQL.

That tradeoff buys simplicity. A file-based store is easy to inspect, back up, diff, and repair by hand. It avoids a database dependency and keeps the control plane easy to restart.

The cost is search quality. Files do not give semantic lookup on their own. The harness needs an indexing or retrieval layer on top if it wants more than file names and keyword search. That is the price of staying simple at the storage layer.
