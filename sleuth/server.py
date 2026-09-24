#!/usr/bin/env python3
"""StackSleuth MCP server: bisect-driven debugging tools.

Every tool shells out to real pytest / git via subprocess. Nothing is
simulated, nothing is invented. The server never applies a patch without an
explicit human approval, and every stage can be written to the evidence log.

Run standalone (stdio transport) with:
    python3 sleuth/server.py
"""
import json
import re
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sleuth-mcp")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_DIR = PROJECT_ROOT / "evidence"
PROPOSALS_DIR = EVIDENCE_DIR / "proposals"
LOG_PATH = EVIDENCE_DIR / "sleuth_log.json"

MAX_DIFF_CHARS = 20000
MAX_BISECT_STEPS = 30


# ---------------------------------------------------------------- helpers

def _run(cmd, cwd, timeout=120, shell=False):
    return subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True,
        timeout=timeout, shell=shell,
    )


def _clean_pycache(repo: Path) -> None:
    """Remove stale bytecode so checkouts during bisect are evaluated fresh."""
    for p in repo.rglob("__pycache__"):
        shutil.rmtree(p, ignore_errors=True)


def _ensure_evidence() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_PATH.exists():
        LOG_PATH.write_text("[]\n", encoding="utf-8")


def _append_log(event: str, data: dict) -> int:
    _ensure_evidence()
    try:
        entries = json.loads(LOG_PATH.read_text(encoding="utf-8") or "[]")
    except json.JSONDecodeError:
        entries = []
    entries.append({
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "data": data,
    })
    LOG_PATH.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    return len(entries)


def _repo(repo_path: str) -> Path:
    repo = Path(repo_path)
    if not repo.is_dir():
        raise ValueError("repo_path is not a directory: %s" % repo_path)
    if not (repo / ".git").is_dir():
        raise ValueError("repo_path is not a git repo: %s" % repo_path)
    return repo


# ---------------------------------------------------------------- tools

@mcp.tool()
def run_tests(repo_path: str) -> dict:
    """Run the full pytest suite in repo_path.

    Returns a pass/fail summary with the ids of failing tests and the tail
    of the pytest output. Appends a run_tests entry to the evidence log.
    """
    repo = _repo(repo_path)
    _clean_pycache(repo)
    p = _run([sys.executable, "-m", "pytest", "--tb=no", "-q"], repo)
    out = (p.stdout or "") + (p.stderr or "")
    summary = {"ok": p.returncode == 0, "returncode": p.returncode}
    for key, pattern in (("passed", r"(\d+) passed"), ("failed", r"(\d+) failed"),
                         ("errors", r"(\d+) error")):
        m = re.search(pattern, out)
        summary[key] = int(m.group(1)) if m else 0
    failing = re.findall(r"^FAILED (\S+)", out, re.M)
    summary["failing_tests"] = failing
    summary["output_tail"] = "\n".join(out.strip().splitlines()[-15:])
    _append_log("run_tests", {
        "repo": str(repo), "passed": summary["passed"],
        "failed": summary["failed"], "failing_tests": failing,
    })
    return summary


@mcp.tool()
def reproduce(repo_path: str, test_id: str, runs: int = 3) -> dict:
    """Run a single failing test in isolation `runs` times.

    Confirms the failure is deterministic (fails every run) rather than
    flaky. Appends a reproduce entry to the evidence log.
    """
    repo = _repo(repo_path)
    _clean_pycache(repo)
    codes = []
    last_out = ""
    for _ in range(int(runs)):
        p = _run([sys.executable, "-m", "pytest", "--tb=short", "-q", test_id], repo)
        codes.append(p.returncode)
        last_out = (p.stdout or "") + (p.stderr or "")
    deterministic = all(c == 1 for c in codes)  # 1 == tests failed; 5 == not collected
    result = {
        "test_id": test_id,
        "runs": int(runs),
        "returncodes": codes,
        "failed_every_run": all(c != 0 for c in codes),
        "deterministic": deterministic,
        "output_tail": "\n".join(last_out.strip().splitlines()[-12:]),
    }
    _append_log("reproduce", {k: v for k, v in result.items() if k != "output_tail"})
    return result


