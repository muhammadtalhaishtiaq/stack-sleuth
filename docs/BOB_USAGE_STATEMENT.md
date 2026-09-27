# IBM Bob Usage Statement — StackSleuth

## How IBM Bob Was Used

StackSleuth is an automated debugging agent that uses IBM Bob as its AI reasoning engine. Bob was used in the following ways during the hackathon:

### 1. Authentication & Setup
- Bob IDE 2.2.0 was installed and launched on the build machine.
- Bob API access was established via API key (Apikey auth scheme).
- Account: talhaishtiaq944.1@gmail.com (Talha M)
- Instance: 20260924-1905-4454-6162-abf9ecfcd88f (ibm-coding-challenge-uat, us-east)
- Team: ibm-hackathon-lablab (40 Bobcoins spending limit, 0 used at time of screenshot)

### 2. The Six Debugging Tasks
Bob's production inference API (the same models that power Bob IDE) was used for AI reasoning across the debugging loop. The local test execution (pytest, git bisect) ran on the build machine; Bob provided the analysis and reasoning.

| Task | Bob Usage | Evidence |
|------|-----------|----------|
| 1. Reproduce failure | Bob analyzed the test failure and identified the off-by-one boundary error root cause | bob-evidence/task-01-reproduce.md |
| 2. Bisect culprit | Bob analyzed git history and confirmed afcc8ee "refactor: simplify discount tier lookup" as the culprit commit | bob-evidence/task-02-bisect.md |
| 3. Draft patch | Bob drafted the fix: change `qty > 10` to `qty >= 10` | bob-evidence/task-03-propose.md |
| 4. Approve & verify | Human gate: patch held for explicit approval. Local pytest verified 10/10 green after fix | Local test output |
| 5. Second variant | Bob analyzed the SAVE10 coupon bug (5% instead of 10%) and provided the corrected mapping | bob-evidence/task-05-variant.md |
| 6. Hardening | Bob listed edge cases: negative quantities, non-numeric input, float quantities, extremely large numbers | bob-evidence/task-06-hardening.md |

### 3. MCP Integration
StackSleuth exposes its tools via a Model Context Protocol (MCP) server (`sleuth-mcp`) configured for Bob IDE. The `.bob/` directory contains:
- `mcp.json`: stdio wiring for the 7 tools
- `custom_modes.yaml`: sleuth-debugger mode definition
- `skills/systematic-debug/SKILL.md`: debugging workflow skill
- `rules/`: approval gate and evidence-first rules

Tools: `run_tests`, `reproduce`, `bisect`, `inspect_commit`, `propose_patch`, `apply_patch`, `log_evidence`.

### 4. What Ran Where
- **Bob (real):** All AI reasoning, root cause analysis, patch drafting, edge case identification via Bob's inference API.
- **Local (real):** Test execution (pytest), git operations (bisect), file I/O. These are deterministic operations that don't require AI.
- **Human (real):** Patch approval gate. No patch applies without explicit human approval.

## Bobcoin Usage
Bob API calls were made using the API key. Exact Bobcoin consumption was not verified through the dashboard at time of writing. The team's spending limit is 40 Bobcoins.

## Why Bob
The debugging loop requires an AI that can: (1) reason about test output and diffs, (2) identify root causes from code, (3) draft minimal fixes, and (4) generalize to new bug types. Bob's models provide exactly this reasoning capability.
