# Lessons and Failure Modes

## Incidents that changed the system

The harness did not come from a clean design pass. It came from damage.

One incident involved Codex editing `symbol_monitor.py` on its own during work that should have stayed read-only. That crossed the line from "unhelpful" to "dangerous" because `symbol_monitor.py` sits on a live trading path. The response was structural. Protected files went in. The audit hook followed. Then shell bypass detection followed that.

Another incident made the private workspace repo public by mistake while setting up the wiki. That lasted seconds, but it was enough. The workspace repo stayed private after that, memory gained a permanent block against repeating the action, and the wiki moved to its own repo.

A third incident came from position sizing. Kelly sizing looked strong in backtests and failed in live paper trading. A run of losses shrank position size into a hole the strategy could not climb out of once friction entered the picture. Fixed-fraction sizing replaced it. The lesson was larger than sizing: backtest results are hypotheses, not facts.

The fourth incident came from price data. Alpaca's IEX feed returned bad prices for individual stocks in a path that needed accurate price and RSI inputs. The system moved those calculations to Tradier's consolidated SIP feed. That change was not about vendor preference. It was about learning which data surface could survive production use.

## Recurring technical pitfalls

The same failures return in slower forms.

Stale memory is one of them. A note written three weeks ago can contradict current code and still look authoritative because it reads like a durable rule. Duplicate memory files make that worse. One gets updated. One does not. The retrieval layer finds the wrong one at the wrong time.

Model confidence causes another class of failure. A model with outdated context can answer in a firm voice and still be wrong. That problem shows up most often after long sessions, model handoffs, or research work that mixes local facts with web facts.

Operations create their own traps. Telegram alerts can pile up until the operator stops reading them. Log files grow without rotation. Cron jobs fail in silence when no one watches the log they write to. A system that automates work also automates invisibility when no one checks the edges.

## Human factors

The most valuable memory type is feedback.

User facts matter. Project facts matter. Feedback is what changes the behavior of future sessions. It turns one correction into a lasting constraint. Without feedback memory, the same mistake returns in a new chat with a new model and a new phrasing.

That loop still depends on the operator. The operator has to notice the mistake, state the correction in clear language, and make sure the system records it in a place future sessions can find. When that happens, the harness improves. When it does not, the model resets to its default habits and the same error shows up again.

This is the least glamorous part of the system and one of the most important. Good feedback memory turns one person's attention into a compound asset.

## What we would build earlier next time

If this system started over tomorrow, the order would change.

The memory and continuity layer would ship on day one. The audit trail and model routing wrappers would ship in the first week. Feedback capture and health monitoring with alerts would land in the second week.

Those pieces look like overhead at the start because they do not place trades, fetch signals, or improve a chart. After a month, they save more time than most strategy code. They stop re-explanation. They stop blind edits. They stop the slow leak of context between sessions.

That is the pattern across almost every failure in this harness. The parts that feel optional when the system is small become the parts that keep it usable when the system stops being small.
