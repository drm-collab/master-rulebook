# Dev Pipeline

## Why the pipeline exists

Agents can write code fast. A trading system can lose money fast.

That combination is the reason the pipeline exists. A patch that compiles can still break a monitor. A patch that works in a toy run can still hit the wrong production path. A patch that passes both checks can still smuggle in a secret or an unintended edit. The harness treats those as different problems because they are different problems.

The pipeline is not there to slow down work. It is there to force evidence at the points where speed hides risk.

## The stages

The pipeline has six stages.

1. PLAN identifies scope, touched files, risks, the verification step, and the rollback path when the change is large enough to deserve one.
2. BUILD writes the code.
3. VERIFY compiles changed Python files and runs the smallest execution check that proves the change behaves as claimed.
4. REVIEW inspects the diff for secrets, unintended edits, and production-path risk.
5. COMMIT happens only when the operator asks for it.
6. DEPLOY happens only when the task includes deployment.

Not every change needs the same amount of planning. Every change needs verification and review.

## Three variants

The harness uses three pipeline variants because not all tasks deserve the same ceremony.

The quick fix is for one or two files with tight scope. It can skip PLAN, move through BUILD fast, and use a narrow verification step. The feature path is for larger changes, three or more files, or work that touches architecture, hooks, cron, or production paths. That path uses a full PLAN and a stronger VERIFY step. The production hotfix sits between them. It uses a micro-plan, the fastest safe verification, and a strict diff review.

The rule is stable across all three: change the paperwork, not the evidence standard.

## Automated enforcement

Some parts of the pipeline run without anyone remembering to ask.

`scripts/guardrails/run_guardrails.py` runs `py_compile` on changed Python files. If compilation fails, the pipeline stops there. The same guardrail runs a staged diff through the secret scanner. That scanner looks for concrete patterns such as API keys, bot tokens, bearer tokens, and private key blocks. If it finds one, the commit does not proceed.

The audit hook adds another layer. Every tool-based file modification gets logged. That means the operator can trace what changed even if the task jumped across models or scripts.

The last enforcement rule is social, but it is still hard: claims of completion without execution evidence are false. The workspace instructions say that in plain language because agents will otherwise stop at BUILD and report success with no proof.

## Skip bureaucracy, not evidence

This phrase became the pipeline's center of gravity because it draws the line in the right place.

A small fix does not need a design memo. A one-line typo fix does not need a committee. But the system still needs to know whether the file compiles and whether the diff touched something it should not have touched.

That distinction matters in practice. Teams often confuse process with rigor. The harness does not. It will let a quick fix skip PLAN when the scope is obvious. It will not let that same fix skip VERIFY or REVIEW.

In a trading system, speed is variable. Evidence is not. That is the whole point of the pipeline.