@mcp.tool()
def bisect(repo_path: str, test_command: str, good_ref: str = "") -> dict:
    """Automate `git bisect` to find the commit that broke the build.

    test_command is a shell command evaluated at each bisected commit; it must
    exit 0 when the commit is good, 1 when bad, 125 when it cannot be
    evaluated (skip). The working tree must be clean. `git bisect reset` is
    always run afterwards. Appends a bisect entry to the evidence log.
    """
    repo = _repo(repo_path)
    # Untracked scratch files (pytest caches, etc.) don't affect checkouts;
    # only tracked modifications block the bisect.
    dirty = [l for l in _run(["git", "status", "--porcelain"], repo).stdout.splitlines()
             if not l.startswith("??")]
    if dirty:
        return {"ok": False, "error": "working tree has uncommitted changes; commit or stash first"}
    if not good_ref:
        roots = _run(["git", "rev-list", "--max-parents=0", "HEAD"], repo).stdout.strip().splitlines()
        if not roots:
            return {"ok": False, "error": "could not determine root commit"}
        good_ref = roots[0]

    steps = []
    culprit = None
    try:
        _run(["git", "bisect", "start"], repo)
        _run(["git", "bisect", "bad", "HEAD"], repo)
        _run(["git", "bisect", "good", good_ref], repo)
        for _ in range(MAX_BISECT_STEPS):
            _clean_pycache(repo)
            head = _run(["git", "rev-parse", "--short", "HEAD"], repo).stdout.strip()
            tp = _run(test_command, repo, shell=True, timeout=120)
            verdict = "good" if tp.returncode == 0 else ("bad" if tp.returncode == 1 else "skip")
            steps.append({"commit": head, "verdict": verdict, "rc": tp.returncode})
            bp = _run(["git", "bisect", verdict], repo)
            combined = (bp.stdout or "") + (bp.stderr or "")
            if "is the first bad commit" in combined:
                # NOTE: HEAD is still on the last tested commit here; git only
                # *reports* the culprit hash, it does not check it out.
                m = re.search(r"([0-9a-f]{7,40}) is the first bad commit", combined)
                if not m:
                    return {"ok": False, "error": "could not parse culprit", "steps": steps}
                culprit = _run(["git", "rev-parse", m.group(1)], repo).stdout.strip()
                break
        else:
            return {"ok": False, "error": "bisect did not converge", "steps": steps}
    finally:
        _run(["git", "bisect", "reset"], repo)
        _clean_pycache(repo)

    message = _run(["git", "log", "-1", "--format=%s", culprit], repo).stdout.strip()
    result = {"ok": True, "culprit": culprit, "message": message, "steps": steps}
    _append_log("bisect", {"culprit": culprit, "message": message,
                           "steps": [{"commit": s["commit"], "verdict": s["verdict"]} for s in steps]})
    return result


@mcp.tool()
def inspect_commit(repo_path: str, commit: str) -> dict:
    """Return the metadata and full diff of a commit as patch-drafting context."""
    repo = _repo(repo_path)
    meta = _run(["git", "show", "--no-patch", "--format=%H%n%an%n%ad%n%s%n%b", commit], repo)
    if meta.returncode != 0:
        return {"ok": False, "error": "unknown commit: %s" % commit}
    lines = meta.stdout.splitlines()
    diff_p = _run(["git", "show", "--format=", "--no-ext-diff", commit], repo)
    diff = diff_p.stdout or ""
    truncated = len(diff) > MAX_DIFF_CHARS
    result = {
        "ok": True,
        "hash": lines[0] if lines else commit,
        "author": lines[1] if len(lines) > 1 else "",
        "date": lines[2] if len(lines) > 2 else "",
        "subject": lines[3] if len(lines) > 3 else "",
        "body": "\n".join(lines[4:]).strip(),
        "diff": diff[:MAX_DIFF_CHARS],
        "diff_truncated": truncated,
    }
    _append_log("inspect_commit", {"commit": result["hash"], "subject": result["subject"]})
    return result


