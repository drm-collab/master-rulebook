# Memory and Continuity

## Memory model

The harness keeps memory in files. That choice shapes the whole system.

Each memory note is a Markdown file with YAML frontmatter. The frontmatter carries three fields: `name`, `description`, and `type`. The body holds the durable fact. The file name gives the topic a stable home. The frontmatter makes the file readable by people and easy to index with scripts.

The harness uses four memory types. `user` files describe the operator, their habits, and facts that do not belong in source code. `feedback` files capture corrections and preferences, because those compound over time. `project` files hold live context for work that spans days or weeks. `reference` files point to outside systems, credentials locations, or infrastructure that the agent must remember without copying the source into code.

`MEMORY.md` is the index. The session loader reads it every time. That file should stay short, capped at 200 lines, because it exists to route the agent to the right note, not to store the whole world. If the index grows past that limit, retrieval quality drops and session startup slows down.

## How sessions start

Session startup is a script, not a ritual. `scripts/guardrails/session_start.py` is the entry point. It shells into the continuity loader, which reads the current thread state and assembles the session context before the agent answers anything.

Two files matter at the start. `conversation_state.json` tells the agent which threads are open, which are closed, what the last summary said, and what comes next. `session_memory_context.md` carries retrieved context for the current session when the loader finds relevant memory. If that file exists, the agent reads it and starts from there.

That handoff removes the usual reset between sessions. The operator does not need to restate what was in progress, which channel it came from, or what the next action should be. The context is already in files.

## Thread continuity

`conversation_state.json` is the thread ledger. It tracks active and closed threads, with fields for title, status, summary, next steps, channels seen, and timestamps such as `opened_at` and `last_activity`. The file also stores session-wide context such as the last model and the last session notes.

This file survives more than one boundary. It survives a new Claude session. It survives a handoff from webchat to Telegram. It survives model changes, because the state lives outside the model. That is the core point. The system does not depend on a single context window staying alive.

The file also gives the operator a clean answer to a hard question: what is still open? Without that ledger, half-finished work disappears into chat history.

## Writing good memory

Good memory files stay narrow. One topic per file. Short descriptions. Explicit decisions with dates when dates matter. If the note records a rule, name the condition and the outcome. If it records a correction, write the correction in the form future sessions can use.

Do not duplicate the same fact across three notes. Duplication creates drift, and drift creates false confidence. Link to the canonical note from the index and leave it there.

Memory should hold intent, constraints, preferences, and external pointers. Code should hold implementation. Git history should hold the edit trail. A memory file is the right place for "never make this repo public" or "use Tradier for price data." It is the wrong place for a line-by-line description of a function change. That belongs in the diff.

## Failure modes

The first failure mode is stale memory. A note can outlive the code that replaced it. When that happens, the note wins the retrieval battle and loses the truth test. The fix is simple and boring: verify retrieved context against current code before acting on it.

The second failure mode is duplicate entries. Two files cover the same topic, then one gets updated and the other does not. The operator reads one thing. The agent reads another.

The third failure mode is bloat. Once `MEMORY.md` turns into a long transcript, the index stops being an index. Keep the index short and push detail into topic files.

The fourth failure mode is over-trust. Retrieved context is a lead, not a verdict. The system still needs a check against source files and state files.

The fifth failure mode is time drift. Relative phrases such as "tomorrow" or "last week" rot fast. Use absolute dates in memory when a date affects action. A note that says "exit on Monday 03/23" still means something next month. A note that says "exit tomorrow" does not.
