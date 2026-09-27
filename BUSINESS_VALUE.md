# StackSleuth — Business Value

## The Problem
Regression debugging is expensive. When a test breaks, a senior engineer spends 30 minutes to 3 hours: reproducing the failure, manually bisecting through commits, reading diffs, crafting a fix, and verifying. For teams with large codebases and frequent commits, this is a daily tax on velocity.

Worse, manual debugging is error-prone. Engineers guess at the culprit instead of proving it via bisect. They apply fixes without a clear approval trail. And the knowledge of "how we found it" is lost — there's no evidence log.

## The Solution
StackSleuth automates the entire debugging loop while keeping the human in control:

- **Speed:** What takes an engineer 1-3 hours, StackSleuth does in minutes (2 bisect steps, deterministic reproduction, instant patch proposal).
- **Correctness:** Bisect *proves* the culprit commit — no guessing. The patch is minimal and verified by re-running the full suite.
- **Safety:** Every patch is held at a human approval gate. Nothing is auto-applied. The engineer reviews the diff and rationale before saying go.
- **Auditability:** The append-only evidence log records every stage (detected → reproduced → bisected → proposed → approved → verified). For regulated industries, this is the debugging paper trail.
- **Generalization:** Task 5 proves it works on unseen bugs, not just the seeded demo. The loop is bug-type agnostic.

## Who Benefits
- **Engineering teams:** Faster incident resolution, less toil, more time for feature work.
- **SRE/On-call:** Automated first-responder for test failures in CI/CD pipelines.
- **Regulated industries (finance, healthcare):** The evidence log and human gate satisfy audit and compliance requirements for automated code changes.
- **IBM:** Showcases Bob's agent capabilities (MCP tools, iterative reasoning, human-in-the-loop) in a concrete, high-value workflow.

## Market
The AI code assistant market is crowded with autocomplete and chat. StackSleuth is different: it's an *autonomous debugging agent* with proof (bisect), safety (human gate), and evidence (audit log). This is the "SRE agent" category — high willingness to pay because it directly reduces MTTR (mean time to resolution) and engineering toil.
