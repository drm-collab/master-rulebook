# Model Coordination

## Roles, not rankings

The harness does not ask one model to do everything. It routes work by fit.

Claude is the orchestrator. Claude reads the workspace, decides what kind of task is in front of it, dispatches bounded work, and judges the result. That role matters more than raw model quality because the system fails at the seams, not in the middle of a single answer.

Codex handles code. It audits diffs, writes patches, runs backtests, and reviews design changes that depend on the filesystem. Grok handles live web research. It fetches current information through either browser automation or the xAI API. The local MLX model handles cheap maintenance triage on the Mac Studio. It runs at no token cost and returns answers fast enough to sit in a health-check pipeline.

None of these roles imply a ranking. They describe tool fit. Codex is better at bounded code work than Grok. Grok is better at live research than Codex. The local model is worse at both, but cheap enough to use for routine triage.

## Decision matrix

The routing rules stay blunt on purpose. Code audit goes to Codex. Backtest goes to Codex. Design review for a patch goes to Codex. Live research goes to Grok browser, with three deep-research rounds when the claim matters. Quick lookup goes to the Grok API. Maintenance triage goes to the local MLX server first, with Grok as fallback if the local model is down.

Second opinions are a special case. When the system wants a check, not a delegate, Claude can send the same question to more than one model and compare the evidence. That only works if the prompt is concrete and the scoring rule is clear.

## Dispatch paths

`skills/codex/run_codex.sh` is the Codex wrapper. It reads a prompt file, writes a response file, and exposes a small set of switches that matter in practice: sandbox mode, writable paths, model override, and `--network` for tasks that need live data. The wrapper also injects a context-skip header by default so Codex does not burn tokens reading memory and continuity files before touching the task.

Grok has two paths. `skills/grok/grok_browser.py` drives a Chrome session on the debug port for deep research. Its default loop runs three rounds: first-pass search, gap-filling search, then synthesis. Each round carries an honesty constraint that tells Grok to cite URLs, flag uncertainty, and mark unsupported claims as unverified. `skills/grok/run_grok.sh` is the API path. It is cheaper to automate and supports flags such as `--search`, `--research`, and `--thinking`.

The local MLX path is plain HTTP. The server listens on port 8897 and exposes an OpenAI-compatible chat endpoint. Maintenance scripts post a prompt and read back a short triage result.

## Context transfer

Claude is the only model that sees the full workspace as part of its working loop. That makes Claude the control plane.

Grok never gets filesystem access. If Grok needs code context, Claude pastes the relevant file content into the prompt. The MLX server works the same way. It gets a report over HTTP, not a path to inspect.

Codex can receive disk access through its wrapper, but Claude still treats Codex as a bounded worker, not as a second orchestrator. The prompt should include the files that matter. That keeps the task narrow and avoids budget burn from blind exploration.

## Failure modes

The first coordination failure came from waste, not error. Codex would spend part of its budget exploring the workspace before addressing the task. The context-skip header in `run_codex.sh` fixed that by blocking irrelevant reads at the top of the prompt.

The second failure is Grok describing code it never saw. Grok is useful for current facts and outside research. It is not a source of truth for local implementation details. Claude has to verify those claims before it acts.

The third failure is model disagreement. Confidence is cheap. Evidence is not. When two models disagree, trust the one that points to code, logs, state files, or URLs that survive inspection.

The fourth failure is handoff loss. A thread starts in webchat, continues in Telegram, and returns to a new session later. `conversation_state.json` closes that gap. The file holds the open thread, the last summary, and the next step, so the model handoff does not erase the work.