@mcp.tool()
def propose_patch(repo_path: str, test_id: str, culprit_commit: str,
                  patch_diff: str, rationale: str) -> dict:
    """Persist a patch proposal (unified diff + rationale) for human review.

    The patch is NEVER applied by this tool. Use apply_patch with
    approved=true after a human has reviewed the proposal.
    """
    _repo(repo_path)  # validate
    _ensure_evidence()
    proposal_id = uuid.uuid4().hex[:8]
    diff_path = PROPOSALS_DIR / ("%s.diff" % proposal_id)
    md_path = PROPOSALS_DIR / ("%s.md" % proposal_id)
    # Never strip the diff: trailing blank context lines are part of the hunk.
    if not patch_diff.endswith("\n"):
        patch_diff += "\n"
    diff_path.write_text(patch_diff, encoding="utf-8")
    md_path.write_text(
        "# Patch proposal %s\n\n- status: proposed\n- test: %s\n- culprit: %s\n"
        "- created: %s\n\n## Rationale\n\n%s\n" % (
            proposal_id, test_id, culprit_commit,
            datetime.now(timezone.utc).isoformat(), rationale.strip()),
        encoding="utf-8",
    )
    _append_log("propose_patch", {"proposal_id": proposal_id, "test_id": test_id,
                                  "culprit": culprit_commit})
    return {"ok": True, "proposal_id": proposal_id,
            "diff_path": str(diff_path), "rationale_path": str(md_path),
            "status": "proposed (NOT applied)"}


@mcp.tool()
def apply_patch(repo_path: str, proposal_id: str, approved: bool = False) -> dict:
    """Apply a proposed patch ONLY when approved=true is passed explicitly.

    This is the human gate: without approved=true the tool refuses and the
    working tree is untouched. After applying, the full test suite is re-run.
    """
    repo = _repo(repo_path)
    if approved is not True:
        _append_log("apply_patch_refused", {"proposal_id": proposal_id})
        return {"applied": False,
                "reason": "refused: explicit human approval required (pass approved=true)"}
    diff_path = PROPOSALS_DIR / ("%s.diff" % proposal_id)
    if not diff_path.exists():
        return {"applied": False, "reason": "unknown proposal_id: %s" % proposal_id}
    check = _run(["git", "apply", "--check", str(diff_path)], repo)
    if check.returncode != 0:
        return {"applied": False,
                "reason": "patch does not apply cleanly: %s" % (check.stderr.strip()[:500])}
    ap = _run(["git", "apply", str(diff_path)], repo)
    if ap.returncode != 0:
        return {"applied": False, "reason": "git apply failed: %s" % (ap.stderr.strip()[:500])}
    md_path = PROPOSALS_DIR / ("%s.md" % proposal_id)
    if md_path.exists():
        text = md_path.read_text(encoding="utf-8").replace("status: proposed", "status: applied")
        md_path.write_text(text, encoding="utf-8")
    tests = run_tests(str(repo))
    _append_log("apply_patch", {"proposal_id": proposal_id, "approved": True,
                                "tests_passed": tests.get("passed"),
                                "tests_failed": tests.get("failed")})
    return {"applied": True, "proposal_id": proposal_id,
            "verification": tests}


@mcp.tool()
def log_evidence(event: str, data: dict) -> dict:
    """Append a timestamped entry to evidence/sleuth_log.json."""
    n = _append_log(event, data or {})
    return {"ok": True, "event": event, "entries": n}


if __name__ == "__main__":
    _ensure_evidence()
    mcp.run()
